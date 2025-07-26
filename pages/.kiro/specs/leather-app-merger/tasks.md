# Implementation Plan

- [x] 1. Create shared utility modules and database manager





  - Extract common database operations into a DatabaseManager class
  - Create FileManager class for shared file operations
  - Implement common utility functions for validation and error handling
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 6.3, 6.4_

- [x] 2. Set up unified application structure with tab framework





  - Create main application file with Streamlit tab configuration
  - Implement shared initialization logic for paths and database
  - Set up session state management with tab-specific prefixes
  - Create basic tab structure with placeholder content
  - _Requirements: 1.1, 1.2, 5.1, 5.2, 6.5_

- [ ] 3. Implement High Quality Leather tab functionality
  - [x] 3.1 Create file upload and auto-processing workflow





    - Implement file upload component with validation
    - Integrate existing `run_invoice_automation` function
    - Add automatic JSON validation and missing field detection
    - Implement session state management for validation results
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.2 Build invoice overrides interface





    - Create form inputs for invoice number, reference, and date
    - Add container/truck information text area
    - Implement real-time database validation for duplicates
    - Add suggested invoice reference generation
    - _Requirements: 2.4_

  - [ ] 3.3 Implement invoice version selection and generation
    - Create checkboxes for Normal, FOB, and Combine versions
    - Integrate existing invoice generation scripts
    - Add incoterm detection from templates
    - Implement ZIP file creation and download functionality
    - _Requirements: 2.5, 2.6_

- [ ] 4. Implement 2nd Layer Leather tab functionality
  - [ ] 4.1 Create manual file upload and invoice details form
    - Implement file upload component
    - Create form inputs for invoice reference, date, and unit price
    - Add real-time database validation
    - Implement suggested invoice reference functionality
    - _Requirements: 3.1, 3.2_

  - [ ] 4.2 Build processing workflow and JSON manipulation
    - Integrate `Second_Layer(main).py` script execution
    - Implement `update_and_aggregate_json` function
    - Add PO number extraction and fallback logic
    - Handle Cambodia timezone for creating_date field
    - _Requirements: 3.3_

  - [ ] 4.3 Create invoice summary display and document generation
    - Build comprehensive invoice summary with metrics display
    - Integrate `hybrid_generate_invoice.py` script execution
    - Implement temporary directory management for document generation
    - Add ZIP file creation and download functionality
    - _Requirements: 3.4, 3.5, 3.6_

- [ ] 5. Implement shared helper functions and error handling
  - Create centralized error handling with consistent formatting
  - Implement shared file cleanup and temporary file management
  - Add common validation functions for both tabs
  - Create shared ZIP file creation utility
  - _Requirements: 4.1, 4.4, 4.5, 6.1, 6.2_

- [ ] 6. Add session state isolation and tab switching logic
  - Implement tab-specific session state prefixes (hq_ and sl_)
  - Ensure independent state management between tabs
  - Add state preservation when switching tabs
  - Implement proper cleanup when tabs are reset
  - _Requirements: 1.3, 1.4, 6.2_

- [ ] 7. Integrate database operations and optimize performance
  - Consolidate database initialization into shared function
  - Implement optimized query functions with proper indexing
  - Add connection error handling and graceful degradation
  - Create shared invoice reference suggestion logic
  - _Requirements: 4.1, 4.2, 4.3, 6.3_

- [ ] 8. Implement consistent UI styling and user experience
  - Apply consistent headers and styling across both tabs
  - Add clear instructions and help text for each processing type
  - Implement consistent error message formatting
  - Add loading spinners and progress indicators
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 9. Add comprehensive error handling and validation
  - Implement try-catch blocks around all subprocess calls
  - Add file validation for uploaded Excel files
  - Create user-friendly error messages with troubleshooting hints
  - Add input sanitization and validation for all form fields
  - _Requirements: 4.4, 5.5, 6.4_

- [ ] 10. Create unified main application file
  - Combine all components into single main application
  - Implement proper import structure and path management
  - Add application-wide configuration and constants
  - Create main function with tab routing logic
  - _Requirements: 1.1, 1.2, 5.1, 6.5_

- [ ] 11. Test tab independence and cross-functionality
  - Write tests to verify session state isolation between tabs
  - Test file upload and processing in both tabs simultaneously
  - Verify database operations work correctly across tabs
  - Test error handling and recovery in both tabs
  - _Requirements: 1.3, 1.4, 4.1, 4.2_

- [ ] 12. Optimize performance and add cleanup mechanisms
  - Implement efficient file cleanup for temporary files
  - Add memory optimization for large file processing
  - Create automatic cleanup on application restart
  - Add performance monitoring for database operations
  - _Requirements: 4.4, 4.5, 6.4_