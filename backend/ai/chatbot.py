import os

from dotenv import load_dotenv
from groq import Groq

from backend.services.analytics import build_ai_context


load_dotenv()


def ask_financial_ai(user_question):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    prompt = f"""
You are a financial analyst AI. Use only the transaction data below.

TRANSACTIONS:
{build_ai_context()}

QUESTION:
{user_question}

Give clear insights, totals, and trends when relevant. If the data is insufficient,
say exactly what is missing.
"""

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600,
    )
    return response.choices[0].message.content