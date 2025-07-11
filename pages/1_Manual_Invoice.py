import streamlit as st
import sqlite3
import os
from pathlib import Path
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Manual Invoice Entry", layout="wide")
st.title("📝 Manual Invoice Entry")
st.info("Use this page to add a simple, single-line invoice directly to the database.")

# --- Configuration ---
try:
    # This assumes the script is in a 'pages' subdirectory.
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIRECTORY = PROJECT_ROOT / "data" / "Invoice Record"
    DATABASE_FILE = DATA_DIRECTORY / "master_invoice_data.db"
    TABLE_NAME = 'invoices'
except Exception:
    # Fallback for local running if not in a 'pages' folder
    PROJECT_ROOT = Path(__file__).resolve().parent
    DATA_DIRECTORY = PROJECT_ROOT / "data" / "Invoice Record"
    DATABASE_FILE = DATA_DIRECTORY / "master_invoice_data.db"
    TABLE_NAME = 'invoices'

# --- Check for Database ---
if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'.")
    st.info("Please ensure the database is initialized before adding entries.")
    st.stop()

# --- Helper Functions ---
def check_if_exists(inv_ref, inv_no):
    """
    Checks if an invoice with the given ref or no already exists to prevent duplicates.
    Returns True if it exists, False otherwise.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER(inv_ref) = LOWER(?) OR LOWER(inv_no) = LOWER(?)"
        cursor.execute(query, (inv_ref, inv_no))
        return cursor.fetchone() is not None

def insert_manual_invoice(data_dict):
    """Inserts a new record into the invoices table."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Constructing the query dynamically based on the dictionary keys
        columns = ', '.join(data_dict.keys())
        placeholders = ', '.join(['?'] * len(data_dict))
        query = f"INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, list(data_dict.values()))
        conn.commit()

# --- Form for Manual Entry ---
with st.form("manual_invoice_form", clear_on_submit=True):
    st.header("Invoice Details")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        inv_no = st.text_input("Invoice No*", help="The main invoice number.")
        inv_ref = st.text_input("Invoice Ref*", help="The internal or customer reference number.")
        inv_date = st.date_input("Invoice Date*")

    with col2:
        po = st.text_input("PO Number*", help="The Purchase Order number for this entry.")
        description = st.text_input("Description", value="Wet Blue Split", help="Optional description of the item.")
        item = st.text_input("Item Code", value="MANUAL-ENTRY", help="An item code for this manual entry.")

    with col3:
        net = st.number_input("Net (e.g., Kgs)*", min_value=0.0, format="%.2f")
        gross = st.number_input("Gross (e.g., Kgs)*", min_value=0.0, format="%.2f")
        unit_price = st.number_input("Unit Price*", min_value=0.0, format="%.4f", help="Price per unit of Net.")
        cbm = st.number_input("CBM*", min_value=0.0, format="%.4f", help="Cubic Meters.")

    # --- Automatic Calculation ---
    st.markdown("---")
    st.header("Calculated Amount")
    calculated_amount = net * unit_price
    st.metric(label="Total Amount", value=f"${calculated_amount:,.2f}")
    st.markdown("*(This is calculated automatically from `Net` x `Unit Price`)*")
    st.markdown("---")

    submitted = st.form_submit_button("💾 Save Manual Invoice", use_container_width=True)

    if submitted:
        # --- Validation ---
        required_fields = [inv_no, inv_ref, po]
        if not all(required_fields):
            st.error("Please fill in all required fields marked with an asterisk (*).")
        elif net <= 0 or gross <= 0 or unit_price <= 0 or cbm <= 0:
            st.error("Net, Gross, Unit Price, and CBM must be greater than zero.")
        elif check_if_exists(inv_ref.strip(), inv_no.strip()):
            st.error(f"An invoice with Ref '{inv_ref}' or No '{inv_no}' already exists. Please use a unique number.")
        else:
            # --- Prepare data for insertion ---
            invoice_data = {
                'inv_no': inv_no.strip(),
                'inv_date': inv_date.strftime("%d/%m/%Y"),
                'inv_ref': inv_ref.strip(),
                'po': po.strip(),
                'item': item.strip(),
                'description': description.strip(),
                'pcs': 1,  # Default for manual entry
                'sqft': 0, # Default for manual entry
                'pallet_count': 0, # Default for manual entry
                'unit': unit_price, # Storing unit_price in the 'unit' column
                'amount': calculated_amount,
                'net': net,
                'gross': gross,
                'cbm': cbm,
                'production_order_no': po.strip(), # Using PO for this field as well
                'creating_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'active'
            }
            
            try:
                insert_manual_invoice(invoice_data)
                st.success(f"Successfully added manual invoice '{inv_no}' to the database!")
                st.balloons()
            except Exception as e:
                st.error(f"An error occurred while saving to the database: {e}")
