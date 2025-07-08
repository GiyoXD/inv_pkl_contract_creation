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
DATA_ROOT = Path("data")
JSON_DIRECTORY = DATA_ROOT / 'invoices_to_process'
PROCESSED_DIRECTORY = DATA_ROOT / 'processed_invoices'
REJECTED_DIRECTORY = DATA_ROOT / 'rejected_invoices'
AMENDMENT_ARCHIVE_DIRECTORY = DATA_ROOT / 'amendment_archive'
DB_DIRECTORY = DATA_ROOT / 'Invoice Record'
DATABASE_FILE = DB_DIRECTORY / 'master_invoice_data.db'
TABLE_NAME = 'invoices'
CONTAINER_TABLE_NAME = 'invoice_containers'
FINAL_COLUMNS = [
    'inv_no', 'inv_date', 'inv_ref', 'po', 'item', 'description', 'pcs',
    'sqft', 'pallet_count', 'unit', 'amount', 'net', 'gross', 'cbm',
    'production_order_no', 'creating_date', 'status'
]

# --- Helper Functions ---
def setup_directories():
    """Create all necessary directories if they don't exist."""
    for directory in [JSON_DIRECTORY, PROCESSED_DIRECTORY, REJECTED_DIRECTORY, AMENDMENT_ARCHIVE_DIRECTORY, DB_DIRECTORY]:
        directory.mkdir(exist_ok=True)

def get_existing_invoice_data(inv_ref, inv_no):
    """
    Gets all data for a specific invoice by checking for a matching
    inv_ref OR inv_no, regardless of status or case.
    """
    if not os.path.exists(DATABASE_FILE):
        return None
    with sqlite3.connect(DATABASE_FILE) as conn:
        # FINAL, CORRECTED QUERY: Checks for either identifier, case-insensitively.
        query = f"""
        SELECT i.*,
               (SELECT GROUP_CONCAT(c.container_description, ', ')
                FROM {CONTAINER_TABLE_NAME} c
                WHERE c.inv_ref = i.inv_ref) AS containers
        FROM {TABLE_NAME} i
        WHERE LOWER(i.inv_ref) = LOWER(?) OR LOWER(i.inv_no) = LOWER(?)
        """
        # Pass both parameters to the SQL query
        df = pd.read_sql_query(query, conn, params=(inv_ref, inv_no))
        return df if not df.empty else None

