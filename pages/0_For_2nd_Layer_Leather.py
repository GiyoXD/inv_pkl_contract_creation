import streamlit as st
import sys
from pathlib import Path
import subprocess
import json
import datetime
import sqlite3
import re
import os
import zipfile
import io
import tempfile

# --- Database Initialization Function ---
def initialize_database(db_file: Path):
    """
    Initializes the database by creating tables if they don't already exist.
    This function is designed to be run every time the script starts to ensure
    the database is always ready before any operations are attempted.
    """
    try:
        # The 'with' statement ensures the connection is properly closed.
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            # Use 'IF NOT EXISTS' to prevent errors on subsequent runs.
            # This makes the operation idempotent and safe.
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT, inv_no TEXT, inv_date TEXT,
                inv_ref TEXT UNIQUE, po TEXT, item TEXT, description TEXT, pcs TEXT,
                sqft TEXT, pallet_count TEXT, unit TEXT, amount TEXT, net TEXT,
                gross TEXT, cbm TEXT, production_order_no TEXT, creating_date TEXT,
                status TEXT DEFAULT 'active'
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_containers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_ref TEXT NOT NULL,
                container_description TEXT NOT NULL,
                FOREIGN KEY (inv_ref) REFERENCES invoices (inv_ref)
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inv_ref ON invoice_containers (inv_ref);")
            conn.commit()
        return True
    except sqlite3.Error as e:
        # If any SQLite error occurs during initialization, display it.
        st.error(f"Database Initialization Failed: {e}")
        return False

# --- Path and Constant Setup ---
# Resolve paths relative to the script's location.
APP_DIR = Path(__file__).resolve().parent
# Assuming a standard Streamlit layout where this script is in a 'pages' folder,
# the project root is the parent directory of the script's directory.
PROJECT_ROOT = APP_DIR.parent
DATABASE_FILE = PROJECT_ROOT / "data" / "Invoice Record" / 'master_invoice_data.db'

# --- Early Database Setup ---
# Create the directory for the database file if it doesn't exist.
DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
# Initialize the database immediately. The result is stored in a global-like
# constant to indicate if the DB is usable throughout this script run.
DB_ENABLED = initialize_database(DATABASE_FILE)


# --- Streamlit App UI ---
st.set_page_config(page_title="Generate Invoice", layout="wide")
st.title("Automated Invoice Generator")

# --- Session State Initialization ---
# Use session_state to store values that need to persist across reruns.
if 'paths_initialized' not in st.session_state:
    st.session_state.paths_initialized = True
    st.session_state.db_enabled = DB_ENABLED
    st.session_state.update({
        "PROJECT_ROOT": PROJECT_ROOT, "CREATE_JSON_DIR": PROJECT_ROOT / "create_json",
        "INVOICE_GEN_DIR": PROJECT_ROOT / "invoice_gen", "DATA_DIR": PROJECT_ROOT / "data",
        "JSON_OUTPUT_DIR": PROJECT_ROOT / "data" / "invoices_to_process",
        "TEMP_UPLOAD_DIR": PROJECT_ROOT / "data" / "temp_uploads", "RESULT_DIR": PROJECT_ROOT / "result",
        "TEMPLATE_DIR": PROJECT_ROOT / "invoice_gen" / "TEMPLATE", "CONFIG_DIR": PROJECT_ROOT / "invoice_gen" / "config",
        "DATABASE_FILE": DATABASE_FILE, "TABLE_NAME": 'invoices'
    })

# --- Helper Functions ---
def check_value_exists(column_name: str, value: str) -> bool:
    """Checks if a specific value exists in a given column."""
    if not st.session_state.get('db_enabled'): return False
    try:
        with sqlite3.connect(st.session_state.DATABASE_FILE) as conn:
            query = f"SELECT 1 FROM {st.session_state.TABLE_NAME} WHERE LOWER({column_name}) = LOWER(?) LIMIT 1"
            return conn.cursor().execute(query, (value,)).fetchone() is not None
    except Exception as e:
        st.warning(f"DB error checking existence: {e}"); return False

def get_suggested_inv_ref() -> str:
    """Generates a suggested invoice reference number based on existing entries."""
    default = f"INV{datetime.datetime.now().strftime('%Y')}-1"
    if not st.session_state.get('db_enabled'): return default
    try:
        with sqlite3.connect(st.session_state.DATABASE_FILE) as conn:
            refs = [r[0] for r in conn.execute(f"SELECT inv_ref FROM {st.session_state.TABLE_NAME} WHERE inv_ref IS NOT NULL")]
        if not refs: return default
        pattern = re.compile(r"([a-zA-Z]+)(\d{4})-(\d+)")
        max_num, prefix = -1, 'INV'
        current_year = datetime.datetime.now().strftime('%Y')
        for ref in refs:
            if m := pattern.match(str(ref)):
                year, num_str = m.group(2), m.group(3)
                if year == current_year:
                    num = int(num_str)
                    if num > max_num:
                        max_num = num
                        prefix = m.group(1)
        return f"{prefix}{current_year}-{max_num + 1}"
    except Exception as e:
        st.warning(f"DB error suggesting Ref: {e}"); return default

