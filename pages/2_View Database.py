import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Database Viewer", layout="wide")
st.title("View Invoice Database 🔎")

# --- Configuration ---
# All data-related folders are now located inside the main 'data' directory.
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'

if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'.")
    st.info("Please add an invoice first.")
    st.stop()

# --- Initialize Session State for Filters ---
filter_keys = [
    'view_option', 'ref_filter', 'no_filter', 'po_filter',
    'item_filter', 'inv_date_text_filter', 'prod_order_filter', 'date_range' # Added prod_order_filter
]
for key in filter_keys:
    if key not in st.session_state:
        if key == 'view_option':
            st.session_state[key] = "Active"
        elif key == 'date_range':
            st.session_state[key] = None
        else:
            st.session_state[key] = ""

# --- Helper Function for Resetting Filters ---
def reset_filters():
    """Callback function to reset all filter widgets to their default state."""
    st.session_state.view_option = "Active"
    st.session_state.ref_filter = ""
    st.session_state.no_filter = ""
    st.session_state.po_filter = ""
    st.session_state.item_filter = ""
    st.session_state.inv_date_text_filter = ""
    st.session_state.prod_order_filter = "" # Added prod_order_filter
    st.session_state.date_range = None

# --- Filter Controls ---
with st.expander("🔍 Filters", expanded=True):
    st.radio(
        "Choose which invoices to display:",
        ("Active", "Voided", "All"),
        horizontal=True,
        key='view_option'
    )

    # --- UPDATED: Reorganized filter layout ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Filter by Invoice Ref:", key='ref_filter')
        st.text_input("Filter by Invoice No:", key='no_filter')
    with col2:
        st.text_input("Filter by PO:", key='po_filter')
        st.text_input("Filter by Item Code:", key='item_filter')
    with col3:
        st.text_input("Filter by Production Order No:", key='prod_order_filter') # NEW filter
        st.text_input("Filter by Invoice Date (as text):", key='inv_date_text_filter')

    # --- Date Range Filter ---
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            min_date_query = pd.to_datetime(conn.execute(f"SELECT MIN(creating_date) FROM {TABLE_NAME}").fetchone()[0])
            max_date_query = pd.to_datetime(conn.execute(f"SELECT MAX(creating_date) FROM {TABLE_NAME}").fetchone()[0])
            min_date_default = min_date_query.date()
            max_date_default = max_date_query.date()
    except Exception:
        min_date_default = datetime.now().date()
        max_date_default = datetime.now().date()

    if st.session_state.date_range is None:
        st.session_state.date_range = (min_date_default, max_date_default)

    st.date_input(
        "Filter by Creation Date Range:",
        key='date_range',
        min_value=min_date_default,
        max_value=max_date_default
    )

    st.button("Reset All Filters", on_click=reset_filters, use_container_width=True)

# --- Dynamic SQL Query Building (Efficient Filtering) ---
try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        base_query = f"SELECT * FROM {TABLE_NAME}"
        conditions = []
        params = []

        if st.session_state.view_option == "Active":
            conditions.append("status = ?")
            params.append('active')
        elif st.session_state.view_option == "Voided":
            conditions.append("status = ?")
            params.append('voided')

        text_filters_config = {
            'ref_filter': 'inv_ref', 'no_filter': 'inv_no',
            'po_filter': 'po', 'item_filter': 'item',
            'inv_date_text_filter': 'inv_date',
            'prod_order_filter': 'production_order_no' # NEW filter
        }
        for key, column in text_filters_config.items():
            if st.session_state[key]:
                conditions.append(f"{column} LIKE ?")
                params.append(f"%{st.session_state[key]}%")

        if st.session_state.date_range and len(st.session_state.date_range) == 2:
            start_date, end_date = st.session_state.date_range
            start_datetime = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S')
            conditions.append("creating_date BETWEEN ? AND ?")
            params.extend([start_datetime, end_datetime])

        if conditions:
            query = f"{base_query} WHERE {' AND '.join(conditions)}"
        else:
            query = base_query
        query += " ORDER BY creating_date DESC"

        df = pd.read_sql_query(query, conn, params=params)

except Exception as e:
    st.error(f"Could not read data from the database. Error: {e}")
    st.exception(e)
    st.stop()

# --- Display Results ---
if df.empty:
    st.info("No records match your current filter criteria.")
else:
    # --- Check for missing 'po' data in the results ---
    missing_po_df = df[df['po'].isnull() | (df['po'].astype(str).str.strip() == '')]
    if not missing_po_df.empty:
        # --- REVISED: Use inv_no as the indicator ---
        invoices_with_missing_po = missing_po_df['inv_no'].unique()
        st.warning(
            f"Warning: The following Invoice Number(s) in the current view have a missing PO number: "
            f"`{', '.join(invoices_with_missing_po)}`"
        )
        
    # --- Check for missing 'production_order_no' data ---
    missing_prod_order_df = df[df['production_order_no'].isnull() | (df['production_order_no'].astype(str).str.strip() == '')]
    if not missing_prod_order_df.empty:
        # --- REVISED: Use inv_no as the indicator ---
        invoices_with_missing_prod_order = missing_prod_order_df['inv_no'].unique()
        st.warning(
            f"Warning: The following Invoice Number(s) in the current view have a missing Production Order Number: "
            f"`{', '.join(invoices_with_missing_prod_order)}`"
        )

    with sqlite3.connect(DATABASE_FILE) as conn:
        total_records = conn.execute(f"SELECT COUNT(DISTINCT inv_ref) FROM {TABLE_NAME}").fetchone()[0]
    st.success(f"Showing {len(df)} rows from {df['inv_ref'].nunique()} unique invoices (Total invoices in DB: {total_records}).")
    st.dataframe(df)
