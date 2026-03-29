from fastapi import APIRouter, HTTPException
from database.crud import get_company, get_financials

router = APIRouter()


@router.get("/company/{ticker}")
async def get_company_data(ticker: str):
    """Retrieve stored company profile."""
    data = get_company(ticker.upper())
    if not data:
        raise HTTPException(404, f"No data found for {ticker}. Run /analyze first.")
    # Remove large text fields from default response
    data.pop("raw_10k_text", None)
    data.pop("raw_website_text", None)
    return data


@router.get("/company/{ticker}/financials")
async def get_company_financials(ticker: str, data_type: str = None):
    """Retrieve stored financial statements."""
    data = get_financials(ticker.upper(), data_type=data_type)
    if not data:
        raise HTTPException(
            404, f"No financials found for {ticker}. Run /analyze first."
        )
    return {"ticker": ticker.upper(), "financials": data}
