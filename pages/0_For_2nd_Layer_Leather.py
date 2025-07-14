import streamlit as st
import sys
from pathlib import Path
import subprocess
import json
import datetime
import sqlite3
import re
import os

# --- Page Configuration ---
st.set_page_config(page_title="Generate Invoice", layout="wide")
st.title("Automated Invoice Generator ⚙️")

# --- Project Path & Database Configuration ---
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = PROJECT_ROOT / "data"
    DATA_DIRECTORY = DATA_DIR / 'Invoice Record'
    DATABASE_FILE = DATA_DIRECTORY / 'master_invoice_data.db'
    TABLE_NAME = 'invoices'
    
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
except IndexError:
    st.warning("Could not determine project root. Database features will be disabled.")
    DATABASE_FILE = None
except Exception as e:
    st.error(f"An error occurred during path setup: {e}")
    st.stop()


# --- Helper Functions ---

def check_value_exists(column_name: str, value: str) -> bool:
    """Checks if a specific value exists in a given column in the database."""
    if not DATABASE_FILE or not os.path.exists(DATABASE_FILE):
        return False
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            query = f"SELECT 1 FROM {TABLE_NAME} WHERE LOWER({column_name}) = LOWER(?) LIMIT 1"
            cursor.execute(query, (value,))
            return cursor.fetchone() is not None
    except Exception as e:
        st.warning(f"DB error checking for existing value: {e}")
        return False

def get_suggested_inv_ref() -> str:
    """Suggests the next invoice reference number based on database records."""
    current_year = datetime.datetime.now().strftime('%Y')
    default_suggestion = f"INV{current_year}-1"
    
    if not DATABASE_FILE or not os.path.exists(DATABASE_FILE):
        return default_suggestion
        
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.execute(f"SELECT inv_ref FROM {TABLE_NAME} WHERE inv_ref IS NOT NULL")
            all_refs = [ref[0] for ref in cursor.fetchall()]
        
        if not all_refs:
            return default_suggestion
            
        pattern = re.compile(r"([a-zA-Z]+)(\d{4})-(\d+)")
        max_num = -1
        highest_ref_info = {'prefix': 'INV', 'number': 0}
        
        for ref in all_refs:
            match = pattern.match(str(ref))
            if match:
                num = int(match.group(3))
                if num > max_num:
                    max_num = num
                    highest_ref_info['prefix'] = match.group(1)
                    highest_ref_info['number'] = num
                    
        if max_num == -1:
            return default_suggestion
            
        return f"{highest_ref_info['prefix']}{current_year}-{highest_ref_info['number'] + 1}"
    except Exception as e:
        st.warning(f"DB error suggesting Invoice Ref: {e}")
        return default_suggestion

def update_and_aggregate_json(json_path: Path, inv_ref: str, inv_date: datetime.date, unit_price: float, po_number: str):
    """
    Reads a JSON, calculates all totals from its data, injects all new fields
    into the aggregated_summary, and saves it back.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # --- 1. Calculate Aggregated Totals from raw_data ---
        total_pcs = 0
        total_pallets = 0
        raw_data = data.get("raw_data", {})
        for table_key in raw_data:
            table_data = raw_data[table_key]
            total_pcs += sum(table_data.get("pcs", []))
            total_pallets += len(table_data.get("pallet_count", []))
        
        # --- 2. Calculate Total Amount ---
        total_amount = 0.0
        agg_summary = data.get("aggregated_summary", {})
        total_net = agg_summary.get("net")
        if total_net is not None:
            total_amount = unit_price * float(total_net)
        
        # Display calculated values in the UI for confirmation
        st.info(f"✅ Calculated Total Amount: {total_amount:,.2f}")
        st.info(f"✅ Calculated Total Pcs: {total_pcs}")
        st.info(f"✅ Calculated Total Pallets: {total_pallets}")
            
        # --- 3. Update raw_data with invoice info ---
        for table_key in raw_data:
            num_entries = len(raw_data[table_key].get("po", []))
            raw_data[table_key]["inv_no"] = [po_number] * num_entries
            raw_data[table_key]["inv_ref"] = [inv_ref] * num_entries
            raw_data[table_key]["inv_date"] = [inv_date.strftime("%d/%m/%Y")] * num_entries
            raw_data[table_key]["unit"] = [unit_price] * num_entries

        # --- 4. Update aggregated_summary with all values ---
        if "aggregated_summary" not in data:
            data["aggregated_summary"] = {}
            
        data["aggregated_summary"]["inv_no"] = po_number
        data["aggregated_summary"]["inv_ref"] = inv_ref
        data["aggregated_summary"]["inv_date"] = inv_date.strftime("%d/%m/%Y")
        data["aggregated_summary"]["unit"] = unit_price
        data["aggregated_summary"]["amount"] = total_amount
        # --- Using the correct keys as requested ---
        data["aggregated_summary"]["pcs"] = total_pcs
        data["aggregated_summary"]["pallet_count"] = total_pallets
            
        # --- 5. Write updated data back to the file ---
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        return True

    except Exception as e:
        st.error(f"Failed to update and aggregate JSON file. Details: {e}")
        return False

def get_po_from_json(json_path: Path) -> str | None:
    """Safely reads a JSON file and extracts the PO number from the aggregated_summary first."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        agg_summary = data.get("aggregated_summary", {})
        if agg_summary and agg_summary.get("po"):
            return str(agg_summary["po"]).strip()
            
    except (json.JSONDecodeError, KeyError, Exception) as e:
        st.warning(f"Could not extract PO number from JSON. Details: {e}")
        return None
    return None


