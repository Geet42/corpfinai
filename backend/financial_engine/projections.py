from models.valuation import ScenarioAssumptions, ScenarioOutput
from typing import Dict
from datetime import datetime


class ProjectionEngine:
    PROJECTION_YEARS = 5

    def project(
        self,
        assumptions: ScenarioAssumptions,
        latest_revenue: float,
        latest_shares: float,
    ) -> ScenarioOutput:
        """Build 5-year projections from assumptions."""
        projected_revenue: Dict[str, float] = {}
        projected_ebitda: Dict[str, float] = {}
        projected_fcf: Dict[str, float] = {}

        base_year = datetime.now().year
        revenue = latest_revenue

        for year_offset in range(1, self.PROJECTION_YEARS + 1):
            year = str(base_year + year_offset)
            revenue = revenue * (1 + assumptions.revenue_growth_rate)
            ebitda = revenue * assumptions.ebitda_margin
            capex = revenue * assumptions.capex_percent_revenue
            # Simplified FCF = EBITDA - Capex (ignoring tax/WC for hackathon)
            fcf = ebitda - capex

            projected_revenue[year] = round(revenue, 2)
            projected_ebitda[year] = round(ebitda, 2)
            projected_fcf[year] = round(fcf, 2)

        # DCF Valuation
        dcf_value = self._dcf(
            fcf_projections=projected_fcf,
            wacc=assumptions.wacc,
            terminal_growth=assumptions.terminal_growth_rate,
        )

        implied_price = dcf_value / latest_shares if latest_shares else 0
        latest_ebitda = list(projected_ebitda.values())[-1]
        ev_ebitda = dcf_value / latest_ebitda if latest_ebitda else 0

        return ScenarioOutput(
            assumptions=assumptions,
            projected_revenue=projected_revenue,
            projected_ebitda=projected_ebitda,
            projected_fcf=projected_fcf,
            dcf_value=round(dcf_value, 2),
            implied_share_price=round(implied_price, 2),
            ev_ebitda_multiple=round(ev_ebitda, 2),
        )

    def _dcf(
        self, fcf_projections: dict, wacc: float, terminal_growth: float
    ) -> float:
        """Discounted Cash Flow with terminal value (Gordon Growth Model)."""
        if wacc <= terminal_growth:
            return 0.0

        years = sorted(fcf_projections.keys())
        pv_sum = 0.0
        for i, year in enumerate(years, 1):
            pv_sum += fcf_projections[year] / ((1 + wacc) ** i)

        # Terminal value
        last_fcf = fcf_projections[years[-1]]
        terminal_value = (last_fcf * (1 + terminal_growth)) / (
            wacc - terminal_growth
        )
        pv_terminal = terminal_value / ((1 + wacc) ** len(years))

        return pv_sum + pv_terminal
