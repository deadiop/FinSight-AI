import hashlib
from app.database.db import insert_transaction


def make_key(t):
    """Creates unique fingerprint for each transaction"""
    return hashlib.md5(
        f"{t.get('date','')}-{t.get('description','')}-{t.get('amount','')}".encode()
    ).hexdigest()


def normalize(t):
    try:
        return {
            "date": str(t.get("date", "")).strip(),
            "description": str(t.get("description", "")).strip().lower(),
            "amount": float(t.get("amount", 0) or 0),
            "category": str(t.get("category", "Uncategorized")).strip()
        }
    except:
        return None


def ingest_transactions(transactions):

    if not transactions:
        print("No data to ingest")
        return

    seen = set()
    clean = []

    # ---------------- GLOBAL DEDUP (CRITICAL FIX) ----------------
    for t in transactions:

        nt = normalize(t)
        if not nt:
            continue

        key = make_key(nt)

        if key not in seen:
            seen.add(key)
            clean.append(nt)

    # ---------------- INSERT ONLY CLEAN DATA ----------------
    count = 0

    for t in clean:
        try:
            insert_transaction(
                t["date"],
                t["description"],
                t["amount"],
                t["category"]
            )
            count += 1
        except Exception as e:
            print("Insert failed:", t, e)

    print(f"Inserted {count} UNIQUE transactions")