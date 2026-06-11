import os
import pandas as pd
import streamlit as st

from app.parsers.pdf_parser import extract_pdf_text
from app.ai.extractor import extract_transactions
from app.services.ingestion import save_transactions
from app.services.analytics import (
    generate_cashflow_report,
    generate_category_report
)
from app.ai.insights import generate_financial_insights
from app.ai.chatbot import ask_financial_ai


# -----------------------------------------
# PAGE CONFIG
# -----------------------------------------

st.set_page_config(
    page_title="AI Financial Analyzer",
    layout="wide"
)

st.title("💰 AI Financial Analyzer")
st.markdown(
    "Upload a bank statement PDF and receive AI-powered financial insights."
)

# -----------------------------------------
# FILE UPLOAD
# -----------------------------------------

uploaded_file = st.file_uploader(
    "Upload Bank Statement PDF",
    type=["pdf"]
)

if uploaded_file:

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join(
        "uploads",
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("🚀 Run Analysis"):

        # -----------------------------------------
        # EXTRACT PDF TEXT
        # -----------------------------------------

        st.subheader("📄 Extracted Text")

        text = extract_pdf_text(file_path)

        st.text_area(
            "PDF Content",
            text,
            height=250
        )

        # -----------------------------------------
        # EXTRACT TRANSACTIONS
        # -----------------------------------------

        st.subheader("🔍 Transactions")

        transactions = extract_transactions(text)

        st.json(transactions)

        # -----------------------------------------
        # SAVE TO DATABASE
        # -----------------------------------------

        st.subheader("💾 Database")

        save_transactions(transactions)

        st.success("Transactions saved successfully.")

        # -----------------------------------------
        # CASHFLOW REPORT
        # -----------------------------------------

        st.subheader("💰 Cashflow Summary")

        report = generate_cashflow_report()

        total_income = 0
        total_expense = 0

        for transaction_type, amount in report:

            if transaction_type.lower() == "credit":
                total_income += float(amount)

            elif transaction_type.lower() == "debit":
                total_expense += float(amount)

        net_cashflow = total_income - total_expense

        savings_rate = (
            (net_cashflow / total_income) * 100
            if total_income > 0
            else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Income",
            f"₹{total_income:,.2f}"
        )

        col2.metric(
            "Expenses",
            f"₹{total_expense:,.2f}"
        )

        col3.metric(
            "Net Cashflow",
            f"₹{net_cashflow:,.2f}"
        )

        col4.metric(
            "Savings Rate",
            f"{savings_rate:.1f}%"
        )

        # -----------------------------------------
        # CATEGORY REPORT
        # -----------------------------------------

        st.subheader("📊 Category Breakdown")

        category_report = generate_category_report()

        category_df = pd.DataFrame(
            category_report,
            columns=[
                "Category",
                "Amount"
            ]
        )

        st.dataframe(
            category_df,
            use_container_width=True
        )

        # -----------------------------------------
        # CHART
        # -----------------------------------------

        st.subheader("📈 Spending Distribution")

        if not category_df.empty:

            st.bar_chart(
                category_df.set_index("Category")
            )

        # -----------------------------------------
        # AI INSIGHTS
        # -----------------------------------------

        st.subheader("🤖 AI Financial Insights")

        try:

            insights = generate_financial_insights()

            st.write(insights)

        except Exception as e:

            st.error(
                f"Insight generation failed: {e}"
            )


# -----------------------------------------
# SIDEBAR CHATBOT
# -----------------------------------------

st.sidebar.title("💬 Finance AI")

question = st.sidebar.text_input(
    "Ask a question about your finances"
)

if question:

    try:

        answer = ask_financial_ai(question)

        st.sidebar.subheader("Answer")

        st.sidebar.write(answer)

    except Exception as e:

        st.sidebar.error(str(e))