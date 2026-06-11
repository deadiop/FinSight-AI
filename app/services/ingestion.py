from groq import Groq
from app.services.analytics import (
    generate_cashflow_report,
    generate_category_report
)
import os


def generate_financial_insights():

    # Get cashflow data
    report = generate_cashflow_report()

    total_income = 0
    total_expense = 0

    for transaction_type, amount in report:

        if transaction_type == "credit":
            total_income += float(amount)

        elif transaction_type == "debit":
            total_expense += float(amount)

    # Get category data
    category_report = generate_category_report()

    category_text = ""

    for category, amount in category_report:

        category_text += (
            f"{category}: ₹{float(amount):.2f}\n"
        )

    # Initialize Groq client
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are a professional financial advisor.

Analyze the following financial data.

FINANCIAL SUMMARY

Income: ₹{total_income}
Expenses: ₹{total_expense}
Savings: ₹{total_income - total_expense}

SPENDING CATEGORIES

{category_text}

Provide:

1. Savings Rate (%)
2. Top Spending Categories
3. Financial Observations
4. Suggestions to Save Money
5. Estimated Monthly Savings Opportunity

Keep the response concise and actionable.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=700
    )

    return response.choices[0].message.content