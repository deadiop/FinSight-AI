from groq import Groq
from app.services.analytics import (
    generate_cashflow_report,
    generate_category_report
)
import os


def generate_financial_insights():

    report = generate_cashflow_report()

    total_income = report["income"]
    total_expense = report["expense"]
    net_savings = report["net"]

    category_report = (
        generate_category_report()
    )

    category_text = ""

    for row in category_report:

        category_text += (
            f"{row['category']}: "
            f"Income ₹{row['income']:.2f}, "
            f"Expense ₹{row['expense']:.2f}\n"
        )

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
You are a professional financial advisor.

Income: ₹{total_income:.2f}
Expenses: ₹{total_expense:.2f}
Savings: ₹{net_savings:.2f}

Categories:

{category_text}

Provide:

1. Savings Rate
2. Top Spending Categories
3. Financial Observations
4. Suggestions
5. Monthly Saving Opportunities

Keep it concise.
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