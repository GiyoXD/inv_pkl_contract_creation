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
# REJECTED_DIRECTORY is no longer needed as files will be deleted.
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
    # REJECTED_DIRECTORY has been removed from this setup.
    for directory in [JSON_DIRECTORY, PROCESSED_DIRECTORY, AMENDMENT_ARCHIVE_DIRECTORY, DB_DIRECTORY]:
        directory.mkdir(exist_ok=True)

def get_existing_invoice_data(inv_ref, inv_no):
    """
    Gets all data for a specific invoice based on an EXACT match of inv_ref or inv_no.
    """
    if not os.path.exists(DATABASE_FILE):
        return None
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        query = f"""
        SELECT i.*,
               (SELECT GROUP_CONCAT(c.container_description, ', ')
                FROM {CONTAINER_TABLE_NAME} c
                WHERE c.inv_ref = i.inv_ref) AS containers
        FROM {TABLE_NAME} i
        WHERE (LOWER(i.inv_ref) = LOWER(?) AND i.inv_ref != '') OR (LOWER(i.inv_no) = LOWER(?) AND i.inv_no != '')
        """
        df = pd.read_sql_query(query, conn, params=(inv_ref, inv_no))
        return df if not df.empty else None
    finally:
        if conn:
            conn.close()


def process_json_file(file_path):
    """
    Processes JSON focusing on 'processed_tables_data' and
    extracts container info if provided by the upstream script.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_tables = data.get('processed_tables_data')
    if not processed_tables:
        if 'aggregated_summary' in data:
            df = pd.DataFrame([data['aggregated_summary']])
        else:
            raise ValueError("File does not contain a 'processed_tables_data' or 'aggregated_summary' section.")
    else:
        all_dfs = [pd.DataFrame(table_data) for table_data in processed_tables.values()]
        df = pd.concat(all_dfs, ignore_index=True)

    # --- Data Cleaning ---
    df['inv_no'] = df['inv_no'].apply(lambda x: x if isinstance(x, str) and x.strip() and not x.startswith('0') else pd.NA).ffill()
    df['inv_ref'] = df['inv_ref'].apply(lambda x: str(x).strip() if isinstance(x, str) and x.strip() else pd.NA).ffill()
    df['inv_date'] = pd.to_datetime(df['inv_date'], errors='coerce').ffill().dt.strftime('%Y-%m-%d')

    # --- Extract Container Info ---
    manual_containers = []
    if 'container_type' in df.columns:
        container_str = df['container_type'].dropna().astype(str).unique()
        if len(container_str) > 0:
            manual_containers = [c.strip() for c in container_str[0].split(',') if c.strip()]

    # --- Common final processing ---
    df['creating_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df['status'] = 'active'
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    return df.reindex(columns=FINAL_COLUMNS), manual_containers

def display_containers(container_list):
    """Displays a list of containers as colorful, styled tags."""
    if not container_list:
        st.markdown("`None`")
        return

    colors = ["#FFC107", "#03A9F4", "#4CAF50", "#F44336", "#9C27B0", "#FF9800"]
    html_tags = ""
    for i, container in enumerate(container_list):
        color = colors[i % len(colors)]
        html_tags += f"""
        <span style="background-color: {color}; color: white; padding: 5px 10px; margin: 3px; border-radius: 5px; display: inline-block;">
            {container}
        </span>
        """
    st.markdown(html_tags, unsafe_allow_html=True)


def handle_amendment(source_file_path, new_df, existing_df, manual_containers):
    """The UI for approving an amendment, now with deletion for rejected files."""
    st.warning(f"This Invoice Ref **'{new_df['inv_ref'].iloc[0]}'** or Invoice No **'{new_df['inv_no'].iloc[0]}'** already exists. Please review the changes and approve the amendment.", icon="⚠️")

    st.header("Review Changes")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Data in Database")
        st.dataframe(existing_df.drop(columns=['containers'], errors='ignore'))
    with col2:
        st.subheader("New Data from File")
        st.dataframe(new_df)

    st.subheader("Containers / Trucks")
    display_containers(manual_containers)

    st.header("Approve Amendment?")
    c1, c2, _ = st.columns([1, 1, 4])
    if c1.button("✅ Accept Changes", use_container_width=True):
        inv_refs_to_delete = existing_df['inv_ref'].unique().tolist()
        new_inv_ref = new_df['inv_ref'].iloc[0]

        conn = None
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()

            st.write(f"Deleting all records for matched Invoice Refs: `{', '.join(inv_refs_to_delete)}`...")
            for ref in inv_refs_to_delete:
                cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (ref,))
                cursor.execute(f"DELETE FROM {CONTAINER_TABLE_NAME} WHERE inv_ref = ?", (ref,))

            st.write("Inserting new records...")
            new_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)

            if manual_containers:
                st.write("Saving container info...")
                for container in manual_containers:
                    cursor.execute(f"INSERT INTO {CONTAINER_TABLE_NAME} (inv_ref, container_description) VALUES (?, ?)", (new_inv_ref, container))
            conn.commit()
        finally:
            if conn:
                conn.close()

        shutil.move(str(source_file_path), str(PROCESSED_DIRECTORY / source_file_path.name))
        st.success("Amendment approved! Old data was replaced and the source file was processed.")
        st.rerun()

    if c2.button("❌ Reject Changes", use_container_width=True):
        os.remove(source_file_path) # DELETES the file
        st.warning("Amendment rejected. The source JSON file has been permanently deleted.")
        st.rerun()


def handle_new_invoice(source_file_path, new_df, manual_containers):
    """The UI for adding a new invoice, now with deletion for rejected files."""
    st.info(f"Now verifying new invoice: **{source_file_path.name}**")
    new_inv_ref = new_df['inv_ref'].iloc[0]

    st.dataframe(new_df)
    st.subheader("Containers / Trucks")
    display_containers(manual_containers)

    c1, c2, _ = st.columns([1, 1, 4])
    if c1.button("✅ Accept", use_container_width=True):
        conn = None
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            new_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)

            if manual_containers:
                cursor = conn.cursor()
                st.write("Saving container info...")
                for container in manual_containers:
                    cursor.execute(f"INSERT INTO {CONTAINER_TABLE_NAME} (inv_ref, container_description) VALUES (?, ?)",
                                   (new_inv_ref, container))
                conn.commit()
        finally:
            if conn:
                conn.close()

        shutil.move(str(source_file_path), str(PROCESSED_DIRECTORY / source_file_path.name))
        st.success(f"Invoice '{new_inv_ref}' was added."); st.rerun()

    if c2.button("❌ Reject", use_container_width=True):
        os.remove(source_file_path) # DELETES the file
        st.warning(f"Invoice '{new_inv_ref}' was rejected and the source file has been deleted."); st.rerun()

# --- Main Application Logic ---
setup_directories()
json_files = sorted(JSON_DIRECTORY.glob('*.json'))

if not json_files:
    st.success("✅ No new invoices to process."); st.stop()

file_to_process = json_files[0]

try:
    new_invoice_df, manual_containers = process_json_file(file_to_process)

    if new_invoice_df.empty:
        raise ValueError("Processing the file resulted in an empty dataset.")

    inv_ref = str(new_invoice_df['inv_ref'].iloc[0]).strip()
    inv_no = str(new_invoice_df['inv_no'].iloc[0]).strip()

    if not inv_ref and not inv_no:
        raise ValueError("Could not determine a valid Invoice Ref or Invoice No from the file.")

    existing_invoice_df = get_existing_invoice_data(inv_ref, inv_no)

    if existing_invoice_df is not None:
        handle_amendment(file_to_process, new_invoice_df, existing_invoice_df, manual_containers)
    else:
        handle_new_invoice(file_to_process, new_invoice_df, manual_containers)

except Exception as e:
    st.error(f"Error processing file '{file_to_process.name}': {e}")
    st.exception(e)
    # Changed button text and action to "Delete"
    if st.button("🗑️ Delete Corrupted File"):
        os.remove(file_to_process) # DELETES the file
        st.warning(f"The corrupted file '{file_to_process.name}' has been deleted.")
        st.rerun()
    st.stop()