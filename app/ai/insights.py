import ollama
from app.services.analytics import (
    generate_cashflow_report,
    generate_category_report
)


def generate_financial_insights():

    cashflow = generate_cashflow_report()
    categories = generate_category_report()

    summary = "Cashflow Report:\n"

    for row in cashflow:
        summary += f"{row[0]}: ₹{row[1]}\n"

    summary += "\nCategory Report:\n"

    for row in categories:
        summary += f"{row[0]}: ₹{row[1]}\n"

    prompt = f"""
You are a financial advisor.

Analyze the following financial data.

{summary}

Provide:

1. Savings rate
2. Top spending categories
3. Financial observations
4. Suggestions to save money
5. Estimated monthly savings opportunity

Keep it concise.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]