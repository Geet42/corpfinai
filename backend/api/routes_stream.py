"""
SSE (Server-Sent Events) endpoint for real-time pipeline progress.
Streams each pipeline step as it completes so the frontend can update live.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
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
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _sse_event(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


async def _run_pipeline(ticker: str):
    """Generator that yields SSE events as each pipeline step completes."""
    ticker = ticker.upper()

    try:
        # ---- STEP 1: Ingestion ----
        yield _sse_event("step", {"step": "ingestion", "status": "running"})
        await asyncio.sleep(0)  # yield control

        yf_ingester = YahooFinanceIngester(ticker)
        profile = yf_ingester.get_profile()
        income_stmts = yf_ingester.get_income_statements()
        balance_sheets = yf_ingester.get_balance_sheets()
        cash_flows = yf_ingester.get_cash_flows()
        price_history = yf_ingester.get_price_history()

        filing_text = None
        try:
            sec = SECEdgarIngester(settings.SEC_USER_AGENT)
            filing_text = sec.get_latest_10k_text(ticker)
        except Exception as e:
            logger.warning(f"SEC EDGAR failed: {e}")

        website_text = None
        try:
            if profile.website:
                scraper = CompanyWebScraper()
                website_text = scraper.scrape_about_page(profile.website)
        except Exception as e:
            logger.warning(f"Web scrape failed: {e}")

        yield _sse_event("step", {
            "step": "ingestion",
            "status": "complete",
            "data": f"{len(income_stmts)} income, {len(balance_sheets)} balance, {len(cash_flows)} cashflow",
        })
        await asyncio.sleep(0)

        # ---- STEP 2: Storage ----
        yield _sse_event("step", {"step": "storage", "status": "running"})
        await asyncio.sleep(0)

        save_company(profile.model_dump(), raw_10k=filing_text, raw_website=website_text)
        for stmt in income_stmts:
            save_financials(ticker, stmt.period, "income", stmt.model_dump_json())
        for sheet in balance_sheets:
            save_financials(ticker, sheet.period, "balance", sheet.model_dump_json())
        for cf in cash_flows:
            save_financials(ticker, cf.period, "cashflow", cf.model_dump_json())

        yield _sse_event("step", {"step": "storage", "status": "complete"})
        await asyncio.sleep(0)

        # ---- STEP 2.5: RAG Ingest ----
        rag_chunks = 0
        if filing_text:
            yield _sse_event("step", {"step": "rag_ingest", "status": "running"})
            await asyncio.sleep(0)
            try:
                rag_chunks = ingest_filing(ticker, filing_text)
            except Exception as e:
                logger.warning(f"RAG ingest failed: {e}")
            yield _sse_event("step", {
                "step": "rag_ingest",
                "status": "complete",
                "data": f"{rag_chunks} chunks indexed",
            })
            await asyncio.sleep(0)

        # ---- STEP 3: Financial Analysis ----
        yield _sse_event("step", {"step": "financial_analysis", "status": "running"})
        await asyncio.sleep(0)

        ratio_analyzer = RatioAnalyzer()
        ratios = ratio_analyzer.analyze(income_stmts, balance_sheets, cash_flows)

        latest_revenue = income_stmts[0].revenue if income_stmts else 0
        latest_shares = (
            income_stmts[0].shares_outstanding
            if income_stmts and income_stmts[0].shares_outstanding
            else 1e9
        )

        growth_vals = [r.get("revenue_growth", 0.05) for r in ratios.values() if "revenue_growth" in r]
        margin_vals = [r.get("ebitda_margin", 0.2) for r in ratios.values() if "ebitda_margin" in r]
        capex_vals = [r.get("capex_intensity", 0.05) for r in ratios.values() if "capex_intensity" in r]

        avg_growth = max(-0.2, min(0.5, sum(growth_vals) / max(1, len(growth_vals))))
        avg_margin = max(0.01, min(0.8, sum(margin_vals) / max(1, len(margin_vals))))
        avg_capex = max(0.01, min(0.3, sum(capex_vals) / max(1, len(capex_vals))))

        projection_engine = ProjectionEngine()
        scenarios = [
            projection_engine.project(
                ScenarioAssumptions(label="Base", revenue_growth_rate=round(avg_growth, 4),
                    ebitda_margin=round(avg_margin, 4), capex_percent_revenue=round(avg_capex, 4),
                    wacc=0.10, terminal_growth_rate=0.025),
                latest_revenue, latest_shares),
            projection_engine.project(
                ScenarioAssumptions(label="Upside", revenue_growth_rate=round(avg_growth * 1.5, 4),
                    ebitda_margin=round(min(avg_margin * 1.1, 0.8), 4),
                    capex_percent_revenue=round(avg_capex * 0.9, 4),
                    wacc=0.09, terminal_growth_rate=0.03),
                latest_revenue, latest_shares),
            projection_engine.project(
                ScenarioAssumptions(label="Downside", revenue_growth_rate=round(max(avg_growth * 0.5, -0.1), 4),
                    ebitda_margin=round(max(avg_margin * 0.85, 0.01), 4),
                    capex_percent_revenue=round(min(avg_capex * 1.2, 0.3), 4),
                    wacc=0.12, terminal_growth_rate=0.02),
                latest_revenue, latest_shares),
        ]

        sensitivity_analyzer = SensitivityAnalyzer()
        last_fcf = list(scenarios[0].projected_fcf.values())[-1] if scenarios else 0
        sensitivity = sensitivity_analyzer.generate_matrix(
            last_fcf, latest_shares,
            wacc_range=[0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
            growth_range=[0.01, 0.015, 0.02, 0.025, 0.03],
        )

        comp_analysis = ComparableAnalysis()
        net_debt_val = (balance_sheets[0].total_debt - balance_sheets[0].cash_and_equivalents) if balance_sheets else 0
        comparables = comp_analysis.compute_multiples(
            market_cap=profile.market_cap or 0, net_debt=net_debt_val,
            ebitda=income_stmts[0].ebitda if income_stmts else 0,
            net_income=income_stmts[0].net_income if income_stmts else 0,
            shares_outstanding=latest_shares,
        )

        yield _sse_event("step", {"step": "financial_analysis", "status": "complete"})
        await asyncio.sleep(0)

        # ---- STEP 3.5: Monte Carlo Simulation ----
        yield _sse_event("step", {"step": "monte_carlo", "status": "running"})
        await asyncio.sleep(0)

        from financial_engine.monte_carlo import MonteCarloSimulator
        mc_sim = MonteCarloSimulator(n_simulations=1000)
        monte_carlo_result = mc_sim.simulate(
            base_revenue=latest_revenue,
            base_shares=latest_shares,
            avg_growth=avg_growth,
            avg_margin=avg_margin,
            avg_capex=avg_capex,
        )

        yield _sse_event("step", {
            "step": "monte_carlo",
            "status": "complete",
            "data": f"{monte_carlo_result.get('n_simulations', 0)} simulations",
        })
        await asyncio.sleep(0)

        # ---- STEP 4: AI Agent ----
        yield _sse_event("step", {"step": "ai_analysis", "status": "running"})
        await asyncio.sleep(0)

        agent_result = {"analysis": "", "traces": [], "steps_taken": 0}
        if settings.OPENAI_API_KEY:
            try:
                from agent.orchestrator import CorpFinAgent
                agent = CorpFinAgent()
                agent_result = agent.analyze(ticker)
            except Exception as e:
                logger.error(f"Agent failed: {e}")
                agent_result["analysis"] = f"Agent error: {str(e)}"
        else:
            agent_result["analysis"] = "Set OPENAI_API_KEY for AI agent analysis."

        yield _sse_event("step", {
            "step": "ai_analysis",
            "status": "complete",
            "data": f"{agent_result['steps_taken']} agent steps",
        })
        await asyncio.sleep(0)

        # ---- STEP 5: Output Generation ----
        yield _sse_event("step", {"step": "output_generation", "status": "running"})
        await asyncio.sleep(0)

        advisory_gen = AdvisoryGenerator()
        advisory_text = advisory_gen.generate(
            ticker, profile.model_dump(), ratios, [s.model_dump() for s in scenarios],
        )

        pptx_gen = PresentationGenerator()
        pptx_gen.generate(
            ticker, profile.model_dump(), ratios,
            [s.model_dump() for s in scenarios], advisory_text,
        )

        # PDF Memo
        from generators.memo_pdf import PDFMemoGenerator
        pdf_gen = PDFMemoGenerator()
        pdf_gen.generate(
            ticker=ticker,
            company=profile.model_dump(),
            ratios=ratios,
            scenarios=[s.model_dump() for s in scenarios],
            advisory=advisory_text,
            agent_analysis=agent_result.get("analysis", ""),
            monte_carlo=monte_carlo_result,
        )

        yield _sse_event("step", {"step": "output_generation", "status": "complete"})
        await asyncio.sleep(0)

        # ---- STEP 6: Quality Evaluation ----
        yield _sse_event("step", {"step": "evaluation", "status": "running"})
        await asyncio.sleep(0)

        from evaluation import EvaluationEngine
        eval_engine = EvaluationEngine()
        quality_checks = eval_engine.evaluate(
            ratios=ratios,
            scenarios=[s.model_dump() for s in scenarios],
            sensitivity=[c.model_dump() for c in sensitivity],
            company=profile.model_dump(),
            income_count=len(income_stmts),
            balance_count=len(balance_sheets),
            cashflow_count=len(cash_flows),
            rag_chunks=rag_chunks,
            agent_steps=agent_result["steps_taken"],
        )

        passed = sum(1 for c in quality_checks if c["passed"])
        total = len(quality_checks)
        yield _sse_event("step", {
            "step": "evaluation",
            "status": "complete",
            "data": f"{passed}/{total} checks passed",
        })
        await asyncio.sleep(0)

        # ---- FINAL: Send complete result ----
        final_data = {
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
            "monte_carlo": monte_carlo_result,
            "rag_chunks_indexed": rag_chunks,
            "exports": {"pptx": f"/api/export/{ticker}/pptx", "pdf": f"/api/export/{ticker}/pdf"},
            "quality_checks": quality_checks,
            "disclaimer": "Educational purposes only. Not investment advice.",
        }

        yield _sse_event("complete", final_data)

    except Exception as e:
        logger.error(f"SSE Pipeline failed: {e}", exc_info=True)
        yield _sse_event("error", {"message": str(e)})


@router.get("/analyze/{ticker}/stream")
async def analyze_company_stream(ticker: str):
    """SSE endpoint: streams pipeline progress in real-time."""
    return StreamingResponse(
        _run_pipeline(ticker),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
