import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.company import CompanyProfile
from models.financials import IncomeStatement, BalanceSheet, CashFlowStatement
from models.valuation import ScenarioAssumptions, ScenarioOutput, SensitivityCell


def test_company_profile():
    profile = CompanyProfile(
        ticker="AAPL",
        name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        description="Apple designs and sells electronics.",
        website="https://apple.com",
        market_cap=3000000000000,
    )
    assert profile.ticker == "AAPL"
    assert profile.market_cap == 3000000000000


def test_income_statement():
    stmt = IncomeStatement(
        ticker="AAPL",
        period="2024",
        revenue=394000000000,
        cost_of_revenue=214000000000,
        gross_profit=180000000000,
        operating_expenses=55000000000,
        operating_income=125000000000,
        ebitda=135000000000,
        net_income=100000000000,
    )
    assert stmt.revenue == 394000000000
    assert stmt.period == "2024"


def test_scenario_assumptions():
    assumptions = ScenarioAssumptions(
        label="Base",
        revenue_growth_rate=0.08,
        ebitda_margin=0.34,
        capex_percent_revenue=0.05,
        wacc=0.10,
        terminal_growth_rate=0.025,
    )
    assert assumptions.label == "Base"
    assert assumptions.wacc == 0.10


def test_sensitivity_cell():
    cell = SensitivityCell(wacc=0.10, terminal_growth=0.025, implied_price=185.50)
    assert cell.implied_price == 185.50
