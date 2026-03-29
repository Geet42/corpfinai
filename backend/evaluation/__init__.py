"""
Evaluation Engine: Automated quality checks on pipeline outputs.
Validates financial data integrity, model sanity, and output completeness.
Each check returns pass/fail with explanation - shown in pipeline traces.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class QualityCheck:
    def __init__(self, name: str, passed: bool, detail: str, severity: str = "warning"):
        self.name = name
        self.passed = passed
        self.detail = detail
        self.severity = severity  # "info", "warning", "critical"

    def to_dict(self):
        return {
            "name": self.name,
            "passed": self.passed,
            "detail": self.detail,
            "severity": self.severity,
            "icon": "✅" if self.passed else ("⚠️" if self.severity == "warning" else "❌"),
        }


class EvaluationEngine:
    """Run quality checks across all pipeline outputs."""

    def evaluate(
        self,
        ratios: dict,
        scenarios: list,
        sensitivity: list,
        company: dict,
        income_count: int,
        balance_count: int,
        cashflow_count: int,
        rag_chunks: int,
        agent_steps: int,
    ) -> List[Dict]:
        checks = []

        # ---- Data Completeness Checks ----
        checks.append(self._check_data_completeness(
            income_count, balance_count, cashflow_count
        ))
        checks.append(self._check_company_profile(company))
        checks.append(self._check_rag_coverage(rag_chunks))

        # ---- Financial Ratio Sanity ----
        checks.extend(self._check_ratio_sanity(ratios))

        # ---- DCF Model Sanity ----
        checks.extend(self._check_dcf_sanity(scenarios))

        # ---- Sensitivity Matrix Sanity ----
        checks.append(self._check_sensitivity_sanity(sensitivity))

        # ---- Agent Completeness ----
        checks.append(self._check_agent_execution(agent_steps))

        # ---- Cross-Validation ----
        checks.append(self._check_cross_validation(scenarios, company))

        return [c.to_dict() for c in checks]

    def _check_data_completeness(self, income: int, balance: int, cashflow: int) -> QualityCheck:
        total = income + balance + cashflow
        if total >= 9:  # 3+ years of all 3 statements
            return QualityCheck("Data Completeness", True,
                f"{income} income, {balance} balance, {cashflow} cashflow statements ingested")
        elif total >= 3:
            return QualityCheck("Data Completeness", True,
                f"Partial data: {income} income, {balance} balance, {cashflow} cashflow",
                severity="warning")
        else:
            return QualityCheck("Data Completeness", False,
                f"Insufficient data: only {total} statements found", severity="critical")

    def _check_company_profile(self, company: dict) -> QualityCheck:
        required = ["name", "sector", "industry", "market_cap"]
        missing = [f for f in required if not company.get(f)]
        if not missing:
            return QualityCheck("Company Profile", True,
                f"{company.get('name', 'Unknown')} - all key fields present")
        return QualityCheck("Company Profile", False,
            f"Missing fields: {', '.join(missing)}", severity="warning")

    def _check_rag_coverage(self, chunks: int) -> QualityCheck:
        if chunks >= 20:
            return QualityCheck("10-K RAG Index", True,
                f"{chunks} chunks indexed - qualitative analysis available")
        elif chunks > 0:
            return QualityCheck("10-K RAG Index", True,
                f"Only {chunks} chunks - limited qualitative coverage", severity="warning")
        else:
            return QualityCheck("10-K RAG Index", False,
                "No 10-K filing indexed - qualitative analysis unavailable", severity="warning")

    def _check_ratio_sanity(self, ratios: dict) -> List[QualityCheck]:
        checks = []
        if not ratios:
            checks.append(QualityCheck("Ratio Analysis", False,
                "No ratios computed", severity="critical"))
            return checks

        latest_period = sorted(ratios.keys())[-1]
        latest = ratios[latest_period]

        # Margin bounds check
        for margin_key, label in [
            ("gross_margin", "Gross Margin"),
            ("ebitda_margin", "EBITDA Margin"),
            ("net_margin", "Net Margin"),
        ]:
            val = latest.get(margin_key)
            if val is not None:
                if -1.0 <= val <= 1.0:
                    checks.append(QualityCheck(f"{label} Sanity", True,
                        f"{label} = {val:.1%} (within expected range)"))
                else:
                    checks.append(QualityCheck(f"{label} Sanity", False,
                        f"{label} = {val:.1%} - outside [-100%, 100%] range",
                        severity="critical"))

        # Revenue growth reasonableness
        growth = latest.get("revenue_growth")
        if growth is not None:
            if -0.5 <= growth <= 1.0:
                checks.append(QualityCheck("Revenue Growth Sanity", True,
                    f"YoY growth = {growth:.1%}"))
            else:
                checks.append(QualityCheck("Revenue Growth Sanity", False,
                    f"YoY growth = {growth:.1%} - unusually extreme",
                    severity="warning"))

        return checks

    def _check_dcf_sanity(self, scenarios: list) -> List[QualityCheck]:
        checks = []
        if not scenarios:
            checks.append(QualityCheck("DCF Model", False,
                "No scenarios generated", severity="critical"))
            return checks

        for s in scenarios:
            a = s.get("assumptions", s) if isinstance(s, dict) else s
            label = a.get("label", "Unknown") if isinstance(a, dict) else getattr(a, "label", "Unknown")
            dcf = s.get("dcf_value", 0) if isinstance(s, dict) else getattr(s, "dcf_value", 0)
            price = s.get("implied_share_price", 0) if isinstance(s, dict) else getattr(s, "implied_share_price", 0)

            if dcf > 0 and price > 0:
                checks.append(QualityCheck(f"DCF {label} Case", True,
                    f"DCF = ${dcf/1e9:.1f}B, Implied Price = ${price:.2f}"))
            else:
                checks.append(QualityCheck(f"DCF {label} Case", False,
                    f"Invalid DCF output: value=${dcf}, price=${price}",
                    severity="critical"))

        # Check ordering: Upside > Base > Downside
        prices = {}
        for s in scenarios:
            if isinstance(s, dict):
                label = s.get("assumptions", {}).get("label", "")
                prices[label] = s.get("implied_share_price", 0)

        if prices.get("Upside", 0) > prices.get("Base", 0) > prices.get("Downside", 0):
            checks.append(QualityCheck("Scenario Ordering", True,
                "Upside > Base > Downside - ordering correct"))
        elif all(v > 0 for v in prices.values()):
            checks.append(QualityCheck("Scenario Ordering", False,
                f"Unexpected ordering: Up=${prices.get('Upside',0):.0f}, "
                f"Base=${prices.get('Base',0):.0f}, Down=${prices.get('Downside',0):.0f}",
                severity="warning"))

        return checks

    def _check_sensitivity_sanity(self, sensitivity: list) -> QualityCheck:
        if not sensitivity:
            return QualityCheck("Sensitivity Matrix", False,
                "No sensitivity analysis generated", severity="critical")

        valid_cells = [c for c in sensitivity
                       if (c.get("implied_price", 0) if isinstance(c, dict)
                           else getattr(c, "implied_price", 0)) > 0]

        if len(valid_cells) >= 20:
            return QualityCheck("Sensitivity Matrix", True,
                f"{len(valid_cells)}/{len(sensitivity)} valid cells computed")
        return QualityCheck("Sensitivity Matrix", True,
            f"Only {len(valid_cells)}/{len(sensitivity)} valid cells",
            severity="warning")

    def _check_agent_execution(self, steps: int) -> QualityCheck:
        if steps >= 3:
            return QualityCheck("Agent Execution", True,
                f"Agent completed {steps} reasoning steps with tool calls")
        elif steps > 0:
            return QualityCheck("Agent Execution", True,
                f"Agent ran {steps} steps - may need more iteration",
                severity="warning")
        else:
            return QualityCheck("Agent Execution", False,
                "Agent did not execute (API key missing or error)",
                severity="warning")

    def _check_cross_validation(self, scenarios: list, company: dict) -> QualityCheck:
        """Check if DCF valuation is within reasonable range of market cap."""
        mc = company.get("market_cap")
        if not mc or not scenarios:
            return QualityCheck("Cross-Validation", True,
                "Cannot cross-validate without market cap", severity="info")

        base = next((s for s in scenarios if
                     (s.get("assumptions", {}).get("label") if isinstance(s, dict)
                      else getattr(s, "assumptions", {}).get("label", "")) == "Base"), None)
        if not base:
            return QualityCheck("Cross-Validation", True,
                "No base scenario for cross-validation", severity="info")

        dcf = base.get("dcf_value", 0) if isinstance(base, dict) else getattr(base, "dcf_value", 0)
        ratio = dcf / mc if mc else 0

        if 0.3 <= ratio <= 3.0:
            return QualityCheck("Cross-Validation", True,
                f"Base DCF is {ratio:.1f}x market cap - within plausible range")
        else:
            return QualityCheck("Cross-Validation", False,
                f"Base DCF is {ratio:.1f}x market cap - significant divergence. "
                "Assumptions may need review.", severity="warning")
