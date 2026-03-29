import requests
from bs4 import BeautifulSoup
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CompanyWebScraper:
    def scrape_about_page(self, url: str) -> Optional[str]:
        """Scrape company about/investor page for brand positioning text."""
        try:
            resp = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; CorpFinAI/1.0; hackathon project)"
                    )
                },
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)
            return text[:20000]
        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
            return None
