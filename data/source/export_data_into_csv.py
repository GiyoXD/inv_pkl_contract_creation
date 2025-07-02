import sqlite3
import pandas as pd
import os

# --- Configuration ---
# Define a dedicated directory for data files
DATA_DIRECTORY = 'Invoice Record'
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
OUTPUT_CSV_FILE = os.path.join(DATA_DIRECTORY, 'database_export_sorted_by_ref.csv')
TABLE_NAME = 'invoices'

# Corrected list with standard space indentation
COLUMNS_TO_EXPORT = [
    'inv_no', 'inv_date', 'inv_ref',
    'po', 'item', 'description', 'pcs', 'sqft', 'pallet_count',
    'unit', 'amount', 'net', 'gross', 'cbm', 'production_order_no', 'creating_date'
]

def export_data_from_db():
    """Connects to the database and exports the data to CSV, sorted by reference number."""
    # Check if the database file exists before trying to connect
    if not os.path.exists(DATABASE_FILE):
        print(f"--- ERROR: Database file not found at '{DATABASE_FILE}'. ---")
        print("Please run the script to create the database first.")
        return

    print(f"Connecting to database: {DATABASE_FILE}")
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            select_columns_str = ", ".join([f'"{col}"' for col in COLUMNS_TO_EXPORT])
            query = f"SELECT {select_columns_str} FROM {TABLE_NAME} ORDER BY inv_ref"
            
            print("Reading and sorting data from the database by reference number...")
            df = pd.read_sql_query(query, conn)
        
        print(f"Successfully read {len(df)} rows.")

        if not df.empty:
            # Ensure the data directory exists before saving the CSV
            os.makedirs(DATA_DIRECTORY, exist_ok=True)
            print(f"Exporting sorted data to CSV file: {OUTPUT_CSV_FILE}")
            df.to_csv(OUTPUT_CSV_FILE, index=False)
            print("CSV export complete.")
        else:
            print("Database table is empty. Nothing to export.")

    except Exception as e:
        print(f"--- ERROR: Could not export data. Error: {e} ---")

if __name__ == "__main__":
    export_data_from_db()