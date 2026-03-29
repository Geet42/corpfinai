import yfinance as yf
from models.company import CompanyProfile
from models.financials import IncomeStatement, BalanceSheet, CashFlowStatement
from typing import List
import logging

logger = logging.getLogger(__name__)


class YahooFinanceIngester:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)

    def get_profile(self) -> CompanyProfile:
        info = self.stock.info
        return CompanyProfile(
            ticker=self.ticker,
            name=info.get("longName", self.ticker),
            sector=info.get("sector", "Unknown"),
            industry=info.get("industry", "Unknown"),
            description=info.get("longBusinessSummary", ""),
            website=info.get("website", ""),
            market_cap=info.get("marketCap"),
            employees=info.get("fullTimeEmployees"),
            country=info.get("country", ""),
            exchange=info.get("exchange", ""),
            currency=info.get("currency", "USD"),
        )

    def get_income_statements(self) -> List[IncomeStatement]:
        """Extract last 4 years of income statements."""
        df = self.stock.financials
        statements = []
        if df is None or df.empty:
            return statements
        for col in df.columns:
            period = str(col.year)
            try:
                stmt = IncomeStatement(
                    ticker=self.ticker,
                    period=period,
                    revenue=self._safe_get(df, col, "Total Revenue"),
                    cost_of_revenue=self._safe_get(df, col, "Cost Of Revenue"),
                    gross_profit=self._safe_get(df, col, "Gross Profit"),
                    operating_expenses=self._safe_get(df, col, "Operating Expense"),
                    operating_income=self._safe_get(df, col, "Operating Income"),
                    ebitda=self._safe_get(df, col, "EBITDA"),
                    net_income=self._safe_get(df, col, "Net Income"),
                    eps=self._safe_get(df, col, "Basic EPS", default=None),
                    shares_outstanding=self._safe_get(
                        df, col, "Basic Average Shares", default=None
                    ),
                )
                statements.append(stmt)
            except Exception as e:
                logger.warning(f"Skipping period {period}: {e}")
        return statements

    def get_balance_sheets(self) -> List[BalanceSheet]:
        df = self.stock.balance_sheet
        sheets = []
        if df is None or df.empty:
            return sheets
        for col in df.columns:
            period = str(col.year)
            try:
                sheet = BalanceSheet(
                    ticker=self.ticker,
                    period=period,
                    total_assets=self._safe_get(df, col, "Total Assets"),
                    total_liabilities=self._safe_get(
                        df, col, "Total Liabilities Net Minority Interest"
                    ),
                    total_equity=self._safe_get(df, col, "Stockholders Equity"),
                    cash_and_equivalents=self._safe_get(
                        df, col, "Cash And Cash Equivalents"
                    ),
                    total_debt=self._safe_get(df, col, "Total Debt"),
                    current_assets=self._safe_get(df, col, "Current Assets"),
                    current_liabilities=self._safe_get(df, col, "Current Liabilities"),
                )
                sheets.append(sheet)
            except Exception as e:
                logger.warning(f"Skipping BS period {period}: {e}")
        return sheets

    def get_cash_flows(self) -> List[CashFlowStatement]:
        df = self.stock.cashflow
        flows = []
        if df is None or df.empty:
            return flows
        for col in df.columns:
            period = str(col.year)
            try:
                flow = CashFlowStatement(
                    ticker=self.ticker,
                    period=period,
                    operating_cash_flow=self._safe_get(df, col, "Operating Cash Flow"),
                    capital_expenditure=self._safe_get(df, col, "Capital Expenditure"),
                    free_cash_flow=self._safe_get(df, col, "Free Cash Flow"),
                    dividends_paid=self._safe_get(
                        df, col, "Common Stock Dividend Paid", default=0
                    ),
                    share_buybacks=self._safe_get(
                        df, col, "Repurchase Of Capital Stock", default=0
                    ),
                )
                flows.append(flow)
            except Exception as e:
                logger.warning(f"Skipping CF period {period}: {e}")
        return flows

    def get_price_history(self, period: str = "5y") -> dict:
        hist = self.stock.history(period=period)
        if hist is None or hist.empty:
            return {"dates": [], "close": [], "volume": []}
        return {
            "dates": [d.strftime("%Y-%m-%d") for d in hist.index],
            "close": hist["Close"].tolist(),
            "volume": hist["Volume"].tolist(),
        }

    @staticmethod
    def _safe_get(df, col, row_name, default=0.0):
        try:
            val = df.loc[row_name, col]
            if val is None:
                return default
            import math
            if isinstance(val, float) and math.isnan(val):
                return default
            return float(val)
        except (KeyError, TypeError, ValueError):
            return default
