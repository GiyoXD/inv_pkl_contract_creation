import streamlit as st
import sqlite3
import os
import pandas as pd

st.set_page_config(page_title="Manage Invoice", layout="wide")
st.title("Manage Invoice State 📝")

# --- Configuration and Database Setup ---
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'

if not os.path.exists(DATABASE_FILE):
    st.error(f"Database file not found at '{DATABASE_FILE}'. Please create it first.")
    st.stop()

# --- Database Action Functions ---

def find_invoices(search_mode, search_term):
    """Finds invoices regardless of status."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        query = f"SELECT DISTINCT inv_no, inv_ref, status FROM {TABLE_NAME} WHERE {search_mode} LIKE ? ORDER BY inv_no"
        cursor = conn.cursor()
        cursor.execute(query, (f'%{search_term}%',))
        # Return status along with other info
        return [{'inv_no': row[0], 'inv_ref': row[1], 'status': row[2]} for row in cursor.fetchall()]

def get_invoice_details(inv_ref):
    """Retrieves all details for a given invoice reference."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        return pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} WHERE inv_ref = ?", conn, params=(inv_ref,))

def void_invoice_action(inv_ref_to_void):
    """Updates an invoice's status to 'voided' (soft delete)."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.cursor().execute(f"UPDATE {TABLE_NAME} SET status = 'voided' WHERE inv_ref = ?", (inv_ref_to_void,))
        conn.commit()

def permanently_delete_invoice_action(inv_ref_to_delete):
    """Permanently deletes an invoice from the database (hard delete)."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        conn.cursor().execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (inv_ref_to_delete,))
        conn.commit()

# --- Main Application UI ---

st.header("1. Find Invoice to Manage")
search_mode_label = st.radio("Search By:", ("Invoice Reference", "Invoice Number"), index=1, horizontal=True)
search_column = "inv_ref" if search_mode_label == "Invoice Reference" else "inv_no"
search_term = st.text_input(f"Enter part of the {search_mode_label}:")

if search_term:
    matches = find_invoices(search_column, search_term)
    if not matches:
        st.warning(f"No invoices found matching '{search_term}'.")
        st.stop()

    # Create a display mapping that shows the status
    display_map = {f"Inv No: {m['inv_no']} (Ref: {m['inv_ref']}) - Status: {m['status'].upper()}": m['inv_ref'] for m in matches}
    selected_display_option = st.selectbox("Select an invoice to manage:", options=list(display_map.keys()))

    if selected_display_option:
        selected_ref = display_map[selected_display_option]
        
        st.header("2. Review Invoice and Confirm Action")
        invoice_df = get_invoice_details(selected_ref)
        
        if invoice_df.empty:
            st.error("Could not retrieve invoice details.")
            st.stop()

        # Get the current status from the dataframe
        current_status = invoice_df['status'].iloc[0]
        st.dataframe(invoice_df)

        # --- State-Dependent Action Block ---
        if current_status == 'active':
            st.subheader("Action: Void Invoice")
            st.info("This invoice is ACTIVE. The only available action is to void it. This is a safe, reversible action.")
            
            if st.button(f"Confirm and VOID Invoice: {selected_ref}"):
                void_invoice_action(selected_ref)
                st.success(f"Successfully voided invoice '{selected_ref}'. To delete it, please select it again.")
                st.rerun()

        elif current_status == 'voided':
            st.subheader("Action: Permanently Delete Invoice")
            st.error(f"""
                **DANGER ZONE:** This invoice is already VOIDED. The next step is permanent deletion.
                - This action **CANNOT** be undone.
                - All data for invoice **{selected_ref}** will be lost forever.
            """)
            
            confirm_delete = st.checkbox("I understand the risk and want to permanently delete this invoice.")

            if confirm_delete:
                if st.button(f"PERMANENTLY DELETE INVOICE: {selected_ref}", type="primary"):
                    permanently_delete_invoice_action(selected_ref)
                    st.success(f"Successfully and permanently deleted invoice '{selected_ref}'.")
                    st.rerun()
        else:
            st.warning(f"This invoice has an unrecognised status ('{current_status}') and cannot be managed.")