from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.api.upload import router as upload_router
from backend.api.agent import router as agent_router
from backend.api.auth import router as auth_router, get_current_user

from backend.database.db import SessionLocal, engine, fetch_transactions, clear_transactions, get_db
from backend.models.transaction import Base, User
from backend.services.analytics import (
    get_financial_summary,
    expenses_by_category
)
from backend.ai.insights import generate_financial_insights

app = FastAPI(
    title="FinSight AI",
    version="1.0.0",
    description="AI-Powered Financial Analysis Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- DATABASE STARTUP ----------------
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")


# ---------------- ROUTERS ----------------
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(agent_router)


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {
        "message": "FinSight AI Backend Running"
    }


# ---------------- HEALTH ----------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ---------------- FINANCIAL SUMMARY ----------------
@app.get("/summary")
def financial_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return get_financial_summary(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- CATEGORY ANALYTICS ----------------
@app.get("/categories")
def categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return expenses_by_category(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- TRANSACTIONS ENDPOINTS ----------------
@app.get("/transactions")
def get_all_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return fetch_transactions(current_user.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/transactions")
def clear_all_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        clear_transactions(current_user.id, db)
        return {"status": "success", "message": "All transactions cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- INSIGHTS ENDPOINTS ----------------
@app.get("/insights")
def get_insights(current_user: User = Depends(get_current_user)):
    try:
        insights = generate_financial_insights(current_user.id)
        return {"status": "success", "insights": insights}
    except Exception as e:
        return {"status": "error", "error": str(e)}