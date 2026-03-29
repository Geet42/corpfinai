from langchain_openai import ChatOpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)


class AdvisoryGenerator:
    """Generate strategic advisory using LLM with structured financial data."""

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            self.llm = None

    def generate(
        self,
        ticker: str,
        company_data: dict,
        ratios: dict,
        scenarios: list,
    ) -> str:
        """Generate strategic advisory text."""
        if not self.llm:
            return self._fallback_advisory(ticker, company_data, ratios)

        sorted_periods = sorted(ratios.keys())
        latest = ratios.get(sorted_periods[-1], {}) if sorted_periods else {}

        prompt = f"""You are a senior investment banker providing strategic advisory.
Based on the following data for {ticker} ({company_data.get('name', '')}):

Sector: {company_data.get('sector', 'N/A')}
Industry: {company_data.get('industry', 'N/A')}
Market Cap: ${company_data.get('market_cap', 0) / 1e9:.1f}B

Latest Financial Metrics:
- Revenue Growth: {latest.get('revenue_growth', 'N/A')}
- EBITDA Margin: {latest.get('ebitda_margin', 'N/A')}
- Net Margin: {latest.get('net_margin', 'N/A')}
- Debt/Equity: {latest.get('debt_to_equity', 'N/A')}
- FCF Margin: {latest.get('fcf_margin', 'N/A')}

Scenario Analysis Results:
{self._format_scenarios(scenarios)}

Provide a concise strategic advisory covering:
1. Funding options (equity raise, debt issuance, convertible notes, etc.)
2. Strategic options (M&A targets, divestitures, partnerships)
3. Capital allocation recommendations
4. Key risks and mitigants

Keep it professional and label all suggestions as estimates.
DISCLAIMER: This is for educational purposes only, not investment advice."""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Advisory generation failed: {e}")
            return self._fallback_advisory(ticker, company_data, ratios)

    def _format_scenarios(self, scenarios) -> str:
        lines = []
        for s in scenarios:
            if isinstance(s, dict):
                a = s.get("assumptions", {})
                lines.append(
                    f"- {a.get('label', 'Scenario')}: "
                    f"DCF ${s.get('dcf_value', 0) / 1e6:,.0f}M, "
                    f"Implied Price ${s.get('implied_share_price', 0):,.2f}"
                )
            else:
                lines.append(
                    f"- {s.assumptions.label}: "
                    f"DCF ${s.dcf_value / 1e6:,.0f}M, "
                    f"Implied Price ${s.implied_share_price:,.2f}"
                )
        return "\n".join(lines) if lines else "No scenario data available."

    def _fallback_advisory(self, ticker, company_data, ratios) -> str:
        """Deterministic fallback when LLM is unavailable."""
        mc = company_data.get("market_cap", 0)
        sector = company_data.get("sector", "Unknown")

        sorted_periods = sorted(ratios.keys())
        latest = ratios.get(sorted_periods[-1], {}) if sorted_periods else {}
        d_e = latest.get("debt_to_equity", 0)

        advisory_parts = [
            f"Strategic Advisory for {company_data.get('name', ticker)} ({ticker})\n",
            f"Operating in the {sector} sector with a market cap of ${mc / 1e9:.1f}B.\n"
            if mc
            else "",
        ]

        if d_e and d_e < 0.5:
            advisory_parts.append(
                "The company maintains a conservative balance sheet with low leverage, "
                "providing capacity for strategic debt issuance to fund growth or acquisitions."
            )
        elif d_e and d_e > 1.5:
            advisory_parts.append(
                "Elevated leverage suggests the company should prioritize deleveraging "
                "before pursuing capital-intensive growth strategies."
            )

        advisory_parts.append(
            "\nDISCLAIMER: This is generated for educational purposes only "
            "and does not constitute investment advice."
        )

        return "\n".join(advisory_parts)
