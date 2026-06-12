import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "finance.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def insert_transaction(
    date,
    description,
    amount,
    category
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO transactions
        (
            date,
            description,
            amount,
            category
        )
        VALUES (?, ?, ?, ?)
    """, (
        date,
        description,
        amount,
        category
    ))

    conn.commit()
    conn.close()


def fetch_transactions():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM transactions
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows