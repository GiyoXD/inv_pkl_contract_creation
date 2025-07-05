import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Edit Invoice", layout="wide")
st.title("Edit Invoice ✏️")

# All data-related folders are now located inside the main 'data' directory.
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'

if not os.path.exists(DATABASE_FILE): st.error(f"Database file not found at '{DATABASE_FILE}'."); st.stop()

def find_active_invoices(search_mode, search_term):
    with sqlite3.connect(DATABASE_FILE) as conn:
        query = f"SELECT DISTINCT inv_no, inv_ref FROM {TABLE_NAME} WHERE {search_mode} LIKE ? AND status = 'active' ORDER BY inv_no"
        return [{'inv_no': row[0], 'inv_ref': row[1]} for row in conn.cursor().execute(query, (f'%{search_term}%',)).fetchall()]

def get_invoice_df(inv_ref):
    with sqlite3.connect(DATABASE_FILE) as conn:
        return pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} WHERE inv_ref = ?", conn, params=(inv_ref,))

def update_invoice(inv_ref, edited_df):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Delete old records for this invoice reference
        cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (inv_ref,))
        # Append the new, edited records
        edited_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        conn.commit()

st.header("1. Find Invoice to Edit")
search_mode_label = st.radio("Search By:", ("Invoice Reference", "Invoice Number"), index=1, horizontal=True)
search_column = "inv_ref" if search_mode_label == "Invoice Reference" else "inv_no"
search_term = st.text_input(f"Enter part of the {search_mode_label}:")

if search_term:
    matches = find_active_invoices(search_column, search_term)
    if not matches: st.warning(f"No active invoices found matching '{search_term}'."); st.stop()
    
    display_map = {f"Inv No: {m['inv_no']} (Ref: {m['inv_ref']})": m['inv_ref'] for m in matches}
    selected_display_option = st.selectbox("Select an invoice to edit:", options=list(display_map.keys()))

    if selected_display_option:
        selected_ref = display_map[selected_display_option]
        
        st.header(f"2. Editing Invoice: {selected_ref}")
        invoice_df = get_invoice_df(selected_ref)
        
        # Use st.data_editor to allow for table-like editing
        # We drop status because it should not be user-editable here.
        edited_df = st.data_editor(
            invoice_df.drop(columns=['status']),
            num_rows="dynamic", # Allow adding/deleting rows
            key=f"editor_{selected_ref}"
        )
        
        if st.button("💾 Save Changes"):
            # Re-add the 'status' column before saving
            edited_df['status'] = 'active'
            
            # Basic validation
            if 'inv_ref' not in edited_df or not (edited_df['inv_ref'] == selected_ref).all():
                st.error(f"Error: The 'inv_ref' column must not be changed from '{selected_ref}'.")
            else:
                try:
                    update_invoice(selected_ref, edited_df)
                    st.success(f"Invoice '{selected_ref}' has been updated successfully!")
                    st.info("The editor will now refresh.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save changes. Error: {e}")