def update_and_aggregate_json(json_path: Path, inv_ref: str, inv_date: datetime.date, unit_price: float, po_number: str) -> dict | None:
    """
    Updates the JSON data with invoice details, aggregates summary information,
    and returns the summary as a dictionary.
    """
    try:
        with open(json_path, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            raw_data = data.get("raw_data", {})
            summary = data.get("aggregated_summary", {})
            
            # Extract and calculate values
            net_value = float(summary.get("net", 0))
            total_pcs = sum(sum(t.get("pcs", [])) for t in raw_data.values())
            total_pallets = sum(len(t.get("pallet_count", [])) for t in raw_data.values())
            total_amount = unit_price * net_value
            date_str = inv_date.strftime("%d/%m/%Y")

            # Get representative item and description
            first_item, first_desc = "N/A", "N/A"
            for table_data in raw_data.values():
                if table_data.get("item") and table_data["item"][0]:
                    first_item = table_data["item"][0]
                if table_data.get("description") and table_data["description"][0]:
                    first_desc = table_data["description"][0]
                if first_item != "N/A" and first_desc != "N/A":
                    break
            
            # Update raw data tables with invoice info
            for table in raw_data.values():
                entries = len(table.get("po", []))
                table.update({
                    "inv_no": [po_number] * entries, "inv_ref": [inv_ref] * entries,
                    "inv_date": [date_str] * entries, "unit": [unit_price] * entries
                })

            # Update aggregated summary
            summary.update({
                "inv_no": po_number, "inv_ref": inv_ref, "inv_date": date_str, "unit": unit_price,
                "amount": total_amount, "pcs": total_pcs, "pallet_count": total_pallets, "net": net_value
            })
            data["aggregated_summary"] = summary
            
            # Write changes back to JSON
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

            # Prepare dictionary to return for UI display
            summary_for_ui = {
                "po_number": po_number,
                "amount": total_amount,
                "pcs": total_pcs,
                "pallet_count": total_pallets,
                "net": net_value,
                "gross": summary.get("gross", 0.0),
                "cbm": summary.get("cbm", 0.0),
                "item": first_item,
                "description": first_desc
            }
            return summary_for_ui

    except Exception as e:
        st.error(f"Failed to update JSON. Details: {e}")
        return None

def get_po_from_json(json_path: Path) -> str | None:
    """Extracts the Purchase Order number from the JSON file."""
    try:
        with open(json_path, 'r') as f: return str(json.load(f).get("aggregated_summary", {}).get("po", "")).strip() or None
    except Exception: return None

# --- Main UI and Processing Logic ---
st.header("1. Upload Source Excel File")
uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

if uploaded_file:
    st.markdown("---")
    st.header("2. Enter Invoice Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        suggested_ref = get_suggested_inv_ref()
        inv_ref = st.text_input("Invoice Reference", value=suggested_ref)
        if inv_ref and inv_ref != suggested_ref and check_value_exists('inv_ref', inv_ref): st.warning("Ref already exists in the database.")
    with col2: inv_date = st.date_input("Invoice Date", datetime.date.today())
    with col3: unit_price = st.number_input("Unit Price", min_value=0.0, value=0.61, step=0.01)

    st.markdown("---")
    if st.button(f"Process '{uploaded_file.name}'", use_container_width=True, type="primary"):
        if not st.session_state.get('db_enabled'):
            st.error("Database is not connected. Cannot proceed.")
            st.stop()
        
        temp_file_path = st.session_state.TEMP_UPLOAD_DIR / uploaded_file.name
        try:
            st.session_state.TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            with open(temp_file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        except Exception as e:
            st.error(f"Could not save uploaded file: {e}"); st.stop()

        po_number = None
        summary_data = None
        final_json_path = None

        # --- Step 1: Create JSON file ---
        with st.spinner("Step 1 of 2: Creating data file from Excel..."):
            try:
                buffer_file = st.session_state.JSON_OUTPUT_DIR / "__buffer.json"
                run_dir = st.session_state.CREATE_JSON_DIR
                
                if not run_dir.is_dir():
                    st.error(f"Processing directory not found. Expected at: {run_dir}")
                    st.error("Please check your project's directory structure. The 'create_json' folder should be in the main project directory.")
                    st.stop()

                subprocess.run([sys.executable, str(run_dir / "Second_Layer(main).py"), str(temp_file_path), "-o", str(buffer_file)], check=True, capture_output=True, text=True, cwd=str(run_dir), encoding='utf-8')
                
                po_number_from_json = get_po_from_json(buffer_file)
                fallback_po_number = Path(uploaded_file.name).stem
                po_number = po_number_from_json or fallback_po_number
                
                summary_data = update_and_aggregate_json(buffer_file, inv_ref, inv_date, unit_price, po_number)
                if not summary_data:
                    st.stop()
                
                final_json_path = st.session_state.JSON_OUTPUT_DIR / f"{po_number}.json"
                buffer_file.replace(final_json_path)
                st.success(f"Step 1 complete: Data file created as '{final_json_path.name}'.")
            except subprocess.CalledProcessError as e:
                st.error("Step 1 FAILED."); st.text_area("Full Error Log:", e.stdout + e.stderr, height=200); st.stop()
            finally:
                if 'buffer_file' in locals() and buffer_file.exists(): buffer_file.unlink()

        # --- Step 2: Generate documents into a temporary directory ---
        # A temporary directory is created to hold the output files.
        # It will be automatically deleted at the end of this process.
        temp_output_dir_obj = tempfile.TemporaryDirectory()
        temp_output_dir = Path(temp_output_dir_obj.name)

        try:
            with st.spinner("Step 2 of 2: Generating documents..."):
                try:
                    run_dir = st.session_state.INVOICE_GEN_DIR
                    new_backend_script_name = "hybrid_generate_invoice.py"
                    # The subprocess now writes the output to the temporary directory
                    result = subprocess.run([
                        sys.executable, str(run_dir / new_backend_script_name), str(final_json_path),
                        "--outputdir", str(temp_output_dir), "--templatedir", str(st.session_state.TEMPLATE_DIR),
                        "--configdir", str(st.session_state.CONFIG_DIR)
                    ], check=True, capture_output=True, text=True, cwd=str(run_dir), encoding='utf-8')
                    st.success("Step 2 complete: Documents generated temporarily.")
                except subprocess.CalledProcessError as e:
                    st.error("Step 2 FAILED."); st.text_area("Full Error Log:", e.stdout + e.stderr, height=300); st.stop()

            # --- Display Summary and Prepare In-Memory ZIP for Download ---
            if po_number and summary_data:
                st.markdown("---")
                st.header("Invoice Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("PO Number", summary_data.get("po_number", "N/A"))
                col2.metric("Total Amount", f"${summary_data.get('amount', 0):,.2f}")
                col3.metric("Net Weight (KG)", f"{summary_data.get('net', 0):,.2f}")
                col4.metric("Gross Weight", f"{summary_data.get('gross', 0):,.2f}")

                col5, col6, col7 = st.columns(3)
                col5.metric("Total Pcs", f"{summary_data.get('pcs', 0):,}")
                col6.metric("Total Pallets", summary_data.get('pallet_count', 0))
                col7.metric("Total CBM", f"{summary_data.get('cbm', 0):,.3f}")

                st.text(f"Item: {summary_data.get('item', 'N/A')}")
                st.text(f"Description: {summary_data.get('description', 'N/A')}")

                st.markdown("---")
                st.header("3. Download Generated Documents")

                generated_files = sorted(list(temp_output_dir.glob(f"* {po_number}.xlsx")))
                
                if not generated_files and (not final_json_path or not final_json_path.exists()):
                    st.error("Processing succeeded, but no output files were found to package.")
                    st.stop()

                st.info(f"Found {len(generated_files)} documents and 1 data file for PO **{po_number}** to be packaged.")
                
                # --- Create ZIP in memory, not on disk ---
                zip_filename = f"{po_number}.zip"
                zip_buffer = io.BytesIO()  # Create an in-memory binary buffer

                with st.spinner("Creating ZIP archive in memory..."):
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        # Add the generated Excel documents to the zip
                        for file_path in generated_files:
                            # Write the file from the temp directory into the in-memory zip
                            zipf.write(file_path, arcname=file_path.name)
                        
                        # --- MODIFICATION START ---
                        # Add the data.json file to the zip
                        if final_json_path and final_json_path.exists():
                            zipf.write(final_json_path, arcname=final_json_path.name)
                        # --- MODIFICATION END ---
                
                # Prepare the in-memory buffer for reading
                zip_buffer.seek(0)
                
                st.download_button(
                    label=f"Download All Documents and Data (.zip)",
                    data=zip_buffer,  # Use the in-memory buffer as the data source
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )

        finally:
            # --- Final Cleanup Logic ---
            # This block runs regardless of success or failure, ensuring cleanup.
            st.markdown("---")
            with st.expander("Cleanup Information"):
                st.write("Temporary files are being removed from the server.")
                try:
                    # Clean up the original uploaded file
                    if temp_file_path and temp_file_path.exists():
                        temp_file_path.unlink()
                        st.write(f"- Removed temporary upload: `{temp_file_path.name}`")
                    
                    # Clean up the temporary directory containing the generated Excel files
                    temp_output_dir_obj.cleanup()
                    st.write(f"- Removed temporary document output directory.")
                    
                    # NOTE: The final_json_path is intentionally NOT deleted here
                    # because it is part of the persistent data flow.
                    # It resides in `data/invoices_to_process` and should be managed separately.
                    
                    st.success("Cleanup complete!")
                except Exception as e:
                    st.warning(f"An error occurred during file cleanup: {e}")