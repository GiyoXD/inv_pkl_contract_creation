import os
import subprocess
import argparse
import sys
from pathlib import Path
import logging
from typing import List, Optional
import shutil
import tkinter as tk
from tkinter import filedialog
import re

# Setup basic logging for the wrapper script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_path: Path, args: List[str] = [], cwd: Optional[Path] = None, script_name: str = "") -> bool:
    """Runs a Python script using subprocess, handling potential errors."""
    if not script_path.is_file():
        logging.error(f"Script not found: {script_path}")
        return False

    command = [sys.executable, str(script_path)] + args
    script_name = script_name or script_path.name
    logging.info(f"Running {script_name}...")
    logging.info(f"  Command: {' '.join(command)}")
    if cwd and Path(cwd).is_dir():
        logging.info(f"  Working Directory for {script_name}: {cwd}")

    try:
        result = subprocess.run(
            command, capture_output=True, text=True, check=True,
            cwd=cwd, encoding='utf-8', errors='replace'
        )
        if result.stdout:
            logging.info(f"{script_name} Output:\n--- START ---\n{result.stdout.strip()}\n--- END ---")
        if result.stderr:
            logging.warning(f"{script_name} Stderr:\n--- START ---\n{result.stderr.strip()}\n--- END ---")
        
        logging.info(f"{script_name} completed successfully.")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Error running {script_name} (Return Code: {e.returncode}):")
        logging.error(f"Stdout:\n{e.stdout.strip() if e.stdout else 'No stdout captured.'}")
        logging.error(f"Stderr:\n{e.stderr.strip() if e.stderr else 'No stderr captured.'}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while trying to run {script_name}: {e}")
        return False

def select_excel_file() -> Optional[Path]:
    """Opens a file dialog for the user to select an Excel file."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Input Excel File",
        initialdir=str(Path.cwd()),
        filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
    )
    root.destroy()
    return Path(file_path) if file_path else None

def main():
    parser = argparse.ArgumentParser(description="Automate JSON creation and multi-sheet Invoice generation.")
    parser.add_argument("-i", "--input", help="Path to the input Excel file. If not provided, a file dialog will open.", type=str)
    args = parser.parse_args()

    input_excel_path = Path(args.input).resolve() if args.input else select_excel_file()
    if not input_excel_path or not input_excel_path.is_file():
        logging.info("No valid input file selected. Exiting.")
        sys.exit(0)

    identifier = input_excel_path.stem
    logging.info(f"Processing file with identifier: {identifier}")

    # --- Define Directory Structure ---
    project_root = Path(__file__).resolve().parent
    current_working_dir = Path.cwd()
    data_dir = current_working_dir / "data" / "invoices_to_process"
    invoice_output_dir = current_working_dir / "result" / identifier
    for d in [data_dir, invoice_output_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    create_json_dir = project_root / "create_json"
    invoice_gen_dir = project_root / "invoice_gen"
    
    # --- MODIFIED: Point to the sheet-splitting script ---
    # This now assumes your advanced script is named 'hybrid_generate_invoice.py'
    create_json_script = create_json_dir / "main.py"
    invoice_gen_script = invoice_gen_dir / "hybrid_generate_invoice.py"
    template_dir = invoice_gen_dir / "TEMPLATE"
    config_dir = invoice_gen_dir / "config"
    
    # --- Step 1: Run create_json/main.py ---
    logging.info("--- Step 1: Creating JSON data file ---")
    create_json_args = ["--input-excel", str(input_excel_path), "--output-dir", str(data_dir)]
    if not run_script(create_json_script, args=create_json_args, cwd=create_json_dir, script_name="create_json"):
        logging.error("JSON creation script failed. Aborting."); sys.exit(1)

    expected_json_path = data_dir / f"{identifier}.json"
    if not expected_json_path.is_file():
        logging.error(f"Expected JSON output file was not found: {expected_json_path}"); sys.exit(1)
    logging.info(f"JSON file successfully created: {expected_json_path}")
    
    # --- Step 2: Run sheet-splitting invoice generation ---
    logging.info("--- Step 2: Generating separate Excel file for each sheet ---")
    invoice_gen_args = [
        str(expected_json_path),
        "--output", str(invoice_output_dir),
        "--templatedir", str(template_dir),
        "--configdir", str(config_dir),
    ]
    generation_successful = run_script(
        invoice_gen_script, args=invoice_gen_args, cwd=invoice_gen_dir, script_name="hybrid_invoice_gen"
    )

    # --- Final Summary ---
    if generation_successful:
        logging.info("--- Automation Completed Successfully ---")
        generated_files = list(invoice_output_dir.glob(f"* {identifier}.xlsx"))
        if generated_files:
            logging.info(f"Generated {len(generated_files)} files in: {invoice_output_dir.resolve()}")
            for i, file in enumerate(generated_files):
                logging.info(f"  {i+1}. {file.name}")
        else:
            logging.warning("Invoice generation script ran, but no output files were found.")
    else:
        logging.error("--- Automation FAILED --- Invoice generation script failed. Review logs for errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()