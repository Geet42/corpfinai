from langchain.tools import tool
from database.crud import get_company, get_financials
import json


@tool
def retrieve_company_data(ticker: str) -> str:
    """Retrieve stored company profile and financial data from the database.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
    """
    company = get_company(ticker.upper())
    financials = get_financials(ticker.upper())
    if not company:
        return f"No data found for {ticker}. The company data has not been ingested yet."
    return json.dumps(
        {
            "profile": {
                k: v
                for k, v in company.items()
                if k not in ("raw_10k_text", "raw_website_text")
            },
            "financials_count": len(financials),
            "periods": list(set(f["period"] for f in financials)),
        },
        indent=2,
        default=str,
    )


@tool
def retrieve_financial_statements(ticker: str, statement_type: str = "all") -> str:
    """Retrieve specific financial statements for a ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL)
        statement_type: One of 'income', 'balance', 'cashflow', or 'all' (default: all)
    """
    ticker = ticker.upper()
    if statement_type == "all":
        data = get_financials(ticker)
    else:
        data = get_financials(ticker, data_type=statement_type)
    if not data:
        return f"No {statement_type} data found for {ticker}."
    return json.dumps(data, indent=2, default=str)
