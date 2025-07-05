import streamlit as st
import os
import shutil
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Backup & Restore", layout="wide")
st.title("Database Backup & Restore 🛡️")

# --- Configuration ---
# All data-related folders are now located inside the main 'data' directory.
DATA_ROOT = "data"
DATA_DIRECTORY = os.path.join(DATA_ROOT, 'Invoice Record')
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
BACKUP_DIRECTORY = 'backups'
RESTORE_CONFIRM_PHRASE = "overwrite my live data"
DELETE_CONFIRM_PHRASE = "delete this backup forever"

# --- Helper Functions (create_backup, get_existing_backups, etc.) ---
def create_backup():
    if not os.path.exists(DATABASE_FILE):
        st.error("Database file not found. Cannot perform backup.")
        return
    os.makedirs(BACKUP_DIRECTORY, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file_name = f"master_invoice_data_{timestamp}.db"
    backup_file_path = os.path.join(BACKUP_DIRECTORY, backup_file_name)
    try:
        shutil.copy2(DATABASE_FILE, backup_file_path)
        st.success(f"Successfully created backup: **{backup_file_name}**")
    except Exception as e:
        st.error(f"Failed to create backup. Error: {e}")

def get_existing_backups():
    if not os.path.exists(BACKUP_DIRECTORY): return []
    files = [f for f in os.listdir(BACKUP_DIRECTORY) if f.endswith('.db')]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIRECTORY, x)), reverse=True)
    return files

def restore_from_backup(backup_file_name):
    backup_file_path = os.path.join(BACKUP_DIRECTORY, backup_file_name)
    shutil.copy2(backup_file_path, DATABASE_FILE)

def delete_backup_file(backup_file_name):
    backup_file_path = os.path.join(BACKUP_DIRECTORY, backup_file_name)
    os.remove(backup_file_path)

# --- NEW: Callback functions to reset state after an action ---
def handle_restore_callback(backup_file):
    restore_from_backup(backup_file)
    # Reset the widgets for the restore action
    st.session_state.confirm_restore = False
    st.session_state.typed_restore = ""
    st.success(f"Successfully restored database from **{backup_file}**.")
    st.balloons()

def handle_delete_callback(backup_file):
    delete_backup_file(backup_file)
    # Reset the widgets for the delete action
    st.session_state.confirm_delete = False
    st.session_state.typed_delete = ""
    st.success(f"Successfully deleted backup file: **{backup_file}**")

# --- UI Layout ---

# Section 1: Create Backup
st.header("1. Create a New Backup")
st.info("Click the button to create a safe, timestamped copy of your database.")
if st.button("➕ Create Backup Now", use_container_width=True):
    with st.spinner("Creating backup..."):
        create_backup()

st.divider()

# Section 2: Manage Existing Backups
st.header("2. Manage Existing Backups")
existing_backups = get_existing_backups()

if not existing_backups:
    st.write("No backups available to manage.")
else:
    selected_backup = st.selectbox(
        "Select a backup file to manage:",
        options=existing_backups,
        key="selected_backup" # Add a key to the selectbox
    )

    if selected_backup:
        # --- Restore Sub-section ---
        with st.expander("Restore From This Backup"):
            st.warning(
                f"Restoring from **{selected_backup}** will overwrite your live data. "
                f"All changes made since this backup was created will be **permanently lost**."
            )
            st.checkbox("I understand I will lose current data.", key="confirm_restore")
            st.text_input("Confirm restore phrase:", key="typed_restore", placeholder=f"Type '{RESTORE_CONFIRM_PHRASE}'")
            
            # Button is disabled if confirmation phrase doesn't match OR checkbox is unticked
            is_restore_disabled = (st.session_state.typed_restore.strip() != RESTORE_CONFIRM_PHRASE or not st.session_state.confirm_restore)
            st.button("Restore From This Backup", on_click=handle_restore_callback, args=(selected_backup,), disabled=is_restore_disabled)
        
        # --- Delete Sub-section ---
        with st.expander("Delete This Backup"):
            st.error(f"**DANGER ZONE:** You are about to permanently delete the backup file **{selected_backup}**. This action cannot be undone.", icon="⚠️")
            
            st.checkbox("I understand this backup will be deleted forever.", key="confirm_delete")
            st.text_input("Confirm delete phrase:", key="typed_delete", placeholder=f"Type '{DELETE_CONFIRM_PHRASE}'")

            # Button is disabled if confirmation phrase doesn't match OR checkbox is unticked
            is_delete_disabled = (st.session_state.typed_delete.strip() != DELETE_CONFIRM_PHRASE or not st.session_state.confirm_delete)
            st.button("Permanently Delete This Backup", type="primary", on_click=handle_delete_callback, args=(selected_backup,), disabled=is_delete_disabled)