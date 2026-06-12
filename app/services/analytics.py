from app.database.db import get_connection


def generate_cashflow_report():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT amount
        FROM transactions
    """)

    rows = cursor.fetchall()

    conn.close()

    income = 0.0
    expense = 0.0

    for row in rows:

        amount = float(row[0])

        if amount > 0:
            income += amount
        else:
            expense += abs(amount)

    return {
        "income": income,
        "expense": expense,
        "net": income - expense
    }


def generate_category_report():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            category,
            SUM(
                CASE
                    WHEN amount > 0
                    THEN amount
                    ELSE 0
                END
            ) AS income,

            SUM(
                CASE
                    WHEN amount < 0
                    THEN ABS(amount)
                    ELSE 0
                END
            ) AS expense

        FROM transactions

        GROUP BY category
    """)

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "category": row[0],
            "income": float(row[1] or 0),
            "expense": float(row[2] or 0)
        }
        for row in rows
    ]