# --- Main UI ---
st.header("1. Upload Source Excel File")
uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

if uploaded_file:
    st.markdown("---")
    st.header("2. Enter Invoice Details")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        suggested_ref = get_suggested_inv_ref()
        inv_ref = st.text_input(
            "Invoice Reference", 
            value=suggested_ref, 
            help=f"Enter the reference number. Suggested format: {suggested_ref}"
        )
        if inv_ref and inv_ref != suggested_ref and check_value_exists('inv_ref', inv_ref):
            st.warning(f"⚠️ Invoice Ref `{inv_ref}` already exists in the database.")
    with col2:
        inv_date = st.date_input("Invoice Date", datetime.date.today(), help="Select the date for the invoice.")
    with col3:
        unit_price = st.number_input("Unit Price", min_value=0.0, value=1.0, step=0.01, help="Enter the price per unit.")

    st.markdown("---")

    if st.button(f"Process '{uploaded_file.name}'", use_container_width=True, type="primary"):
        try:
            PROJECT_ROOT = Path(__file__).resolve().parents[1]
            CREATE_JSON_DIR = PROJECT_ROOT / "create_json"
            INVOICE_GEN_DIR = PROJECT_ROOT / "invoice_gen"
            CREATE_JSON_SCRIPT = CREATE_JSON_DIR / "Second_Layer(main).py"
            INVOICE_GEN_SCRIPT = INVOICE_GEN_DIR / "hybrid_generate_invoice.py"
            DATA_DIR = PROJECT_ROOT / "data"
            JSON_OUTPUT_DIR = DATA_DIR / "invoices_to_process"
            TEMP_UPLOAD_DIR = DATA_DIR / "temp_uploads"
            RESULT_DIR = PROJECT_ROOT / "result"
            TEMPLATE_DIR = INVOICE_GEN_DIR / "TEMPLATE"
            CONFIG_DIR = INVOICE_GEN_DIR / "configs"
            for dir_path in [JSON_OUTPUT_DIR, TEMP_UPLOAD_DIR, RESULT_DIR]:
                dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            st.error(f"Error during initial setup. Please check directory structure. Details: {e}")
            st.stop()

        original_identifier = Path(uploaded_file.name).stem
        temp_file_path = TEMP_UPLOAD_DIR / uploaded_file.name

        try:
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        except Exception as e:
            st.error(f"Could not save uploaded file. Error: {e}")
            st.stop()

        buffer_file = JSON_OUTPUT_DIR / f"__buffer.json"
        final_json_path = None

        # --- Step 1: Create JSON file ---
        with st.spinner("Step 1 of 2: Extracting data and aggregating totals..."):
            try:
                command1 = [
                    sys.executable, str(CREATE_JSON_SCRIPT),
                    str(temp_file_path),
                    "-o", str(buffer_file)
                ]
                subprocess.run(
                    command1, check=True, capture_output=True, text=True,
                    cwd=str(CREATE_JSON_DIR), encoding='utf-8', errors='replace'
                )
                
                po_number = get_po_from_json(buffer_file) or original_identifier
                if po_number == original_identifier:
                    st.warning("Could not find PO Number in JSON. Using original filename as the PO number.")
                
                if check_value_exists('inv_no', po_number):
                    st.warning(f"⚠️ Invoice No (from PO) `{po_number}` already exists in the database.")

                # This single function now handles all calculations and updates
                if not update_and_aggregate_json(buffer_file, inv_ref, inv_date, unit_price, po_number):
                    st.stop()

                final_json_path = JSON_OUTPUT_DIR / f"{po_number}.json"
                buffer_file.replace(final_json_path)
                st.success(f"✔️ Step 1 complete: JSON file '{final_json_path.name}' created and fully updated.")

            except subprocess.CalledProcessError as e:
                st.error("Step 1 FAILED: Could not create the JSON file.")
                st.text_area("Error details:", e.stderr, height=200)
                st.stop()
            finally:
                if buffer_file.exists():
                    buffer_file.unlink()

        # --- Step 2: Generate Final Invoice ---
        with st.spinner("Step 2 of 2: Generating final invoice..."):
            try:
                po_identifier = final_json_path.stem
                final_output_path = RESULT_DIR / f"INV PKL CT {po_identifier}.xlsx"
                
                command2 = [
                    sys.executable,
                    str(INVOICE_GEN_SCRIPT),
                    str(final_json_path),
                    "--output", str(final_output_path),
                    "--templatedir", str(TEMPLATE_DIR),
                    "--configdir", str(CONFIG_DIR),
                    "-c", "config"
                ]
                subprocess.run(
                    command2, check=True, capture_output=True, text=True,
                    cwd=str(INVOICE_GEN_DIR), encoding='utf-8', errors='replace'
                )
                st.success("✔️ Step 2 complete: Final invoice generated!")

                # --- Download Button ---
                st.header("3. Download Your File")
                with open(final_output_path, "rb") as fp:
                    st.download_button(
                        label="📥 Download Generated Invoice",
                        data=fp,
                        file_name=final_output_path.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            except subprocess.CalledProcessError as e:
                st.error("Step 2 FAILED: Could not generate the final invoice.")
                st.text_area("Error details:", e.stderr, height=200)
                st.stop()