from langchain.tools import tool
from database.crud import get_financials
import json


@tool
def get_chart_data(ticker: str, metric: str) -> str:
    """Get time-series data for charting a specific financial metric.
    metric: one of revenue, ebitda, net_income, free_cash_flow, gross_margin, ebitda_margin.
    Returns JSON with periods and values suitable for chart rendering."""
    income_data = get_financials(ticker, data_type="income")
    cashflow_data = get_financials(ticker, data_type="cashflow")

    result = {"metric": metric, "ticker": ticker, "data": []}

    if metric in ("revenue", "ebitda", "net_income", "gross_margin", "ebitda_margin"):
        for item in sorted(income_data, key=lambda x: x["period"]):
            d = item["data"]
            value = None
            if metric == "revenue":
                value = d.get("revenue", 0)
            elif metric == "ebitda":
                value = d.get("ebitda", 0)
            elif metric == "net_income":
                value = d.get("net_income", 0)
            elif metric == "gross_margin":
                rev = d.get("revenue", 0)
                gp = d.get("gross_profit", 0)
                value = round(gp / rev, 4) if rev else 0
            elif metric == "ebitda_margin":
                rev = d.get("revenue", 0)
                eb = d.get("ebitda", 0)
                value = round(eb / rev, 4) if rev else 0
            result["data"].append({"period": item["period"], "value": value})

    elif metric == "free_cash_flow":
        for item in sorted(cashflow_data, key=lambda x: x["period"]):
            d = item["data"]
            result["data"].append({
                "period": item["period"],
                "value": d.get("free_cash_flow", 0),
            })

    return json.dumps(result, indent=2)
