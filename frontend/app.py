import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from api import (
    get_summary,
    get_categories,
    ask_agent,
    upload_file,
    get_transactions,
    clear_transactions,
    get_insights,
)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = "uploader_1"

st.set_page_config(page_title="FinSight AI - Financial Document Processor", page_icon="₹", layout="wide")

st.title("FinSight AI - Financial Document Processor")

with st.sidebar:
    st.header("AI Assistant")
    question = st.text_input("Ask about your finances")
    if question:
        try:
            with st.spinner("Thinking..."):
                response = ask_agent(question)
                answer = response.get("answer", "No response received.")
                st.write(answer)
        except Exception as exc:
            st.error(str(exc))

    st.divider()
    if st.button("Reset Database (Erase All Data)", type="primary", use_container_width=True):
        try:
            clear_transactions()
            # Increment uploader key to clear uploaded files in the UI
            current_num = int(st.session_state.uploader_key.split("_")[1])
            st.session_state.uploader_key = f"uploader_{current_num + 1}"
            st.success("Transactions cleared.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

uploads = st.file_uploader(
    "Upload bank statements or transaction files",
    type=["pdf", "csv", "xlsx", "xls"],
    accept_multiple_files=True,
    key=st.session_state.uploader_key,
)

if uploads:
    total_inserted = 0
    total_skipped = 0
    with st.spinner("Processing uploaded documents..."):
        for uploaded_file in uploads:
            try:
                result = upload_file(uploaded_file)
                if "error" in result:
                    st.error(f"{uploaded_file.name}: {result['error']}")
                else:
                    found = result.get("transactions_found", 0)
                    saved = result.get("transactions_saved", 0)
                    total_inserted += saved
                    total_skipped += (found - saved)
            except Exception as exc:
                st.error(f"{uploaded_file.name}: {exc}")

    st.success(f"Imported {total_inserted} transactions. Skipped {total_skipped} duplicate or invalid rows.")

# Fetch data via API
try:
    transactions_data = get_transactions()
    df = pd.DataFrame(transactions_data)
except Exception as exc:
    st.error(f"Failed to fetch transactions: {exc}")
    df = pd.DataFrame()

try:
    cashflow = get_summary()
except Exception as exc:
    st.error(f"Failed to fetch cashflow summary: {exc}")
    cashflow = {"income": 0.0, "expense": 0.0, "net": 0.0}

try:
    categories = get_categories()
except Exception as exc:
    st.error(f"Failed to fetch category analytics: {exc}")
    categories = []

col1, col2, col3 = st.columns(3)
col1.metric("Income", f"₹{cashflow.get('income', 0.0):,.2f}")
col2.metric("Expenses", f"₹{cashflow.get('expense', 0.0):,.2f}")
col3.metric("Net Cashflow", f"₹{cashflow.get('net', 0.0):,.2f}")

st.subheader("Transactions")
if df.empty:
    st.info("Upload a PDF, CSV, or Excel file to begin.")
else:
    display_df = df[["date", "description", "amount", "category", "source_file"]]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.subheader("Expense Distribution")
category_df = pd.DataFrame(categories)
expense_df = category_df[category_df["expense"] > 0] if not category_df.empty else pd.DataFrame()

if expense_df.empty:
    st.info("No expense data available yet.")
else:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(expense_df["expense"], labels=expense_df["category"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Expense Distribution")
    ax.axis("equal")
    st.pyplot(fig)

st.subheader("AI Financial Insights")
if st.button("Generate insights", type="primary", disabled=df.empty):
    try:
        with st.spinner("Generating insights..."):
            res = get_insights()
            if res.get("status") == "error":
                st.error(res.get("error", "Error generating insights."))
            else:
                st.write(res.get("insights", "No insights generated."))
    except Exception as exc:
        st.error(str(exc))

report_text = f"""
FINANCIAL REPORT

Income: ₹{cashflow.get('income', 0.0):,.2f}
Expenses: ₹{cashflow.get('expense', 0.0):,.2f}
Net Cashflow: ₹{cashflow.get('net', 0.0):,.2f}

Transactions: {len(df)}
"""

st.download_button(
    "Download Report",
    report_text,
    file_name="financial_report.txt",
    mime="text/plain",
    disabled=df.empty,
)
