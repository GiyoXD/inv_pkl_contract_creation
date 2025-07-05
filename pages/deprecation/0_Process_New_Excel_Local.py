import streamlit as st
import os
import sys
from pathlib import Path
import subprocess
import platform
import openpyxl
import re

# --- Page Configuration ---
st.set_page_config(page_title="Process & Generate Invoices", layout="wide")
st.title("Process Excel & Generate Final Invoices ⚙️📄")

# --- Project Path Configuration ---
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    CREATE_JSON_DIR = PROJECT_ROOT / "create_json"
    INVOICE_GEN_DIR = PROJECT_ROOT / "invoice_gen"
    if str(CREATE_JSON_DIR) not in sys.path:
        sys.path.insert(0, str(CREATE_JSON_DIR))
    if str(INVOICE_GEN_DIR) not in sys.path:
        sys.path.insert(0, str(INVOICE_GEN_DIR))
    
    from main import run_invoice_automation
    INVOICE_GEN_SCRIPT = INVOICE_GEN_DIR / "generate_invoice.py"
except (ImportError, IndexError) as e:
    st.error(f"Error: Could not find project scripts. Details: {e}")
    st.exception(e)
    st.stop()

# --- Directory Configuration ---
DATA_DIR = PROJECT_ROOT / "data"
JSON_OUTPUT_DIR = DATA_DIR / "invoices_to_process"
TEMP_UPLOAD_DIR = DATA_DIR / "temp_uploads"
RESULT_DIR = PROJECT_ROOT / "result"
TEMPLATE_DIR = INVOICE_GEN_DIR / "TEMPLATE" # Path to the template directory

JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULT_DIR.mkdir(parents=True, exist_ok=True)

# --- REVISED: Helper function to find Incoterms from the correct template file ---
def find_incoterm_from_template(identifier: str):
    """
    Determines the correct template based on the identifier's prefix
    and scans that template for incoterms.
    """
    terms_to_find = ["DAP", "FCA", "CIP"]
    
    # 1. Extract prefix from identifier (e.g., 'JF' from 'JF25034')
    match = re.match(r'([A-Za-z]+)', identifier)
    if not match:
        st.warning(f"Could not determine prefix from filename '{identifier}' to find the correct template.")
        return None
    prefix = match.group(1)
    
    # 2. Construct the expected template file path
    template_file_path = TEMPLATE_DIR / f"{prefix}.xlsx"
    
    if not template_file_path.exists():
        st.warning(f"Template file '{template_file_path.name}' not found for prefix '{prefix}'. Cannot detect incoterm.")
        return None
        
    # 3. Scan the found template file
    workbook = None
    try:
        workbook = openpyxl.load_workbook(template_file_path, read_only=True)
        sheet = workbook.active
        for row in sheet.iter_rows(min_row=1, max_row=50): # Scan first 50 rows
            for cell in row:
                if cell.value and isinstance(cell.value, str):
                    for term in terms_to_find:
                        # Perform a direct, case-sensitive substring search
                        if term in cell.value:
                            return term
        return None # No term found in the template
    except Exception as e:
        st.warning(f"Could not scan template file '{template_file_path.name}'. Error: {e}")
        return None
    finally:
        if workbook:
            workbook.close()

# --- UI and Logic ---
st.header("1. Upload Excel File")
uploaded_file = st.file_uploader("Choose an XLSX file to process", type="xlsx")

if uploaded_file:
    # --- Scan the correct TEMPLATE file for the Incoterm ---
    identifier = Path(uploaded_file.name).stem
    detected_term = find_incoterm_from_template(identifier)
    
    # --- User Feedback ---
    if detected_term:
        st.success(f"💡 Detected Incoterm '{detected_term}' from the '{identifier.split('2')[0]}.xlsx' template. Output filenames will be adjusted.")
    else:
        st.warning("💡 No special incoterm (DAP, FCA, CIP) detected in the corresponding template. Using 'Normal' as the default name.")

    st.header("2. Select Final Invoice Versions to Create")
    col1, col2, col3 = st.columns(3)
    with col1:
        gen_normal = st.checkbox("Normal Invoice", value=True)
    with col2:
        gen_fob = st.checkbox("FOB Version", value=True)
    with col3:
        gen_combine = st.checkbox("Combine Version", value=True)

    st.header("3. Process and Generate")
    if st.button(f"Process '{uploaded_file.name}' and Generate Final Invoices", use_container_width=True, type="primary"):
        if not (gen_normal or gen_fob or gen_combine):
            st.error("Please select at least one invoice version to generate.")
            st.stop()

        temp_file_path = TEMP_UPLOAD_DIR / uploaded_file.name
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # --- Step 1: Create the JSON data file ---
        st.info("Step 1: Processing Excel file to create structured JSON data...")
        try:
            run_invoice_automation(
                input_excel_override=str(temp_file_path),
                output_dir_override=str(JSON_OUTPUT_DIR)
            )
            json_path = JSON_OUTPUT_DIR / f"{identifier}.json"
            if not json_path.exists():
                raise FileNotFoundError("The JSON data file was not created by the processing script.")
            st.success(f"Step 1 Complete: JSON data file '{json_path.name}' created.")
        except Exception as e:
            st.error(f"An error occurred during Step 1 (JSON Creation): {e}")
            st.exception(e)
            st.stop()
        
        # --- Step 2: Generate the final invoice Excel files ---
        st.info("Step 2: Generating final formatted invoice(s) from JSON data...")
        invoice_output_dir = RESULT_DIR / identifier
        invoice_output_dir.mkdir(parents=True, exist_ok=True)
        
        modes_to_run = []
        if gen_normal:
            mode_name = detected_term if detected_term else "normal"
            modes_to_run.append((mode_name, []))
        if gen_fob:
            modes_to_run.append(("fob", ["--fob"]))
        if gen_combine:
            mode_name = f"{detected_term} Combine" if detected_term else "combine"
            modes_to_run.append((mode_name, ["--custom"]))
        
        success_count = 0
        for mode_name, mode_flags in modes_to_run:
            with st.spinner(f"Generating {mode_name.upper()} version..."):
                output_filename = f"CT&INV&PL {identifier} {mode_name.upper()}.xlsx"
                output_path = invoice_output_dir / output_filename
                command = [
                    sys.executable, str(INVOICE_GEN_SCRIPT), str(json_path),
                    "--output", str(output_path),
                    "--templatedir", str(TEMPLATE_DIR),
                    "--configdir", str(INVOICE_GEN_DIR / "config"),
                ] + mode_flags
                
                try:
                    subprocess.run(command, check=True, capture_output=True, text=True, cwd=INVOICE_GEN_DIR, encoding='utf-8', errors='replace')
                    st.text(f"  > Successfully generated: {output_filename}")
                    success_count += 1
                except subprocess.CalledProcessError as e:
                    st.error(f"Failed to generate {mode_name.upper()} version.")
                    st.text_area(f"Error details for {mode_name}", e.stderr, height=200)

        # --- Final Summary ---
        st.divider()
        if success_count > 0:
            st.success(f"Step 2 Complete! {success_count} final invoice file(s) were created.")
            st.info(f"You can find them in the folder: `{invoice_output_dir.resolve()}`")
            
            try:
                if platform.system() == "Windows": os.startfile(invoice_output_dir)
                elif platform.system() == "Darwin": subprocess.run(["open", invoice_output_dir])
                else: subprocess.run(["xdg-open", invoice_output_dir])
            except Exception: st.warning("Could not automatically open the file explorer.")
        
        st.info("The processed JSON data is also ready. Navigate to the 'Add / Amend Invoice' page to add it to the database.")

        if temp_file_path.exists():
            os.remove(temp_file_path)
