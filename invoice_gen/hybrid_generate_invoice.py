import argparse
import json
import shutil
import openpyxl
import sys
import re
from pathlib import Path

# --- Import Reusable and New Utilities ---
import text_replace_utils
import invoice_utils
import packing_list_utils
import merge_utils

def calculate_and_inject_totals(data: dict) -> dict:
    """
    Calculates summary values from raw data (like total pallets)
    and injects them into the main data dictionary for easy access.
    """
    print("Calculating and injecting summary totals...")
    if 'raw_data' not in data:
        print("  -> No 'raw_data' found, skipping calculation.")
        return data

    # --- Calculate Grand Total of Pallets ---
    grand_total_pallets = 0
    raw_data = data.get('raw_data', {})
    for table_data in raw_data.values():
        # The number of pallets is the number of items in the 'pallet_count' list
        pallet_count_for_table = len(table_data.get('pallet_count', []))
        grand_total_pallets += pallet_count_for_table

    print(f"  -> Calculated Grand Total Pallets: {grand_total_pallets}")

    # --- Inject the calculated total into a predictable location ---
    # Ensure the target dictionary exists before adding to it
    if 'aggregated_summary' not in data:
        data['aggregated_summary'] = {}
    
    data['aggregated_summary']['total_pallets'] = grand_total_pallets

    # This function can be expanded later to calculate total CBM, total gross weight, etc.

    return data

