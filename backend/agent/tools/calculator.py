from langchain.tools import tool
from financial_engine.projections import ProjectionEngine
from financial_engine.sensitivity import SensitivityAnalyzer
from models.valuation import ScenarioAssumptions
import json


@tool
def run_scenario_analysis(
    latest_revenue: float,
    latest_shares: float,
    revenue_growth: float,
    ebitda_margin: float,
    capex_pct: float,
    wacc: float,
    terminal_growth: float,
    label: str = "Custom",
) -> str:
    """Run a financial scenario projection with DCF valuation.
    Provide assumptions and get 5-year projections with implied share price.
    Revenue/shares in raw numbers (e.g., 394000000000 for $394B).
    Rates as decimals (e.g., 0.08 for 8%)."""
    assumptions = ScenarioAssumptions(
        label=label,
        revenue_growth_rate=revenue_growth,
        ebitda_margin=ebitda_margin,
        capex_percent_revenue=capex_pct,
        wacc=wacc,
        terminal_growth_rate=terminal_growth,
    )
    engine = ProjectionEngine()
    result = engine.project(assumptions, latest_revenue, latest_shares)
    return result.model_dump_json(indent=2)


@tool
def run_sensitivity(base_fcf: float, shares: float) -> str:
    """Generate a WACC vs Terminal Growth sensitivity matrix for share price.
    Returns implied share prices across different WACC and growth rate combinations.
    base_fcf: the projected Year 5 free cash flow in raw numbers.
    shares: total shares outstanding."""
    analyzer = SensitivityAnalyzer()
    wacc_range = [0.07, 0.08, 0.09, 0.10, 0.11, 0.12]
    growth_range = [0.01, 0.015, 0.02, 0.025, 0.03]
    cells = analyzer.generate_matrix(base_fcf, shares, wacc_range, growth_range)
    return json.dumps([c.model_dump() for c in cells], indent=2)
