from database.db import SessionLocal, CompanyDB, FinancialDataDB
import json


def save_company(
    profile_dict: dict, raw_10k: str = None, raw_website: str = None
):
    db = SessionLocal()
    try:
        existing = (
            db.query(CompanyDB)
            .filter(CompanyDB.ticker == profile_dict["ticker"])
            .first()
        )
        valid_columns = {c.name for c in CompanyDB.__table__.columns}
        if existing:
            for k, v in profile_dict.items():
                if k in valid_columns and k not in ("last_updated", "raw_10k_text", "raw_website_text"):
                    setattr(existing, k, v)
            if raw_10k:
                existing.raw_10k_text = raw_10k
            if raw_website:
                existing.raw_website_text = raw_website
        else:
            # Filter to only include columns that exist in CompanyDB
            valid_columns = {c.name for c in CompanyDB.__table__.columns}
            filtered_profile = {k: v for k, v in profile_dict.items() if k in valid_columns and k not in ("last_updated", "raw_10k_text", "raw_website_text")}
            company = CompanyDB(
                **filtered_profile,
                raw_10k_text=raw_10k,
                raw_website_text=raw_website,
            )
            db.add(company)
        db.commit()
    finally:
        db.close()


def save_financials(ticker: str, period: str, data_type: str, data_json: str):
    db = SessionLocal()
    try:
        # Remove existing entry for same ticker/period/type to avoid duplicates
        db.query(FinancialDataDB).filter(
            FinancialDataDB.ticker == ticker,
            FinancialDataDB.period == period,
            FinancialDataDB.data_type == data_type,
        ).delete()
        record = FinancialDataDB(
            ticker=ticker, period=period, data_type=data_type, data_json=data_json
        )
        db.add(record)
        db.commit()
    finally:
        db.close()


def get_company(ticker: str) -> dict:
    db = SessionLocal()
    try:
        company = (
            db.query(CompanyDB)
            .filter(CompanyDB.ticker == ticker.upper())
            .first()
        )
        if company:
            return {
                c.name: getattr(company, c.name)
                for c in company.__table__.columns
            }
        return None
    finally:
        db.close()


def get_financials(ticker: str, data_type: str = None) -> list:
    db = SessionLocal()
    try:
        query = db.query(FinancialDataDB).filter(
            FinancialDataDB.ticker == ticker.upper()
        )
        if data_type:
            query = query.filter(FinancialDataDB.data_type == data_type)
        return [
            {
                "period": r.period,
                "type": r.data_type,
                "data": json.loads(r.data_json),
            }
            for r in query.all()
        ]
    finally:
        db.close()
