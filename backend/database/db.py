from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import datetime

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class CompanyDB(Base):
    __tablename__ = "companies"
    ticker = Column(String, primary_key=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    description = Column(Text)
    website = Column(String)
    market_cap = Column(Float)
    employees = Column(Integer)
    country = Column(String)
    raw_10k_text = Column(Text)
    raw_website_text = Column(Text)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)


class FinancialDataDB(Base):
    __tablename__ = "financials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, index=True)
    period = Column(String)
    data_type = Column(String)
    data_json = Column(Text)


Base.metadata.create_all(engine)
