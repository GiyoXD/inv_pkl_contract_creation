import json
import pandas as pd
import os
from pathlib import Path
import sqlite3
from datetime import datetime  # --- NEW: Import the datetime module

# --- Configuration ---
JSON_DIRECTORY = 'invoices_to_process'
DATA_DIRECTORY = 'Invoice Record'
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'

# --- MODIFIED: Define the final structure of the database table with the new date field ---
FINAL_COLUMNS = [
    'inv_no', 'inv_date', 'inv_ref',
    'po', 'item', 'description', 'pcs', 'sqft', 'pallet_count',
    'unit', 'amount', 'net', 'gross', 'cbm', 'production_order_no',
    'creating_date'  # --- NEW: Added the new column for the creation timestamp
]

def create_database_table_if_not_exists():
    """Ensures the database file and the 'invoices' table exist with the correct schema."""
    try:
        os.makedirs(DATA_DIRECTORY, exist_ok=True)
        with sqlite3.connect(DATABASE_FILE) as conn:
            # The following line automatically includes the new 'creating_date' column
            column_definitions = ", ".join([f'"{col}" TEXT' for col in FINAL_COLUMNS])
            conn.execute(f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({column_definitions})')
        print(f"Database '{DATABASE_FILE}' and table '{TABLE_NAME}' are ready.")
    except sqlite3.Error as e:
        print(f"--- DATABASE ERROR: Failed to create or verify table. Error: {e} ---")
        exit()

def process_batch_invoices():
    """
    Processes JSON files. Validation is based ONLY on the first table found.
    If the first table is a valid header, all tables in the file are processed.
    """
    json_path = Path(JSON_DIRECTORY)
    if not json_path.is_dir():
        print(f"--- ERROR: Directory not found: '{JSON_DIRECTORY}' ---")
        return

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            existing_refs = set(pd.read_sql_query(f"SELECT DISTINCT inv_ref FROM {TABLE_NAME}", conn)['inv_ref'])
        print(f"Found {len(existing_refs)} existing reference numbers in the database.")
    except Exception:
        existing_refs = set()

    successfully_added_refs = []
    
    print(f"\nScanning for JSON files in '{JSON_DIRECTORY}'...")
    
    for json_file in sorted(json_path.glob('*.json')):
        print(f"\n--- Processing: {json_file.name} ---")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("REJECTED: Invalid JSON format.")
            continue
        except Exception as e:
            print(f"REJECTED: Could not read file. Error: {e}")
            continue

        all_tables_data = data.get('processed_tables_data', {})
        if not all_tables_data:
            print("REJECTED: File does not contain 'processed_tables_data'.")
            continue

        header_info = None
        
        table_keys = list(all_tables_data.keys())
        
        if table_keys:
            first_table_data = all_tables_data[table_keys[0]]
            if 'inv_no' in first_table_data and first_table_data['inv_no'] and \
               'inv_date' in first_table_data and first_table_data['inv_date'] and \
               'inv_ref' in first_table_data and first_table_data['inv_ref']:
                
                header_info = {
                    "inv_no": str(first_table_data['inv_no'][0]),
                    "inv_date": str(first_table_data['inv_date'][0]),
                    "inv_ref": str(first_table_data['inv_ref'][0])
                }

        if header_info is None:
            print("REJECTED: No valid header (inv_no, inv_date, inv_ref) found in the first table.")
            continue

        file_ref_no = header_info['inv_ref']

        if file_ref_no in existing_refs:
            print(f"REJECTED: Reference # '{file_ref_no}' already exists in the database.")
            continue

        print(f"ACCEPTED: Ref # '{file_ref_no}' | Inv # '{header_info['inv_no']}'. Preparing to add to database.")
        
        all_line_items = []
        for table_key in table_keys:
            table_data = all_tables_data[table_key]
            all_line_items.append(pd.DataFrame(table_data))

        combined_df = pd.concat(all_line_items, ignore_index=True)
        
        combined_df['inv_ref'] = header_info['inv_ref']
        combined_df['inv_no'] = header_info['inv_no']
        combined_df['inv_date'] = header_info['inv_date']

        # --- NEW: Add the real-time creation timestamp to the DataFrame ---
        creation_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        combined_df['creating_date'] = creation_timestamp

        for col in FINAL_COLUMNS:
            if col not in combined_df.columns:
                combined_df[col] = None
        
        # This line now correctly includes 'creating_date' in the final DataFrame
        final_df = combined_df[FINAL_COLUMNS]
        
        final_df = final_df.sort_values(by='inv_ref')

        try:
            with sqlite3.connect(DATABASE_FILE) as conn:
                final_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
            
            successfully_added_refs.append(file_ref_no)
            existing_refs.add(file_ref_no)
            print(f"Successfully added Reference # '{file_ref_no}' to the database.")

        except Exception as e:
            print(f"--- ERROR: Failed to write Reference # '{file_ref_no}' to database. Error: {e} ---")

    print("\n\n--- Batch Complete ---")
    if successfully_added_refs:
        print(f"Successfully added {len(successfully_added_refs)} new invoice(s):")
        for ref_no in sorted(successfully_added_refs):
            print(f"  - {ref_no}")
    else:
        print("No new data was added to the database in this run.")

if __name__ == "__main__":
    if not os.path.exists(JSON_DIRECTORY):
        os.makedirs(JSON_DIRECTORY)
        print(f"Created directory '{JSON_DIRECTORY}'. Please place your JSON files inside and run again.")
    else:
        create_database_table_if_not_exists()
        process_batch_invoices()