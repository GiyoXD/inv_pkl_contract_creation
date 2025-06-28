import sqlite3
import os
import questionary

# --- Configuration ---
DATA_DIRECTORY = 'Invoice Record'
DATABASE_FILE = os.path.join(DATA_DIRECTORY, 'master_invoice_data.db')
TABLE_NAME = 'invoices'
REF_COLUMN = 'inv_ref' # This ensures we always use the 'inv_ref' column

def get_matching_invoices(search_term):
    """
    Queries the database for invoice references (inv_ref) that contain the search term.
    Returns a list of matches.
    """
    if not search_term or not os.path.exists(DATABASE_FILE):
        return []

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            # This query correctly uses the REF_COLUMN ('inv_ref')
            sql_query = f"SELECT DISTINCT {REF_COLUMN} FROM {TABLE_NAME} WHERE {REF_COLUMN} LIKE ? ORDER BY {REF_COLUMN}"
            params = (f'%{search_term}%',)
            cursor.execute(sql_query, params)
            results = cursor.fetchall()
            return [row[0] for row in results]
    except sqlite3.Error as e:
        print(f"--- DATABASE ERROR during search: {e} ---")
        return []

def remove_invoice_by_ref(inv_ref_to_delete):
    """
    Removes all rows from the database that match the given inv_ref.
    """
    if not inv_ref_to_delete:
        print("--- ERROR: No inv_ref provided. ---")
        return

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            # This query correctly uses the REF_COLUMN ('inv_ref')
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE {REF_COLUMN} = ?", (inv_ref_to_delete,))
            count = cursor.fetchone()[0]

            if count == 0:
                print(f"--- INFO: No records found with inv_ref # '{inv_ref_to_delete}'. No action taken. ---")
                return

            confirm = questionary.confirm(
                f"Found {count} record(s) with inv_ref # '{inv_ref_to_delete}'. Are you sure you want to permanently delete them?",
                default=False
            ).ask()

            if not confirm:
                print("--- CANCELED: Deletion aborted by user. ---")
                return

            # This DELETE statement correctly uses the REF_COLUMN ('inv_ref')
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE {REF_COLUMN} = ?", (inv_ref_to_delete,))
            rows_deleted = cursor.rowcount
            conn.commit()
            print(f"\n--- SUCCESS: Successfully deleted {rows_deleted} record(s) with inv_ref # '{inv_ref_to_delete}'. ---")

    except sqlite3.Error as e:
        print(f"--- DATABASE ERROR: An error occurred. Error: {e} ---")
    except Exception as e:
        print(f"--- UNEXPECTED ERROR: {e} ---")


# --- MAIN EXECUTION (With updated, clearer text) ---
if __name__ == "__main__":
    if not os.path.exists(DATABASE_FILE):
        print(f"\n--- ERROR: Database file not found at '{DATABASE_FILE}'. ---")
    else:
        # STEP 1: Ask the user for a search term for the inv_ref.
        search_term = questionary.text("Enter a part of the inv_ref to search for (e.g., 'CLF' or '2024'):").ask()

        if not search_term:
            print("--- CANCELED: No search term entered. ---")
        else:
            # STEP 2: Find all inv_ref values that match the search term.
            print(f"\nSearching for any inv_ref containing '{search_term}'...")
            matches = get_matching_invoices(search_term)

            if not matches:
                print(f"--- INFO: No inv_ref found matching '{search_term}'. ---")
            else:
                # STEP 3: Present the matching inv_ref values in a list.
                matches.append("--- CANCEL ---")
                
                selected_inv_ref = questionary.select(
                    "Select the inv_ref you want to delete:",
                    choices=matches
                ).ask()

                # STEP 4: Process the user's selection.
                if selected_inv_ref and selected_inv_ref != "--- CANCEL ---":
                    remove_invoice_by_ref(selected_inv_ref)
                else:
                    print("--- CANCELED: Operation aborted by user. ---")

# --- THIS IS THE END OF THE SCRIPT ---