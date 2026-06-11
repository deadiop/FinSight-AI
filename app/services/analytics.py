from app.database.db import get_connection


def generate_cashflow_report():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            transaction_type,
            SUM(amount)
        FROM transactions
        GROUP BY transaction_type
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def generate_category_report():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            category,
            SUM(amount)
        FROM transactions
        WHERE transaction_type = 'debit'
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results