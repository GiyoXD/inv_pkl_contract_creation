import streamlit as st
import os
import sys
from pathlib import Path
import subprocess
import openpyxl
import re
import io
import zipfile
import json
import datetime
import sqlite3
import time
import tempfile
from zoneinfo import ZoneInfo

# --- Page Configuration ---
st.set_page_config(page_title="Process & Generate Invoices", layout="wide")
st.title("Process Excel & Generate Final Invoices ⚙️📄")

# --- Database Initialization (FAST TWEAK) ---
def initialize_database(db_file: Path):
    """
    Creates tables and performance indexes if they don't exist.
    The function-based indexes here are the key to the speed improvement.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            # Create main table if it doesn't exist
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT, inv_no TEXT, inv_date TEXT,
                inv_ref TEXT UNIQUE, po TEXT, item TEXT, description TEXT, pcs TEXT,
                sqft TEXT, pallet_count TEXT, unit TEXT, amount TEXT, net TEXT,
                gross TEXT, cbm TEXT, production_order_no TEXT, creating_date TEXT,
                status TEXT DEFAULT 'active'
            );
            """)
            # Create function-based indexes for fast, case-insensitive lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_lower_inv_ref ON invoices (LOWER(inv_ref));")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_lower_inv_no ON invoices (LOWER(inv_no));")
            conn.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Database Initialization Failed: {e}")
        return False

# --- Session State Initialization ---
def reset_workflow_state():
    """Callback to reset the state when a new file is uploaded."""
    st.session_state['validation_done'] = False
    st.session_state['json_path'] = None
    st.session_state['missing_fields'] = []
    st.session_state['identifier'] = None

if 'validation_done' not in st.session_state:
    reset_workflow_state()

# --- Project Path Configuration ---
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    CREATE_JSON_DIR = PROJECT_ROOT / "create_json"
    INVOICE_GEN_DIR = PROJECT_ROOT / "invoice_gen"
    if str(CREATE_JSON_DIR) not in sys.path: sys.path.insert(0, str(CREATE_JSON_DIR))
    if str(INVOICE_GEN_DIR) not in sys.path: sys.path.insert(0, str(INVOICE_GEN_DIR))
    from main import run_invoice_automation
    INVOICE_GEN_SCRIPT = INVOICE_GEN_DIR / "generate_invoice.py"
except (ImportError, IndexError) as e:
    st.error(f"Error: Could not find project scripts. Details: {e}"); st.exception(e); st.stop()

# --- Directory and Database Configuration ---
DATA_DIR = PROJECT_ROOT / "data"
JSON_OUTPUT_DIR = DATA_DIR / "invoices_to_process"
TEMP_UPLOAD_DIR = DATA_DIR / "temp_uploads"
TEMPLATE_DIR = INVOICE_GEN_DIR / "TEMPLATE"
DATA_DIRECTORY = DATA_DIR / 'Invoice Record'
DATABASE_FILE = DATA_DIRECTORY / 'master_invoice_data.db'
TABLE_NAME = 'invoices'

for dir_path in [JSON_OUTPUT_DIR, TEMP_UPLOAD_DIR, DATA_DIRECTORY]:
    dir_path.mkdir(parents=True, exist_ok=True)

# --- Call the Database Initializer ---
DB_ENABLED = initialize_database(DATABASE_FILE)
if not DB_ENABLED:
    st.error("Database connection could not be established. The app may not function correctly.")
    st.stop()

def cleanup_old_files(directories: list, max_age_seconds: int = 3600):
    """Deletes files older than a specified age in a list of directories."""
    cutoff_time = time.time() - max_age_seconds
    for directory in directories:
        if not directory.exists(): continue
        try:
            for filepath in directory.iterdir():
                if filepath.is_file():
                    try:
                        if filepath.stat().st_mtime < cutoff_time:
                            filepath.unlink()
                    except OSError:
                        pass
        except Exception:
            pass

