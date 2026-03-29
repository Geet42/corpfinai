"""
Monte Carlo Simulation: Run N simulations with randomized assumptions
to produce a probability distribution of implied share prices.
"""

import numpy as np
from typing import Dict, List
from financial_engine.projections import ProjectionEngine
from models.valuation import ScenarioAssumptions
import logging

logger = logging.getLogger(__name__)


class MonteCarloSimulator:
    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
        self.engine = ProjectionEngine()

    def simulate(
        self,
        base_revenue: float,
        base_shares: float,
        avg_growth: float,
        avg_margin: float,
        avg_capex: float,
        growth_std: float = None,
        margin_std: float = None,
    ) -> Dict:
        """
        Run Monte Carlo simulation by randomizing key assumptions.
        Returns distribution statistics and histogram data.
        """
        if growth_std is None:
            growth_std = max(abs(avg_growth) * 0.3, 0.02)
        if margin_std is None:
            margin_std = max(abs(avg_margin) * 0.15, 0.02)

        prices = []
        dcf_values = []

        np.random.seed(42)  # Reproducible for demo

        for _ in range(self.n_simulations):
            # Randomize assumptions within reasonable bounds
            growth = np.random.normal(avg_growth, growth_std)
            growth = np.clip(growth, -0.3, 0.6)

            margin = np.random.normal(avg_margin, margin_std)
            margin = np.clip(margin, 0.01, 0.8)

            capex = np.random.normal(avg_capex, avg_capex * 0.2)
            capex = np.clip(capex, 0.01, 0.3)

            wacc = np.random.normal(0.10, 0.015)
            wacc = np.clip(wacc, 0.06, 0.15)

            terminal_growth = np.random.normal(0.025, 0.005)
            terminal_growth = np.clip(terminal_growth, 0.01, 0.04)

            # Ensure WACC > terminal growth
            if wacc <= terminal_growth:
                wacc = terminal_growth + 0.02

            assumptions = ScenarioAssumptions(
                label="MonteCarlo",
                revenue_growth_rate=float(growth),
                ebitda_margin=float(margin),
                capex_percent_revenue=float(capex),
                wacc=float(wacc),
                terminal_growth_rate=float(terminal_growth),
            )

            try:
                result = self.engine.project(assumptions, base_revenue, base_shares)
                if result.implied_share_price > 0:
                    prices.append(result.implied_share_price)
                    dcf_values.append(result.dcf_value)
            except Exception:
                continue

        if not prices:
            return {"error": "No valid simulations completed"}

        prices_arr = np.array(prices)

        # Build histogram bins
        n_bins = 30
        hist_counts, bin_edges = np.histogram(prices_arr, bins=n_bins)
        histogram = []
        for i in range(len(hist_counts)):
            histogram.append({
                "bin_start": round(float(bin_edges[i]), 2),
                "bin_end": round(float(bin_edges[i + 1]), 2),
                "count": int(hist_counts[i]),
                "label": f"${bin_edges[i]:.0f}-${bin_edges[i+1]:.0f}",
            })

        return {
            "n_simulations": len(prices),
            "mean_price": round(float(np.mean(prices_arr)), 2),
            "median_price": round(float(np.median(prices_arr)), 2),
            "std_dev": round(float(np.std(prices_arr)), 2),
            "percentile_5": round(float(np.percentile(prices_arr, 5)), 2),
            "percentile_25": round(float(np.percentile(prices_arr, 25)), 2),
            "percentile_75": round(float(np.percentile(prices_arr, 75)), 2),
            "percentile_95": round(float(np.percentile(prices_arr, 95)), 2),
            "min_price": round(float(np.min(prices_arr)), 2),
            "max_price": round(float(np.max(prices_arr)), 2),
            "histogram": histogram,
            "assumptions_used": {
                "growth_mean": round(avg_growth, 4),
                "growth_std": round(growth_std, 4),
                "margin_mean": round(avg_margin, 4),
                "margin_std": round(margin_std, 4),
            },
        }
