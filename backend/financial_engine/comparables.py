from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ComparableAnalysis:
    """Compute comparable company multiples from available data."""

    def compute_multiples(
        self,
        market_cap: float,
        net_debt: float,
        ebitda: float,
        net_income: float,
        shares_outstanding: float,
    ) -> Dict[str, Optional[float]]:
        """Calculate EV/EBITDA and P/E multiples."""
        ev = market_cap + net_debt if market_cap else 0

        ev_ebitda = None
        if ebitda and ebitda > 0 and ev > 0:
            ev_ebitda = round(ev / ebitda, 2)

        pe_ratio = None
        if net_income and net_income > 0 and market_cap:
            pe_ratio = round(market_cap / net_income, 2)

        eps = None
        if net_income and shares_outstanding and shares_outstanding > 0:
            eps = round(net_income / shares_outstanding, 2)

        return {
            "enterprise_value": round(ev, 2) if ev else None,
            "ev_ebitda": ev_ebitda,
            "pe_ratio": pe_ratio,
            "eps": eps,
            "market_cap": market_cap,
            "net_debt": round(net_debt, 2) if net_debt else None,
        }