cleanup_old_files([TEMP_UPLOAD_DIR, JSON_OUTPUT_DIR])


# --- Helper and Validation Functions (OPTIMIZED) ---
def get_suggested_inv_ref():
    """
    Efficiently suggests the next invoice reference number for the current year
    by querying the database for the maximum existing number.
    """
    current_year = datetime.datetime.now().strftime('%Y')
    prefix = "INV"
    suggestion = f"{prefix}{current_year}-1"

    if not os.path.exists(DATABASE_FILE):
        return suggestion

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            query = f"""
                SELECT inv_ref FROM {TABLE_NAME}
                WHERE inv_ref LIKE ?
                ORDER BY CAST(SUBSTR(inv_ref, INSTR(inv_ref, '-') + 1) AS INTEGER) DESC
                LIMIT 1
            """
            pattern = f"_%{current_year}-%"
            cursor.execute(query, (pattern,))
            last_ref = cursor.fetchone()

            if not last_ref:
                return suggestion

            last_ref_str = last_ref[0]
            match = re.match(r"([a-zA-Z]+)(\d{4})-(\d+)", last_ref_str)
            if match:
                prefix = match.group(1)
                last_num = int(match.group(3))
                return f"{prefix}{current_year}-{last_num + 1}"
            else:
                return suggestion

    except Exception as e:
        st.warning(f"DB error suggesting Invoice Ref: {e}")
        return suggestion

def check_existing_identifiers(inv_no: str = None, inv_ref: str = None) -> dict:
    """
    Checks for the existence of an invoice number and/or invoice reference
    in a single database connection. This is now fast due to the indexes.
    """
    results = {}
    if not os.path.exists(DATABASE_FILE) or (not inv_no and not inv_ref):
        return results

    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            if inv_no:
                query_no = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER(inv_no) = LOWER(?) LIMIT 1"
                cursor.execute(query_no, (inv_no,))
                if cursor.fetchone():
                    results['inv_no'] = True
            if inv_ref:
                query_ref = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER(inv_ref) = LOWER(?) LIMIT 1"
                cursor.execute(query_ref, (inv_ref,))
                if cursor.fetchone():
                    results['inv_ref'] = True
    except Exception as e:
        st.warning(f"DB error checking for existing values: {e}")
    return results

def find_incoterm_from_template(identifier: str):
    terms_to_find = ["DAP", "FCA", "CIP"]
    if not identifier: return None
    match = re.match(r'([A-Za-z]+)', identifier)
    if not match: return None
    prefix = match.group(1)
    template_file_path = TEMPLATE_DIR / f"{prefix}.xlsx"
    if not template_file_path.exists(): return None
    try:
        workbook = openpyxl.load_workbook(template_file_path, read_only=True)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=1, max_row=50):
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for term in terms_to_find:
                        if term in cell.value:
                            workbook.close(); return term
        workbook.close()
    except Exception: pass
    return None

