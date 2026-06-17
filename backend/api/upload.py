import os
import tempfile
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

# Fixed module paths: changed 'backend.' to 'app.'
from backend.database.db import SessionLocal

from backend.parsers.pdf_parser import extract_pdf_text
from backend.parsers.csv_parser import parse_csv
from backend.parsers.excel_parser import parse_excel  # Updated to match excel_parser.py

from backend.agents.transaction_extractor import (
    extract_transactions
)
from backend.services.ingestion import (
    save_transactions
)
from backend.models.transaction import User
from backend.api.auth import get_current_user

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    extension = (
        file.filename
        .split(".")[-1]
        .lower()
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f".{extension}"
    ) as tmp:
        content = await file.read()
        tmp.write(content)
        file_path = tmp.name

    try:
        transactions = []

        if extension == "pdf":
            text = extract_pdf_text(
                file_path
            )
            transactions = extract_transactions(
                text
            )

        elif extension == "csv":
            transactions = parse_csv(
                file_path
            )

        elif extension in ["xlsx", "xls"]:
            transactions = parse_excel(
                file_path
            )

        else:
            return {
                "error": "Unsupported file type"
            }

        saved_count = save_transactions(db, transactions, source_file=file.filename, user_id=current_user.id)

        return {
            "status": "success",
            "file": file.filename,
            "transactions_found": len(transactions),
            "transactions_saved": saved_count if saved_count is not None else len(transactions)
        }

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)