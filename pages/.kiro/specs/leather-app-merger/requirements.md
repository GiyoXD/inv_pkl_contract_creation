# Requirements Document

## Introduction

This feature involves merging two separate Streamlit applications for leather invoice processing into a single unified application with a tabbed interface. The current system has two separate scripts: one for high quality leather processing and another for 2nd layer leather processing. Both applications share similar functionality but have different processing workflows and UI elements. The goal is to create a single, cohesive application that provides both processing options through an intuitive tabbed interface while maintaining all existing functionality.

## Requirements

### Requirement 1

**User Story:** As a user processing leather invoices, I want to access both high quality and 2nd layer leather processing from a single application, so that I can efficiently handle different types of leather processing without switching between separate applications.

#### Acceptance Criteria

1. WHEN the application loads THEN the system SHALL display a tabbed interface with two tabs: "High Quality Leather" and "2nd Layer Leather"
2. WHEN I click on either tab THEN the system SHALL display the appropriate processing interface for that leather type
3. WHEN I switch between tabs THEN the system SHALL preserve my work in progress on each tab independently
4. WHEN I upload a file in one tab THEN it SHALL NOT affect the state of the other tab

### Requirement 2

**User Story:** As a user processing high quality leather invoices, I want all the existing functionality from the original high quality leather script, so that my workflow remains unchanged.

#### Acceptance Criteria

1. WHEN I select the "High Quality Leather" tab THEN the system SHALL provide automatic Excel processing and validation
2. WHEN I upload an Excel file THEN the system SHALL automatically process it using the `run_invoice_automation` function
3. WHEN processing is complete THEN the system SHALL display validation results and missing field warnings
4. WHEN I provide invoice overrides THEN the system SHALL allow me to specify invoice number, reference, date, and container information
5. WHEN I select invoice versions THEN the system SHALL offer Normal, FOB, and Combine versions
6. WHEN I generate invoices THEN the system SHALL create the selected versions and provide a ZIP download

### Requirement 3

**User Story:** As a user processing 2nd layer leather invoices, I want all the existing functionality from the original 2nd layer leather script, so that my workflow remains unchanged.

#### Acceptance Criteria

1. WHEN I select the "2nd Layer Leather" tab THEN the system SHALL provide manual invoice detail entry
2. WHEN I upload an Excel file THEN the system SHALL require me to enter invoice reference, date, and unit price
3. WHEN I process the file THEN the system SHALL use the `Second_Layer(main).py` script for JSON creation
4. WHEN processing is complete THEN the system SHALL display an invoice summary with metrics
5. WHEN documents are generated THEN the system SHALL use the `hybrid_generate_invoice.py` script
6. WHEN processing is complete THEN the system SHALL provide a ZIP download with all generated documents

### Requirement 4

**User Story:** As a system administrator, I want the merged application to use shared database and helper functions, so that data consistency is maintained and code duplication is minimized.

#### Acceptance Criteria

1. WHEN the application initializes THEN the system SHALL use a single database initialization function for both tabs
2. WHEN checking for existing invoice references THEN the system SHALL use shared database query functions
3. WHEN suggesting invoice references THEN the system SHALL use a common function that works for both leather types
4. WHEN performing file cleanup THEN the system SHALL use shared cleanup functions
5. WHEN handling temporary files THEN the system SHALL use common directory structures and file management

### Requirement 5

**User Story:** As a user, I want the application to have a clean and intuitive interface, so that I can easily understand which processing type to use and navigate between them.

#### Acceptance Criteria

1. WHEN the application loads THEN the system SHALL display a clear title indicating it's a unified leather processing application
2. WHEN I view the tabs THEN the system SHALL clearly label them as "High Quality Leather Processing" and "2nd Layer Leather Processing"
3. WHEN I'm in either tab THEN the system SHALL display appropriate headers and instructions specific to that processing type
4. WHEN I switch tabs THEN the system SHALL maintain consistent styling and layout patterns
5. WHEN errors occur THEN the system SHALL display them in a consistent manner across both tabs

### Requirement 6

**User Story:** As a developer maintaining the system, I want the merged application to have clean, maintainable code structure, so that future updates and bug fixes can be applied efficiently.

#### Acceptance Criteria

1. WHEN reviewing the code THEN the system SHALL have shared functions extracted into common utilities
2. WHEN examining the tab implementations THEN each tab SHALL be implemented as a separate function
3. WHEN looking at database operations THEN they SHALL be consolidated into shared helper functions
4. WHEN checking file operations THEN they SHALL use common path configurations and error handling
5. WHEN reviewing the main application flow THEN it SHALL use clear separation between shared initialization and tab-specific logic