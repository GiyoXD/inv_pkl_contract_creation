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
st.title("Automated Invoice Generator ⚙️")

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

def update_and_aggregate_json(json_path: Path, inv_ref: str, inv_date: datetime.date, unit_price: float, po_number: str):
    """Updates the JSON data with invoice details and aggregates summary information."""
    try:
        with open(json_path, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            raw_data = data.get("raw_data", {})
            net_value = float(data.get("aggregated_summary", {}).get("net", 0))
            total_pcs = sum(sum(t.get("pcs", [])) for t in raw_data.values())
            total_pallets = sum(len(t.get("pallet_count", [])) for t in raw_data.values())
            total_amount = unit_price * net_value
            st.info(f"✅ Calculated Totals: Amount={total_amount:,.2f}, Pcs={total_pcs}, Pallets={total_pallets}")
            date_str = inv_date.strftime("%d/%m/%Y")
            for table in raw_data.values():
                entries = len(table.get("po", []))
                table.update({"inv_no": [po_number] * entries, "inv_ref": [inv_ref] * entries, "inv_date": [date_str] * entries, "unit": [unit_price] * entries})
            data.setdefault("aggregated_summary", {}).update({"inv_no": po_number, "inv_ref": inv_ref, "inv_date": date_str, "unit": unit_price, "amount": total_amount, "pcs": total_pcs, "pallet_count": total_pallets, "net": net_value})
            f.seek(0); json.dump(data, f, indent=4); f.truncate()
        return True
    except Exception as e:
        st.error(f"Failed to update JSON. Details: {e}"); return False

def get_po_from_json(json_path: Path) -> str | None:
    """Extracts the Purchase Order number from the JSON file."""
    try:
        with open(json_path, 'r') as f: return str(json.load(f).get("aggregated_summary", {}).get("po", "")).strip() or None
    except Exception: return None

# --- Main UI and Processing Logic ---
st.header("1. Upload Source Excel File")
uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

if uploaded_file:
    st.markdown("---"); st.header("2. Enter Invoice Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        suggested_ref = get_suggested_inv_ref()
        inv_ref = st.text_input("Invoice Reference", value=suggested_ref)
        # The check for existing inv_ref is kept as a non-blocking warning.
        if inv_ref and inv_ref != suggested_ref and check_value_exists('inv_ref', inv_ref): st.warning("⚠️ Ref already exists in the database.")
    with col2: inv_date = st.date_input("Invoice Date", datetime.date.today())
    with col3: unit_price = st.number_input("Unit Price", min_value=0.0, value=1.0, step=0.01)

    st.markdown("---")
    if st.button(f"Process '{uploaded_file.name}'", use_container_width=True, type="primary"):
        if not st.session_state.get('db_enabled'):
            st.error("Database is not connected. Cannot proceed.")
            st.stop()
        
        # This blocking check is removed to allow processing without saving to DB.
        # if check_value_exists('inv_ref', inv_ref):
        #     st.error(f"Invoice Reference '{inv_ref}' already exists. Please use a unique reference.")
        #     st.stop()

        temp_file_path = st.session_state.TEMP_UPLOAD_DIR / uploaded_file.name
        try:
            with open(temp_file_path, "wb") as f: f.write(uploaded_file.getbuffer())
        except Exception as e:
            st.error(f"Could not save uploaded file: {e}"); st.stop()

        with st.expander("Processing Log", expanded=True):
            final_json_path, po_number = None, None

            # --- Step 1: Create JSON file ---
            with st.spinner("Step 1 of 3: Creating data file..."):
                try:
                    buffer_file = st.session_state.JSON_OUTPUT_DIR / "__buffer.json"
                    run_dir = st.session_state.CREATE_JSON_DIR
                    
                    # Add a check to ensure the target directory for the subprocess exists
                    if not run_dir.is_dir():
                        st.error(f"Processing directory not found. Expected at: {run_dir}")
                        st.error("Please check your project's directory structure. The 'create_json' folder should be in the main project directory.")
                        st.stop()

                    subprocess.run([sys.executable, str(run_dir / "Second_Layer(main).py"), str(temp_file_path), "-o", str(buffer_file)], check=True, capture_output=True, text=True, cwd=str(run_dir))
                    
                    po_number_from_json = get_po_from_json(buffer_file)
                    fallback_po_number = Path(uploaded_file.name).stem
                    po_number = po_number_from_json or fallback_po_number
                    
                    if not update_and_aggregate_json(buffer_file, inv_ref, inv_date, unit_price, po_number): st.stop()
                    
                    final_json_path = st.session_state.JSON_OUTPUT_DIR / f"{po_number}.json"
                    buffer_file.replace(final_json_path)
                    st.success(f"✔️ Step 1 complete: Data file created as '{final_json_path.name}'.")
                except subprocess.CalledProcessError as e:
                    st.error("Step 1 FAILED.", icon="🚨"); st.text_area("Full Error Log:", e.stdout + e.stderr, height=200); st.stop()
                finally:
                    if 'buffer_file' in locals() and buffer_file.exists(): buffer_file.unlink()

            # --- Step 2: Generate documents ---
            with st.spinner("Step 2 of 3: Generating documents..."):
                try:
                    run_dir = st.session_state.INVOICE_GEN_DIR
                    result = subprocess.run([
                        sys.executable, str(run_dir / "hybrid_generate_invoice.py"), str(final_json_path), 
                        "--outputdir", str(st.session_state.RESULT_DIR), "--templatedir", str(st.session_state.TEMPLATE_DIR), 
                        "--configdir", str(st.session_state.CONFIG_DIR)
                    ], check=True, capture_output=True, text=True, cwd=str(run_dir))
                    st.text(result.stdout)
                    st.success("✔️ Step 2 complete: All documents generated.")
                except subprocess.CalledProcessError as e:
                    st.error("Step 2 FAILED.", icon="🚨"); st.text_area("Full Error Log:", e.stdout + e.stderr, height=300); st.stop()

            # --- Step 3: Save record to database ---
            #
            # As requested, this step has been disabled. The script will no longer push data to the SQLite database.
            #
            # with st.spinner("Step 3 of 4: Saving record to database..."):
            #     try:
            #         with open(final_json_path, 'r', encoding='utf-8') as f:
            #             summary = json.load(f).get("aggregated_summary", {})
            #         with sqlite3.connect(st.session_state.DATABASE_FILE) as conn:
            #             invoice_data = {
            #                 'inv_no': summary.get('inv_no'), 'inv_date': summary.get('inv_date'),
            #                 'inv_ref': summary.get('inv_ref'), 'po': po_number,
            #                 'pcs': str(summary.get('pcs', '')), 'pallet_count': str(summary.get('pallet_count', '')),
            #                 'unit': str(summary.get('unit', '')), 'amount': str(summary.get('amount', '')),
            #                 'net': str(summary.get('net', '')), 'creating_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #             }
            #             conn.execute("""
            #                 INSERT INTO invoices (inv_no, inv_date, inv_ref, po, pcs, pallet_count, unit, amount, net, creating_date)
            #                 VALUES (:inv_no, :inv_date, :inv_ref, :po, :pcs, :pallet_count, :unit, :amount, :net, :creating_date)
            #             """, invoice_data)
            #             conn.commit()
            #         st.success("✔️ Step 3 complete: Record saved to database.")
            #     except Exception as e:
            #         st.error(f"Step 3 FAILED: Could not save to database.", icon="🚨"); st.error(e); st.stop()

            # --- Step 3 (previously Step 4): Archive and Download ---
            with st.spinner("Step 3 of 3: Archiving files..."):
                generated_files = list(st.session_state.RESULT_DIR.glob(f"* {po_number}.xlsx"))
                if not generated_files:
                    st.error("Could not find any generated files to archive.", icon="🚨"); st.stop()
                
                zip_path = st.session_state.RESULT_DIR / f"Generated Documents {po_number}.zip"
                try:
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for file in generated_files:
                            st.write(f"Compressing `{file.name}`...")
                            zipf.write(file, arcname=file.name)
                    st.success(f"✔️ Step 3 complete: Archived {len(generated_files)} files successfully!")
                    with open(zip_path, "rb") as fp:
                        st.download_button(
                            label=f"📥 Download All Files ({zip_path.name})", 
                            data=fp, file_name=zip_path.name, mime="application/zip", use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Step 3 FAILED: Could not create ZIP archive.", icon="🚨"); st.error(e); st.stop()