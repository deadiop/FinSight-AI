import os

from dotenv import load_dotenv
from groq import Groq

from backend.services.analytics import generate_cashflow_report, generate_category_report


load_dotenv()


def generate_financial_insights():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    cashflow = generate_cashflow_report()
    categories = generate_category_report()
    category_text = "\n".join(
        f"{row['category']}: Income INR {row['income']:.2f} | Expense INR {row['expense']:.2f}"
        for row in categories
    ) or "No category data available."

    prompt = f"""
You are a professional financial advisor.

FINANCIAL SUMMARY:
- Income: INR {cashflow['income']:.2f}
- Expenses: INR {cashflow['expense']:.2f}
- Net Savings: INR {cashflow['net']:.2f}

SPENDING CATEGORIES:
{category_text}

TASK:
1. Calculate savings rate percentage.
2. Identify top spending categories.
3. Detect unusual spending patterns.
4. Give 3 practical saving suggestions.
5. Estimate monthly saving improvement potential.

Rules:
- Use only the supplied data.
- Do not invent numbers.
- Keep the response concise and structured.
"""

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=700,
    )
    return response.choices[0].message.content