def process_json_file(file_path):
    """
    Reads a JSON file and converts its content into a standardized DataFrame
    and a list of container types.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_tables_data = data.get('processed_tables_data', {})
    if not all_tables_data: raise ValueError("File does not contain 'processed_tables_data'.")

    first_table = next(iter(all_tables_data.values()))
    header_info = {
        "inv_no": str(first_table.get('inv_no', ['N/A'])[0]).strip(),
        "inv_date": str(first_table.get('inv_date', ['N/A'])[0]).strip(),
        "inv_ref": str(first_table.get('inv_ref', ['N/A'])[0]).strip()
    }

    container_str = str(first_table.get('container_type', [''])[0])
    container_list = [c.strip() for c in container_str.split(',') if c.strip()]

    all_line_items = [pd.DataFrame(tbl) for tbl in all_tables_data.values()]
    df = pd.concat(all_line_items, ignore_index=True)
    df['inv_ref'] = header_info['inv_ref']
    df['inv_no'] = header_info['inv_no']
    df['inv_date'] = header_info['inv_date']
    df['creating_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['status'] = 'active'

    if 'container_type' in df.columns:
        df = df.drop(columns=['container_type'])

    return df.reindex(columns=FINAL_COLUMNS), container_list

def handle_amendment(source_file_path, new_df, existing_df, new_container_list):
    """
    The UI and logic for approving an amendment, using the "delete-then-replace" method.
    """
    st.warning(f"This Invoice Ref **'{new_df['inv_ref'].iloc[0]}'** or Invoice No **'{new_df['inv_no'].iloc[0]}'** already exists. Please review the changes and approve the amendment.", icon="⚠️")

    st.header("Review Changes")
    existing_containers = existing_df['containers'].iloc[0] if 'containers' in existing_df.columns and not pd.isna(existing_df['containers'].iloc[0]) else "None"
    new_containers_str = ", ".join(new_container_list) if new_container_list else "None"

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Data in Database")
        st.markdown(f"**Containers:** `{existing_containers}`")
        st.dataframe(existing_df.drop(columns=['containers'], errors='ignore'))
    with col2:
        st.subheader("New Data from File")
        st.markdown(f"**Containers:** `{new_containers_str}`")
        st.dataframe(new_df)

    st.header("Approve Amendment?")
    c1, c2, _ = st.columns([1, 1, 4])
    if c1.button("✅ Accept Changes", use_container_width=True):
        inv_ref_to_replace = new_df['inv_ref'].iloc[0]

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            
            archive_filename = f"{inv_ref_to_replace}_archived_on_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
            existing_df.to_json(AMENDMENT_ARCHIVE_DIRECTORY / archive_filename, orient='records', indent=4)
            
            st.write(f"Deleting old records for Invoice Ref: `{inv_ref_to_replace}`...")
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (inv_ref_to_replace,))
            cursor.execute(f"DELETE FROM {CONTAINER_TABLE_NAME} WHERE inv_ref = ?", (inv_ref_to_replace,))
            
            st.write("Inserting new records...")
            new_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            if new_container_list:
                for container in new_container_list:
                    cursor.execute(f"INSERT INTO {CONTAINER_TABLE_NAME} (inv_ref, container_description) VALUES (?, ?)", (inv_ref_to_replace, container))
            
            conn.commit()

        shutil.move(str(source_file_path), str(PROCESSED_DIRECTORY / source_file_path.name))
        st.success("Amendment approved! Old data was replaced in the database.")
        st.rerun()

    if c2.button("❌ Reject Changes", use_container_width=True):
        shutil.move(str(source_file_path), str(REJECTED_DIRECTORY / source_file_path.name))
        st.warning("Amendment rejected. The new file has been moved to the 'rejected_invoices' folder.")
        st.rerun()

def handle_new_invoice(source_file_path, new_df, container_list):
    """The UI and logic for adding a brand new invoice."""
    st.info(f"Now verifying new invoice: **{source_file_path.name}**")
    new_inv_ref = new_df['inv_ref'].iloc[0]
    
    new_containers_str = ", ".join(container_list) if container_list else "None"
    st.markdown(f"**Containers/Trucks:** `{new_containers_str}`")
    st.dataframe(new_df)

    c1, c2, _ = st.columns([1, 1, 4])
    if c1.button("✅ Accept", use_container_width=True):
        with sqlite3.connect(DATABASE_FILE) as conn:
            new_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            
            if container_list:
                cursor = conn.cursor()
                for container in container_list:
                    cursor.execute(f"INSERT INTO {CONTAINER_TABLE_NAME} (inv_ref, container_description) VALUES (?, ?)",
                                   (new_inv_ref, container))
                conn.commit()
                
        shutil.move(str(source_file_path), str(PROCESSED_DIRECTORY / source_file_path.name))
        st.success(f"Invoice '{new_inv_ref}' was added."); st.rerun()
    if c2.button("❌ Reject", use_container_width=True):
        shutil.move(str(source_file_path), str(REJECTED_DIRECTORY / source_file_path.name))
        st.warning(f"Invoice '{new_inv_ref}' was rejected."); st.rerun()

# --- Main Application Logic ---
setup_directories()
json_files = sorted(JSON_DIRECTORY.glob('*.json'))

if not json_files:
    st.success("✅ No new invoices to process."); st.stop()

file_to_process = json_files[0]

try:
    new_invoice_df, container_list = process_json_file(file_to_process)
    
    # Clean and get both identifiers
    inv_ref = str(new_invoice_df['inv_ref'].iloc[0]).strip()
    inv_no = str(new_invoice_df['inv_no'].iloc[0]).strip()

    # Pass BOTH inv_ref and inv_no to the checking function
    existing_invoice_df = get_existing_invoice_data(inv_ref, inv_no)

    if existing_invoice_df is not None:
        # --- Amendment Workflow ---
        handle_amendment(file_to_process, new_invoice_df, existing_invoice_df, container_list)
    else:
        # --- New Invoice Workflow ---
        handle_new_invoice(file_to_process, new_invoice_df, container_list)

except Exception as e:
    st.error(f"Error processing file '{file_to_process.name}': {e}")
    st.exception(e) 
    if st.button("Move Corrupted File to Rejected"):
        shutil.move(str(file_to_process), str(REJECTED_DIRECTORY / file_to_process.name))
        st.rerun()
    st.stop()