import json
import re
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def extract_transactions(raw_text):
    # Initialize the Groq client
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    # Construct the instruction prompt
    prompt = f"""
You are a financial transaction extractor. Extract all transactions from the text below.
For each transaction, determine if it is an outflow (expense/debit/withdrawal) or an inflow (income/deposit/credit).
Represent outflows as negative numbers (e.g., -150.00) and inflows as positive numbers (e.g., 50000.00).
Provide a specific category for each transaction (e.g., Food, Transport, Utilities, Entertainment, Income, Shopping, etc.). Do not just use 'Debit' or 'Credit' as the category if a more specific category is clear from the description.

Return ONLY a valid JSON array of objects. Do not include any explanation or markdown formatting other than the JSON itself.

Example output format:
[
  {{
    "date": "2025-01-01",
    "description": "Salary Credit",
    "amount": 50000.00,
    "category": "Income"
  }},
  {{
    "date": "2025-01-02",
    "description": "Swiggy Order",
    "amount": -450.00,
    "category": "Food"
  }}
]

TEXT:
{raw_text}
"""

    # Request inference from Llama model
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    # Isolate array JSON block from response markup noise
    match = re.search(
        r"\[.*\]",
        content,
        re.DOTALL
    )

    if not match:
        return []

    try:
        return json.loads(match.group())
    except Exception:
        return []