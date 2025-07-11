import logging
import json
import argparse # Import the argument parsing library
from decimal import Decimal, InvalidOperation

# Import the tools and configuration from your other files
from excel_handler import ExcelHandler
import sheet_parser
from config import (
    SHEET_NAME,
    STOP_EXTRACTION_ON_EMPTY_COLUMN
)

# Set up basic logging to see the output from the modules
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# The main function now accepts file paths as arguments
def run_final_extraction(input_filepath, output_filepath):
    """
    Finds and extracts data, immediately parses CBM values, aggregates all data,
    and generates a final JSON with parsed raw data and a summarized view.
    """
    # --- 1. EXTRACTION ---
    logging.info(f"--- Starting Extraction for {input_filepath} ---")
    handler = ExcelHandler(input_filepath) # Use the input filepath argument
    sheet = handler.load_sheet(sheet_name=SHEET_NAME)
    if not sheet:
        logging.error("Failed to load the sheet. Exiting.")
        return

    all_tables_data = {}
    last_found_row = 0
    table_count = 0
    column_mapping = None

    while True:
        sheet_parser.HEADER_SEARCH_ROW_RANGE = (last_found_row + 1, sheet.max_row)
        header_info = sheet_parser.find_and_map_smart_headers(sheet)
        
        if not header_info:
            logging.info("No more valid tables found. Ending search.")
            break

        header_row, current_mapping = header_info
        if column_mapping is None:
            column_mapping = current_mapping

        logging.info(f"Found table {table_count + 1} at row {header_row}")

        extracted_data = sheet_parser.extract_multiple_tables(sheet, [header_row], column_mapping)
        if extracted_data:
            table_count += 1
            all_tables_data[table_count] = extracted_data[1]
            num_rows_in_table = len(extracted_data[1].get(STOP_EXTRACTION_ON_EMPTY_COLUMN, []))
            last_found_row = header_row + num_rows_in_table
        else:
            break
            
    handler.close()

    if not all_tables_data:
        logging.warning("Extraction finished, but no data was returned.")
        return

    # --- 2. POST-EXTRACTION PROCESSING ---
    logging.info("--- Parsing CBM values in raw data ---")
    for table_id, table_data in all_tables_data.items():
        if 'cbm' in table_data:
            calculated_cbm_list = [sheet_parser.parse_and_calculate_cbm(cbm_str) for cbm_str in table_data['cbm']]
            all_tables_data[table_id]['cbm'] = calculated_cbm_list

    # --- 3. AGGREGATION ---
    fields_to_sum = {'net', 'gross', 'cbm'}
    fields_to_collect = {'po', 'item', 'description'}

    final_totals = {field: Decimal('0') for field in fields_to_sum}
    final_strings = {field: set() for field in fields_to_collect}

    for table_data in all_tables_data.values():
        for field in fields_to_sum:
            for value in table_data.get(field, []):
                try:
                    if value is not None and str(value).strip():
                        final_totals[field] += Decimal(str(value))
                except (InvalidOperation, TypeError):
                    continue
                    
        for field in fields_to_collect:
            for value in table_data.get(field, []):
                if value is not None and str(value).strip():
                    final_strings[field].add(str(value))

    # --- 4. FINALIZE AND OUTPUT JSON ---
    aggregated_summary = {field: float(total) for field, total in final_totals.items()}
    for field, value_set in final_strings.items():
        aggregated_summary[field] = ", ".join(sorted(list(value_set)))

    final_output = {"raw_data": all_tables_data, "aggregated_summary": aggregated_summary}

    def json_converter(o):
        if isinstance(o, Decimal): return str(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    output_json = json.dumps(final_output, indent=4, default=json_converter)

    logging.info("--- Aggregation Complete! ---")
    print("\nFinal JSON Output:")
    print(output_json)

    # Use the output filepath argument to save the file
    with open(output_filepath, "w") as f:
        f.write(output_json)
    logging.info(f"Saved output to {output_filepath}")


if __name__ == "__main__":
    # --- NEW: Set up command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Extract and process data from an Excel invoice file.")
    
    # Required argument for the input file
    parser.add_argument("input_file", help="Path to the input Excel file (e.g., JF.xlsx).")
    
    # Optional argument for the output file
    parser.add_argument("-o", "--output", default="output.json", help="Path for the output JSON file (default: output.json).")
    
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    run_final_extraction(args.input_file, args.output)