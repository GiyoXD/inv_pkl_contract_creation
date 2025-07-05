import streamlit as st
import pandas as pd
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import shutil
import json

# --- Page Configuration ---
st.set_page_config(page_title="Add Invoice", layout="wide")
st.title("Add / Amend Invoice ➕")

# --- Configuration ---
# All data-related folders are now located inside the main 'data' directory.
DATA_ROOT = Path("data")
JSON_DIRECTORY = DATA_ROOT / 'invoices_to_process'
PROCESSED_DIRECTORY = DATA_ROOT / 'processed_invoices'
REJECTED_DIRECTORY = DATA_ROOT / 'rejected_invoices'
AMENDMENT_ARCHIVE_DIRECTORY = DATA_ROOT / 'amendment_archive'
DB_DIRECTORY = DATA_ROOT / 'Invoice Record'
DATABASE_FILE = DB_DIRECTORY / 'master_invoice_data.db'
TABLE_NAME = 'invoices'
FINAL_COLUMNS = [
    'inv_no', 'inv_date', 'inv_ref', 'po', 'item', 'description', 'pcs',
    'sqft', 'pallet_count', 'unit', 'amount', 'net', 'gross', 'cbm',
    'production_order_no', 'creating_date', 'status'
]

# --- Helper Functions ---
def setup_directories():
    """Create all necessary directories if they don't exist."""
    JSON_DIRECTORY.mkdir(exist_ok=True)
    PROCESSED_DIRECTORY.mkdir(exist_ok=True)
    REJECTED_DIRECTORY.mkdir(exist_ok=True)
    AMENDMENT_ARCHIVE_DIRECTORY.mkdir(exist_ok=True)
    DB_DIRECTORY.mkdir(exist_ok=True)

def get_active_invoice_data(inv_ref):
    """Gets all data for a specific ACTIVE invoice reference. Returns a DataFrame or None."""
    if not os.path.exists(DATABASE_FILE):
        return None
    with sqlite3.connect(DATABASE_FILE) as conn:
        query = f"SELECT * FROM {TABLE_NAME} WHERE inv_ref = ? AND status = 'active'"
        df = pd.read_sql_query(query, conn, params=(inv_ref,))
        return df if not df.empty else None

def process_json_file(file_path):
    """Reads a JSON file and converts its content into a standardized DataFrame."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_tables_data = data.get('processed_tables_data', {})
    if not all_tables_data: raise ValueError("File does not contain 'processed_tables_data'.")

    first_table = next(iter(all_tables_data.values()))
    header_info = {
        "inv_no": str(first_table.get('inv_no', ['N/A'])[0]),
        "inv_date": str(first_table.get('inv_date', ['N/A'])[0]),
        "inv_ref": str(first_table.get('inv_ref', ['N/A'])[0])
    }

    all_line_items = [pd.DataFrame(tbl) for tbl in all_tables_data.values()]
    df = pd.concat(all_line_items, ignore_index=True)
    df['inv_ref'] = header_info['inv_ref']
    df['inv_no'] = header_info['inv_no']
    df['inv_date'] = header_info['inv_date']
    df['creating_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['status'] = 'active'
    return df.reindex(columns=FINAL_COLUMNS)

def handle_amendment(source_file_path, new_df, existing_df):
    """The UI and logic for approving an amendment."""
    st.warning(f"This invoice No **'{new_df['inv_no'].iloc[0]}'** already exists as an active record. Please review the changes and approve.", icon="⚠️")

    st.header("Review Changes")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Data in Database")
        st.dataframe(existing_df)
    with col2:
        st.subheader("New Data from File")
        st.dataframe(new_df)

    st.header("Approve Amendment?")
    c1, c2, _ = st.columns([1, 1, 4])
    if c1.button("✅ Accept Changes", use_container_width=True):
        # 1. Archive the old data
        archive_filename = f"{new_df['inv_ref'].iloc[0]}_archived_on_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        existing_df.to_json(AMENDMENT_ARCHIVE_DIRECTORY / archive_filename, orient='records', indent=4)

        # 2. Overwrite the old data in the database
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (new_df['inv_ref'].iloc[0],))
            new_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            conn.commit()

        # 3. Move the source file of the change
        shutil.move(str(source_file_path), str(PROCESSED_DIRECTORY / source_file_path.name))
        st.success("Amendment approved! Old data archived and database updated.")
        st.rerun()

    if c2.button("❌ Reject Changes", use_container_width=True):
        shutil.move(str(source_file_path), str(REJECTED_DIRECTORY / source_file_path.name))
        st.warning("Amendment rejected. The new file has been moved to the 'rejected_invoices' folder.")
        st.rerun()

def handle_new_invoice(source_file_path, new_df):
    """The UI and logic for adding a brand new invoice."""
    st.info(f"Now verifying new invoice: **{source_file_path.name}**")
    st.dataframe(new_df)

    c1, c2, _ = st.columns([1, 1, 4])
    if c1.button("✅ Accept", use_container_width=True):
        with sqlite3.connect(DATABASE_FILE) as conn:
            new_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        shutil.move(str(source_file_path), str(PROCESSED_DIRECTORY / source_file_path.name))
        st.success(f"Invoice '{new_df['inv_ref'].iloc[0]}' was added."); st.rerun()
    if c2.button("❌ Reject", use_container_width=True):
        shutil.move(str(source_file_path), str(REJECTED_DIRECTORY / source_file_path.name))
        st.warning(f"Invoice '{new_df['inv_ref'].iloc[0]}' was rejected."); st.rerun()

# --- Main Application Logic ---
setup_directories()
json_files = sorted(JSON_DIRECTORY.glob('*.json'))

if not json_files:
    st.success("✅ No new invoices to process."); st.stop()

# Process the first file found in the directory
file_to_process = json_files[0]

try:
    new_invoice_df = process_json_file(file_to_process)
    inv_ref = new_invoice_df['inv_ref'].iloc[0]

    # Check if this invoice reference already exists and is active
    existing_invoice_df = get_active_invoice_data(inv_ref)

    if existing_invoice_df is not None:
        # --- Amendment Workflow ---
        handle_amendment(file_to_process, new_invoice_df, existing_invoice_df)
    else:
        # --- New Invoice Workflow ---
        handle_new_invoice(file_to_process, new_invoice_df)

except Exception as e:
    st.error(f"Error processing file '{file_to_process.name}': {e}")
    if st.button("Move Corrupted File to Rejected"):
        shutil.move(str(file_to_process), str(REJECTED_DIRECTORY / file_to_process.name))
        st.rerun()
    st.stop()