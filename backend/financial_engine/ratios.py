from models.financials import IncomeStatement, BalanceSheet, CashFlowStatement
from typing import List, Dict


class RatioAnalyzer:
    def analyze(
        self,
        income: List[IncomeStatement],
        balance: List[BalanceSheet],
        cashflow: List[CashFlowStatement],
    ) -> Dict:
        """Compute historical ratios for trend analysis."""
        ratios = {}

        for stmt in income:
            period = stmt.period
            ratios[period] = {
                "gross_margin": (
                    stmt.gross_profit / stmt.revenue if stmt.revenue else 0
                ),
                "operating_margin": (
                    stmt.operating_income / stmt.revenue if stmt.revenue else 0
                ),
                "ebitda_margin": (
                    stmt.ebitda / stmt.revenue if stmt.revenue else 0
                ),
                "net_margin": (
                    stmt.net_income / stmt.revenue if stmt.revenue else 0
                ),
                "revenue": stmt.revenue,
                "ebitda": stmt.ebitda,
                "net_income": stmt.net_income,
            }

        # Revenue growth YoY
        sorted_income = sorted(income, key=lambda x: x.period)
        for i in range(1, len(sorted_income)):
            prev_rev = sorted_income[i - 1].revenue
            curr_rev = sorted_income[i].revenue
            period = sorted_income[i].period
            if prev_rev and prev_rev > 0:
                ratios[period]["revenue_growth"] = (curr_rev - prev_rev) / prev_rev
            else:
                ratios[period]["revenue_growth"] = 0

        # Balance sheet ratios
        for sheet in balance:
            period = sheet.period
            if period not in ratios:
                ratios[period] = {}
            ratios[period]["current_ratio"] = (
                sheet.current_assets / sheet.current_liabilities
                if sheet.current_liabilities
                else 0
            )
            ratios[period]["debt_to_equity"] = (
                sheet.total_debt / sheet.total_equity if sheet.total_equity else 0
            )
            ratios[period]["net_debt"] = (
                sheet.total_debt - sheet.cash_and_equivalents
            )
            ratios[period]["total_assets"] = sheet.total_assets
            ratios[period]["total_equity"] = sheet.total_equity
            ratios[period]["total_debt"] = sheet.total_debt

        # FCF metrics from cashflow
        for cf in cashflow:
            period = cf.period
            if period not in ratios:
                ratios[period] = {}
            matching_income = next(
                (s for s in income if s.period == period), None
            )
            if matching_income and matching_income.revenue:
                ratios[period]["fcf_margin"] = (
                    cf.free_cash_flow / matching_income.revenue
                )
                ratios[period]["capex_intensity"] = (
                    abs(cf.capital_expenditure) / matching_income.revenue
                )
            ratios[period]["free_cash_flow"] = cf.free_cash_flow
            ratios[period]["operating_cash_flow"] = cf.operating_cash_flow

        return ratios
