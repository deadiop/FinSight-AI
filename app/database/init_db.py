from app.database.db import get_connection


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date TEXT,
        description TEXT,
        amount REAL,
        transaction_type TEXT,
        category TEXT,
        currency TEXT DEFAULT 'INR',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()