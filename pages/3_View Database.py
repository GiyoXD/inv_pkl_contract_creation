# 3_View Database.py (Corrected)
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Database Viewer", layout="wide")
st.title("View Invoice Database 🔎")

# --- Configuration ---
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'
CONTAINER_TABLE_NAME = 'invoice_containers'

if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'."); st.info("Please add an invoice first."); st.stop()

# --- Initialize Session State for Filters ---
filter_keys = ['view_option', 'ref_filter', 'no_filter', 'po_filter', 'item_filter',
               'inv_date_text_filter', 'prod_order_filter', 'date_range', 'container_filter']
for key in filter_keys:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'date_range' else ("Active" if key == 'view_option' else "")

# --- Helper Function for Resetting Filters ---
def reset_filters():
    for key in filter_keys:
        st.session_state[key] = None if key == 'date_range' else ("Active" if key == 'view_option' else "")

# --- Filter Controls ---
with st.expander("🔍 Filters", expanded=True):
    st.radio("Choose which invoices to display:", ("Active", "Voided", "All"), horizontal=True, key='view_option')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Filter by Invoice Ref:", key='ref_filter')
        st.text_input("Filter by Invoice No:", key='no_filter')
    with col2:
        st.text_input("Filter by PO:", key='po_filter')
        st.text_input("Filter by Item Code:", key='item_filter')
    with col3:
        st.text_input("Filter by Production Order No:", key='prod_order_filter')
        st.text_input("Filter by Container/Truck:", key='container_filter')

    today = datetime.now().date()
    if st.session_state.date_range is None: st.session_state.date_range = (today, today)
    st.date_input("Filter by Creation Date Range:", value=st.session_state.date_range, key='date_range')
    st.button("Reset All Filters", on_click=reset_filters, use_container_width=True)

# --- Dynamic SQL Query Building (Efficient Filtering) ---
try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        # CORRECTED: Using c.inv_ref to join with i.inv_ref
        base_query = f"""
        SELECT
            i.*,
            (SELECT GROUP_CONCAT(c.container_description, ', ')
             FROM {CONTAINER_TABLE_NAME} c
             WHERE c.inv_ref = i.inv_ref) AS containers
        FROM {TABLE_NAME} i
        """
        conditions = []
        params = []

        if st.session_state.view_option == "Active":
            conditions.append("i.status = ?"); params.append('active')
        elif st.session_state.view_option == "Voided":
            conditions.append("i.status = ?"); params.append('voided')

        text_filters_config = {
            'ref_filter': 'i.inv_ref', 'no_filter': 'i.inv_no', 'po_filter': 'i.po',
            'item_filter': 'i.item', 'inv_date_text_filter': 'i.inv_date',
            'prod_order_filter': 'i.production_order_no'
        }
        for key, column in text_filters_config.items():
            if st.session_state[key]:
                conditions.append(f"LOWER({column}) LIKE ?"); params.append(f"%{st.session_state[key].lower()}%")

        # CORRECTED: Subquery now correctly selects c.inv_ref
        if st.session_state.container_filter:
            conditions.append(f"""
            i.inv_ref IN (SELECT c.inv_ref FROM {CONTAINER_TABLE_NAME} c WHERE LOWER(c.container_description) LIKE ?)
            """)
            params.append(f"%{st.session_state.container_filter.lower()}%")

        if st.session_state.date_range and len(st.session_state.date_range) == 2:
            start_date, end_date = st.session_state.date_range
            start_datetime = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S')
            conditions.append("i.creating_date BETWEEN ? AND ?"); params.extend([start_datetime, end_datetime])

        if conditions: query = f"{base_query} WHERE {' AND '.join(conditions)}"
        else: query = base_query

        query += " ORDER BY i.creating_date DESC"

        df = pd.read_sql_query(query, conn, params=params)

except Exception as e:
    st.error(f"Could not read data from the database. Error: {e}"); st.exception(e); st.stop()

# --- Display Results ---
if df.empty:
    st.info("No records match your current filter criteria.")
else:
    st.markdown("---")
    with sqlite3.connect(DATABASE_FILE) as conn:
        total_records = conn.execute(f"SELECT COUNT(DISTINCT inv_ref) FROM {TABLE_NAME}").fetchone()[0]
    st.success(f"Showing **{len(df)}** rows from **{df['inv_ref'].nunique()}** unique invoices (Total invoices in DB: **{total_records}**).")
    st.dataframe(df)