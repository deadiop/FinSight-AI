import csv


def parse_csv(file_path):
    transactions = []

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transactions.append({
                "date": row.get("date"),
                "description": row.get("description"),
                "amount": float(row.get("amount", 0)),
                "category": row.get("category", "Uncategorized")
            })

    return transactions