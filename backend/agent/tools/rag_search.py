from langchain.tools import tool
from agent.rag_engine import query_filing, get_filing_context
import json


@tool
def search_10k_filing(ticker: str, query: str = "risk factors and business overview") -> str:
    """Search the company's 10-K SEC filing for specific information.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        query: What to search for (default: risk factors and business overview)
    """
    ticker = ticker.upper()
    passages = query_filing(ticker, query, n_results=5)
    if not passages:
        return f"No 10-K filing data found for {ticker}."

    results = []
    for i, p in enumerate(passages, 1):
        results.append(
            f"--- Passage {i} (Section: {p['section']}) ---\n{p['text']}"
        )

    return "\n\n".join(results)
