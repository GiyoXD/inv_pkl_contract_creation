import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(page_title="Export Data", layout="wide")
st.title("⬇️ Export Data to CSV")

# --- Configuration ---
# All data-related folders are now located inside the main 'data' directory.
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'
CONTAINER_TABLE_NAME = 'invoice_containers'

if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'.")
    st.stop()

# --- UI to select export mode ---
st.header("1. Select Export Mode")
export_mode = st.radio(
    "Choose the format for the data export:",
    ('Summarized by Invoice', 'All Individual Rows'),
    horizontal=True,
    label_visibility="collapsed"
)

# --- Filter Controls ---
st.header("2. Filter Data for Export by Creation Date")

try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        min_date_result = conn.execute(f"SELECT MIN(creating_date) FROM {TABLE_NAME}").fetchone()[0]
        max_date_result = conn.execute(f"SELECT MAX(creating_date) FROM {TABLE_NAME}").fetchone()[0]
        
        start_date_default = pd.to_datetime(min_date_result).date() if min_date_result else datetime.now().date() - timedelta(days=365)
        end_date_default = pd.to_datetime(max_date_result).date() if max_date_result else datetime.now().date()

except Exception as e:
    st.warning(f"Could not read min/max dates. Using default range. Error: {e}")
    start_date_default = datetime.now().date() - timedelta(days=365)
    end_date_default = datetime.now().date()


col1, col2 = st.columns(2)
start_date_filter = col1.date_input("Start Date", start_date_default)
end_date_filter = col2.date_input("End Date", end_date_default)

start_datetime = datetime.combine(start_date_filter, datetime.min.time())
end_datetime = datetime.combine(end_date_filter, datetime.max.time())

df_export = pd.DataFrame() 

try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        if export_mode == 'Summarized by Invoice':
            # --- MODIFICATION START ---
            # Added SUM for the cbm column.
            query = f"""
                SELECT
                    i.inv_no,
                    i.inv_ref,
                    i.inv_date,
                    MAX(i.status) as status,
                    SUM(CAST(i.sqft AS REAL)) as total_sqft,
                    SUM(CAST(i.amount AS REAL)) as total_amount,
                    SUM(CAST(i.pcs AS INTEGER)) as total_pcs,
                    SUM(CAST(i.net AS REAL)) as total_net,
                    SUM(CAST(i.gross AS REAL)) as total_gross,
                    SUM(CAST(i.cbm AS REAL)) as total_cbm,
                    i.creating_date,
                    (SELECT GROUP_CONCAT(c.container_description, ', ')
                     FROM {CONTAINER_TABLE_NAME} c
                     WHERE c.inv_ref = i.inv_ref) AS containers
                FROM {TABLE_NAME} i
                WHERE i.creating_date BETWEEN ? AND ?
                GROUP BY i.inv_no, i.inv_ref, i.inv_date, i.creating_date
                ORDER BY i.creating_date DESC
            """
            # --- MODIFICATION END ---
            params = [start_datetime.strftime('%Y-%m-%d %H:%M:%S'), end_datetime.strftime('%Y-%m-%d %H:%M:%S')]
            df_export = pd.read_sql_query(query, conn, params=params)

        else: # 'All Individual Rows'
            query = f"SELECT * FROM {TABLE_NAME} WHERE creating_date BETWEEN ? AND ?"
            params = [start_datetime.strftime('%Y-%m-%d %H:%M:%S'), end_datetime.strftime('%Y-%m-%d %H:%M:%S')]
            df_export = pd.read_sql_query(query, conn, params=params)

except Exception as e:
    st.error(f"Could not read data. Error: {e}")
    st.stop()


# --- Display Preview and Export Button ---
st.header("3. Preview and Download")
st.write(f"Found **{len(df_export)}** records matching your criteria for the **'{export_mode}'** mode.")
st.dataframe(df_export)

if not df_export.empty:
    csv = df_export.to_csv(index=False).encode('utf-8')
    
    file_name_mode = "summarized" if export_mode == 'Summarized by Invoice' else "all_rows"
    file_name = f"invoice_export_{file_name_mode}_{start_date_filter}_to_{end_date_filter}.csv"

    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=file_name,
        mime='text/csv',
        use_container_width=True
    )
else:
    st.warning("No data to export for the selected filters. Try expanding the date range.")