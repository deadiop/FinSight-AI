from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.models.transaction import User
from backend.api.auth import get_current_user
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
def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    # Fixed indentation inside the route function block body
    answer = ask_finance_agent(
        request.question,
        user_id=current_user.id
    )

    return {
        "answer": answer
    }