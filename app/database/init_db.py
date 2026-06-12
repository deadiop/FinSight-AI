from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "finance.db"


def init_db():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            UNIQUE(date, description, amount)
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_date
        ON transactions(date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_category
        ON transactions(category)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_amount
        ON transactions(amount)
    """)

    conn.commit()
    conn.close()

    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    init_db()