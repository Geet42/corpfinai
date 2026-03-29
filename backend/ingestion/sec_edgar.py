import requests
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SECEdgarIngester:
    def __init__(self, user_agent: str):
        self.headers = {"User-Agent": user_agent}

    def get_cik(self, ticker: str) -> Optional[str]:
        """Lookup CIK number from ticker."""
        try:
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            resp = requests.get(tickers_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            for entry in data.values():
                if entry["ticker"].upper() == ticker.upper():
                    return str(entry["cik_str"]).zfill(10)
        except Exception as e:
            logger.error(f"CIK lookup failed: {e}")
        return None

    def get_latest_10k_text(self, ticker: str, max_chars: int = 50000) -> Optional[str]:
        """Fetch text from the latest 10-K filing (trimmed for LLM context)."""
        cik = self.get_cik(ticker)
        if not cik:
            logger.warning(f"No CIK found for {ticker}")
            return None
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accessions = recent.get("accessionNumber", [])
            docs = recent.get("primaryDocument", [])

            for i, form in enumerate(forms):
                if form == "10-K":
                    accession = accessions[i].replace("-", "")
                    doc = docs[i]
                    cik_stripped = cik.lstrip("0")
                    filing_url = (
                        f"https://www.sec.gov/Archives/edgar/data/"
                        f"{cik_stripped}/{accession}/{doc}"
                    )
                    filing_resp = requests.get(
                        filing_url, headers=self.headers, timeout=15
                    )
                    text = filing_resp.text[:max_chars]
                    return text
        except Exception as e:
            logger.error(f"10-K fetch failed: {e}")
        return None
