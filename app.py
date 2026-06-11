import os
import tempfile

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from app.parsers.pdf_parser import extract_pdf_text
from app.parsers.csv_parser import extract_csv_text
from app.parsers.excel_parser import extract_excel_text
from app.parsers.image_parser import extract_image_text

from app.ai.extractor import extract_transactions
from app.services.ingestion import save_transactions

from app.services.analytics import (
    generate_cashflow_report,
    generate_category_report
)

from app.ai.insights import generate_financial_insights
from app.ai.chatbot import ask_financial_ai


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Financial Analyzer",
    layout="wide"
)

st.title("💰 AI Financial Analyzer")

st.write(
    "Upload one or more Bank Statements "
    "(PDF, CSV, Excel, Images)"
)

# ---------------------------------------------------
# MULTI FILE UPLOAD
# ---------------------------------------------------

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

# ---------------------------------------------------
# PROCESS FILES
# ---------------------------------------------------

if uploaded_files:

    st.success(f"{len(uploaded_files)} file(s) selected")

    if st.button("🚀 Analyze All Files"):

        with st.spinner("Processing statements..."):

            total_transactions = []

            for uploaded_file in uploaded_files:

                extension = (
                    uploaded_file.name
                    .split(".")[-1]
                    .lower()
                )

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=f".{extension}"
                ) as tmp_file:

                    tmp_file.write(
                        uploaded_file.getvalue()
                    )

                    file_path = tmp_file.name

                try:

                    # PDF
                    if extension == "pdf":

                        text = extract_pdf_text(
                            file_path
                        )

                    # CSV
                    elif extension == "csv":

                        text = extract_csv_text(
                            file_path
                        )

                    # EXCEL
                    elif extension in [
                        "xlsx",
                        "xls"
                    ]:

                        text = extract_excel_text(
                            file_path
                        )

                    # IMAGE
                    elif extension in [
                        "png",
                        "jpg",
                        "jpeg"
                    ]:

                        text = extract_image_text(
                            file_path
                        )

                    else:
                        continue

                    transactions = (
                        extract_transactions(text)
                    )

                    total_transactions.extend(
                        transactions
                    )

                except Exception as e:

                    st.error(
                        f"{uploaded_file.name}: {e}"
                    )

            # SAVE ALL TRANSACTIONS

            if total_transactions:

                save_transactions(
                    total_transactions
                )

        st.success(
            f"Processed {len(total_transactions)} transactions"
        )

        st.divider()

        # ---------------------------------------------------
        # CASHFLOW
        # ---------------------------------------------------

        report = generate_cashflow_report()

        income = 0
        expense = 0

        for t_type, amount in report:

            if t_type == "credit":

                income += float(amount)

            else:

                expense += float(amount)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Income",
            f"₹{income:,.2f}"
        )

        col2.metric(
            "Expenses",
            f"₹{expense:,.2f}"
        )

        col3.metric(
            "Net Cashflow",
            f"₹{income-expense:,.2f}"
        )

        st.divider()

        # ---------------------------------------------------
        # CATEGORY REPORT
        # ---------------------------------------------------

        st.subheader(
            "📊 Spending Categories"
        )

        category_report = (
            generate_category_report()
        )

        if category_report:

            df = pd.DataFrame(
                category_report,
                columns=[
                    "Category",
                    "Amount"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            fig, ax = plt.subplots(
                figsize=(7, 7)
            )

            ax.pie(
                df["Amount"],
                labels=df["Category"],
                autopct="%1.1f%%"
            )

            ax.set_title(
                "Expense Distribution"
            )

            st.pyplot(fig)

        st.divider()

        # ---------------------------------------------------
        # AI INSIGHTS
        # ---------------------------------------------------

        st.subheader(
            "🤖 AI Financial Insights"
        )

        insights = (
            generate_financial_insights()
        )

        st.write(insights)

        st.divider()

        # ---------------------------------------------------
        # DOWNLOAD REPORT
        # ---------------------------------------------------

        report_text = f"""
AI FINANCIAL REPORT

Total Income:
₹{income}

Total Expenses:
₹{expense}

Net Cashflow:
₹{income-expense}

AI Insights:

{insights}
"""

        st.download_button(
            label="📥 Download Report",
            data=report_text,
            file_name="financial_report.txt",
            mime="text/plain"
        )

# ---------------------------------------------------
# SIDEBAR CHATBOT
# ---------------------------------------------------

st.sidebar.title(
    "💬 Financial AI Assistant"
)

question = st.sidebar.text_input(
    "Ask anything about your finances"
)

if question:

    try:

        answer = ask_financial_ai(
            question
        )

        st.sidebar.write(answer)

    except Exception as e:

        st.sidebar.error(str(e))