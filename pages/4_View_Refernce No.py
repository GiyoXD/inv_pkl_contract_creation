import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(page_title="Invoice Summary", layout="wide")
st.title("Invoice Summary & Lookup 🧾")
st.info("This page provides a summarized view of each invoice, showing total sqft, amount, and associated containers.")

# --- Configuration ---
try:
    # This assumes the script is in a 'pages' subdirectory.
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIRECTORY = PROJECT_ROOT / "data" / "Invoice Record"
    DATABASE_FILE = DATA_DIRECTORY / "master_invoice_data.db"
    TABLE_NAME = 'invoices'
    CONTAINER_TABLE_NAME = 'invoice_containers'
except Exception:
    # Fallback for local running if not in a 'pages' folder
    PROJECT_ROOT = Path(__file__).resolve().parent
    DATA_DIRECTORY = PROJECT_ROOT / "data" / "Invoice Record"
    DATABASE_FILE = DATA_DIRECTORY / "master_invoice_data.db"
    TABLE_NAME = 'invoices'
    CONTAINER_TABLE_NAME = 'invoice_containers'


# --- Check for Database ---
if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'.")
    st.info("Please go to the 'Add Invoice' page to add an invoice first.")
    st.stop()

# --- Initialize Session State for Filters ---
if 'summary_ref_filter' not in st.session_state:
    st.session_state.summary_ref_filter = ""
if 'summary_no_filter' not in st.session_state:
    st.session_state.summary_no_filter = ""
if 'summary_container_filter' not in st.session_state:
    st.session_state.summary_container_filter = ""
if 'summary_date_range' not in st.session_state:
    st.session_state.summary_date_range = None

# --- Helper Function for Resetting Filters ---
def reset_summary_filters():
    """Callback function to reset all filter widgets to their default state."""
    st.session_state.summary_ref_filter = ""
    st.session_state.summary_no_filter = ""
    st.session_state.summary_container_filter = ""
    st.session_state.summary_date_range = None


# --- Filter Controls ---
with st.expander("🔍 Filters", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Filter by Invoice Ref:", key='summary_ref_filter')
    with col2:
        st.text_input("Filter by Invoice No:", key='summary_no_filter')
    with col3:
        st.text_input("Filter by Container:", key='summary_container_filter')

    # --- Date Range Filter (Corrected to handle empty database) ---
    min_date_default = datetime.now().date()
    max_date_default = datetime.now().date()

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            # Fetch min and max dates only if the table is not empty
            min_date_result = conn.execute(f"SELECT MIN(creating_date) FROM {TABLE_NAME}").fetchone()[0]
            if min_date_result:  # Check if a date was actually returned
                min_date_query = pd.to_datetime(min_date_result)
                min_date_default = min_date_query.date()

            max_date_result = conn.execute(f"SELECT MAX(creating_date) FROM {TABLE_NAME}").fetchone()[0]
            if max_date_result:  # Check if a date was actually returned
                max_date_query = pd.to_datetime(max_date_result)
                max_date_default = max_date_query.date()

    except (sqlite3.Error, TypeError, ValueError):
        # This block will catch other potential database errors,
        # and the defaults defined above will be used.
        pass

    if st.session_state.summary_date_range is None:
        st.session_state.summary_date_range = (min_date_default, max_date_default)

    st.date_input(
        "Filter by Creation Date Range:",
        key='summary_date_range',
        value=st.session_state.summary_date_range,
        min_value=min_date_default,
        max_value=max_date_default
    )
    
    st.button("Reset Filters", on_click=reset_summary_filters, use_container_width=True)


# --- Build and Execute SQL Query ---
try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        # This query groups by invoice details and calculates the sum of sqft and amount.
        # It also joins with the containers table to get a list of associated containers.
        query = f"""
            SELECT
                i.inv_no,
                i.inv_ref,
                i.inv_date,
                MAX(i.status) as status,
                SUM(CAST(i.sqft AS REAL)) as total_sqft,
                SUM(CAST(i.amount AS REAL)) as total_amount,
                i.creating_date,
                (SELECT GROUP_CONCAT(c.container_description, ', ')
                 FROM {CONTAINER_TABLE_NAME} c
                 WHERE c.inv_ref = i.inv_ref) AS containers
            FROM {TABLE_NAME} i
        """

        conditions = []
        params = []

        # Apply text filters
        if st.session_state.summary_ref_filter:
            conditions.append("i.inv_ref LIKE ?")
            params.append(f"%{st.session_state.summary_ref_filter}%")
        if st.session_state.summary_no_filter:
            conditions.append("i.inv_no LIKE ?")
            params.append(f"%{st.session_state.summary_no_filter}%")
        
        # Apply container filter using a subquery
        if st.session_state.summary_container_filter:
            conditions.append(f"i.inv_ref IN (SELECT c.inv_ref FROM {CONTAINER_TABLE_NAME} c WHERE c.container_description LIKE ?)")
            params.append(f"%{st.session_state.summary_container_filter}%")

        # Apply date range filter
        if st.session_state.summary_date_range and len(st.session_state.summary_date_range) == 2:
            start_date, end_date = st.session_state.summary_date_range
            start_datetime = datetime.combine(start_date, datetime.min.time()).strftime('%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.combine(end_date, datetime.max.time()).strftime('%Y-%m-%d %H:%M:%S')
            conditions.append("i.creating_date BETWEEN ? AND ?")
            params.extend([start_datetime, end_datetime])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add the GROUP BY and ORDER BY clauses
        query += """
            GROUP BY i.inv_no, i.inv_ref, i.inv_date, i.creating_date
            ORDER BY i.creating_date DESC
        """

        df_summary = pd.read_sql_query(query, conn, params=params)

except sqlite3.Error as e:
    st.error(f"An error occurred while querying the database: {e}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
    st.stop()


# --- Display Results ---
if df_summary.empty:
    st.warning("No invoices match your current filter criteria.")
else:
    st.success(f"Found {len(df_summary)} matching invoices.")

    # Reorder columns for better presentation
    display_columns = [
        'inv_no', 'inv_ref', 'inv_date', 'containers', 'total_sqft',
        'total_amount', 'status', 'creating_date'
    ]
    # Ensure all columns exist before trying to display them
    display_columns = [col for col in display_columns if col in df_summary.columns]

    # Fill NaN values in 'containers' column for better display
    if 'containers' in df_summary.columns:
        df_summary['containers'] = df_summary['containers'].fillna('N/A')

    st.dataframe(df_summary[display_columns], use_container_width=True)

    # --- Totals ---
    st.markdown("---")
    # Ensure columns are numeric before summing
    total_sqft_sum = pd.to_numeric(df_summary['total_sqft'], errors='coerce').sum()
    total_amount_sum = pd.to_numeric(df_summary['total_amount'], errors='coerce').sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Sqft for Displayed Invoices", value=f"{total_sqft_sum:,.2f}")
    with col2:
        st.metric(label="Total Amount for Displayed Invoices", value=f"{total_amount_sum:,.2f}")