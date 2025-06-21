Invoice Generation Automation
1. Overview
This project automates the process of generating customized commercial invoices, packing lists, and contracts from a single source Excel file. It is designed to handle complex data layouts with multiple tables, perform calculations and data distribution, and apply specific formatting based on templates and configuration files.

The automation is a two-step process:

JSON Creation: It first reads the input Excel file, parses the data according to predefined rules, performs calculations (like CBM distribution), and aggregates the data. The result is a structured JSON file.

Invoice Generation: It then uses the generated JSON data along with an Excel template to populate the final invoice document. It supports generating multiple versions of the invoice (e.g., Normal, FOB, Custom) from the same data.

2. Project Structure
For the automation to work correctly, your files must be organized in the following structure:

.
├── create_json/
│   ├── config.py               # Main configuration for data parsing
│   ├── data_processor.py       # Handles data calculations and aggregation
│   ├── excel_handler.py        # Utility for handling Excel files
│   ├── handle_json.py          # Utility for handling JSON files
│   ├── main.py                 # Main script for the JSON creation process
│   └── sheet_parser.py         # Parses the structure of the input Excel sheet
│
├── invoice_gen/
│   ├── config/
│   │   ├── JF_config.json      # Example: Config for templates prefixed with "JF"
│   │   └── MOTO_config.json    # Example: Config for templates prefixed with "MOTO"
│   ├── TEMPLATE/
│   │   ├── JF.xlsx             # Example: Template for "JF" invoices
│   │   └── MOTO.xlsx           # Example: Template for "MOTO" invoices
│   ├── generate_invoice.py     # Main script for invoice generation
│   ├── invoice_utils.py        # Utility functions for invoice generation
│   ├── merge_utils.py          # Utility for handling merged cells in Excel
│   └── text_replace_utils.py   # Utility for find-and-replace operations
│
├── data/                         # Output folder for intermediate JSON files
├── result/                       # Output folder for final Excel invoices
├── run_automation.py             # The main script to run the entire process
└── requirement.bat               # Script to install required libraries

3. Setup
Step 1: Install Required Libraries
Before running the automation for the first time, you need to install the necessary Python libraries.

Simply run the requirement.bat file included in the project. It will execute the following commands:

pip install openpyxl
pip install python-dateutil

Step 2: Configuration
The automation is highly configurable.

create_json/config.py
This is the primary configuration file for data extraction and processing.

TARGET_HEADERS_MAP: This is the most critical part. You must map the column headers from your source Excel file to the script's internal "canonical" names. The script can recognize multiple variations (including in different languages) for each header.

COLUMNS_TO_DISTRIBUTE: Specify which columns (like 'net' and 'gross' weight) should have their values distributed across empty rows based on a basis column.

DISTRIBUTION_BASIS_COLUMN: Defines the column (e.g., 'pcs') used as the basis for the distribution calculation.

CUSTOM_AGGREGATION_WORKBOOK_PREFIXES: A list of prefixes (e.g., "JF", "MOTO"). If an input Excel file's name starts with one of these prefixes, it will use a "custom" aggregation logic.

invoice_gen/TEMPLATE/
Place your master Excel templates in this directory. The filename of the template (e.g., JF.xlsx) is important, as it's used to find the corresponding configuration.

invoice_gen/config/
This directory holds JSON configuration files that control the layout and styling of the final generated invoice.

The name of the config file must match the prefix of the template it corresponds to (e.g., JF_config.json is used for the JF.xlsx template).

These files define where data is placed, how headers and footers are written, column widths, font styles, and cell merging rules.

4. How to Run the Automation
The entire process is started by running the run_automation.py script from your terminal from the root directory.

Option 1: Interactive Mode (Recommended)
If you run the script without any arguments, a file selection dialog will open, allowing you to choose the input Excel file.

python run_automation.py

By default, this will generate three versions of the invoice: Normal, FOB, and Custom.

Option 2: Command-Line Mode
You can specify the input file and limit the output versions using command-line arguments.

-i or --input: Specify the path to the input Excel file.

--fob: Use this flag to generate only the FOB version of the invoice.

--custom: Use this flag to generate only the Custom version of the invoice.

Examples:

To process a specific file and generate all invoice versions:

python run_automation.py -i "path/to/your/JF12345.xlsx"

To process a file and generate only the FOB version:

python run_automation.py -i "path/to/your/JF12345.xlsx" --fob

5. Output
The script generates two sets of outputs in the project's root directory:

Intermediate JSON Data (/data/): A data folder will be created. It contains the structured JSON file generated from the source Excel (e.g., JF12345.json). This file is used as the input for the final invoice generation step and is useful for debugging.

Final Invoices (/result/<identifier>/): A result folder is created. Inside it, a subfolder named after the input file's identifier (e.g., JF12345) will contain the final Excel invoices.

CT&INV&PL JF12345 NORMAL.xlsx

CT&INV&PL JF12345 FOB.xlsx

CT&INV&PL JF12345 CUSTOM.xlsx

6. Important Notes
Logging: The script produces detailed logs in the terminal. If something goes wrong, the log messages are the first place to look for errors.

File Naming: The automation relies heavily on file naming conventions. Ensure your template and config files are named correctly according to their corresponding prefixes.

Excel Headers: If the script fails to extract data, the most likely cause is a mismatch between the headers in your Excel file and the variations defined in the TARGET_HEADERS_MAP within create_json/config.py.