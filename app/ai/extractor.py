import json
import re
import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


def extract_transactions(raw_text):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY not found")

    client = Groq(api_key=api_key)

    prompt = f"""
Extract all financial transactions from the text below.

Return ONLY valid JSON.

Format:

[
  {{
    "date": "01-01-2026",
    "description": "Amazon Purchase",
    "amount": -500,
    "category": "Shopping"
  }}
]

RULES:
- No markdown
- No explanations
- Return only JSON
- Expense = negative amount
- Income = positive amount

TEXT:
{raw_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=4000
    )

    content = response.choices[0].message.content

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