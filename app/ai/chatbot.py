import os
from app.database.db import get_connection
from groq import Groq


def ask_financial_ai(user_question):
    # 1. Fetch transaction history from DB
    conn = get_connection()
    cursor = conn.cursor()

    # NOTE: Added a LIMIT 200 safeguard so large history doesn't crash the LLM context.
    cursor.execute("""
        SELECT 
            date, 
            description, 
            amount, 
            category 
        FROM transactions 
        ORDER BY date DESC
        LIMIT 200
    """)
    rows = cursor.fetchall()
    conn.close()

    # 2. Handle empty database edge-case
    if not rows:
        context = "No transaction data available yet."
    else:
        context = "\n".join(
            [
                f"Date: {row[0]}, "
                f"Description: {row[1]}, "
                f"Amount: ₹{row[2]}, "
                f"Category: {row[3]}"
                for row in rows
            ]
        )

    # 3. Initialize Groq Client
    # It will automatically find os.environ.get("GROQ_API_KEY") 
    # without explicitly declaring os.getenv() inside the constructor.
    client = Groq()

    # 4. Construct Prompt
    prompt = f"""
You are a financial analyst.

Use ONLY the data below.

TRANSACTIONS:
{context}

QUESTION:
{user_question}

Answer clearly and accurately.
"""

    # 5. Call LLM API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content