from pydantic import BaseModel
from typing import Dict, List, Optional


class ScenarioAssumptions(BaseModel):
    label: str
    revenue_growth_rate: float
    ebitda_margin: float
    capex_percent_revenue: float
    wacc: float
    terminal_growth_rate: float


class ScenarioOutput(BaseModel):
    assumptions: ScenarioAssumptions
    projected_revenue: Dict[str, float]
    projected_ebitda: Dict[str, float]
    projected_fcf: Dict[str, float]
    dcf_value: float
    implied_share_price: float
    ev_ebitda_multiple: float


class SensitivityCell(BaseModel):
    wacc: float
    terminal_growth: float
    implied_price: float


class ValuationSummary(BaseModel):
    ticker: str
    current_price: float
    scenarios: List[ScenarioOutput]
    sensitivity_matrix: List[SensitivityCell]
    comparable_ev_ebitda: Optional[float] = None
    comparable_pe: Optional[float] = None
