import streamlit as st
import os
from pathlib import Path
import sqlite3

# --- Page Configuration ---
st.set_page_config(page_title="DANGER ZONE", layout="centered")
st.title("🔥 DANGER ZONE: Database Reset 🔥")
st.warning(
    "**WARNING:** This page will permanently delete all invoice and container data from the database. "
    "This action is irreversible and requires a special password."
)

# --- Configuration (Copied from other scripts for consistency) ---
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


# --- Database Initialization Logic (Copied from initialize_database.py) ---
def initialize_empty_database():
    """
    Creates brand new, empty 'invoices' and 'invoice_containers' tables.
    """
    try:
        # Ensure the directory exists
        DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            
            # Drop tables if they exist to ensure a clean slate
            cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            cursor.execute(f"DROP TABLE IF EXISTS {CONTAINER_TABLE_NAME}")

            invoices_table_query = """
            CREATE TABLE invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT, inv_no TEXT, inv_date TEXT,
                inv_ref TEXT, po TEXT, item TEXT, description TEXT, pcs TEXT,
                sqft TEXT, pallet_count TEXT, unit TEXT, amount TEXT, net TEXT,
                gross TEXT, cbm TEXT, production_order_no TEXT, creating_date TEXT,
                status TEXT DEFAULT 'active'
            );
            """
            cursor.execute(invoices_table_query)

            containers_table_query = """
            CREATE TABLE invoice_containers (
                id INTEGER PRIMARY KEY AUTOINCREMENT, inv_ref TEXT NOT NULL,
                container_description TEXT NOT NULL,
                FOREIGN KEY (inv_ref) REFERENCES invoices (inv_ref)
            );
            """
            cursor.execute(containers_table_query)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_ref ON invoice_containers (inv_ref);")
        return True, "Database re-initialized successfully."
    except Exception as e:
        return False, f"An error occurred during database initialization: {e}"


# --- Verification Step ---
st.markdown("---")
st.header("Authorization Required")
st.write("To prevent accidental deletion, please enter the special database reset password.")

# This password should be different from your main login password for added security.
NUKE_PASSWORD = "nuke_it_all_2025" 

password_input = st.text_input("Enter Reset Password:", type="password", key="nuke_password")

# The button is disabled until the correct password is entered.
password_is_correct = (password_input == NUKE_PASSWORD)


# --- Final Button ---
st.markdown("---")
st.header("Final Confirmation")

if st.button("🔥 NUKE DATABASE AND START OVER 🔥", type="primary", disabled=not password_is_correct, use_container_width=True):
    st.warning("Final warning... Processing request...")
    
    try:
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
            st.success("Successfully deleted the old database file.")
        else:
            st.info("No old database file to delete. Proceeding to create a new one.")
        
        # Re-create the empty database
        success, message = initialize_empty_database()
        
        if success:
            st.success("✅✅✅ DATABASE RESET COMPLETE! ✅✅✅")
            st.balloons()
        else:
            st.error(f"Failed to re-initialize the database. Error: {message}")

    except Exception as e:
        st.error(f"An critical error occurred during the deletion process: {e}")
        st.error("The database may be in an unstable state. Please check the files manually.")

elif not password_is_correct:
    st.info("The final button is disabled until the correct reset password is provided above.")
