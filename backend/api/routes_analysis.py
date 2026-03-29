from fastapi import APIRouter, HTTPException
from ingestion.yahoo_finance import YahooFinanceIngester
from ingestion.sec_edgar import SECEdgarIngester
from ingestion.web_scraper import CompanyWebScraper
from financial_engine.ratios import RatioAnalyzer
from financial_engine.projections import ProjectionEngine
from financial_engine.sensitivity import SensitivityAnalyzer
from financial_engine.comparables import ComparableAnalysis
from generators.presentation import PresentationGenerator
from generators.advisory import AdvisoryGenerator
from agent.rag_engine import ingest_filing
from database.crud import save_company, save_financials
from models.valuation import ScenarioAssumptions
from config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze/{ticker}")
async def analyze_company(ticker: str):
    """Full pipeline: ingest -> store -> model -> analyze -> generate outputs."""
    ticker = ticker.upper()
    pipeline_log = []

    try:
        # ---- STEP 1: Data Ingestion ----
        pipeline_log.append({"step": "ingestion", "status": "running"})

        yf_ingester = YahooFinanceIngester(ticker)
        profile = yf_ingester.get_profile()
        income_stmts = yf_ingester.get_income_statements()
        balance_sheets = yf_ingester.get_balance_sheets()
        cash_flows = yf_ingester.get_cash_flows()
        price_history = yf_ingester.get_price_history()

        # SEC EDGAR (best-effort, non-blocking)
        filing_text = None
        try:
            sec = SECEdgarIngester(settings.SEC_USER_AGENT)
            filing_text = sec.get_latest_10k_text(ticker)
        except Exception as e:
            logger.warning(f"SEC EDGAR fetch failed (non-critical): {e}")

        # Web scrape (best-effort)
        website_text = None
        try:
            if profile.website:
                scraper = CompanyWebScraper()
                website_text = scraper.scrape_about_page(profile.website)
        except Exception as e:
            logger.warning(f"Web scrape failed (non-critical): {e}")

        pipeline_log.append({
            "step": "ingestion",
            "status": "complete",
            "data": (
                f"{len(income_stmts)} income stmts, "
                f"{len(balance_sheets)} balance sheets, "
                f"{len(cash_flows)} cashflow stmts"
            ),
        })

        # ---- STEP 2: Store in Database ----
        pipeline_log.append({"step": "storage", "status": "running"})
        save_company(
            profile.model_dump(), raw_10k=filing_text, raw_website=website_text
        )
        for stmt in income_stmts:
            save_financials(ticker, stmt.period, "income", stmt.model_dump_json())
        for sheet in balance_sheets:
            save_financials(ticker, sheet.period, "balance", sheet.model_dump_json())
        for cf in cash_flows:
            save_financials(ticker, cf.period, "cashflow", cf.model_dump_json())
        pipeline_log.append({"step": "storage", "status": "complete"})

        # ---- STEP 2.5: RAG Ingest (10-K filing into vector store) ----
        rag_chunks = 0
        if filing_text:
            try:
                pipeline_log.append({"step": "rag_ingest", "status": "running"})
                rag_chunks = ingest_filing(ticker, filing_text)
                pipeline_log.append({
                    "step": "rag_ingest",
                    "status": "complete",
                    "data": f"{rag_chunks} chunks indexed",
                })
            except Exception as e:
                logger.warning(f"RAG ingest failed (non-critical): {e}")
                pipeline_log.append({
                    "step": "rag_ingest",
                    "status": "complete",
                    "data": "skipped",
                })

        # ---- STEP 3: Financial Analysis (DETERMINISTIC) ----
        pipeline_log.append({"step": "financial_analysis", "status": "running"})

        ratio_analyzer = RatioAnalyzer()
        ratios = ratio_analyzer.analyze(income_stmts, balance_sheets, cash_flows)

        # Build 3 scenarios
        latest_revenue = income_stmts[0].revenue if income_stmts else 0
        latest_shares = (
            income_stmts[0].shares_outstanding
            if income_stmts and income_stmts[0].shares_outstanding
            else 1e9
        )

        # Calculate average historical metrics for base case
        growth_vals = [
            r.get("revenue_growth", 0.05)
            for r in ratios.values()
            if "revenue_growth" in r
        ]
        margin_vals = [
            r.get("ebitda_margin", 0.2)
            for r in ratios.values()
            if "ebitda_margin" in r
        ]
        capex_vals = [
            r.get("capex_intensity", 0.05)
            for r in ratios.values()
            if "capex_intensity" in r
        ]

        avg_growth = sum(growth_vals) / max(1, len(growth_vals))
        avg_margin = sum(margin_vals) / max(1, len(margin_vals))
        avg_capex = sum(capex_vals) / max(1, len(capex_vals))

        # Clamp values to reasonable ranges
        avg_growth = max(-0.2, min(0.5, avg_growth))
        avg_margin = max(0.01, min(0.8, avg_margin))
        avg_capex = max(0.01, min(0.3, avg_capex))

        projection_engine = ProjectionEngine()
        scenarios = [
            projection_engine.project(
                ScenarioAssumptions(
                    label="Base",
                    revenue_growth_rate=round(avg_growth, 4),
                    ebitda_margin=round(avg_margin, 4),
                    capex_percent_revenue=round(avg_capex, 4),
                    wacc=0.10,
                    terminal_growth_rate=0.025,
                ),
                latest_revenue,
                latest_shares,
            ),
            projection_engine.project(
                ScenarioAssumptions(
                    label="Upside",
                    revenue_growth_rate=round(avg_growth * 1.5, 4),
                    ebitda_margin=round(min(avg_margin * 1.1, 0.8), 4),
                    capex_percent_revenue=round(avg_capex * 0.9, 4),
                    wacc=0.09,
                    terminal_growth_rate=0.03,
                ),
                latest_revenue,
                latest_shares,
            ),
            projection_engine.project(
                ScenarioAssumptions(
                    label="Downside",
                    revenue_growth_rate=round(max(avg_growth * 0.5, -0.1), 4),
                    ebitda_margin=round(max(avg_margin * 0.85, 0.01), 4),
                    capex_percent_revenue=round(min(avg_capex * 1.2, 0.3), 4),
                    wacc=0.12,
                    terminal_growth_rate=0.02,
                ),
                latest_revenue,
                latest_shares,
            ),
        ]

        # Sensitivity matrix
        sensitivity_analyzer = SensitivityAnalyzer()
        last_fcf = list(scenarios[0].projected_fcf.values())[-1] if scenarios else 0
        sensitivity = sensitivity_analyzer.generate_matrix(
            last_fcf,
            latest_shares,
            wacc_range=[0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            growth_range=[0.01, 0.015, 0.02, 0.025, 0.03],
        )

        # Comparable multiples
        comp_analysis = ComparableAnalysis()
        net_debt_val = 0
        if balance_sheets:
            net_debt_val = (
                balance_sheets[0].total_debt - balance_sheets[0].cash_and_equivalents
            )
        comparables = comp_analysis.compute_multiples(
            market_cap=profile.market_cap or 0,
            net_debt=net_debt_val,
            ebitda=income_stmts[0].ebitda if income_stmts else 0,
            net_income=income_stmts[0].net_income if income_stmts else 0,
            shares_outstanding=latest_shares,
        )

        pipeline_log.append({"step": "financial_analysis", "status": "complete"})

        # ---- STEP 4: AI Agent Analysis ----
        pipeline_log.append({"step": "ai_analysis", "status": "running"})
        agent_result = {"analysis": "", "traces": [], "steps_taken": 0}
        if settings.OPENAI_API_KEY:
            try:
                from agent.orchestrator import CorpFinAgent

                agent = CorpFinAgent()
                agent_result = agent.analyze(ticker)
            except Exception as e:
                logger.error(f"Agent failed: {e}")
                agent_result = {
                    "analysis": f"Agent unavailable: {str(e)}",
                    "traces": [],
                    "steps_taken": 0,
                }
        else:
            agent_result["analysis"] = (
                "AI agent analysis requires an OpenAI API key. "
                "Set OPENAI_API_KEY in your .env file. "
                "The deterministic financial model above is fully functional."
            )
        pipeline_log.append({
            "step": "ai_analysis",
            "status": "complete",
            "steps": agent_result["steps_taken"],
        })

        # ---- STEP 5: Generate Outputs ----
        pipeline_log.append({"step": "output_generation", "status": "running"})

        # Advisory
        advisory_gen = AdvisoryGenerator()
        advisory_text = advisory_gen.generate(
            ticker,
            profile.model_dump(),
            ratios,
            [s.model_dump() for s in scenarios],
        )

        # PPTX
        pptx_gen = PresentationGenerator()
        pptx_path = pptx_gen.generate(
            ticker,
            profile.model_dump(),
            ratios,
            [s.model_dump() for s in scenarios],
            advisory_text,
        )
        pipeline_log.append({"step": "output_generation", "status": "complete"})

        return {
            "ticker": ticker,
            "company": profile.model_dump(),
            "ratios": ratios,
            "scenarios": [s.model_dump() for s in scenarios],
            "sensitivity": [c.model_dump() for c in sensitivity],
            "comparables": comparables,
            "agent_analysis": agent_result["analysis"],
            "agent_traces": agent_result["traces"],
            "advisory": advisory_text,
            "price_history": price_history,
            "pipeline_log": pipeline_log,
            "exports": {"pptx": f"/api/export/{ticker}/pptx", "pdf": f"/api/export/{ticker}/pdf"},
            "rag_chunks_indexed": rag_chunks,
            "disclaimer": (
                "This analysis is generated for educational purposes only. "
                "It does not constitute investment advice."
            ),
        }

    except Exception as e:
        logger.error(f"Pipeline failed for {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
