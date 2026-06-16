from fastapi import APIRouter
from pydantic import BaseModel
# Fixed module paths: shifted from backend. to app.
from backend.agents.finance_agent import (
    ask_finance_agent
)

router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"]
)

class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):
    # Fixed indentation inside the route function block body
    answer = ask_finance_agent(
        request.question
    )

    return {
        "answer": answer
    }