from collections import defaultdict
import pandas as pd
from backend.database.db import fetch_transactions


def transactions_dataframe(user_id, db=None):
    rows = fetch_transactions(user_id, db)
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=["id", "date", "description", "amount", "category", "source_file", "created_at"]
        )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype("string")
    return df


def generate_cashflow_report(user_id, db=None):
    df = transactions_dataframe(user_id, db)
    if df.empty:
        return {"income": 0.0, "expense": 0.0, "net": 0.0}

    income = float(df.loc[df["amount"] > 0, "amount"].sum())
    expense = float(df.loc[df["amount"] < 0, "amount"].abs().sum())
    return {"income": income, "expense": expense, "net": income - expense}


def generate_category_report(user_id, db=None):
    df = transactions_dataframe(user_id, db)
    if df.empty:
        return []

    grouped = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for _, row in df.iterrows():
        category = row.get("category") or "Uncategorized"
        amount = float(row.get("amount") or 0.0)
        if amount > 0:
            grouped[category]["income"] += amount
        elif amount < 0:
            grouped[category]["expense"] += abs(amount)

    return [
        {"category": category, "income": values["income"], "expense": values["expense"]}
        for category, values in sorted(grouped.items())
    ]


def build_ai_context(user_id, limit=200, db=None):
    df = transactions_dataframe(user_id, db)
    if df.empty:
        return "No transactions have been uploaded yet."

    recent = df.sort_values("date", ascending=False).head(limit)
    lines = [
        f"Date: {row.date}, Description: {row.description}, "
        f"Amount: INR {row.amount:.2f}, Category: {row.category}"
        for row in recent.itertuples()
    ]
    return "\n".join(lines)


# Wrappers to match imports in main.py
def get_financial_summary(user_id, db=None):
    return generate_cashflow_report(user_id, db)


def expenses_by_category(user_id, db=None):
    return generate_category_report(user_id, db)