def validate_json_data(json_path: Path, required_keys: list) -> list:
    if not json_path.exists():
        st.error(f"Validation failed: JSON file '{json_path.name}' not found."); return required_keys
    try:
        with open(json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        missing_or_empty_keys = set(required_keys)
        if 'processed_tables_data' in data and isinstance(data['processed_tables_data'], dict):
            all_tables_data = {}
            for table_data in data['processed_tables_data'].values():
                if isinstance(table_data, dict): all_tables_data.update(table_data)
            for key in required_keys:
                if key in all_tables_data and isinstance(all_tables_data[key], list) and any(item is not None and str(item).strip() for item in all_tables_data[key]):
                    missing_or_empty_keys.discard(key)
        return sorted(list(missing_or_empty_keys))
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Validation failed due to invalid JSON: {e}"); return required_keys

# --- Main UI ---
st.header("1. Upload Excel File")
uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx", on_change=reset_workflow_state)

if uploaded_file and not st.session_state.get('validation_done'):
    st.session_state['identifier'] = Path(uploaded_file.name).stem
    temp_file_path = TEMP_UPLOAD_DIR / uploaded_file.name
    
    try:
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Automatically processing and validating your file..."):
            try:
                run_invoice_automation(input_excel_override=str(temp_file_path), output_dir_override=str(JSON_OUTPUT_DIR))
                
                json_path = JSON_OUTPUT_DIR / f"{st.session_state['identifier']}.json"
                if not json_path.exists():
                    st.error("Processing failed: The JSON data file was not created by the automation script.")
                    st.stop()
                
                required_columns = ['inv_no', 'inv_date', 'inv_ref', 'po', 'item', 'pcs', 'sqft', 'pallet_count', 'unit', 'amount', 'net', 'gross', 'cbm', 'production_order_no']
                st.session_state['missing_fields'] = validate_json_data(json_path, required_columns)
                st.session_state['json_path'] = str(json_path)
                st.session_state['validation_done'] = True
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred during initial processing: {e}")
                st.exception(e) 
                st.stop()

    finally:
        if temp_file_path.exists():
            try:
                temp_file_path.unlink() 
            except OSError as e:
                st.warning(f"Could not delete temporary file: {temp_file_path}. Error: {e}")

if st.session_state.get('validation_done'):
    st.subheader("✔️ Automatic Validation Complete")
    missing_fields = st.session_state.get('missing_fields', [])
    if missing_fields: st.warning(f"⚠️ **Validation Warning:** Missing fields: **{', '.join(missing_fields)}**.")
    else: st.success("✅ **Validation Complete:** All required data fields are present.")
    st.divider()

    st.header("2. Optional Invoice Overrides")
    st.markdown("Use these fields to add or correct data.")
    col1, col2 = st.columns(2)

    suggested_ref = get_suggested_inv_ref()

    with col1:
        user_inv_no = st.text_input("Invoice No", key="user_inv_no")
        user_inv_ref = st.text_input(
            "Invoice Ref",
            value=suggested_ref,
            key="user_inv_ref",
            help="This is the automatically suggested Invoice Ref. You can override it."
        )

        check_no = user_inv_no.strip()
        check_ref = user_inv_ref.strip() if user_inv_ref != suggested_ref else None

        if check_no or check_ref:
            existing = check_existing_identifiers(inv_no=check_no, inv_ref=check_ref)
            if existing.get('inv_no'):
                st.warning(f"⚠️ Invoice No `{check_no}` already exists in the database.")
            if existing.get('inv_ref'):
                st.warning(f"⚠️ Invoice Ref `{check_ref}` already exists in the database.")

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        selected_date_obj = st.date_input("Invoice Date", value=tomorrow, format="DD/MM/YYYY")
        user_inv_date = selected_date_obj.strftime("%d/%m/%Y") if selected_date_obj else ""

    with col2:
        user_container_types = st.text_area("Container / Truck (One per line)", height=150)

    st.header("3. Select Final Invoice Versions")
    c1, c2, c3 = st.columns(3)
    with c1: gen_normal = st.checkbox("Normal Invoice", value=True)
    with c2: gen_fob = st.checkbox("FOB Version", value=True)
    with c3: gen_combine = st.checkbox("Combine Version", value=True)

    st.header("4. Generate Final Invoices")
    if st.button("Generate Final Invoices", use_container_width=True, type="primary"):
        if not (gen_normal or gen_fob or gen_combine): st.error("Please select at least one invoice version."); st.stop()

        json_path = Path(st.session_state['json_path'])
        final_user_inv_ref = user_inv_ref if user_inv_ref else get_suggested_inv_ref()
        container_list = [line.strip() for line in user_container_types.split('\n') if line.strip()]

        if user_inv_no or final_user_inv_ref or user_inv_date or container_list:
            with st.spinner("Applying manual overrides to JSON file..."):
                try:
                    with open(json_path, 'r+', encoding='utf-8') as f:
                        data = json.load(f); was_modified = False
                        
                        # Get current time in Cambodia timezone for the creation date
                        cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
                        creating_date_str = datetime.datetime.now(cambodia_tz).strftime("%Y-%m-%d %H:%M:%S")
                        
                        if 'processed_tables_data' in data:
                            for table_data in data['processed_tables_data'].values():
                                if 'amount' not in table_data or not isinstance(table_data['amount'], list): continue
                                num_rows = len(table_data['amount'])
                                
                                # Add the creation date using Cambodia timezone
                                table_data['creating_date'] = [creating_date_str] * num_rows; was_modified = True
                                
                                if user_inv_no: table_data['inv_no'] = [user_inv_no.strip()] * num_rows; was_modified = True
                                if final_user_inv_ref: table_data['inv_ref'] = [final_user_inv_ref.strip()] * num_rows; was_modified = True
                                if user_inv_date: table_data['inv_date'] = [user_inv_date] * num_rows; was_modified = True
                                if container_list:
                                    table_data['container_type'] = [', '.join(container_list)] * num_rows; was_modified = True
                        if was_modified:
                            f.seek(0); json.dump(data, f, indent=4); f.truncate()
                            st.success("Overrides applied to JSON file.")
                except Exception as e:
                    st.error(f"Error during JSON Override: {e}"); st.stop()

        with st.spinner("Generating selected invoice files..."):
            identifier = st.session_state['identifier']
            files_to_zip = [{"name": json_path.name, "data": json_path.read_bytes()}]
            
            detected_term = find_incoterm_from_template(identifier)
            modes_to_run = [("fob", ["--fob"]), ("combine", ["--custom"])]
            if gen_normal: modes_to_run.insert(0, (detected_term if detected_term else "normal", []))
            if not gen_fob: modes_to_run = [m for m in modes_to_run if m[0] != 'fob']
            if not gen_combine: modes_to_run = [m for m in modes_to_run if m[0] != 'combine']

            success_count = 0
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                for mode_name, mode_flags in modes_to_run:
                    final_mode_name = mode_name.upper()
                    if mode_name == 'combine':
                        term_part = f"{detected_term.upper()} " if detected_term else ""
                        final_mode_name = f"{term_part}COMBINE"
                    
                    output_filename = f"CT&INV&PL {identifier} {final_mode_name}.xlsx"
                    output_path = temp_dir_path / output_filename
                    
                    command = [sys.executable, str(INVOICE_GEN_SCRIPT), str(json_path), "--output", str(output_path), "--templatedir", str(TEMPLATE_DIR), "--configdir", str(INVOICE_GEN_DIR / "config")] + mode_flags
                    
                    sub_env = os.environ.copy()
                    sub_env['PYTHONIOENCODING'] = 'utf-8'

                    try:
                        subprocess.run(command, check=True, capture_output=True, text=True, cwd=INVOICE_GEN_DIR, encoding='utf-8', errors='replace', env=sub_env)
                        files_to_zip.append({"name": output_filename, "data": output_path.read_bytes()})
                        success_count += 1
                    except subprocess.CalledProcessError as e:
                        st.error(f"Failed to generate '{final_mode_name}' version. Error: {e.stderr}")

            if success_count > 0:
                st.success(f"Successfully created {success_count} invoice file(s)!")
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for file_info in files_to_zip: zip_file.writestr(file_info["name"], file_info["data"])
                st.header("5. Download Your Files")
                st.download_button(label=f"📥 Download All Files ({len(files_to_zip)}) as ZIP", data=zip_buffer.getvalue(), file_name=f"Invoices-{identifier}.zip", mime="application/zip", use_container_width=True, type="primary")
            else:
                st.error("Processing finished, but no files were generated. Check for errors above.")