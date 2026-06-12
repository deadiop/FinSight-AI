import pandas as pd

def extract_excel_transactions(file_path):
    """
    Read Excel file and convert rows into
    transaction dictionaries.
    """
    # 1. Read the Excel file
    df = pd.read_excel(file_path)

    # 2. Normalize column names
    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    # 3. Replace NaN values
    df = df.fillna("")

    transactions = []

    # 4. Iterate through rows
    for _, row in df.iterrows():
        transaction = {
            "date": str(
                row.get("date", "")
            ).strip(),

            "description": str(
                row.get("description", "")
            ).strip(),

            "amount": float(
                row.get("amount", 0) or 0
            ),

            "category": str(
                row.get(
                    "category",
                    "Uncategorized"
                )
            ).strip()
        }

        transactions.append(transaction)

    return transactions