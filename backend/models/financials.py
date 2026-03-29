from pydantic import BaseModel
from typing import Optional


class IncomeStatement(BaseModel):
    ticker: str
    period: str
    revenue: float
    cost_of_revenue: float
    gross_profit: float
    operating_expenses: float
    operating_income: float
    ebitda: float
    net_income: float
    eps: Optional[float] = None
    shares_outstanding: Optional[float] = None


class BalanceSheet(BaseModel):
    ticker: str
    period: str
    total_assets: float
    total_liabilities: float
    total_equity: float
    cash_and_equivalents: float
    total_debt: float
    current_assets: float
    current_liabilities: float


class CashFlowStatement(BaseModel):
    ticker: str
    period: str
    operating_cash_flow: float
    capital_expenditure: float
    free_cash_flow: float
    dividends_paid: Optional[float] = 0
    share_buybacks: Optional[float] = 0
