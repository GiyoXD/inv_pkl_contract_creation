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

if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'.")
    st.stop()

# --- Load Data ---
try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        
    # UPDATED: Use the reliable 'creating_date' column.
    df['creating_date'] = pd.to_datetime(df['creating_date'], errors='coerce')

except Exception as e:
    st.error(f"Could not read data. Error: {e}")
    st.stop()

# --- Filter Controls ---
st.header("Filter Data for Export by Creation Date")
start_date_default = df['creating_date'].min().date() if not df.empty else datetime.now().date() - timedelta(days=365)
end_date_default = df['creating_date'].max().date() if not df.empty else datetime.now().date()

col1, col2 = st.columns(2)
start_date_filter = col1.date_input("Start Date", start_date_default)
end_date_filter = col2.date_input("End Date", end_date_default)

# Convert dates for filtering
start_datetime = datetime.combine(start_date_filter, datetime.min.time())
end_datetime = datetime.combine(end_date_filter, datetime.max.time())

# Apply filters
filtered_df = df[
    (df['creating_date'] >= start_datetime) &
    (df['creating_date'] <= end_datetime)
].copy()


# --- Display Preview and Export Button ---
st.header("Preview of Export Data")
st.write(f"Found **{len(filtered_df)}** records matching your criteria.")
st.dataframe(filtered_df)

if not filtered_df.empty:
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"invoice_export_{start_date_filter}_to_{end_date_filter}.csv",
        mime='text/csv',
        use_container_width=True
    )
else:
    st.warning("No data to export for the selected filters. Try expanding the date range.")