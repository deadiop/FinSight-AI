from app.database.db import get_connection
from groq import Groq
import os


def ask_financial_ai(user_question):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            transaction_date,
            description,
            amount,
            transaction_type,
            category
        FROM transactions
        ORDER BY transaction_date
    """)

    transactions = cursor.fetchall()

    cursor.close()
    conn.close()

    context = ""

    for row in transactions:
        context += (
            f"Date: {row[0]}, "
            f"Description: {row[1]}, "
            f"Amount: {row[2]}, "
            f"Type: {row[3]}, "
            f"Category: {row[4]}\n"
        )

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are a financial analyst.

Use ONLY the transaction data below.

Transaction Data:
{context}

Question:
{user_question}

Give a clear answer.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content