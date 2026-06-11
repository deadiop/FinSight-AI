import json
import re
import ollama


def extract_transactions(raw_text: str):

    prompt = f"""
Extract all financial transactions.

Return ONLY a JSON array.

No explanations.
No markdown.
No text before or after JSON.

Format:

[
  {{
    "date": "",
    "description": "",
    "amount": 0,
    "transaction_type": "credit/debit"
  }}
]

TEXT:

{raw_text}
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

    content = response["message"]["content"]

    print("\n=== RAW LLM OUTPUT ===\n")
    print(content)

    # Extract JSON array safely
    match = re.search(r"\[.*\]", content, re.DOTALL)

    if not match:
        raise ValueError("No JSON array found in LLM response")

    json_text = match.group()

    transactions = json.loads(json_text)

    # Normalize data
    for transaction in transactions:

        transaction["transaction_type"] = (
            transaction["transaction_type"]
            .lower()
            .strip()
        )

        transaction["amount"] = abs(
            float(transaction["amount"])
        )

    return transactions