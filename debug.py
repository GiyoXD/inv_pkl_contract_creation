import sys
from pathlib import Path
import time
import logging

# --- Configuration ---
# IMPORTANT: Change this to the name of the XLSX file that causes the crash.
# The file must be located in your "data/temp_uploads/" folder.
TEST_EXCEL_FILE = "your_problematic_file.xlsx"

# --- DO NOT EDIT BELOW THIS LINE ---

# Setup logging to see detailed output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the project root directory (where this debug script is)
PROJECT_ROOT = Path(__file__).resolve().parent

# **CRUCIAL**: Add the 'create_json' subdirectory to Python's path
# This allows us to import the correct 'main.py' script.
CREATE_JSON_DIR = PROJECT_ROOT / "create_json"
if str(CREATE_JSON_DIR) not in sys.path:
    sys.path.insert(0, str(CREATE_JSON_DIR))

# Try to import the function that the Streamlit app uses
try:
    # We assume the function is named 'run_invoice_automation' based on the Streamlit code
    from main import run_invoice_automation
except ImportError:
    logging.error("FATAL: Could not import 'run_invoice_automation' from 'create_json/main.py'.")
    logging.error("Please ensure the function exists in that file and there are no syntax errors.")
    sys.exit(1)

# Define paths for the test
temp_file_path = PROJECT_ROOT / "data" / "temp_uploads" / TEST_EXCEL_FILE
json_output_dir = PROJECT_ROOT / "data" / "invoices_to_process"
json_output_dir.mkdir(parents=True, exist_ok=True) # Ensure output directory exists

# Check if the test file exists
if not temp_file_path.exists():
    logging.error(f"FATAL: The test file was not found at: {temp_file_path}")
    logging.error("Please make sure the file name is correct and it's in the 'data/temp_uploads' folder.")
    sys.exit(1)

# --- Run the Target Function ---
logging.info("="*50)
logging.info(f"Attempting to run 'run_invoice_automation' from 'create_json/main.py'...")
logging.info(f"Input file: {temp_file_path}")
logging.info("="*50)

start_time = time.time()
try:
    # Call the function directly, just like the Streamlit app does
    run_invoice_automation(
        input_excel_override=str(temp_file_path),
        output_dir_override=str(json_output_dir)
    )
    logging.info("\n✅ SUCCESS: The function 'run_invoice_automation' completed without crashing.")

except Exception as e:
    logging.error(f"\n❌ ERROR: The function crashed with an exception!")
    import traceback
    traceback.print_exc() # Print the full, detailed error

finally:
    end_time = time.time()
    logging.info(f"\nProcess finished or was stopped in {end_time - start_time:.2f} seconds.")
    logging.info("="*50)