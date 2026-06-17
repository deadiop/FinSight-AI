import hashlib
from backend.database.db import insert_transaction


def _fingerprint(transaction):
    raw = (
        f"{transaction['date']}|"
        f"{transaction['description'].lower()}|"
        f"{transaction['amount']:.2f}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_transaction(transaction, source_file=None):
    import pandas as pd
    try:
        # Normalize keys to lowercase for easy lookup
        normalized_keys = {str(k).lower().strip(): v for k, v in transaction.items()}
        
        # 1. Resolve Date
        date_aliases = ["date", "transaction date", "tx date", "value date", "post date", "booking date"]
        date_val = None
        for alias in date_aliases:
            if alias in normalized_keys and normalized_keys[alias]:
                date_val = str(normalized_keys[alias]).strip()
                break
                
        # 2. Resolve Description
        desc_aliases = ["description", "narration", "particulars", "transaction details", "details", "remarks", "memo", "payee", "title"]
        desc_val = None
        for alias in desc_aliases:
            if alias in normalized_keys and normalized_keys[alias]:
                desc_val = str(normalized_keys[alias]).strip()
                break
                
        # 3. Resolve Category
        cat_aliases = ["category", "type", "transaction type", "tag", "classification"]
        cat_val = "Uncategorized"
        for alias in cat_aliases:
            if alias in normalized_keys and normalized_keys[alias]:
                cat_val = str(normalized_keys[alias]).strip()
                break

        # 4. Resolve Amount
        # Check for separate withdrawal / deposit columns first
        withdrawal_aliases = ["withdrawal amt.", "withdrawal", "withdrawals", "debit amt.", "debit", "outflow", "spent"]
        deposit_aliases = ["deposit amt.", "deposit", "deposits", "credit amt.", "credit", "inflow", "received"]
        
        amount_val = 0.0
        found_amount = False
        
        # Check if there is a separate withdrawal column with a valid value
        withdrawal_val = None
        for alias in withdrawal_aliases:
            if alias in normalized_keys and normalized_keys[alias] is not None and str(normalized_keys[alias]).strip() != "":
                try:
                    val = float(str(normalized_keys[alias]).replace(",", "").strip())
                    if val > 0:
                        withdrawal_val = -val
                    elif val < 0:
                        withdrawal_val = val
                    break
                except ValueError:
                    pass
                    
        # Check if there is a separate deposit column with a valid value
        deposit_val = None
        for alias in deposit_aliases:
            if alias in normalized_keys and normalized_keys[alias] is not None and str(normalized_keys[alias]).strip() != "":
                try:
                    val = float(str(normalized_keys[alias]).replace(",", "").strip())
                    if val > 0:
                        deposit_val = val
                    elif val < 0:
                        deposit_val = -val
                    break
                except ValueError:
                    pass

        if withdrawal_val is not None and withdrawal_val != 0:
            amount_val = withdrawal_val
            found_amount = True
            if cat_val == "Uncategorized" or cat_val.lower() == "nan":
                cat_val = "Debit"
        elif deposit_val is not None and deposit_val != 0:
            amount_val = deposit_val
            found_amount = True
            if cat_val == "Uncategorized" or cat_val.lower() == "nan":
                cat_val = "Credit"
        else:
            # If no separate columns, look for a single amount column
            amt_aliases = ["amount", "transaction amount", "amt", "value"]
            for alias in amt_aliases:
                if alias in normalized_keys and normalized_keys[alias] is not None and str(normalized_keys[alias]).strip() != "":
                    try:
                        amount_val = float(str(normalized_keys[alias]).replace(",", "").strip())
                        found_amount = True
                        break
                    except ValueError:
                        pass

        if not date_val or not desc_val or not found_amount or amount_val == 0:
            return None

        # Format/Normalize date to standard ISO format YYYY-MM-DD
        try:
            parsed_date = pd.to_datetime(date_val, errors="coerce")
            if pd.notna(parsed_date):
                date_val = parsed_date.strftime("%Y-%m-%d")
        except Exception:
            pass

        # Determine/Normalize sign based on category if single amount column was used
        category_lower = cat_val.lower()
        
        # Suffix/substring check to match custom categories like "Food & Dining" or "Salary Credit"
        is_expense = any(k in category_lower for k in ["debit", "expense", "payment", "outflow", "shopping", "food", "bill", "travel", "entertainment", "grocery", "dining", "utility", "rent", "subscription", "transport", "fuel", "medical", "insurance", "tax", "fee", "personal", "service", "leisure", "withdrawal"])
        is_income = any(k in category_lower for k in ["credit", "income", "salary", "deposit", "refund", "interest", "dividend", "bonus", "received"])

        if is_expense:
            if amount_val > 0:
                amount_val = -amount_val
        elif is_income:
            if amount_val < 0:
                amount_val = -amount_val

    except Exception as e:
        print(f"Error normalising transaction: {e}")
        return None

    return {
        "date": date_val,
        "description": desc_val,
        "amount": amount_val,
        "category": cat_val,
        "source_file": source_file,
    }


def ingest_transactions(transactions, source_file=None, user_id=None, db=None):
    seen = set()
    inserted = 0
    skipped = 0

    for transaction in transactions or []:
        normalized = normalize_transaction(transaction, source_file)
        if not normalized:
            skipped += 1
            continue

        key = _fingerprint(normalized)
        if key in seen:
            skipped += 1
            continue

        seen.add(key)
        inserted += insert_transaction(
            normalized["date"],
            normalized["description"],
            normalized["amount"],
            normalized["category"],
            normalized["source_file"],
            user_id=user_id,
            db=db,
        )

    return {"inserted": inserted, "skipped": skipped}


# Wrapper required by backend/api/upload.py
def save_transactions(db, transactions, source_file=None, user_id=None):
    result = ingest_transactions(transactions, source_file=source_file, user_id=user_id, db=db)
    return result["inserted"]