import os
from groq import Groq
from dotenv import load_dotenv

# Fixed module paths: shifted from backend. to app.
from backend.database.db import SessionLocal
from backend.models.transaction import Transaction

load_dotenv()

def ask_finance_agent(question):
    db = SessionLocal()
    context = ""  # Initialized empty context to prevent scoping reference errors if DB crashes

    try:
        rows = db.query(Transaction).all()
        financial_data = []

        for row in rows:
            financial_data.append(
                f"{row.date} | {row.description} | {row.amount} | {row.category}"
            )

        context = "\n".join(financial_data)

    finally:
        db.close()

    # Fixed Indentation: Everything below now safely sits inside the function block
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are an expert financial advisor.
User financial data:
{context}

Question:
{question}

Give a clear answer using the financial data above.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content