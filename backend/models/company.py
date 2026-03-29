from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyProfile(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    description: str
    website: str
    market_cap: Optional[float] = None
    employees: Optional[int] = None
    country: str = ""
    exchange: str = ""
    currency: str = "USD"
    last_updated: datetime = datetime.now()
