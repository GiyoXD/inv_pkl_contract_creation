# Invoice Management System

A comprehensive business automation platform for leather industry invoice processing, featuring automated Excel-to-invoice generation, web-based management interface, and complete invoice lifecycle management.

## 🎯 Overview

This system provides end-to-end invoice management capabilities:

- **Automated Invoice Generation**: Convert Excel files to professional invoices using customizable templates
- **Web Dashboard**: Streamlit-based interface for invoice management and analytics
- **Database Management**: SQLite-powered storage with full CRUD operations
- **Multi-format Support**: Generate Normal, FOB, and Custom invoice variants
- **Data Validation**: Built-in verification workflows to ensure data integrity

## 🏗️ System Architecture

### Core Components

```
├── 📊 Web Interface (Streamlit)
│   ├── app.py                    # Main dashboard with KPIs and analytics
│   └── pages/                    # Feature-specific pages
│
├── 🔄 Automation Pipeline
│   ├── main.py                   # Master automation orchestrator
│   ├── create_json/              # Excel → JSON conversion
│   └── invoice_gen/              # JSON → Invoice generation
│
├── 💾 Data Management
│   └── data/                     # All data storage
│       ├── invoices_to_process/  # Incoming JSON files
│       ├── Invoice Record/       # SQLite database
│       ├── processed_invoices/   # Completed invoices
│       ├── failed_invoices/      # Error handling
│       └── backups/              # Database backups
│
└── 📄 Templates & Configuration
    └── invoice_gen/
        ├── TEMPLATE/             # Excel invoice templates
        └── config/               # Template configurations
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

**Required packages:**
- `streamlit` - Web interface
- `pandas` - Data processing
- `openpyxl` - Excel file handling
- `sqlite3` - Database (built-in)
- `python-dateutil` - Date processing

### Launch the Application

```bash
# Start the web interface
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📋 Features

### 🖥️ Web Interface Features

| Page | Function | Description |
|------|----------|-------------|
| **Dashboard** | Analytics & KPIs | Revenue tracking, invoice metrics, visual analytics |
| **High Quality Leather** | Data Entry | Specialized form for premium leather products |
| **2nd Layer Leather** | Data Entry | Form for secondary leather products |
| **Verify Data** | Quality Control | Review and approve incoming invoice data |
| **Edit Invoice** | Data Management | Modify existing invoices with undo/redo |
| **View Database** | Data Explorer | Advanced filtering and search capabilities |
| **Reference Numbers** | Lookup | Quick reference number verification |
| **Void Invoice** | Status Management | Deactivate invoices (soft delete) |
| **Backup Database** | Data Protection | Create and manage database backups |
| **Export Data** | Reporting | Export filtered data to various formats |
| **Pallet Calculator** | Utility | Calculate shipping pallet requirements |

### 🤖 Automation Features

- **Batch Processing**: Process multiple Excel files automatically
- **Template System**: Configurable invoice layouts per client/product type
- **Multi-variant Generation**: Create Normal, FOB, and Custom versions simultaneously
- **Error Handling**: Automatic failure detection and quarantine
- **Data Validation**: Built-in checks for data integrity

## 🔧 Configuration

### Invoice Templates

Templates are stored in `invoice_gen/TEMPLATE/` and named by prefix:
- `JF.xlsx` - For files starting with "JF"
- `MOTO.xlsx` - For files starting with "MOTO"

### Template Configuration

Each template requires a corresponding config file in `invoice_gen/config/`:
- `JF_config.json` - Layout rules for JF template
- `MOTO_config.json` - Layout rules for MOTO template

### Data Processing Rules

Configure data extraction in `create_json/config.py`:
- **Header Mapping**: Map Excel columns to system fields
- **Distribution Logic**: Define how values spread across rows
- **Aggregation Rules**: Custom calculations per client type

## 📊 Usage Examples

### Automated Invoice Generation

```bash
# Interactive mode (file picker)
python main.py

# Command line with specific file
python main.py -i "path/to/JF12345.xlsx"

# Generate only FOB version
python main.py -i "path/to/JF12345.xlsx" --fob

# Generate only Custom version
python main.py -i "path/to/JF12345.xlsx" --custom
```

### Web Interface Workflow

1. **Upload Data**: Use specialized forms or place JSON files in `data/invoices_to_process/`
2. **Verify**: Review incoming data in "Verify Data To Insert" page
3. **Process**: Accept or reject data with built-in validation
4. **Manage**: Edit, view, or void invoices as needed
5. **Export**: Generate reports and backups

## 📁 Data Flow

```
Excel File → JSON Conversion → Invoice Generation → Database Storage
     ↓              ↓                    ↓                    ↓
  Raw Data    Structured Data      Final Output        Persistent Store
```

### File Processing States

- **Incoming**: `data/invoices_to_process/` - Awaiting verification
- **Failed**: `data/failed_invoices/` - Processing errors
- **Processed**: Database storage - Successfully imported
- **Generated**: `result/` - Final invoice files

## 🛡️ Data Management

### Database Schema

**Main Tables:**
- `invoices` - Core invoice line items
- `invoice_containers` - Shipping container/truck information

**Key Fields:**
- `inv_ref` - Primary invoice reference
- `inv_no` - Invoice number
- `status` - active/voided
- `creating_date` - Timestamp
- `amount`, `sqft`, `pcs` - Quantities
- `net`, `gross`, `cbm` - Shipping metrics

### Backup & Recovery

- **Automatic Backups**: Available through web interface
- **Export Options**: CSV, Excel, JSON formats
- **Data Integrity**: Transaction-based updates
- **Soft Deletes**: Voided invoices retained for audit

## 🎨 Customization

### Adding New Templates

1. Create Excel template in `invoice_gen/TEMPLATE/`
2. Add corresponding config JSON in `invoice_gen/config/`
3. Update `create_json/config.py` for data mapping
4. Test with sample data

### Extending Web Interface

- Add new pages in `pages/` directory
- Follow naming convention: `N_Page_Name.py`
- Use existing database connection patterns
- Implement consistent UI styling

## 🔍 Troubleshooting

### Common Issues

**Excel Processing Fails**
- Check header mapping in `create_json/config.py`
- Verify Excel file format and structure
- Review error logs in failed_invoices folder

**Template Not Found**
- Ensure template filename matches prefix
- Verify config file exists with correct naming
- Check file permissions

**Database Errors**
- Verify SQLite file permissions
- Check disk space availability
- Review data types and constraints

### Logging

All operations are logged with timestamps. Check console output for detailed error information during processing.

## 📈 Analytics & Reporting

The dashboard provides:
- **Revenue Tracking**: Total amounts by time period
- **Volume Metrics**: Square footage and piece counts
- **Product Analysis**: Top-performing items
- **Trend Visualization**: Monthly/quarterly patterns
- **Export Capabilities**: Filtered data extraction

## 🔒 Security Notes

- Database files stored locally
- No external network dependencies
- Sensitive operations require confirmation
- Audit trail maintained for all changes
- Backup functionality for data protection

## 📞 Support

For issues or enhancements:
1. Check troubleshooting section
2. Review error logs
3. Verify configuration files
4. Test with sample data

---

*Built for efficient leather industry invoice management with focus on automation, accuracy, and user experience.*