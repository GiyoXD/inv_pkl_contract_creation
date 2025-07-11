import streamlit as st
import sys
from pathlib import Path
import subprocess
import json

# --- Page Configuration ---
st.set_page_config(page_title="Generate Invoice", layout="wide")
st.title("Automated Invoice Generator ⚙️")

# --- Helper Function ---
def get_po_from_json(json_path: Path) -> str | None:
    """Safely reads a JSON file and extracts the first PO number."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        raw_data = data.get("raw_data", {})
        if not raw_data:
            return None
        first_table_key = next(iter(raw_data))
        first_table_data = raw_data[first_table_key]
        po_list = first_table_data.get("po", [])
        if po_list and po_list[0]:
            return str(po_list[0]).strip()
    except Exception:
        return None
    return None

# --- Main UI ---
st.header("1. Upload Source Excel File")
uploaded_file = st.file_uploader("Choose an XLSX file", type="xlsx")

if uploaded_file:
    try:
        # --- Project Path Configuration ---
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

    if st.button(f"Process '{uploaded_file.name}'", use_container_width=True, type="primary"):
        buffer_file = JSON_OUTPUT_DIR / f"__buffer.json"
        final_json_path = None

        # --- Step 1: Create JSON file ---
        with st.spinner("Step 1 of 2: Extracting data from Excel..."):
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

                po_number = get_po_from_json(buffer_file)

                if po_number:
                    final_json_path = JSON_OUTPUT_DIR / f"{po_number}.json"
                else:
                    final_json_path = JSON_OUTPUT_DIR / f"{original_identifier}.json"
                    st.warning("Could not find PO Number. Using original filename.")
                
                buffer_file.replace(final_json_path)
                st.success(f"✔️ Step 1 complete: JSON file '{final_json_path.name}' created.")

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
                st.header("2. Download Your File")
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