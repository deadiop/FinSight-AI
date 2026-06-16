from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.upload import router as upload_router
from backend.api.agent import router as agent_router
from backend.database.db import SessionLocal, engine, fetch_transactions, clear_transactions
from backend.models.transaction import Base
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# # ---------------- DATABASE STARTUP ----------------
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized.")


# # ---------------- ROUTERS ----------------
app.include_router(upload_router)
app.include_router(agent_router)


# # ---------------- ROOT ----------------
@app.get("/")
def root():
    return {
        "message": "FinSight AI Backend Running"
    }


# # ---------------- HEALTH ----------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# # ---------------- FINANCIAL SUMMARY ----------------
@app.get("/summary")
def financial_summary():
    db = SessionLocal()
    try:
        return get_financial_summary(db)
    finally:
        db.close()


# # ---------------- CATEGORY ANALYTICS ----------------
@app.get("/categories")
def categories():
    db = SessionLocal()
    try:
        return expenses_by_category(db)
    finally:
        db.close()


# # ---------------- TRANSACTIONS ENDPOINTS ----------------
@app.get("/transactions")
def get_all_transactions():
    return fetch_transactions()


@app.delete("/transactions")
def clear_all_transactions():
    clear_transactions()
    return {"status": "success", "message": "All transactions cleared"}


# # ---------------- INSIGHTS ENDPOINTS ----------------
@app.get("/insights")
def get_insights():
    try:
        insights = generate_financial_insights()
        return {"status": "success", "insights": insights}
    except Exception as e:
        return {"status": "error", "error": str(e)}