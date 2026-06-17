import os
import socket
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.transaction import Transaction, Base

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "finance.db"

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None


def check_host(host, port=5432, timeout=2):
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except Exception as e:
        print(f"check_host failed: {e}")
        return False



def init_db():
    global engine, SessionLocal
    url = DATABASE_URL
    if not url:
        url = f"sqlite:///{DB_PATH}"
    
    use_sqlite = True
    if url.startswith("postgresql"):
        try:
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 5432
            
            print(f"Testing database host connection ({host}:{port})...")
            if check_host(host, port, timeout=2):
                use_sqlite = False
                print("Database host is reachable. Connecting to PostgreSQL...")
            else:
                print("Database host is unreachable or connection timed out.")
        except Exception as e:
            print(f"Error checking database host: {e}")
            
    if use_sqlite:
        fallback_url = f"sqlite:///{DB_PATH}"
        print(f"Using database: {fallback_url}")
        engine = create_engine(fallback_url, connect_args={"check_same_thread": False})
    else:
        print(f"Using database: {url}")
        engine = create_engine(url, pool_pre_ping=True, pool_recycle=300)
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as conn:
            print("Successfully connected to the database!")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def insert_transaction(date, description, amount, category, source_file=None, user_id=None, db=None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        # Check if transaction with same date, description, amount, user_id already exists to avoid duplicates
        existing = db.query(Transaction).filter(
            Transaction.date == date,
            Transaction.description == description,
            Transaction.amount == amount,
            Transaction.user_id == user_id
        ).first()
        if existing:
            return 0

        tx = Transaction(
            date=date,
            description=description,
            amount=amount,
            category=category,
            source_file=source_file,
            user_id=user_id
        )
        db.add(tx)
        db.commit()
        return 1
    except Exception as e:
        db.rollback()
        print(f"Error inserting transaction: {e}")
        return 0
    finally:
        if close_db:
            db.close()


def fetch_transactions(user_id, db=None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        rows = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.date.desc(), Transaction.id.desc()).all()
        return [
            {
                "id": row.id,
                "date": row.date,
                "description": row.description,
                "amount": row.amount,
                "category": row.category,
                "source_file": row.source_file,
                "created_at": row.created_at
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []
    finally:
        if close_db:
            db.close()


def clear_transactions(user_id, db=None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    try:
        db.query(Transaction).filter(Transaction.user_id == user_id).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error clearing transactions: {e}")
    finally:
        if close_db:
            db.close()
