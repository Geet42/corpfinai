import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_engine.projections import ProjectionEngine
from financial_engine.sensitivity import SensitivityAnalyzer
from financial_engine.ratios import RatioAnalyzer
from financial_engine.comparables import ComparableAnalysis
from models.valuation import ScenarioAssumptions
from models.financials import IncomeStatement, BalanceSheet, CashFlowStatement


def test_projection_engine():
    engine = ProjectionEngine()
    assumptions = ScenarioAssumptions(
        label="Base",
        revenue_growth_rate=0.08,
        ebitda_margin=0.34,
        capex_percent_revenue=0.05,
        wacc=0.10,
        terminal_growth_rate=0.025,
    )
    result = engine.project(
        assumptions,
        latest_revenue=394000000000,
        latest_shares=15500000000,
    )
    assert result.dcf_value > 0
    assert result.implied_share_price > 0
    assert len(result.projected_revenue) == 5
    assert result.assumptions.label == "Base"


def test_dcf_wacc_greater_than_growth():
    """WACC must exceed terminal growth for valid DCF."""
    engine = ProjectionEngine()
    assumptions = ScenarioAssumptions(
        label="Invalid",
        revenue_growth_rate=0.05,
        ebitda_margin=0.30,
        capex_percent_revenue=0.05,
        wacc=0.02,
        terminal_growth_rate=0.03,
    )
    result = engine.project(assumptions, 100000000, 1000000)
    # Should handle gracefully (DCF = 0 when WACC <= growth)
    assert result.dcf_value == 0.0


def test_sensitivity_matrix():
    analyzer = SensitivityAnalyzer()
    cells = analyzer.generate_matrix(
        base_fcf=50000000000,
        shares=15500000000,
        wacc_range=[0.08, 0.10, 0.12],
        growth_range=[0.02, 0.03],
    )
    assert len(cells) == 6
    # Check that invalid cells (WACC <= growth) have price 0
    for cell in cells:
        if cell.wacc <= cell.terminal_growth:
            assert cell.implied_price == 0


def test_ratio_analyzer():
    income = [
        IncomeStatement(
            ticker="TEST", period="2023",
            revenue=100, cost_of_revenue=60, gross_profit=40,
            operating_expenses=20, operating_income=20,
            ebitda=25, net_income=15,
        ),
        IncomeStatement(
            ticker="TEST", period="2024",
            revenue=120, cost_of_revenue=70, gross_profit=50,
            operating_expenses=22, operating_income=28,
            ebitda=33, net_income=21,
        ),
    ]
    balance = [
        BalanceSheet(
            ticker="TEST", period="2024",
            total_assets=200, total_liabilities=80,
            total_equity=120, cash_and_equivalents=30,
            total_debt=50, current_assets=90, current_liabilities=40,
        ),
    ]
    cashflow = [
        CashFlowStatement(
            ticker="TEST", period="2024",
            operating_cash_flow=30, capital_expenditure=-5,
            free_cash_flow=25,
        ),
    ]
    analyzer = RatioAnalyzer()
    ratios = analyzer.analyze(income, balance, cashflow)
    assert "2024" in ratios
    assert abs(ratios["2024"]["revenue_growth"] - 0.2) < 0.001
    assert abs(ratios["2024"]["gross_margin"] - (50 / 120)) < 0.001


def test_comparable_analysis():
    comp = ComparableAnalysis()
    result = comp.compute_multiples(
        market_cap=3000000000000,
        net_debt=50000000000,
        ebitda=135000000000,
        net_income=100000000000,
        shares_outstanding=15500000000,
    )
    assert result["ev_ebitda"] is not None
    assert result["pe_ratio"] is not None
    assert result["ev_ebitda"] > 0
