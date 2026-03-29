import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_engine.monte_carlo import MonteCarloSimulator
from evaluation import EvaluationEngine


def test_monte_carlo_basic():
    sim = MonteCarloSimulator(n_simulations=100)
    result = sim.simulate(
        base_revenue=394000000000,
        base_shares=15500000000,
        avg_growth=0.08,
        avg_margin=0.34,
        avg_capex=0.05,
    )
    assert "error" not in result
    assert result["n_simulations"] > 50  # Some might be filtered
    assert result["mean_price"] > 0
    assert result["median_price"] > 0
    assert result["percentile_5"] < result["percentile_95"]
    assert len(result["histogram"]) > 0


def test_monte_carlo_histogram_shape():
    sim = MonteCarloSimulator(n_simulations=500)
    result = sim.simulate(
        base_revenue=100000000000,
        base_shares=5000000000,
        avg_growth=0.05,
        avg_margin=0.25,
        avg_capex=0.04,
    )
    total_count = sum(b["count"] for b in result["histogram"])
    assert total_count == result["n_simulations"]


def test_evaluation_all_good():
    engine = EvaluationEngine()
    ratios = {
        "2023": {
            "gross_margin": 0.45, "ebitda_margin": 0.34,
            "net_margin": 0.25, "revenue_growth": 0.08,
        },
        "2024": {
            "gross_margin": 0.46, "ebitda_margin": 0.35,
            "net_margin": 0.26, "revenue_growth": 0.10,
        },
    }
    scenarios = [
        {"assumptions": {"label": "Base"}, "dcf_value": 3e12, "implied_share_price": 190},
        {"assumptions": {"label": "Upside"}, "dcf_value": 4e12, "implied_share_price": 250},
        {"assumptions": {"label": "Downside"}, "dcf_value": 2e12, "implied_share_price": 130},
    ]
    sensitivity = [{"implied_price": 180, "wacc": 0.1, "terminal_growth": 0.025}] * 25
    company = {"name": "Apple", "sector": "Tech", "industry": "Electronics", "market_cap": 3e12}

    checks = engine.evaluate(
        ratios=ratios, scenarios=scenarios, sensitivity=sensitivity,
        company=company, income_count=4, balance_count=4, cashflow_count=4,
        rag_chunks=50, agent_steps=5,
    )

    assert len(checks) > 8
    passed = sum(1 for c in checks if c["passed"])
    assert passed >= 8  # Most checks should pass with good data


def test_evaluation_catches_bad_data():
    engine = EvaluationEngine()
    ratios = {
        "2024": {
            "gross_margin": 5.0,  # 500% - invalid
            "ebitda_margin": 0.34,
            "net_margin": 0.25,
        },
    }
    scenarios = [
        {"assumptions": {"label": "Base"}, "dcf_value": 0, "implied_share_price": 0},
    ]

    checks = engine.evaluate(
        ratios=ratios, scenarios=scenarios, sensitivity=[],
        company={"name": "Bad"}, income_count=1, balance_count=0, cashflow_count=0,
        rag_chunks=0, agent_steps=0,
    )

    # Should have failures
    failed = [c for c in checks if not c["passed"]]
    assert len(failed) >= 2  # At least margin sanity + DCF failure


def test_evaluation_scenario_ordering():
    engine = EvaluationEngine()
    # Wrong ordering: downside > upside
    scenarios = [
        {"assumptions": {"label": "Base"}, "dcf_value": 2e12, "implied_share_price": 150},
        {"assumptions": {"label": "Upside"}, "dcf_value": 1e12, "implied_share_price": 80},
        {"assumptions": {"label": "Downside"}, "dcf_value": 3e12, "implied_share_price": 200},
    ]

    checks = engine.evaluate(
        ratios={"2024": {"gross_margin": 0.4, "ebitda_margin": 0.3, "net_margin": 0.2}},
        scenarios=scenarios, sensitivity=[{"implied_price": 100}] * 20,
        company={"name": "Test", "market_cap": 2e12},
        income_count=3, balance_count=3, cashflow_count=3,
        rag_chunks=10, agent_steps=3,
    )

    ordering_check = next((c for c in checks if c["name"] == "Scenario Ordering"), None)
    assert ordering_check is not None
    assert not ordering_check["passed"]
