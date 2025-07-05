import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

# --- Page Configuration ---
# This should be the first Streamlit command in your app
st.set_page_config(
    page_title="Invoice Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Invoice Dashboard")
st.info("This is the main dashboard. Select other actions from the sidebar.")

# --- Configuration ---
# All data-related folders are now located inside the main 'data' directory.
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'

if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'.")
    st.info("Please add an invoice first by navigating to the 'Add New Invoice' page from the sidebar.")
    st.stop()

# --- Load Data ---
try:
    with sqlite3.connect(DATABASE_FILE) as conn:
        # Only select active invoices for the dashboard
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} WHERE status = 'active'", conn)

    # --- Data Cleaning and Preparation ---
    if 'creating_date' in df.columns:
        df['creating_date'] = pd.to_datetime(df['creating_date'], errors='coerce')
    else:
        st.warning("Warning: 'creating_date' column not found.")
        df['creating_date'] = pd.NaT # Add dummy column to prevent errors

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['sqft'] = pd.to_numeric(df['sqft'], errors='coerce')
    df.dropna(subset=['creating_date', 'amount'], inplace=True)

except Exception as e:
    st.error(f"Could not read or process data. Error: {e}")
    st.exception(e) # Show full traceback for debugging
    st.stop()

# --- Date Range Filter ---
st.header("Filter by Creation Date")

if df.empty:
    st.warning("No active invoice data found in the database to build a dashboard.")
    st.stop()

start_date_default = df['creating_date'].min().date()
end_date_default = df['creating_date'].max().date()

col1, col2 = st.columns(2)
start_date = col1.date_input("Start Date", start_date_default)
end_date = col2.date_input("End Date", end_date_default)

# Ensure start_date is not after end_date
if start_date > end_date:
    st.error("Error: Start date cannot be after end date.")
    st.stop()

start_datetime = datetime.combine(start_date, datetime.min.time())
end_datetime = datetime.combine(end_date, datetime.max.time())

filtered_df = df[(df['creating_date'] >= start_datetime) & (df['creating_date'] <= end_datetime)]

if filtered_df.empty:
    st.warning("No invoice data found for the selected date range. Try expanding the date filter.")
    st.stop()

# --- Display KPIs ---
st.header("Key Performance Indicators")
total_amount = filtered_df['amount'].sum()
total_sqft = filtered_df['sqft'].sum()
invoice_count = filtered_df['inv_ref'].nunique()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Total Invoiced Amount", value=f"${total_amount:,.2f}")
kpi2.metric(label="Total Square Feet", value=f"{total_sqft:,.0f}")
kpi3.metric(label="Unique Invoices Added", value=invoice_count)

st.divider()

# --- Visualizations ---
st.header("Visualizations")

# Invoiced Amount Over Time (by month)
monthly_data = filtered_df.set_index('creating_date').resample('M')['amount'].sum().reset_index()
monthly_data['creating_date'] = monthly_data['creating_date'].dt.strftime('%b %Y')
st.subheader("Total Amount by Month Added")
st.bar_chart(monthly_data.set_index('creating_date')['amount'])

# Top 10 Items by Amount, grouped by the 'item' field
st.subheader("Top 10 Products by Invoiced Amount (by Item Code)")
top_items = filtered_df.groupby('item')['amount'].sum().nlargest(10)
st.bar_chart(top_items)
