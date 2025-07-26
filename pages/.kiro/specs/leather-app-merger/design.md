# Design Document

## Overview

The unified leather processing application will be built using Streamlit's tab functionality to provide a clean, intuitive interface for both high quality and 2nd layer leather processing. The design focuses on code reusability, maintainability, and preserving all existing functionality while creating a better user experience through a single application entry point.

## Architecture

### High-Level Structure
```
Unified Leather Processing App
├── Shared Initialization
│   ├── Database Setup
│   ├── Path Configuration
│   └── Common Imports
├── Shared Helper Functions
│   ├── Database Operations
│   ├── File Management
│   └── Validation Functions
├── Tab 1: High Quality Leather Processing
│   ├── File Upload & Auto-Processing
│   ├── Validation Display
│   ├── Invoice Overrides
│   └── Multi-Version Generation
└── Tab 2: 2nd Layer Leather Processing
    ├── File Upload
    ├── Manual Invoice Details
    ├── Processing & Summary
    └── Document Generation
```

### Session State Management
Each tab will maintain independent session state using prefixed keys:
- High Quality tab: `hq_*` prefix (e.g., `hq_validation_done`, `hq_json_path`)
- 2nd Layer tab: `sl_*` prefix (e.g., `sl_processing_complete`, `sl_summary_data`)

## Components and Interfaces

### 1. Shared Components

#### Database Manager
```python
class DatabaseManager:
    def __init__(self, db_file: Path)
    def initialize_database() -> bool
    def check_existing_identifiers(inv_no: str, inv_ref: str) -> dict
    def get_suggested_inv_ref() -> str
```

#### File Manager
```python
class FileManager:
    def __init__(self, project_root: Path)
    def setup_directories()
    def cleanup_old_files(directories: list, max_age_seconds: int)
    def save_uploaded_file(uploaded_file, temp_dir: Path) -> Path
```

#### Common Utilities
```python
def find_incoterm_from_template(identifier: str) -> str
def create_zip_download(files: list, filename: str) -> bytes
def display_error_with_details(error: Exception, context: str)
```

### 2. High Quality Leather Tab

#### Processing Pipeline
1. **File Upload & Auto-Processing**
   - Uses `run_invoice_automation()` from existing script
   - Automatic validation with `validate_json_data()`
   - Session state: `hq_validation_done`, `hq_json_path`, `hq_missing_fields`

2. **Invoice Overrides Interface**
   - Invoice number, reference, date inputs
   - Container/truck information text area
   - Real-time validation against database

3. **Version Selection & Generation**
   - Checkboxes for Normal, FOB, Combine versions
   - Uses existing `generate_invoice.py` script
   - Incoterm detection from templates

#### Key Functions
```python
def render_high_quality_tab():
    def reset_hq_workflow_state()
    def process_hq_excel_file(uploaded_file)
    def render_hq_overrides_section()
    def generate_hq_invoices(selected_versions)
```

### 3. 2nd Layer Leather Tab

#### Processing Pipeline
1. **File Upload**
   - Simple file uploader without auto-processing
   - Manual invoice details entry required

2. **Invoice Details Form**
   - Invoice reference (with suggestion)
   - Invoice date picker
   - Unit price input
   - Real-time database validation

3. **Processing & Summary**
   - Uses `Second_Layer(main).py` for JSON creation
   - Uses `hybrid_generate_invoice.py` for document generation
   - Displays comprehensive invoice summary

#### Key Functions
```python
def render_second_layer_tab():
    def process_sl_excel_file(uploaded_file, inv_ref, inv_date, unit_price)
    def update_and_aggregate_json(json_path, inv_ref, inv_date, unit_price, po_number)
    def render_sl_summary(summary_data)
    def generate_sl_documents(json_path)
```

## Data Models

### Session State Schema
```python
# Shared state
{
    "db_enabled": bool,
    "PROJECT_ROOT": Path,
    "DATABASE_FILE": Path,
    # ... other shared paths
}

# High Quality tab state
{
    "hq_validation_done": bool,
    "hq_json_path": str,
    "hq_missing_fields": list,
    "hq_identifier": str
}

# 2nd Layer tab state
{
    "sl_processing_complete": bool,
    "sl_summary_data": dict,
    "sl_final_json_path": Path
}
```

### Database Schema (Unchanged)
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inv_no TEXT,
    inv_date TEXT,
    inv_ref TEXT UNIQUE,
    po TEXT,
    item TEXT,
    description TEXT,
    pcs TEXT,
    sqft TEXT,
    pallet_count TEXT,
    unit TEXT,
    amount TEXT,
    net TEXT,
    gross TEXT,
    cbm TEXT,
    production_order_no TEXT,
    creating_date TEXT,
    status TEXT DEFAULT 'active'
);

CREATE TABLE invoice_containers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inv_ref TEXT NOT NULL,
    container_description TEXT NOT NULL,
    FOREIGN KEY (inv_ref) REFERENCES invoices (inv_ref)
);
```

## Error Handling

### Centralized Error Management
```python
def handle_processing_error(error: Exception, tab_name: str, step: str):
    """Centralized error handling with consistent formatting"""
    st.error(f"Error in {tab_name} - {step}: {str(error)}")
    with st.expander("Error Details"):
        st.exception(error)
```

### Tab-Specific Error Recovery
- **High Quality Tab**: Reset validation state, preserve user inputs
- **2nd Layer Tab**: Clear processing state, maintain form data

### Database Error Handling
- Connection failures: Graceful degradation with warnings
- Constraint violations: User-friendly messages with suggestions
- Performance issues: Timeout handling with retry options

## Testing Strategy

### Unit Testing
1. **Shared Components**
   - Database operations with mock database
   - File management functions with temporary directories
   - Validation functions with sample data

2. **Tab-Specific Functions**
   - High Quality processing pipeline with mock subprocess calls
   - 2nd Layer JSON manipulation with sample files
   - UI rendering functions with Streamlit testing framework

### Integration Testing
1. **Cross-Tab Functionality**
   - Session state isolation between tabs
   - Database consistency across tab operations
   - File system operations coordination

2. **End-to-End Workflows**
   - Complete High Quality processing workflow
   - Complete 2nd Layer processing workflow
   - Tab switching with active processes

### Performance Testing
1. **Database Operations**
   - Index performance with large datasets
   - Concurrent access simulation
   - Query optimization validation

2. **File Processing**
   - Large Excel file handling
   - Memory usage during ZIP creation
   - Temporary file cleanup efficiency

## Implementation Phases

### Phase 1: Foundation
- Extract shared components from existing scripts
- Create unified database manager
- Set up basic tab structure

### Phase 2: High Quality Tab
- Migrate existing high quality functionality
- Implement session state management
- Add error handling and validation

### Phase 3: 2nd Layer Tab
- Migrate existing 2nd layer functionality
- Implement manual processing workflow
- Add summary display and document generation

### Phase 4: Integration & Polish
- Cross-tab testing and bug fixes
- UI/UX improvements and consistency
- Performance optimization and cleanup

## Security Considerations

### File Upload Security
- File type validation (XLSX only)
- File size limits
- Temporary file cleanup
- Path traversal prevention

### Database Security
- SQL injection prevention through parameterized queries
- Input sanitization for all user inputs
- Connection security and timeout handling

### Process Security
- Subprocess execution with controlled environments
- Environment variable isolation
- Error message sanitization to prevent information disclosure