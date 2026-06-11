from datetime import datetime

from app.database.db import get_connection
from app.services.categorizer import categorize_transaction


def save_transactions(transactions):

    conn = get_connection()
    cursor = conn.cursor()

    saved_count = 0
    skipped_count = 0

    for transaction in transactions:

        try:

            formatted_date = datetime.strptime(
                transaction["date"],
                "%d-%m-%Y"
            ).date()

            description = transaction["description"].strip()

            amount = float(transaction["amount"])

            transaction_type = (
                transaction["transaction_type"]
                .lower()
                .strip()
            )

            category = categorize_transaction(
                description
            )

            # Check duplicates
            cursor.execute(
                """
                SELECT transaction_id
                FROM transactions
                WHERE
                    transaction_date = ?
                    AND description = ?
                    AND amount = ?
                    AND transaction_type = ?
                """,
                (
                    str(formatted_date),
                    description,
                    amount,
                    transaction_type
                )
            )

            existing = cursor.fetchone()

            if existing:
                skipped_count += 1
                continue

            # Insert transaction
            cursor.execute(
                """
                INSERT INTO transactions (
                    transaction_date,
                    description,
                    amount,
                    transaction_type,
                    category
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(formatted_date),
                    description,
                    amount,
                    transaction_type,
                    category
                )
            )

            saved_count += 1

        except Exception as e:

            print(
                f"Failed to save transaction: {transaction}"
            )

            print(f"Error: {e}")

    conn.commit()

    cursor.close()
    conn.close()

    print(f"\nSaved: {saved_count} transactions")
    print(
        f"Skipped: {skipped_count} duplicate transactions"
    )