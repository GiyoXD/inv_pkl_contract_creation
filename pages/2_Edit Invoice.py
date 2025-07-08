import streamlit as st
import pandas as pd
import sqlite3
import os
from pathlib import Path

st.set_page_config(page_title="Edit Invoice", layout="wide")
st.title("Edit Invoice ✏️")

# --- Configuration ---
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

# --- Core Functions ---
def find_active_invoices(search_mode, search_term):
    """Finds distinct invoices that are active."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        query = f"SELECT DISTINCT inv_no, inv_ref FROM {TABLE_NAME} WHERE LOWER({search_mode}) LIKE LOWER(?) AND status = 'active' ORDER BY inv_no"
        return [{'inv_no': row[0], 'inv_ref': row[1]} for row in conn.cursor().execute(query, (f'%{search_term}%',)).fetchall()]

def get_invoice_line_items(inv_ref):
    """Gets the main line-item data for a specific invoice."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        # Select all columns except status, which is managed internally
        return pd.read_sql_query(f"SELECT id, inv_no, inv_date, inv_ref, po, item, description, pcs, sqft, pallet_count, unit, amount, net, gross, cbm, production_order_no, creating_date FROM {TABLE_NAME} WHERE inv_ref = ?", conn, params=(inv_ref,))

def get_invoice_containers(inv_ref):
    """Gets the list of containers for a specific invoice."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT container_description FROM {CONTAINER_TABLE_NAME} WHERE inv_ref = ?", (inv_ref,))
        # Return a list of strings
        return [row[0] for row in cursor.fetchall()]

def update_invoice_data(inv_ref, edited_df, container_list):
    """Updates both the invoice line items and the container list in the database."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Use a transaction to ensure all operations succeed or fail together
        cursor.execute("BEGIN TRANSACTION;")
        try:
            # 1. Delete old data from both tables
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE inv_ref = ?", (inv_ref,))
            cursor.execute(f"DELETE FROM {CONTAINER_TABLE_NAME} WHERE inv_ref = ?", (inv_ref,))

            # 2. Insert new line-item data
            # Add status back in for saving
            df_to_save = edited_df.copy()
            df_to_save['status'] = 'active'
            df_to_save.to_sql(TABLE_NAME, conn, if_exists='append', index=False)

            # 3. Insert new container data
            if container_list:
                container_data = [(inv_ref, desc) for desc in container_list]
                cursor.executemany(f"INSERT INTO {CONTAINER_TABLE_NAME} (inv_ref, container_description) VALUES (?, ?)", container_data)
            
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;")
            raise e # Re-raise the exception to be caught by the UI

# --- Undo/Redo State Management Callbacks ---
def undo(history_index_key):
    if st.session_state[history_index_key] > 0:
        st.session_state[history_index_key] -= 1

def redo(history_key, history_index_key):
    if st.session_state[history_index_key] < len(st.session_state[history_key]) - 1:
        st.session_state[history_index_key] += 1

# --- Streamlit UI ---
if not os.path.exists(DATABASE_FILE):
    st.error("Database file not found. Please add an invoice first.")
    st.stop()

st.header("1. Find Invoice to Edit")
search_mode_label = st.radio("Search By:", ("Invoice Number", "Invoice Reference"), index=0, horizontal=True, key="edit_search_mode")
search_column = "inv_no" if search_mode_label == "Invoice Number" else "inv_ref"
search_term = st.text_input(f"Enter part of the {search_mode_label}:", placeholder="e.g., INV-001 or REF-A", key="edit_search_term")

if search_term:
    matches = find_active_invoices(search_column, search_term)
    if not matches:
        st.warning(f"No active invoices found matching '{search_term}'."); st.stop()

    display_map = {f"Inv No: {m['inv_no']} (Ref: {m['inv_ref']})": m['inv_ref'] for m in matches}
    selected_display_option = st.selectbox("Select an invoice to edit:", options=list(display_map.keys()), key="edit_selection")

    if selected_display_option:
        selected_ref = display_map[selected_display_option]
        
        # Define unique session state keys for the current invoice's history
        history_key = f"history_{selected_ref}"
        history_index_key = f"history_index_{selected_ref}"

        # Initialize history if it doesn't exist for this invoice
        if history_key not in st.session_state:
            initial_df = get_invoice_line_items(selected_ref)
            initial_containers = get_invoice_containers(selected_ref)
            # History now stores a dictionary with both dataframes and containers
            st.session_state[history_key] = [{'df': initial_df, 'containers_text': "\n".join(initial_containers)}]
            st.session_state[history_index_key] = 0

        st.header(f"2. Editing Invoice: {selected_ref}")
        
        # The state (df and containers) to be displayed is the one at the current history index
        current_state = st.session_state[history_key][st.session_state[history_index_key]]
        df_to_display = current_state['df']
        containers_to_display = current_state['containers_text']

        # --- Editors for Invoice and Containers ---
        st.subheader("Invoice Line Items")
        edited_df = st.data_editor(
            df_to_display,
            num_rows="dynamic",
            key=f"editor_{selected_ref}",
            use_container_width=True,
            disabled=['id', 'inv_ref'] # Prevent editing of primary key and reference key
        )

        st.subheader("Containers / Trucks (One per line)")
        edited_containers_text = st.text_area(
            "Containers:",
            value=containers_to_display,
            key=f"containers_{selected_ref}",
            height=100
        )

        # Check if a change was made in either editor
        df_changed = not edited_df.equals(df_to_display)
        containers_changed = (edited_containers_text != containers_to_display)

        if df_changed or containers_changed:
            # Truncate the "future" history if we've undone changes and now make a new edit
            st.session_state[history_key] = st.session_state[history_key][:st.session_state[history_index_key] + 1]
            # Add the new, edited state to the history
            new_state = {'df': edited_df, 'containers_text': edited_containers_text}
            st.session_state[history_key].append(new_state)
            # Update the index to point to this new state
            st.session_state[history_index_key] = len(st.session_state[history_key]) - 1
            st.rerun()

        st.markdown("---")
        
        # --- Action Buttons ---
        col1, col2, col3, _ = st.columns([1, 1, 1, 5])

        with col1:
            is_undo_disabled = st.session_state[history_index_key] <= 0
            st.button("↩️ Undo", on_click=undo, args=(history_index_key,), disabled=is_undo_disabled, use_container_width=True)

        with col2:
            is_redo_disabled = st.session_state[history_index_key] >= len(st.session_state[history_key]) - 1
            st.button("↪️ Redo", on_click=redo, args=(history_key, history_index_key), disabled=is_redo_disabled, use_container_width=True)
        
        with col3:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                state_to_save = st.session_state[history_key][st.session_state[history_index_key]]
                df_to_save = state_to_save['df']
                containers_to_save = [line.strip() for line in state_to_save['containers_text'].split('\n') if line.strip()]
                
                # Final validation before saving
                if not (df_to_save['inv_ref'] == selected_ref).all():
                    st.error(f"Error: The 'inv_ref' column cannot be changed. It must remain '{selected_ref}'.")
                else:
                    try:
                        update_invoice_data(selected_ref, df_to_save, containers_to_save)
                        st.success(f"Invoice '{selected_ref}' has been updated successfully!")
                        
                        # Clean up session state for this invoice after saving
                        keys_to_delete = [history_key, history_index_key, f"editor_{selected_ref}", f"containers_{selected_ref}"]
                        for key in keys_to_delete:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.info("Editor will now refresh.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save changes. Error: {e}")