def preprocess_data_for_numerics(data: any, keys_to_convert: set) -> any:
    """
    Recursively traverses a data structure (dict or list) and converts
    string values of specified keys into floats.
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if key in keys_to_convert and isinstance(value, list):
                # This is a target key, process its list of values
                new_list = []
                for item in value:
                    if isinstance(item, str):
                        try:
                            # Remove commas and convert to float
                            new_list.append(float(item.replace(',', '')))
                        except (ValueError, TypeError):
                            new_list.append(item) # Keep original if conversion fails
                    else:
                        new_list.append(item) # Keep non-string items as is
                new_dict[key] = new_list
            else:
                # Recursively process other values
                new_dict[key] = preprocess_data_for_numerics(value, keys_to_convert)
        return new_dict
    elif isinstance(data, list):
        # If it's a list, process each item in the list
        return [preprocess_data_for_numerics(item, keys_to_convert) for item in data]
    else:
        # Return the item as is if it's not a dict or list
        return data

def derive_paths(input_data_path_str: str, template_dir_str: str, config_dir_str: str) -> dict | None:
    """
    Derives template and config file paths based on the input data filename.
    """
    print(f"Deriving paths from input: {input_data_path_str}")
    try:
        input_data_path = Path(input_data_path_str).resolve()
        template_dir = Path(template_dir_str).resolve()
        config_dir = Path(config_dir_str).resolve()

        if not input_data_path.is_file():
            print(f"Error: Input data file not found: {input_data_path}")
            return None
        if not template_dir.is_dir():
            print(f"Error: Template directory not found: {template_dir}")
            return None
        if not config_dir.is_dir():
            print(f"Error: Config directory not found: {config_dir}")
            return None

        base_name = input_data_path.stem
        template_name_part = re.sub(r'(_data|_input|_pkl)$', '', base_name, flags=re.IGNORECASE)

        print(f"Derived template name part: '{template_name_part}'")

        # --- Attempt 1: Exact Match ---
        exact_template_path = template_dir / f"{template_name_part}.xlsx"
        exact_config_path = config_dir / f"{template_name_part}_config.json"
        
        if exact_template_path.is_file() and exact_config_path.is_file():
            print("Found exact match for template and config.")
            return {
                "data": input_data_path,
                "template": exact_template_path,
                "config": exact_config_path
            }

        print("Exact match not found. Attempting prefix matching...")
        
        # --- Attempt 2: Prefix Match (e.g., "PL" from "PL_data_123") ---
        prefix_match = re.match(r'^([a-zA-Z]+)', template_name_part)
        if prefix_match:
            prefix = prefix_match.group(1)
            prefix_template_path = template_dir / f"{prefix}.xlsx"
            prefix_config_path = config_dir / f"{prefix}_config.json"
            if prefix_template_path.is_file() and prefix_config_path.is_file():
                print(f"Found prefix match for template and config using prefix: '{prefix}'")
                return {
                    "data": input_data_path,
                    "template": prefix_template_path,
                    "config": prefix_config_path
                }
        
        print(f"Error: Could not find matching files.")
        if not exact_template_path.is_file(): print(f"-> Missing: {exact_template_path}")
        if not exact_config_path.is_file(): print(f"-> Missing: {exact_config_path}")
        return None

    except Exception as e:
        print(f"Error deriving file paths: {e}")
        return None

def load_json_file(file_path: Path, file_type: str) -> dict:
    """Loads and parses a JSON file (data or config)."""
    print(f"Loading {file_type} from: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"FATAL ERROR: Could not load or parse {file_type} file {file_path}. Error: {e}")
        sys.exit(1)

def main():
    """Main function to orchestrate hybrid invoice generation."""
    parser = argparse.ArgumentParser(description="Generate an invoice document using a hybrid approach.")
    parser.add_argument("input_data_file", help="Path to the input JSON data file. Filename determines template/config.")
    parser.add_argument("-o", "--output", default="result.xlsx", help="Path for the output Excel file (default: result.xlsx)")
    parser.add_argument("-t", "--templatedir", default="./TEMPLATE", help="Directory for template files (default: ./TEMPLATE)")
    parser.add_argument("-c", "--configdir", default="./config", help="Directory for config files (default: ./config)")
    args = parser.parse_args()

    print("--- Starting Hybrid Invoice Generation ---")
    
    # --- 1. Derive Paths, Load Data and Config ---
    paths = derive_paths(args.input_data_file, args.templatedir, args.configdir)
    if not paths:
        sys.exit(1)

    invoice_data = load_json_file(paths['data'], "data")
    config = load_json_file(paths['config'], "config")

    # --- NEW: Pre-process data to handle numeric conversions centrally ---
    keys_to_convert = {'net', 'amount', 'price'}
    print(f"Preprocessing invoice data to convert numeric fields: {keys_to_convert}")
    invoice_data = preprocess_data_for_numerics(invoice_data, keys_to_convert)
    invoice_data = calculate_and_inject_totals(invoice_data)
    # -------------------------------------------------------------------

    # --- 2. Prepare Output File ---
    output_path = Path(args.output)
    print(f"Copying template '{paths['template'].name}' to '{output_path.name}'...")
    try:
        shutil.copy(paths['template'], output_path)
    except Exception as e:
        print(f"FATAL ERROR: Could not copy template file. Error: {e}")
        sys.exit(1)

    # --- 3. Process the Workbook ---
    workbook = None
    try:
        workbook = openpyxl.load_workbook(output_path)
        sheets_to_process_config = config.get("sheets_to_process", {})

        for sheet_name, sheet_config in sheets_to_process_config.items():
            if sheet_name not in workbook.sheetnames:
                print(f"Warning: Sheet '{sheet_name}' defined in config not found in template. Skipping.")
                continue

            print(f"\n--- Processing Sheet: '{sheet_name}' ---")
            worksheet = workbook[sheet_name]
            process_type = sheet_config.get("type")

            # --- HYBRID LOGIC ---
            if process_type == "summary":
                print(f"Processing '{sheet_name}' as a summary sheet (text replacement).")
                text_replace_utils.find_and_replace(
                    workbook=workbook,
                    rules=sheet_config.get("replacements", []),
                    limit_rows=50,
                    limit_cols=20,
                    invoice_data=invoice_data
                )

            elif process_type == "packing_list":
                print(f"Processing '{sheet_name}' as a complex packing list.")
                start_row = sheet_config.get("start_row", 1)

                print("Step 1: Storing original merges below the header...")
                merges_to_restore = merge_utils.store_original_merges(workbook, [sheet_name])

                print("Step 2: Calculating space needed for new data...")
                rows_to_add = packing_list_utils.calculate_rows_to_generate(invoice_data, sheet_config)
                
                if rows_to_add > 0:
                    print(f"Step 3: Preparing sheet by unmerging data area and inserting {rows_to_add} rows at row {start_row}...")
                    merge_utils.force_unmerge_from_row_down(worksheet, start_row)
                    worksheet.insert_rows(start_row, amount=rows_to_add)
                else:
                    print("Step 3: No data to add, skipping row insertion.")

                print("Step 4: Writing new packing list data into the prepared space...")
                packing_list_utils.generate_full_packing_list(
                    worksheet=worksheet,
                    start_row=start_row,
                    packing_list_data=invoice_data,
                    sheet_config=sheet_config
                )
                
                print("Step 5: Restoring original merges in their new, pushed-down locations...")
                merge_utils.find_and_restore_merges_heuristic(
                    workbook=workbook,
                    stored_merges=merges_to_restore,
                    processed_sheet_names=[sheet_name]
                )
            
            else:
                print(f"Warning: Unknown process type '{process_type}' for sheet '{sheet_name}'. Skipping.")

        # --- 4. Save Final Workbook ---
        print("\n--- Saving final workbook ---")
        workbook.save(output_path)
        print(f"✅ Processing complete. Output saved to '{output_path}'")

    except Exception as e:
        print(f"\n--- A CRITICAL ERROR occurred during workbook processing: {e} ---")
        import traceback
        traceback.print_exc()
    finally:
        if workbook:
            workbook.close()
            print("Workbook closed.")

if __name__ == "__main__":
    main()