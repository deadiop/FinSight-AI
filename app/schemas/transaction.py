from pydantic import BaseModel
from datetime import date


class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    transaction_type: str