import streamlit as st
import tempfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from app.database.init_db import init_db

# Initialize database
init_db()

# Parsers
from app.parsers.pdf_parser import extract_pdf_text
from app.parsers.csv_parser import parse_csv
from app.parsers.excel_parser import extract_excel_transactions
from app.parsers.image_parser import extract_image_text

# AI
from app.ai.extractor import extract_transactions
from app.ai.insights import generate_financial_insights
from app.ai.chatbot import ask_financial_ai

# Services
from app.services.ingestion import ingest_transactions
from app.services.analytics import (
    generate_cashflow_report,
    generate_category_report
)

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide"
)

st.title("💰 FinSight AI")
st.caption("AI-Powered Financial Analysis Dashboard")

st.write(
    "Upload bank statements in PDF, CSV, Excel, or Image format."
)

# ---------------- FILE UPLOADER ----------------

uploaded_files = st.file_uploader(
    "Upload Files",
    type=[
        "pdf",
        "csv",
        "xlsx",
        "xls",
        "png",
        "jpg",
        "jpeg"
    ],
    accept_multiple_files=True
)

# ---------------- NORMALIZER ----------------

def normalize_transaction(t):
    try:
        return {
            "date": str(t.get("date", "")).strip(),
            "description": str(
                t.get("description", "")
            ).strip(),
            "amount": float(
                t.get("amount", 0)
            ),
            "category": str(
                t.get(
                    "category",
                    "Uncategorized"
                )
            ).strip()
        }

    except Exception:
        return None


# ---------------- MAIN ANALYSIS ----------------

if uploaded_files:

    if st.button("🚀 Analyze All Files"):

        all_transactions = []

        progress = st.progress(0)

        with st.spinner("Analyzing uploaded files..."):

            total_files = len(uploaded_files)

            for index, uploaded_file in enumerate(uploaded_files):

                extension = (
                    uploaded_file.name
                    .split(".")[-1]
                    .lower()
                )

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=f".{extension}"
                ) as tmp:

                    tmp.write(
                        uploaded_file.getvalue()
                    )

                    file_path = tmp.name

                try:

                    transactions = []

                    # PDF
                    if extension == "pdf":

                        text = extract_pdf_text(
                            file_path
                        )

                        transactions = extract_transactions(
                            text
                        )

                    # CSV
                    elif extension == "csv":

                        transactions = parse_csv(
                            file_path
                        )

                    # Images
                    elif extension in [
                        "png",
                        "jpg",
                        "jpeg"
                    ]:

                        text = extract_image_text(
                            file_path
                        )

                        transactions = extract_transactions(
                            text
                        )

                    # Excel
                    elif extension in [
                        "xlsx",
                        "xls"
                    ]:

                        transactions = extract_excel_transactions(
                            file_path
                        )

                    cleaned = []

                    for t in transactions:

                        nt = normalize_transaction(
                            t
                        )

                        if nt:
                            cleaned.append(nt)

                    all_transactions.extend(
                        cleaned
                    )

                except Exception as e:

                    st.error(
                        f"{uploaded_file.name}: {e}"
                    )

                progress.progress(
                    (index + 1) / total_files
                )

        # Deduplication

        seen = set()
        unique_transactions = []

        for t in all_transactions:

            key = (
                t["date"],
                t["description"],
                t["amount"]
            )

            if key not in seen:

                seen.add(key)

                unique_transactions.append(t)

        # Save

        if unique_transactions:

            ingest_transactions(
                unique_transactions
            )

        st.success(
            f"Processed {len(unique_transactions)} transactions"
        )

        st.divider()

        # Cashflow

        report = generate_cashflow_report()

        income = report.get(
            "income",
            0
        )

        expense = report.get(
            "expense",
            0
        )

        net = report.get(
            "net",
            0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Income",
            f"₹{income:,.2f}"
        )

        col2.metric(
            "Expense",
            f"₹{expense:,.2f}"
        )

        col3.metric(
            "Net Cashflow",
            f"₹{net:,.2f}"
        )

        st.divider()

        # Category Report

        st.subheader(
            "📊 Spending Categories"
        )

        category_report = generate_category_report()

        if category_report:

            df = pd.DataFrame(
                category_report
            )

            df["income"] = pd.to_numeric(
                df["income"],
                errors="coerce"
            ).fillna(0)

            df["expense"] = pd.to_numeric(
                df["expense"],
                errors="coerce"
            ).fillna(0)

            df = df.replace(
                [np.inf, -np.inf],
                np.nan
            ).dropna()

            st.dataframe(
                df,
                use_container_width=True
            )

            expense_df = df[
                df["expense"] > 0
            ]

            if not expense_df.empty:

                fig, ax = plt.subplots()

                ax.pie(
                    expense_df["expense"],
                    labels=expense_df["category"],
                    autopct="%1.1f%%"
                )

                ax.set_title(
                    "Expense Distribution"
                )

                st.pyplot(fig)

        st.divider()

        # AI Insights

        st.subheader(
            "🤖 AI Financial Insights"
        )

        insights = ""

        try:

            insights = (
                generate_financial_insights()
            )

            st.write(insights)

        except Exception as e:

            st.error(
                f"Insights Error: {e}"
            )

        st.divider()

        # Download Report

        report_text = f"""
FINANCIAL REPORT

Income: ₹{income:,.2f}

Expenses: ₹{expense:,.2f}

Net Cashflow: ₹{net:,.2f}

AI INSIGHTS:

{insights}
"""

        st.download_button(
            label="📥 Download Report",
            data=report_text,
            file_name="financial_report.txt",
            mime="text/plain"
        )

# ---------------- SIDEBAR CHATBOT ----------------

st.sidebar.title("💬 AI Assistant")

question = st.sidebar.text_input(
    "Ask about your finances"
)

if question:

    try:

        answer = ask_financial_ai(
            question
        )

        st.sidebar.write(
            answer
        )

    except Exception as e:

        st.sidebar.error(
            str(e)
        )