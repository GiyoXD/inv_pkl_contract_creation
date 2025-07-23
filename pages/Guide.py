import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="User Guide",
    page_icon="📖",
    layout="wide"
)

# --- Language Selection ---
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    language = st.selectbox(
        "🌐 Language / ភាសា / 语言",
        options=["English", "ខ្មែរ (Khmer)", "中文 (Chinese)"],
        index=0
    )

# --- Translation Dictionary ---
translations = {
    "English": {
        "title": "📖 Invoice Management System - User Guide",
        "tab1": "🏠 Getting Started",
        "tab2": "📊 Dashboard", 
        "tab3": "➕ Adding Invoices",
        "tab4": "✏️ Managing Data",
        "tab5": "🔧 Header Mapping",
        "tab6": "❓ Troubleshooting",
        "welcome_title": "🏠 Welcome to the Invoice Management System",
        "what_is_system": "### What is this system?",
        "system_desc": "This is an **automated invoice processing system** designed specifically for leather industry businesses. It helps you convert Excel files into professional invoices and manage your invoice database.",
        "what_can_do": "### What can it do for you?",
        "features": [
            "📄 **Convert Excel files** into professional invoices automatically",
            "📊 **Track your business** with dashboard analytics", 
            "💾 **Store all invoices** in an organized database",
            "📈 **Generate reports** and view business trends",
            "✏️ **Edit and manage** invoice data easily"
        ],
        "who_for": "🎯 Who is this for?",
        "who_list": [
            "**Business owners** managing leather exports",
            "**Accounting staff** processing invoices", 
            "**Sales teams** tracking orders",
            "**Anyone** who needs to convert Excel data to invoices"
        ],
        "benefits": "⚡ Key Benefits",
        "benefits_list": [
            "**Save time** - No manual invoice creation",
            "**Reduce errors** - Automated calculations",
            "**Stay organized** - All data in one place", 
            "**Track performance** - Built-in analytics"
        ],
        "quick_start": "🚀 Quick Start - 3 Simple Steps",
        "step1_title": "### Step 1: Prepare Your Excel File",
        "step1_desc": "- Use your existing Excel format\n- Make sure it has columns like:\n  - PO Number\n  - Item Code\n  - Quantity\n  - Price\n  - Amount",
        "step2_title": "### Step 2: Upload & Process", 
        "step2_desc": "- Go to the appropriate page:\n  - \"High Quality Leather\" for premium products\n  - \"2nd Layer Leather\" for secondary products\n- Upload your Excel file\n- Click \"Process\"",
        "step3_title": "### Step 3: Review & Approve",
        "step3_desc": "- Check the \"Verify\" page\n- Review the processed data\n- Click \"Accept\" to add to database\n- Your invoices are ready!",
        "dashboard_title": "📊 Understanding the Dashboard",
        "dashboard_desc": "The **Dashboard** is your main control center. Here's what you'll see:",
        "key_metrics": "📈 Key Metrics",
        "metrics_list": [
            "**Total Invoiced Amount** - Your total revenue",
            "**Total Square Feet** - Total product quantity", 
            "**Unique Invoices** - Number of invoices processed"
        ],
        "date_filtering": "📅 Date Filtering",
        "date_filter_list": [
            "Use the date picker to filter data",
            "View specific time periods",
            "Compare different months/quarters"
        ],
        "charts_graphs": "📊 Charts & Graphs",
        "charts_list": [
            "**Monthly Revenue** - See your income trends",
            "**Top Products** - Best-selling items",
            "**Performance Tracking** - Business growth"
        ],
        "what_to_look": "🔍 What to Look For",
        "look_for_list": [
            "**Growing trends** - Increasing revenue",
            "**Top performers** - Best products", 
            "**Seasonal patterns** - Busy periods"
        ],
        # Tab 3 - Adding Invoices
        "adding_invoices_title": "➕ Adding New Invoices",
        "adding_desc": "There are **two ways** to add invoices to the system:",
        "method1_title": "Method 1: Using the Web Forms",
        "high_quality_steps": "#### For High Quality Leather:",
        "high_quality_list": [
            "Click \"**High Quality Leather**\" in the sidebar",
            "Upload your Excel file",
            "Fill in any additional information",
            "Click \"**Process File**\"",
            "Wait for processing to complete"
        ],
        "second_layer_steps": "#### For 2nd Layer Leather:",
        "second_layer_list": [
            "Click \"**2nd Layer Leather**\" in the sidebar",
            "Upload your Excel file", 
            "Fill in any additional information",
            "Click \"**Process File**\"",
            "Wait for processing to complete"
        ],
        "method2_title": "Method 2: Direct File Processing",
        "method2_list": [
            "Place your Excel file in the system folder",
            "Run the automation command",
            "Check \"**Verify**\" page",
            "Review and approve the data"
        ],
        "verification_title": "📋 Data Verification Process",
        "verification_desc": "After processing, you'll need to **verify your data**:",
        "verification_steps": [
            "Go to \"**Verify**\" page",
            "You'll see a preview of your data",
            "Check that all information is correct:",
            "- PO numbers",
            "- Item codes", 
            "- Quantities",
            "- Prices",
            "- Amounts",
            "If everything looks good, click \"**✅ Accept**\"",
            "If there are errors, click \"**❌ Reject**\" and fix your Excel file"
        ],
        "tip_message": "💡 **Tip**: Always double-check your data before accepting. Once accepted, the data goes into your permanent database.",
        # Tab 4 - Managing Data
        "managing_data_title": "✏️ Managing Your Invoice Data",
        "viewing_database": "🔍 Viewing Your Database",
        "viewing_desc": "The \"**Database**\" page lets you:",
        "viewing_features": [
            "See all your invoices",
            "Filter by date, PO number, or item",
            "Search for specific records",
            "Export data to Excel"
        ],
        "editing_invoices": "✏️ Editing Invoices",
        "editing_desc": "To edit an existing invoice:",
        "editing_steps": [
            "Go to \"**Edit Invoice**\" page",
            "Search for the invoice by:",
            "- Invoice Number, or",
            "- Invoice Reference",
            "Select the invoice from the list",
            "Make your changes in the data editor",
            "Update container/truck information if needed",
            "Click \"**💾 Save Changes**\""
        ],
        "voiding_invoices": "🗑️ Voiding Invoices",
        "voiding_desc": "To void (cancel) an invoice:",
        "voiding_steps": [
            "Go to \"**Void Invoice**\" page",
            "Search for the invoice",
            "Select it from the list",
            "Click \"**Void Invoice**\"",
            "Confirm your action"
        ],
        "voiding_note": "**Note**: Voided invoices are not deleted, just marked as inactive.",
        "backup_export": "💾 Backup & Export",
        "backup_title": "#### Creating Backups:",
        "backup_steps": [
            "Go to \"**Backup Database**\"",
            "Click \"**Create Backup**\"",
            "Your data is safely stored",
            "Keep backups regularly!"
        ],
        "export_title": "#### Exporting Data:",
        "export_steps": [
            "Go to \"**Export Data**\"",
            "Choose your filters",
            "Select export format",
            "Download your file"
        ],
        # Tab 5 - Troubleshooting
        "troubleshooting_title": "❓ Troubleshooting & FAQ",
        "common_issues": "🚨 Common Issues",
        "issue0_title": "🔧 MOST COMMON: Headers not recognized",
        "issue0_desc": "**90% of problems are caused by incorrect column headers!**",
        "issue0_solution": "**SOLUTION: Go to Header Mapping tab and use these exact headers:**",
        "issue0_headers": [
            "'po' for PO numbers",
            "'item' for item codes", 
            "'pcs' for quantities",
            "'unit' for unit prices",
            "'amount' for total amounts",
            "'sqft' for square feet"
        ],
        "issue1_title": "❌ My Excel file won't process",
        "issue1_causes": "**Possible causes:**",
        "issue1_cause_list": [
            "Excel file format is not supported (use .xlsx)",
            "❗ **MOST COMMON**: Wrong column headers - system can't find your data!",
            "Missing required columns (PO, Item, Amount, etc.)",
            "Data in wrong format (text in number columns)"
        ],
        "issue1_solutions": "**Solutions:**",
        "issue1_solution_list": [
            "Save your file as .xlsx format",
            "🔧 **CHECK HEADER MAPPING TAB FIRST** - Fix your column headers!",
            "Use simple headers like: 'po', 'item', 'pcs', 'unit', 'amount', 'sqft'",
            "Make sure numbers are formatted as numbers, not text"
        ],
        "issue2_title": "⏳ Processing is taking too long",
        "issue2_causes": "**This can happen when:**",
        "issue2_cause_list": [
            "Excel file is very large",
            "File has many empty rows",
            "Complex formulas in the Excel file"
        ],
        "issue2_solutions": "**Solutions:**",
        "issue2_solution_list": [
            "Remove empty rows from your Excel file",
            "Copy data to a new, clean Excel file",
            "Contact support if problem persists"
        ],
        "issue3_title": "🔍 I can't find my invoice",
        "issue3_causes": "**Check these things:**",
        "issue3_cause_list": [
            "Is the invoice actually in the database? (Check \"Database\")",
            "Are you searching with the correct reference number?",
            "Has the invoice been voided?",
            "Check your date filters"
        ],
        "issue4_title": "💾 My data disappeared",
        "issue4_desc": "**Don't panic! Your data might be:**",
        "issue4_cause_list": [
            "Filtered out (check your date/search filters)",
            "In a different status (check voided invoices)",
            "In a backup file"
        ],
        "issue4_recovery": "**Recovery steps:**",
        "issue4_recovery_list": [
            "Clear all filters in \"Database\"",
            "Check \"Backup Database\" for recent backups",
            "Contact your system administrator"
        ],
        "issue5_title": "🚫 No data processed / Empty results",
        "issue5_desc": "**Excel file uploads but no invoices are created:**",
        "issue5_cause_list": [
            "❗ **#1 REASON**: Column headers don't match system expectations",
            "System can't find PO, Item, Amount, or other critical columns",
            "Headers in wrong language or format",
            "Typos in column names"
        ],
        "issue5_solutions": "**SOLUTION:**",
        "issue5_solution_list": [
            "🔧 **GO TO HEADER MAPPING TAB** - This fixes 90% of issues!",
            "Use the EASIEST headers: 'po', 'item', 'pcs', 'unit', 'amount', 'sqft'",
            "Check your Excel headers match the examples exactly",
            "If still failing, try the alternative headers listed in Header Mapping tab"
        ],
        "getting_help": "📞 Getting Help",
        "before_help": "#### Before Asking for Help:",
        "before_help_list": [
            "🔧 **CHECK HEADER MAPPING TAB FIRST** - Solves most problems!",
            "Verify your Excel headers match the system requirements",
            "Try restarting the application",
            "Check if your Excel file works with other data",
            "Note any error messages you see"
        ],
        "when_contacting": "#### When Contacting Support:",
        "when_contacting_list": [
            "Describe what you were trying to do",
            "Share any error messages",
            "Mention which file you were processing",
            "Include screenshots if helpful"
        ],
        "pro_tips": "💡 Pro Tips for Success",
        "excel_tips": "#### Excel File Tips:",
        "excel_tips_list": [
            "Keep files clean and organized",
            "Use consistent column names",
            "Remove empty rows",
            "Save as .xlsx format"
        ],
        "data_tips": "#### Data Management:",
        "data_tips_list": [
            "Create backups regularly",
            "Review data before accepting",
            "Use clear, consistent naming",
            "Keep original Excel files"
        ],
        "system_tips": "#### System Usage:",
        "system_tips_list": [
            "Process files during off-peak hours",
            "Don't close browser during processing",
            "Check dashboard regularly",
            "Export important reports"
        ],
        # Tab 5 - Header Mapping
        "header_mapping_title": "🔧 Excel Header Mapping Guide",
        "header_mapping_desc": "⚠️ **CRITICAL**: Without proper header mapping, NO DATA will flow through to create invoices! Use this guide to ensure your Excel headers match exactly what the system expects.",
        "what_is_mapping": "### What is Header Mapping?",
        "mapping_desc": "The system needs to identify which columns in your Excel file contain specific data (like PO numbers, quantities, etc.). Sometimes your column names might be different from what the system expects.",
        "required_headers": "📋 Required Headers & Their Mappings",
        "required_headers_desc": "Your Excel file must contain these data types. Here are the **actual mappings from the system** - use the EASIEST option first:",
        "header_mappings": [
            "**PO Number** → EASIEST: 'po' | Also accepts: 'PO', 'PO NO.', '订单号'",
            "**Item Code** → EASIEST: 'item' | Also accepts: '物料代码', 'ITEM NO.', 'Item No'",
            "**Pieces/Quantity** → EASIEST: 'pcs' | Also accepts: 'PCS', '总张数', '张数'",
            "**Unit Price** → EASIEST: 'unit' | Also accepts: 'USD', '单价', 'price'",
            "**Total Amount** → EASIEST: 'amount' | Also accepts: '金额', 'USD', 'total'",
            "**Square Feet** → EASIEST: 'sqft' | Also accepts: 'SF', '尺数', '出货数量(sf)'",
            "**Net Weight** → EASIEST: 'net' | Also accepts: 'NW', '净重', 'net weight'",
            "**Gross Weight** → EASIEST: 'gross' | Also accepts: 'GW', '毛重', 'Gross'",
            "**Description** → EASIEST: 'description' | Also accepts: '产品名称', '品名规格', 'desc'",
            "**CBM/Remarks** → EASIEST: 'cbm' | Also accepts: '材积', 'CBM', '备注'",
            "**Production Order** → EASIEST: 'production_order_no' | Also accepts: 'TTX编号', '生产单号'"
        ],
        "common_issues_mapping": "⚠️ Common Header Issues",
        "mapping_issues": [
            "**Different Language**: Headers in local language (Khmer, Chinese, etc.)",
            "**Abbreviations**: Using non-standard abbreviations",
            "**Extra Spaces**: Headers with leading/trailing spaces",
            "**Special Characters**: Headers with symbols or punctuation",
            "**Merged Cells**: Headers spanning multiple cells"
        ],
        "solutions_title": "✅ Solutions When Headers Don't Match",
        "solution_option1": "#### Option 1: Edit Your Excel File (Recommended)",
        "solution1_steps": [
            "Open your Excel file",
            "Rename column headers to the EASIEST options above",
            "Examples: '订单号' → 'po', '物料代码' → 'item', '总张数' → 'pcs'",
            "Use simple lowercase English words when possible",
            "Save the file and try processing again"
        ],
        "solution_option2": "#### Option 2: Report to Administrator",
        "solution2_steps": [
            "Take a screenshot of your Excel headers",
            "Note which columns contain which data",
            "Contact your system administrator with:",
            "- Screenshot of your Excel file headers",
            "- Description of what data each column contains",
            "- Request to add your header names to the system mapping"
        ],
        "example_mapping": "📝 Example Header Mapping",
        "example_desc": "Here's an example of how to map common variations:",
        "example_table": [
            "**Your Header** → **EASIEST Change** → **What It Maps To**",
            "'订单号' → 'po' → PO Number (CRITICAL for invoices)",
            "'物料代码' → 'item' → Item Code (CRITICAL for invoices)",
            "'总张数' → 'pcs' → Pieces/Quantity (CRITICAL for invoices)",
            "'单价' → 'unit' → Unit Price (CRITICAL for invoices)",
            "'金额' → 'amount' → Total Amount (CRITICAL for invoices)",
            "'出货数量(sf)' → 'sqft' → Square Feet (CRITICAL for invoices)",
            "'净重' → 'net' → Net Weight",
            "'毛重' → 'gross' → Gross Weight",
            "'TTX编号' → 'production_order_no' → Production Order",
            "'材积' → 'cbm' → CBM/Remarks"
        ],
        "best_practices_headers": "💡 Best Practices for Excel Headers",
        "header_best_practices": [
            "**Use English names** when possible for better compatibility",
            "**Keep headers simple** - avoid special characters",
            "**Be consistent** - use the same header names across all files",
            "**No empty columns** between data columns",
            "**First row only** - put headers in the first row of your Excel file"
        ],
        "admin_contact": "📞 Need Help with Mapping?",
        "admin_help": [
            "If you frequently use Excel files with non-standard headers:",
            "Contact your administrator to add your header variations to the system",
            "Provide examples of your typical Excel file formats",
            "The admin can configure the system to recognize your specific header names"
        ]
    },
    "ខ្មែរ (Khmer)": {
        "title": "📖 ប្រព័ន្ធគ្រប់គ្រងវិក្កយបត្រ - មគ្គុទ្దេសក៍ការប្រើប្រាស់",
        "tab1": "🏠 ការចាប់ផ្តើម",
        "tab2": "📊 ផ្ទាំងគ្រប់គ្រង",
        "tab3": "➕ បន្ថែមវិក្កយបត្រ", 
        "tab4": "✏️ គ្រប់គ្រងទិន្នន័យ",
        "tab5": "🔧 Header Mapping",
        "tab6": "❓ ដោះស្រាយបញ្ហា",
        "welcome_title": "🏠 សូមស្វាគមន៍មកកាន់ប្រព័ន្ធគ្រប់គ្រងវិក្កយបត្រ",
        "what_is_system": "### ប្រព័ន្ធនេះជាអ្វី?",
        "system_desc": "នេះគឺជា **ប្រព័ន្ធដំណើរការវិក្កយបត្រស្វ័យប្រវត្តិ** ដែលត្រូវបានរចនាឡើងជាពិសេសសម្រាប់អាជីវកម្មឧស្សាហកម្មស្បែក។ វាជួយអ្នកបំប្លែងឯកសារ Excel ទៅជាវិក្កយបត្រអាជីព និងគ្រប់គ្រងមូលដ្ឋានទិន្នន័យវិក្កយបត្ររបស់អ្នក។",
        "what_can_do": "### វាអាចធ្វើអ្វីសម្រាប់អ្នក?",
        "features": [
            "📄 **បំប្លែងឯកសារ Excel** ទៅជាវិក្កយបត្រអាជីពដោយស្វ័យប្រវត្តិ",
            "📊 **តាមដានអាជីវកម្មរបស់អ្នក** ជាមួយការវិភាគផ្ទាំងគ្រប់គ្រង",
            "💾 **រក្សាទុកវិក្កយបត្រទាំងអស់** នៅក្នុងមូលដ្ឋានទិន្នន័យដែលបានរៀបចំ",
            "📈 **បង្កើតរបាយការណ៍** និងមើលនិន្នាការអាជីវកម្ម",
            "✏️ **កែសម្រួល និងគ្រប់គ្រង** ទិន្នន័យវិក្កយបត្រយ៉ាងងាយស្រួល"
        ],
        "who_for": "🎯 សម្រាប់នរណា?",
        "who_list": [
            "**ម្ចាស់អាជីវកម្ម** ដែលគ្រប់គ្រងការនាំចេញស្បែក",
            "**បុគ្គលិកគណនេយ្យ** ដែលដំណើរការវិក្កយបត្រ",
            "**ក្រុមលក់** ដែលតាមដានការបញ្ជាទិញ",
            "**នរណាម្នាក់** ដែលត្រូវការបំប្លែងទិន្នន័យ Excel ទៅជាវិក្កយបត្រ"
        ],
        "benefits": "⚡ អត្ថប្រយោជន៍សំខាន់",
        "benefits_list": [
            "**សន្សំពេលវេលា** - មិនចាំបាច់បង្កើតវិក្កយបត្រដោយដៃ",
            "**កាត់បន្ថយកំហុស** - ការគណនាស្វ័យប្រវត្តិ",
            "**រៀបចំបានល្អ** - ទិន្នន័យទាំងអស់នៅកន្លែងតែមួយ",
            "**តាមដានការអនុវត្ត** - ការវិភាគដែលបានបង្កប់"
        ],
        "quick_start": "🚀 ការចាប់ផ្តើមរហ័ស - ៣ជំហានសាមញ្ញ",
        "step1_title": "### ជំហានទី១៖ រៀបចំឯកសារ Excel របស់អ្នក",
        "step1_desc": "- ប្រើទម្រង់ Excel ដែលមានស្រាប់របស់អ្នក\n- ត្រូវប្រាកដថាវាមានជួរឈរដូចជា៖\n  - លេខ PO\n  - កូដទំនិញ\n  - បរិមាណ\n  - តម្លៃ\n  - ចំនួនទឹកប្រាក់",
        "step2_title": "### ជំហានទី២៖ ផ្ទុកឡើង និងដំណើរការ",
        "step2_desc": "- ទៅកាន់ទំព័រសមស្រប៖\n  - \"High Quality Leather\" សម្រាប់ផលិតផលពិសេស\n  - \"2nd Layer Leather\" សម្រាប់ផលិតផលបន្ទាប់បន្សំ\n- ផ្ទុកឯកសារ Excel របស់អ្នក\n- ចុច \"ដំណើរការ\"",
        "step3_title": "### ជំហានទី៣៖ ពិនិត្យ និងអនុម័ត",
        "step3_desc": "- ពិនិត្យទំព័រ \"Verify\"\n- ពិនិត្យទិន្នន័យដែលបានដំណើរការ\n- ចុច \"ទទួលយក\" ដើម្បីបន្ថែមទៅមូលដ្ឋានទិន្នន័យ\n- វិក្កយបត្ររបស់អ្នកត្រៀមរួចរាល់!",
        "dashboard_title": "📊 ការយល់ដឹងអំពីផ្ទាំងគ្រប់គ្រង",
        "dashboard_desc": "**ផ្ទាំងគ្រប់គ្រង** គឺជាមជ្ឈមណ្ឌលគ្រប់គ្រងសំខាន់របស់អ្នក។ នេះជាអ្វីដែលអ្នកនឹងឃើញ៖",
        "key_metrics": "📈 ម៉ែត្រិកសំខាន់",
        "metrics_list": [
            "**ចំនួនទឹកប្រាក់វិក្កយបត្រសរុប** - ប្រាក់ចំណូលសរុបរបស់អ្នក",
            "**ហ្វីតការ៉េសរុប** - បរិមាណផលិតផលសរុប",
            "**វិក្កយបត្រតែមួយ** - ចំនួនវិក្កយបត្រដែលបានដំណើរការ"
        ],
        "date_filtering": "📅 ការត្រងតាមកាលបរិច្ឆេទ",
        "date_filter_list": [
            "ប្រើឧបករណ៍ជ្រើសរើសកាលបរិច្ឆេទដើម្បីត្រងទិន្នន័យ",
            "មើលរយៈពេលជាក់លាក់",
            "ប្រៀបធៀបខែ/ត្រីមាសផ្សេងៗ"
        ],
        "charts_graphs": "📊 គំនូសតាង និងក្រាហ្វិក",
        "charts_list": [
            "**ប្រាក់ចំណូលប្រចាំខែ** - មើលនិន្នាការប្រាក់ចំណូលរបស់អ្នក",
            "**ផលិតផលកំពូល** - ទំនិញលក់ដាច់បំផុត",
            "**ការតាមដានការអនុវត្ត** - ការលូតលាស់អាជីវកម្ម"
        ],
        "what_to_look": "🔍 អ្វីដែលត្រូវមើល",
        "look_for_list": [
            "**និន្នាការកំណើន** - ប្រាក់ចំណូលកើនឡើង",
            "**អ្នកអនុវត្តកំពូល** - ផលិតផលល្អបំផុត",
            "**លំនាំតាមរដូវ** - រយៈពេលមមាញឹក"
        ],
        # Tab 3 - Adding Invoices
        "adding_invoices_title": "➕ បន្ថែមវិក្កយបត្រថ្មី",
        "adding_desc": "មាន **វិធីពីរ** ដើម្បីបន្ថែមវិក្កយបត្រទៅក្នុងប្រព័ន្ធ៖",
        "method1_title": "វិធីទី១៖ ប្រើប្រាស់ទម្រង់វេប",
        "high_quality_steps": "#### សម្រាប់ស្បែកគុណភាពខ្ពស់៖",
        "high_quality_list": [
            "ចុច \"**High Quality Leather**\" នៅក្នុងរបារចំហៀង",
            "ផ្ទុកឯកសារ Excel របស់អ្នក",
            "បំពេញព័ត៌មានបន្ថែមណាមួយ",
            "ចុច \"**ដំណើរការឯកសារ**\"",
            "រង់ចាំការដំណើរការឱ្យបញ្ចប់"
        ],
        "second_layer_steps": "#### សម្រាប់ស្បែកស្រទាប់ទី២៖",
        "second_layer_list": [
            "ចុច \"**2nd Layer Leather**\" នៅក្នុងរបារចំហៀង",
            "ផ្ទុកឯកសារ Excel របស់អ្នក",
            "បំពេញព័ត៌មានបន្ថែមណាមួយ",
            "ចុច \"**ដំណើរការឯកសារ**\"",
            "រង់ចាំការដំណើរការឱ្យបញ្ចប់"
        ],
        "method2_title": "វិធីទី២៖ ការដំណើរការឯកសារដោយផ្ទាល់",
        "method2_list": [
            "ដាក់ឯកសារ Excel របស់អ្នកនៅក្នុងថតប្រព័ន្ធ",
            "ដំណើរការពាក្យបញ្ជាស្វ័យប្រវត្តិ",
            "ពិនិត្យទំព័រ \"**Verify**\"",
            "ពិនិត្យ និងអនុម័តទិន្នន័យ"
        ],
        "verification_title": "📋 ដំណើរការផ្ទៀងផ្ទាត់ទិន្នន័យ",
        "verification_desc": "បន្ទាប់ពីការដំណើរការ អ្នកនឹងត្រូវ **ផ្ទៀងផ្ទាត់ទិន្នន័យរបស់អ្នក**៖",
        "verification_steps": [
            "ទៅកាន់ទំព័រ \"**Verify**\"",
            "អ្នកនឹងឃើញការមើលជាមុនទិន្នន័យរបស់អ្នក",
            "ពិនិត្យថាព័ត៌មានទាំងអស់ត្រឹមត្រូវ៖",
            "- លេខ PO",
            "- កូដទំនិញ",
            "- បរិមាណ",
            "- តម្លៃ",
            "- ចំនួនទឹកប្រាក់",
            "ប្រសិនបើអ្វីៗមើលទៅល្អ ចុច \"**✅ ទទួលយក**\"",
            "ប្រសិនបើមានកំហុស ចុច \"**❌ បដិសេធ**\" ហើយកែឯកសារ Excel របស់អ្នក"
        ],
        "tip_message": "💡 **ជំនួយ**: តែងតែពិនិត្យទិន្នន័យរបស់អ្នកឱ្យបានពេញលេញមុនពេលទទួលយក។ នៅពេលដែលបានទទួលយកហើយ ទិន្នន័យនឹងចូលទៅក្នុងមូលដ្ឋានទិន្នន័យអចិន្ត្រៃយ៍របស់អ្នក។",
        # Tab 4 - Managing Data
        "managing_data_title": "✏️ គ្រប់គ្រងទិន្នន័យវិក្កយបត្ររបស់អ្នក",
        "viewing_database": "🔍 មើលមូលដ្ឋានទិន្នន័យរបស់អ្នក",
        "viewing_desc": "ទំព័រ \"**Database**\" អនុញ្ញាតឱ្យអ្នក៖",
        "viewing_features": [
            "មើលវិក្កយបត្រទាំងអស់របស់អ្នក",
            "ត្រងតាមកាលបរិច្ឆេទ លេខ PO ឬទំនិញ",
            "ស្វែងរកកំណត់ត្រាជាក់លាក់",
            "នាំចេញទិន្នន័យទៅ Excel"
        ],
        "editing_invoices": "✏️ កែសម្រួលវិក្កយបត្រ",
        "editing_desc": "ដើម្បីកែសម្រួលវិក្កយបត្រដែលមានស្រាប់៖",
        "editing_steps": [
            "ទៅកាន់ទំព័រ \"**Edit Invoice**\"",
            "ស្វែងរកវិក្កយបត្រដោយ៖",
            "- លេខវិក្កយបត្រ ឬ",
            "- សេចក្តីយោងវិក្កយបត្រ",
            "ជ្រើសរើសវិក្កយបត្រពីបញ្ជី",
            "ធ្វើការផ្លាស់ប្តូររបស់អ្នកនៅក្នុងកម្មវិធីកែសម្រួលទិន្នន័យ",
            "ធ្វើបច្ចុប្បន្នភាពព័ត៌មានកុងតឺន័រ/ឡានដឹកទំនិញប្រសិនបើចាំបាច់",
            "ចុច \"**💾 រក្សាទុកការផ្លាស់ប្តូរ**\""
        ],
        "voiding_invoices": "🗑️ លុបចោលវិក្កយបត្រ",
        "voiding_desc": "ដើម្បីលុបចោល (បោះបង់) វិក្កយបត្រ៖",
        "voiding_steps": [
            "ទៅកាន់ទំព័រ \"**Void Invoice**\"",
            "ស្វែងរកវិក្កយបត្រ",
            "ជ្រើសរើសវាពីបញ្ជី",
            "ចុច \"**Void Invoice**\"",
            "បញ្ជាក់សកម្មភាពរបស់អ្នក"
        ],
        "voiding_note": "**ចំណាំ**: វិក្កយបត្រដែលត្រូវបានលុបចោលមិនត្រូវបានលុបទេ គ្រាន់តែត្រូវបានសម្គាល់ថាមិនសកម្ម។",
        "backup_export": "💾 បម្រុងទុក និងនាំចេញ",
        "backup_title": "#### បង្កើតការបម្រុងទុក៖",
        "backup_steps": [
            "ទៅកាន់ \"**Backup Database**\"",
            "ចុច \"**បង្កើតការបម្រុងទុក**\"",
            "ទិន្នន័យរបស់អ្នកត្រូវបានរក្សាទុកដោយសុវត្ថិភាព",
            "រក្សាការបម្រុងទុកជាទៀងទាត់!"
        ],
        "export_title": "#### នាំចេញទិន្នន័យ៖",
        "export_steps": [
            "ទៅកាន់ \"**Export Data**\"",
            "ជ្រើសរើសតម្រងរបស់អ្នក",
            "ជ្រើសរើសទម្រង់នាំចេញ",
            "ទាញយកឯកសាររបស់អ្នក"
        ],
        # Tab 5 - Troubleshooting
        "troubleshooting_title": "❓ ដោះស្រាយបញ្ហា និងសំណួរញឹកញាប់",
        "common_issues": "🚨 បញ្ហាទូទៅ",
        "issue0_title": "🔧 ទូទៅបំផុត: Header មិនត្រូវបានស្គាល់",
        "issue0_desc": "**90% នៃបញ្ហាបណ្តាលមកពី header ជួរឈរមិនត្រឹមត្រូវ!**",
        "issue0_solution": "**ដំណោះស្រាយ: ទៅ Header Mapping tab ហើយប្រើ header ពិតប្រាកដទាំងនេះ:**",
        "issue0_headers": [
            "'po' សម្រាប់លេខ PO",
            "'item' សម្រាប់កូដទំនិញ", 
            "'pcs' សម្រាប់បរិមាណ",
            "'unit' សម្រាប់តម្លៃឯកតា",
            "'amount' សម្រាប់ចំនួនទឹកប្រាក់សរុប",
            "'sqft' សម្រាប់ហ្វីតការ៉េ"
        ],
        "issue1_title": "❌ ឯកសារ Excel របស់ខ្ញុំមិនអាចដំណើរការបាន",
        "issue1_causes": "**មូលហេតុដែលអាចកើតមាន៖**",
        "issue1_cause_list": [
            "ទម្រង់ឯកសារ Excel មិនត្រូវបានគាំទ្រ (ប្រើ .xlsx)",
            "❗ **មូលហេតុទូទៅបំផុត**: Header ជួរឈរមិនត្រូវ - ប្រព័ន្ធរកទិន្នន័យមិនឃើញ!",
            "បាត់ជួរឈរដែលត្រូវការ (po, item, amount, ។ល។)",
            "ទិន្នន័យនៅក្នុងទម្រង់មិនត្រឹមត្រូវ (អក្សរនៅក្នុងជួរឈរលេខ)"
        ],
        "issue1_solutions": "**ដំណោះស្រាយ៖**",
        "issue1_solution_list": [
            "រក្សាទុកឯកសាររបស់អ្នកជាទម្រង់ .xlsx",
            "🔧 **ពិនិត្យ Header Mapping Tab ជាមុនសិន** - កែ header ជួរឈររបស់អ្នក!",
            "ប្រើ header សាមញ្ញដូចជា: 'po', 'item', 'pcs', 'unit', 'amount', 'sqft'",
            "ត្រូវប្រាកដថាលេខត្រូវបានធ្វើទម្រង់ជាលេខ មិនមែនអក្សរ"
        ],
        "issue2_title": "⏳ ការដំណើរការយូរពេក",
        "issue2_causes": "**នេះអាចកើតឡើងនៅពេល៖**",
        "issue2_cause_list": [
            "ឯកសារ Excel ធំណាស់",
            "ឯកសារមានជួរទទេច្រើន",
            "រូបមន្តស្មុគស្មាញនៅក្នុងឯកសារ Excel"
        ],
        "issue2_solutions": "**ដំណោះស្រាយ៖**",
        "issue2_solution_list": [
            "យកជួរទទេចេញពីឯកសារ Excel របស់អ្នក",
            "ចម្លងទិន្នន័យទៅឯកសារ Excel ថ្មីស្អាត",
            "ទាក់ទងការគាំទ្រប្រសិនបើបញ្ហានៅតែបន្ត"
        ],
        "issue3_title": "🔍 ខ្ញុំរកវិក្កយបត្ររបស់ខ្ញុំមិនឃើញ",
        "issue3_causes": "**ពិនិត្យរបស់ទាំងនេះ៖**",
        "issue3_cause_list": [
            "តើវិក្កយបត្រពិតជានៅក្នុងមូលដ្ឋានទិន្នន័យមែនទេ? (ពិនិត្យ \"Database\")",
            "តើអ្នកកំពុងស្វែងរកជាមួយលេខយោងត្រឹមត្រូវមែនទេ?",
            "តើវិក្កយបត្រត្រូវបានលុបចោលហើយមែនទេ?",
            "ពិនិត្យតម្រងកាលបរិច្ឆេទរបស់អ្នក"
        ],
        "issue4_title": "💾 ទិន្នន័យរបស់ខ្ញុំបាត់",
        "issue4_desc": "**កុំភ័យ! ទិន្នន័យរបស់អ្នកអាចនៅ៖**",
        "issue4_cause_list": [
            "ត្រូវបានត្រង (ពិនិត្យតម្រងកាលបរិច្ឆេទ/ការស្វែងរករបស់អ្នក)",
            "នៅក្នុងស្ថានភាពផ្សេង (ពិនិត្យវិក្កយបត្រដែលត្រូវបានលុបចោល)",
            "នៅក្នុងឯកសារបម្រុងទុក"
        ],
        "issue4_recovery": "**ជំហានស្តារ៖**",
        "issue4_recovery_list": [
            "សម្អាតតម្រងទាំងអស់នៅក្នុង \"Database\"",
            "ពិនិត្យ \"Backup Database\" សម្រាប់ការបម្រុងទុកថ្មីៗ",
            "ទាក់ទងអ្នកគ្រប់គ្រងប្រព័ន្ធរបស់អ្នក"
        ],
        "getting_help": "📞 ទទួលបានជំនួយ",
        "before_help": "#### មុនពេលសុំជំនួយ៖",
        "before_help_list": [
            "ពិនិត្យមគ្គុទ្ទេសក៍នេះជាមុនសិន",
            "ព្យាយាមចាប់ផ្តើមកម្មវិធីឡើងវិញ",
            "ពិនិត្យថាតើឯកសារ Excel របស់អ្នកដំណើរការជាមួយទិន្នន័យផ្សេងទៀត",
            "កត់សម្គាល់សារកំហុសណាមួយដែលអ្នកឃើញ"
        ],
        "when_contacting": "#### នៅពេលទាក់ទងការគាំទ្រ៖",
        "when_contacting_list": [
            "ពិពណ៌នាអ្វីដែលអ្នកកំពុងព្យាយាមធ្វើ",
            "ចែករំលែកសារកំហុសណាមួយ",
            "រៀបរាប់ឯកសារណាដែលអ្នកកំពុងដំណើរការ",
            "រួមបញ្ចូលរូបថតអេក្រង់ប្រសិនបើមានប្រយោជន៍"
        ],
        "pro_tips": "💡 ជំនួយអ្នកជំនាញសម្រាប់ភាពជោគជ័យ",
        "excel_tips": "#### ជំនួយឯកសារ Excel៖",
        "excel_tips_list": [
            "រក្សាឯកសារឱ្យស្អាត និងមានការរៀបចំ",
            "ប្រើឈ្មោះជួរឈរដែលស្របគ្នា",
            "យកជួរទទេចេញ",
            "រក្សាទុកជាទម្រង់ .xlsx"
        ],
        "data_tips": "#### គ្រប់គ្រងទិន្នន័យ៖",
        "data_tips_list": [
            "បង្កើតការបម្រុងទុកជាទៀងទាត់",
            "ពិនិត្យទិន្នន័យមុនពេលទទួលយក",
            "ប្រើការដាក់ឈ្មោះច្បាស់លាស់ និងស្របគ្នា",
            "រក្សាទុកឯកសារ Excel ដើម"
        ],
        "system_tips": "#### ការប្រើប្រាស់ប្រព័ន្ធ៖",
        "system_tips_list": [
            "ដំណើរការឯកសារក្នុងអំឡុងពេលមិនមមាញឹក",
            "កុំបិទកម្មវិធីរុករកក្នុងអំឡុងពេលដំណើរការ",
            "ពិនិត្យផ្ទាំងគ្រប់គ្រងជាទៀងទាត់",
            "នាំចេញរបាយការណ៍សំខាន់ៗ"
        ],
        # Tab 5 - Header Mapping
        "header_mapping_title": "🔧 មគ្គុទ្ទេសក៍ការផ្គូផ្គង Header Excel",
        "header_mapping_desc": "⚠️ **សំខាន់ណាស់**: ប្រសិនបើ header mapping មិនត្រឹមត្រូវ គ្មានទិន្នន័យនឹងហូរទៅបង្កើតវិក្កយបត្រទេ! ប្រើមគ្គុទ្ទេសក៍នេះដើម្បីធានាថា Excel headers របស់អ្នកត្រូវនឹងអ្វីដែលប្រព័ន្ធរំពឹងទុក។",
        "what_is_mapping": "### Header Mapping គឺជាអ្វី?",
        "mapping_desc": "ប្រព័ន្ធត្រូវការកំណត់អត្តសញ្ញាណថាតើជួរឈរណានៅក្នុងឯកសារ Excel របស់អ្នកមានទិន្នន័យជាក់លាក់ (ដូចជាលេខ PO, បរិមាណ, ។ល។)។ ពេលខ្លះឈ្មោះជួរឈររបស់អ្នកអាចខុសពីអ្វីដែលប្រព័ន្ធរំពឹងទុក។",
        "required_headers": "📋 Header ដែលត្រូវការ និងការផ្គូផ្គងរបស់វា",
        "required_headers_desc": "ឯកសារ Excel របស់អ្នកត្រូវតែមានប្រភេទទិន្នន័យទាំងនេះ។ នេះជា**ការផ្គូផ្គងពិតប្រាកដពីប្រព័ន្ធ** - ប្រើជម្រើសងាយបំផុតជាមុនសិន៖",
        "header_mappings": [
            "**លេខ PO** → ងាយបំផុត: 'po' | ទទួលយកផងដែរ: 'PO', 'PO NO.', '订单号'",
            "**កូដទំនិញ** → ងាយបំផុត: 'item' | ទទួលយកផងដែរ: '物料代码', 'ITEM NO.', 'Item No'",
            "**បរិមាណ/ចំនួន** → ងាយបំផុត: 'pcs' | ទទួលយកផងដែរ: 'PCS', '总张数', '张数'",
            "**តម្លៃឯកតា** → ងាយបំផុត: 'unit' | ទទួលយកផងដែរ: 'USD', '单价', 'price'",
            "**ចំនួនទឹកប្រាក់សរុប** → ងាយបំផុត: 'amount' | ទទួលយកផងដែរ: '金额', 'USD', 'total'",
            "**ហ្វីតការ៉េ** → ងាយបំផុត: 'sqft' | ទទួលយកផងដែរ: 'SF', '尺数', '出货数量(sf)'",
            "**ទម្ងន់សុទ្ធ** → ងាយបំផុត: 'net' | ទទួលយកផងដែរ: 'NW', '净重', 'net weight'",
            "**ទម្ងន់សរុប** → ងាយបំផុត: 'gross' | ទទួលយកផងដែរ: 'GW', '毛重', 'Gross'",
            "**ការពិពណ៌នា** → ងាយបំផុត: 'description' | ទទួលយកផងដែរ: '产品名称', '品名规格', 'desc'",
            "**CBM/ចំណាំ** → ងាយបំផុត: 'cbm' | ទទួលយកផងដែរ: '材积', 'CBM', '备注'",
            "**លេខបញ្ជាផលិត** → ងាយបំផុត: 'production_order_no' | ទទួលយកផងដែរ: 'TTX编号', '生产单号'"
        ],
        "common_issues_mapping": "⚠️ បញ្ហា Header ទូទៅ",
        "mapping_issues": [
            "**ភាសាផ្សេង**: Header ជាភាសាមូលដ្ឋាន (ខ្មែរ, ចិន, ។ល។)",
            "**អក្សរកាត់**: ការប្រើអក្សរកាត់មិនស្តង់ដារ",
            "**ចន្លោះបន្ថែម**: Header ដែលមានចន្លោះនៅមុខ/ក្រោយ",
            "**តួអក្សរពិសេស**: Header ដែលមាននិមិត្តសញ្ញា ឬសញ្ញាវណ្ណយុត្តិ",
            "**ក្រឡាចត្រង្គបញ្ចូលគ្នា**: Header ដែលលាតសន្ធឹងលើក្រឡាចត្រង្គច្រើន"
        ],
        "solutions_title": "✅ ដំណោះស្រាយនៅពេល Header មិនត្រូវគ្នា",
        "solution_option1": "#### ជម្រើសទី១៖ កែសម្រួលឯកសារ Excel របស់អ្នក (បានណែនាំ)",
        "solution1_steps": [
            "បើកឯកសារ Excel របស់អ្នក",
            "ប្តូរឈ្មោះ header ជួរឈរឱ្យត្រូវនឹងឈ្មោះដែលរំពឹងទុកខាងលើ",
            "ឧទាហរណ៍៖ ប្តូរ '数量' ទៅ 'Quantity'",
            "រក្សាទុកឯកសារ ហើយព្យាយាមដំណើរការម្តងទៀត"
        ],
        "solution_option2": "#### ជម្រើសទី២៖ រាយការណ៍ទៅអ្នកគ្រប់គ្រង",
        "solution2_steps": [
            "ថតរូបអេក្រង់ header Excel របស់អ្នក",
            "កត់សម្គាល់ថាជួរឈរណាមានទិន្នន័យអ្វី",
            "ទាក់ទងអ្នកគ្រប់គ្រងប្រព័ន្ធរបស់អ្នកជាមួយ៖",
            "- រូបថតអេក្រង់ header ឯកសារ Excel របស់អ្នក",
            "- ការពិពណ៌នាអំពីទិន្នន័យដែលជួរឈរនីមួយៗមាន",
            "- សុំឱ្យបន្ថែមឈ្មោះ header របស់អ្នកទៅក្នុងការផ្គូផ្គងប្រព័ន្ធ"
        ],
        "example_mapping": "📝 ឧទាហរណ៍ការផ្គូផ្គង Header",
        "example_desc": "នេះជាឧទាហរណ៍នៃរបៀបផ្គូផ្គងបំលាស់ប្តូរទូទៅ៖",
        "example_table": [
            "**Header របស់អ្នក** → **ប្តូរទៅ** → **ប្រភេទទិន្នន័យ**",
            "'订单号' → 'po' → លេខការបញ្ជាទិញ",
            "'物料代码' → 'item' → កូដផលិតផល/ទំនិញ",
            "'总张数' → 'pcs' → បរិមាណ/ចំនួន",
            "'单价' → 'unit' → តម្លៃក្នុងមួយឯកតា",
            "'金额' → 'amount' → តម្លៃសរុប",
            "'出货数量 (sf)' → 'sqft' → ហ្វីតការ៉េ",
            "'净重' → 'net' → ទម្ងន់សុទ្ធ",
            "'毛重' → 'gross' → ទម្ងន់សរុប",
            "'TTX编号' → 'production_order_no' → លេខបញ្ជាផលិត"
        ],
        "best_practices_headers": "💡 ការអនុវត្តល្អបំផុតសម្រាប់ Header Excel",
        "header_best_practices": [
            "**ប្រើឈ្មោះអង់គ្លេស** នៅពេលដែលអាចធ្វើបានសម្រាប់ភាពឆបគ្នាកាន់តែល្អ",
            "**រក្សា header ឱ្យសាមញ្ញ** - ជៀសវាងតួអក្សរពិសេស",
            "**មានភាពស្របគ្នា** - ប្រើឈ្មោះ header ដូចគ្នានៅលើឯកសារទាំងអស់",
            "**គ្មានជួរឈរទទេ** រវាងជួរឈរទិន្នន័យ",
            "**ជួរទីមួយប៉ុណ្ណោះ** - ដាក់ header នៅជួរទីមួយនៃឯកសារ Excel របស់អ្នក"
        ],
        "admin_contact": "📞 ត្រូវការជំនួយជាមួយការផ្គូផ្គង?",
        "admin_help": [
            "ប្រសិនបើអ្នកប្រើឯកសារ Excel ជាមួយ header មិនស្តង់ដារញឹកញាប់៖",
            "ទាក់ទងអ្នកគ្រប់គ្រងរបស់អ្នកដើម្បីបន្ថែមបំលាស់ប្តូរ header របស់អ្នកទៅក្នុងប្រព័ន្ធ",
            "ផ្តល់ឧទាហរណ៍នៃទម្រង់ឯកសារ Excel ធម្មតារបស់អ្នក",
            "អ្នកគ្រប់គ្រងអាចកំណត់រចនាសម្ព័ន្ធប្រព័ន្ធឱ្យស្គាល់ឈ្មោះ header ជាក់លាក់របស់អ្នក"
        ]
    },
    "中文 (Chinese)": {
        "title": "📖 发票管理系统 - 用户指南",
        "tab1": "🏠 入门指南",
        "tab2": "📊 仪表板",
        "tab3": "➕ 添加发票",
        "tab4": "✏️ 数据管理", 
        "tab5": "🔧 Header Mapping",
        "tab6": "❓ 故障排除",
        "welcome_title": "🏠 欢迎使用发票管理系统",
        "what_is_system": "### 这个系统是什么？",
        "system_desc": "这是一个专为皮革行业企业设计的**自动化发票处理系统**。它帮助您将Excel文件转换为专业发票并管理您的发票数据库。",
        "what_can_do": "### 它能为您做什么？",
        "features": [
            "📄 **自动将Excel文件**转换为专业发票",
            "📊 **通过仪表板分析**跟踪您的业务",
            "💾 **将所有发票**存储在有组织的数据库中",
            "📈 **生成报告**并查看业务趋势",
            "✏️ **轻松编辑和管理**发票数据"
        ],
        "who_for": "🎯 适用对象",
        "who_list": [
            "**管理皮革出口的企业主**",
            "**处理发票的会计人员**",
            "**跟踪订单的销售团队**",
            "**任何需要将Excel数据转换为发票的人**"
        ],
        "benefits": "⚡ 主要优势",
        "benefits_list": [
            "**节省时间** - 无需手动创建发票",
            "**减少错误** - 自动计算",
            "**保持有序** - 所有数据集中在一处",
            "**跟踪性能** - 内置分析功能"
        ],
        "quick_start": "🚀 快速入门 - 3个简单步骤",
        "step1_title": "### 步骤1：准备您的Excel文件",
        "step1_desc": "- 使用您现有的Excel格式\n- 确保它包含以下列：\n  - PO编号\n  - 项目代码\n  - 数量\n  - 价格\n  - 金额",
        "step2_title": "### 步骤2：上传和处理",
        "step2_desc": "- 转到相应页面：\n  - \"High Quality Leather\"用于优质产品\n  - \"2nd Layer Leather\"用于次级产品\n- 上传您的Excel文件\n- 点击\"处理\"",
        "step3_title": "### 步骤3：审核和批准",
        "step3_desc": "- 检查\"Verify\"页面\n- 审核处理后的数据\n- 点击\"接受\"添加到数据库\n- 您的发票准备就绪！",
        "dashboard_title": "📊 了解仪表板",
        "dashboard_desc": "**仪表板**是您的主要控制中心。您将看到以下内容：",
        "key_metrics": "📈 关键指标",
        "metrics_list": [
            "**总开票金额** - 您的总收入",
            "**总平方英尺** - 产品总数量",
            "**唯一发票** - 已处理的发票数量"
        ],
        "date_filtering": "📅 日期筛选",
        "date_filter_list": [
            "使用日期选择器筛选数据",
            "查看特定时间段",
            "比较不同月份/季度"
        ],
        "charts_graphs": "📊 图表和图形",
        "charts_list": [
            "**月收入** - 查看您的收入趋势",
            "**热门产品** - 最畅销商品",
            "**性能跟踪** - 业务增长"
        ],
        "what_to_look": "🔍 需要关注的内容",
        "look_for_list": [
            "**增长趋势** - 收入增加",
            "**顶级表现者** - 最佳产品",
            "**季节性模式** - 繁忙时期"
        ],
        # Tab 3 - Adding Invoices
        "adding_invoices_title": "➕ 添加新发票",
        "adding_desc": "有**两种方式**向系统添加发票：",
        "method1_title": "方法1：使用网页表单",
        "high_quality_steps": "#### 高质量皮革：",
        "high_quality_list": [
            "点击侧边栏中的\"**High Quality Leather**\"",
            "上传您的Excel文件",
            "填写任何附加信息",
            "点击\"**处理文件**\"",
            "等待处理完成"
        ],
        "second_layer_steps": "#### 二层皮革：",
        "second_layer_list": [
            "点击侧边栏中的\"**2nd Layer Leather**\"",
            "上传您的Excel文件",
            "填写任何附加信息",
            "点击\"**处理文件**\"",
            "等待处理完成"
        ],
        "method2_title": "方法2：直接文件处理",
        "method2_list": [
            "将Excel文件放入系统文件夹",
            "运行自动化命令",
            "检查\"**Verify**\"页面",
            "审核并批准数据"
        ],
        "verification_title": "📋 数据验证过程",
        "verification_desc": "处理后，您需要**验证您的数据**：",
        "verification_steps": [
            "转到\"**Verify**\"页面",
            "您将看到数据预览",
            "检查所有信息是否正确：",
            "- PO编号",
            "- 项目代码",
            "- 数量",
            "- 价格",
            "- 金额",
            "如果一切正常，点击\"**✅ 接受**\"",
            "如果有错误，点击\"**❌ 拒绝**\"并修复Excel文件"
        ],
        "tip_message": "💡 **提示**：接受前请务必仔细检查数据。一旦接受，数据将进入您的永久数据库。",
        # Tab 4 - Managing Data
        "managing_data_title": "✏️ 管理您的发票数据",
        "viewing_database": "🔍 查看您的数据库",
        "viewing_desc": "\"**Database**\"页面允许您：",
        "viewing_features": [
            "查看所有发票",
            "按日期、PO编号或项目筛选",
            "搜索特定记录",
            "将数据导出到Excel"
        ],
        "editing_invoices": "✏️ 编辑发票",
        "editing_desc": "要编辑现有发票：",
        "editing_steps": [
            "转到\"**Edit Invoice**\"页面",
            "通过以下方式搜索发票：",
            "- 发票编号，或",
            "- 发票参考",
            "从列表中选择发票",
            "在数据编辑器中进行更改",
            "如需要，更新集装箱/卡车信息",
            "点击\"**💾 保存更改**\""
        ],
        "voiding_invoices": "🗑️ 作废发票",
        "voiding_desc": "要作废（取消）发票：",
        "voiding_steps": [
            "转到\"**Void Invoice**\"页面",
            "搜索发票",
            "从列表中选择",
            "点击\"**Void Invoice**\"",
            "确认您的操作"
        ],
        "voiding_note": "**注意**：作废的发票不会被删除，只是标记为非活动状态。",
        "backup_export": "💾 备份和导出",
        "backup_title": "#### 创建备份：",
        "backup_steps": [
            "转到\"**Backup Database**\"",
            "点击\"**创建备份**\"",
            "您的数据已安全存储",
            "定期保持备份！"
        ],
        "export_title": "#### 导出数据：",
        "export_steps": [
            "转到\"**Export Data**\"",
            "选择您的筛选器",
            "选择导出格式",
            "下载您的文件"
        ],
        # Tab 5 - Troubleshooting
        "troubleshooting_title": "❓ 故障排除和常见问题",
        "common_issues": "🚨 常见问题",
        "issue0_title": "🔧 最常见: 表头无法识别",
        "issue0_desc": "**90%的问题都是由于列标题不正确造成的！**",
        "issue0_solution": "**解决方案: 转到Header Mapping标签并使用这些确切的标题:**",
        "issue0_headers": [
            "'po' 用于PO编号",
            "'item' 用于项目代码", 
            "'pcs' 用于数量",
            "'unit' 用于单价",
            "'amount' 用于总金额",
            "'sqft' 用于平方英尺"
        ],
        "issue1_title": "❌ 我的Excel文件无法处理",
        "issue1_causes": "**可能的原因：**",
        "issue1_cause_list": [
            "不支持Excel文件格式（使用.xlsx）",
            "❗ **最常见原因**: 列标题不匹配 - 系统找不到您的数据！",
            "缺少必需的列（po、item、amount等）",
            "数据格式错误（数字列中有文本）"
        ],
        "issue1_solutions": "**解决方案：**",
        "issue1_solution_list": [
            "将文件保存为.xlsx格式",
            "🔧 **先检查Header Mapping标签** - 修复您的列标题！",
            "使用简单标题如: 'po', 'item', 'pcs', 'unit', 'amount', 'sqft'",
            "确保数字格式为数字，而不是文本"
        ],
        "issue2_title": "⏳ 处理时间过长",
        "issue2_causes": "**这可能发生在：**",
        "issue2_cause_list": [
            "Excel文件非常大",
            "文件有很多空行",
            "Excel文件中有复杂公式"
        ],
        "issue2_solutions": "**解决方案：**",
        "issue2_solution_list": [
            "从Excel文件中删除空行",
            "将数据复制到新的干净Excel文件",
            "如果问题持续存在，请联系支持"
        ],
        "issue3_title": "🔍 我找不到我的发票",
        "issue3_causes": "**检查这些事项：**",
        "issue3_cause_list": [
            "发票实际上在数据库中吗？（检查\"Database\"）",
            "您是否使用正确的参考编号搜索？",
            "发票是否已被作废？",
            "检查您的日期筛选器"
        ],
        "issue4_title": "💾 我的数据消失了",
        "issue4_desc": "**不要惊慌！您的数据可能：**",
        "issue4_cause_list": [
            "被筛选掉了（检查您的日期/搜索筛选器）",
            "处于不同状态（检查作废发票）",
            "在备份文件中"
        ],
        "issue4_recovery": "**恢复步骤：**",
        "issue4_recovery_list": [
            "清除\"Database\"中的所有筛选器",
            "检查\"Backup Database\"中的最近备份",
            "联系您的系统管理员"
        ],
        # Tab 5 - Header Mapping
        "header_mapping_title": "🔧 Excel表头映射指南",
        "header_mapping_desc": "当系统无法自动检测您的Excel列标题时，请使用本指南了解正确的映射方式。",
        "what_is_mapping": "### 什么是表头映射？",
        "mapping_desc": "系统需要识别Excel文件中的哪些列包含特定数据（如PO编号、数量等）。有时您的列名可能与系统期望的不同。",
        "required_headers": "📋 必需的表头及其映射",
        "required_headers_desc": "您的Excel文件必须包含这些数据类型。以下是系统查找的**确切英文名称**：",
        "header_mappings": [
            "**PO编号** → 系统查找：'PO', 'PO Number', 'Purchase Order', 'P.O.'",
            "**项目代码** → 系统查找：'Item', 'Item Code', 'Product Code', 'SKU'",
            "**描述** → 系统查找：'Description', 'Item Description', 'Product Description'",
            "**数量** → 系统查找：'Quantity', 'Qty', 'Amount', 'Pieces'",
            "**单价** → 系统查找：'Price', 'Unit Price', 'Rate', 'Cost'",
            "**总金额** → 系统查找：'Total', 'Amount', 'Total Amount', 'Value'",
            "**平方英尺** → 系统查找：'SqFt', 'Square Feet', 'Sq Ft', 'Area'"
        ],
        "common_issues_mapping": "⚠️ 常见表头问题",
        "mapping_issues": [
            "**不同语言**：使用本地语言的表头（中文、高棉语等）",
            "**缩写**：使用非标准缩写",
            "**多余空格**：表头前后有空格",
            "**特殊字符**：表头包含符号或标点",
            "**合并单元格**：表头跨越多个单元格"
        ],
        "solutions_title": "✅ 表头不匹配时的解决方案",
        "solution_option1": "#### 选项1：编辑您的Excel文件（推荐）",
        "solution1_steps": [
            "打开您的Excel文件",
            "将列标题重命名为上述期望的名称",
            "例如：将'数量'改为'Quantity'",
            "保存文件并重新尝试处理"
        ],
        "solution_option2": "#### 选项2：报告给管理员",
        "solution2_steps": [
            "截取Excel表头的屏幕截图",
            "记录哪些列包含哪些数据",
            "联系系统管理员并提供：",
            "- Excel文件表头的屏幕截图",
            "- 每列包含数据的描述",
            "- 请求将您的表头名称添加到系统映射中"
        ],
        "example_mapping": "📝 表头映射示例",
        "example_desc": "以下是如何映射常见变体的示例：",
        "example_table": [
            "**您的表头** → **更改为** → **数据类型**",
            "'订单号' → 'PO Number' → 采购订单号",
            "'产品代码' → 'Item Code' → 产品/项目代码",
            "'数量' → 'Quantity' → 数量/金额",
            "'单价' → 'Unit Price' → 单位价格",
            "'总金额' → 'Total Amount' → 总价值"
        ],
        "best_practices_headers": "💡 Excel表头最佳实践",
        "header_best_practices": [
            "**尽可能使用英文名称**以获得更好的兼容性",
            "**保持表头简单** - 避免特殊字符",
            "**保持一致性** - 在所有文件中使用相同的表头名称",
            "**数据列之间无空列**",
            "**仅第一行** - 将表头放在Excel文件的第一行"
        ],
        "admin_contact": "📞 需要映射帮助？",
        "admin_help": [
            "如果您经常使用具有非标准表头的Excel文件：",
            "联系管理员将您的表头变体添加到系统中",
            "提供典型Excel文件格式的示例",
            "管理员可以配置系统以识别您的特定表头名称"
        ],
        "getting_help": "📞 获取帮助",
        "before_help": "#### 寻求帮助前：",
        "before_help_list": [
            "首先检查本指南",
            "尝试重启应用程序",
            "检查您的Excel文件是否适用于其他数据",
            "记录您看到的任何错误消息"
        ],
        "when_contacting": "#### 联系支持时：",
        "when_contacting_list": [
            "描述您试图做什么",
            "分享任何错误消息",
            "提及您正在处理哪个文件",
            "如果有帮助，请包含截图"
        ],
        "pro_tips": "💡 成功的专业提示",
        "excel_tips": "#### Excel文件提示：",
        "excel_tips_list": [
            "保持文件整洁有序",
            "使用一致的列名",
            "删除空行",
            "保存为.xlsx格式"
        ],
        "data_tips": "#### 数据管理：",
        "data_tips_list": [
            "定期创建备份",
            "接受前审核数据",
            "使用清晰一致的命名",
            "保留原始Excel文件"
        ],
        "system_tips": "#### 系统使用：",
        "system_tips_list": [
            "在非高峰时间处理文件",
            "处理期间不要关闭浏览器",
            "定期检查仪表板",
            "导出重要报告"
        ],
        # Tab 5 - Header Mapping
        "header_mapping_title": "🔧 Excel表头映射指南",
        "header_mapping_desc": "当系统无法自动检测您的Excel列标题时，请使用本指南了解正确的映射方式。",
        "what_is_mapping": "### 什么是表头映射？",
        "mapping_desc": "系统需要识别Excel文件中的哪些列包含特定数据（如PO编号、数量等）。有时您的列名可能与系统期望的不同。",
        "required_headers": "📋 必需的表头及其映射",
        "required_headers_desc": "您的Excel文件必须包含这些数据类型。以下是系统查找的**确切英文名称**：",
        "header_mappings": [
            "**PO编号** → 系统查找：'PO', 'PO Number', 'Purchase Order', 'P.O.'",
            "**项目代码** → 系统查找：'Item', 'Item Code', 'Product Code', 'SKU'",
            "**描述** → 系统查找：'Description', 'Item Description', 'Product Description'",
            "**数量** → 系统查找：'Quantity', 'Qty', 'Amount', 'Pieces'",
            "**单价** → 系统查找：'Price', 'Unit Price', 'Rate', 'Cost'",
            "**总金额** → 系统查找：'Total', 'Amount', 'Total Amount', 'Value'",
            "**平方英尺** → 系统查找：'SqFt', 'Square Feet', 'Sq Ft', 'Area'"
        ],
        "common_issues_mapping": "⚠️ 常见表头问题",
        "mapping_issues": [
            "**不同语言**：使用本地语言的表头（中文、高棉语等）",
            "**缩写**：使用非标准缩写",
            "**多余空格**：表头前后有空格",
            "**特殊字符**：表头包含符号或标点",
            "**合并单元格**：表头跨越多个单元格"
        ],
        "solutions_title": "✅ 表头不匹配时的解决方案",
        "solution_option1": "#### 选项1：编辑您的Excel文件（推荐）",
        "solution1_steps": [
            "打开您的Excel文件",
            "将列标题重命名为上述期望的名称",
            "例如：将'数量'改为'Quantity'",
            "保存文件并重新尝试处理"
        ],
        "solution_option2": "#### 选项2：报告给管理员",
        "solution2_steps": [
            "截取Excel表头的屏幕截图",
            "记录哪些列包含哪些数据",
            "联系系统管理员并提供：",
            "- Excel文件表头的屏幕截图",
            "- 每列包含数据的描述",
            "- 请求将您的表头名称添加到系统映射中"
        ],
        "example_mapping": "📝 表头映射示例",
        "example_desc": "以下是如何映射常见变体的示例：",
        "example_table": [
            "**您的表头** → **更改为** → **数据类型**",
            "'订单号' → 'PO Number' → 采购订单号",
            "'产品代码' → 'Item Code' → 产品/项目代码",
            "'数量' → 'Quantity' → 数量/金额",
            "'单价' → 'Unit Price' → 单位价格",
            "'总金额' → 'Total Amount' → 总价值"
        ],
        "best_practices_headers": "💡 Excel表头最佳实践",
        "header_best_practices": [
            "**尽可能使用英文名称**以获得更好的兼容性",
            "**保持表头简单** - 避免特殊字符",
            "**保持一致性** - 在所有文件中使用相同的表头名称",
            "**数据列之间无空列**",
            "**仅第一行** - 将表头放在Excel文件的第一行"
        ],
        "admin_contact": "📞 需要映射帮助？",
        "admin_help": [
            "如果您经常使用具有非标准表头的Excel文件：",
            "联系管理员将您的表头变体添加到系统中",
            "提供典型Excel文件格式的示例",
            "管理员可以配置系统以识别您的特定表头名称"
        ]
    }
}

# Get current language translations
t = translations[language]

st.title(t["title"])

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([t["tab1"], t["tab2"], t["tab3"], t["tab4"], t["tab5"], t["tab6"]])

with tab1:
    st.header(t["welcome_title"])
    
    st.markdown(t["what_is_system"])
    st.markdown(t["system_desc"])
    
    st.markdown(t["what_can_do"])
    for feature in t["features"]:
        st.markdown(f"- {feature}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t["who_for"])
        for item in t["who_list"]:
            st.markdown(f"- {item}")
    
    with col2:
        st.subheader(t["benefits"])
        for benefit in t["benefits_list"]:
            st.markdown(f"- {benefit}")
    
    st.markdown("---")
    
    st.subheader(t["quick_start"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(t["step1_title"])
        st.markdown(t["step1_desc"])
    
    with col2:
        st.markdown(t["step2_title"])
        st.markdown(t["step2_desc"])
    
    with col3:
        st.markdown(t["step3_title"])
        st.markdown(t["step3_desc"])

with tab2:
    st.header(t["dashboard_title"])
    
    st.markdown(t["dashboard_desc"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(t["key_metrics"])
        for metric in t["metrics_list"]:
            st.markdown(f"- {metric}")
        
        st.subheader(t["date_filtering"])
        for filter_item in t["date_filter_list"]:
            st.markdown(f"- {filter_item}")
    
    with col2:
        st.subheader(t["charts_graphs"])
        for chart in t["charts_list"]:
            st.markdown(f"- {chart}")
        
        st.subheader(t["what_to_look"])
        for look_item in t["look_for_list"]:
            st.markdown(f"- {look_item}")

with tab3:
    st.header(t["adding_invoices_title"])
    
    st.markdown(t["adding_desc"])
    
    st.subheader(t["method1_title"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(t["high_quality_steps"])
        for i, step in enumerate(t["high_quality_list"], 1):
            st.markdown(f"{i}. {step}")
    
    with col2:
        st.markdown(t["second_layer_steps"])
        for i, step in enumerate(t["second_layer_list"], 1):
            st.markdown(f"{i}. {step}")
    
    st.subheader(t["method2_title"])
    for i, step in enumerate(t["method2_list"], 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    st.subheader(t["verification_title"])
    st.markdown(t["verification_desc"])
    
    for i, step in enumerate(t["verification_steps"], 1):
        if step.startswith("-"):
            st.markdown(f"   {step}")
        else:
            st.markdown(f"{i}. {step}")
    
    st.info(t["tip_message"])

with tab4:
    st.header(t["managing_data_title"])
    
    st.subheader(t["viewing_database"])
    st.markdown(t["viewing_desc"])
    for feature in t["viewing_features"]:
        st.markdown(f"- {feature}")
    
    st.subheader(t["editing_invoices"])
    st.markdown(t["editing_desc"])
    
    for i, step in enumerate(t["editing_steps"], 1):
        if step.startswith("-"):
            st.markdown(f"   {step}")
        else:
            st.markdown(f"{i}. {step}")
    
    st.subheader(t["voiding_invoices"])
    st.markdown(t["voiding_desc"])
    
    for i, step in enumerate(t["voiding_steps"], 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown(t["voiding_note"])
    
    st.subheader(t["backup_export"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(t["backup_title"])
        for i, step in enumerate(t["backup_steps"], 1):
            st.markdown(f"{i}. {step}")
    
    with col2:
        st.markdown(t["export_title"])
        for i, step in enumerate(t["export_steps"], 1):
            st.markdown(f"{i}. {step}")

with tab5:
    st.header(t["header_mapping_title"])
    
    st.markdown(t["header_mapping_desc"])
    
    st.markdown(t["what_is_mapping"])
    st.markdown(t["mapping_desc"])
    
    st.markdown(t["required_headers"])
    st.markdown(t["required_headers_desc"])
    
    for mapping in t["header_mappings"]:
        st.markdown(f"- {mapping}")
    
    st.markdown("---")
    
    st.subheader(t["common_issues_mapping"])
    for issue in t["mapping_issues"]:
        st.markdown(f"- {issue}")
    
    st.markdown("---")
    
    st.subheader(t["solutions_title"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(t["solution_option1"])
        for i, step in enumerate(t["solution1_steps"], 1):
            st.markdown(f"{i}. {step}")
    
    with col2:
        st.markdown(t["solution_option2"])
        for i, step in enumerate(t["solution2_steps"], 1):
            st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    st.subheader(t["example_mapping"])
    st.markdown(t["example_desc"])
    
    for example in t["example_table"]:
        st.markdown(f"- {example}")
    
    st.markdown("---")
    
    st.subheader(t["best_practices_headers"])
    for practice in t["header_best_practices"]:
        st.markdown(f"- {practice}")
    
    st.markdown("---")
    
    st.subheader(t["admin_contact"])
    for help_item in t["admin_help"]:
        st.markdown(f"- {help_item}")

with tab6:
    st.header(t["troubleshooting_title"])
    
    st.subheader(t["common_issues"])
    
    with st.expander(t["issue0_title"], expanded=True):
        st.markdown(t["issue0_desc"])
        st.markdown(t["issue0_solution"])
        for header in t["issue0_headers"]:
            st.markdown(f"- {header}")
        st.info("💡 This solves 90% of processing problems!")
    
    with st.expander(t["issue1_title"]):
        st.markdown(t["issue1_causes"])
        for cause in t["issue1_cause_list"]:
            st.markdown(f"- {cause}")
        
        st.markdown(t["issue1_solutions"])
        for solution in t["issue1_solution_list"]:
            st.markdown(f"- {solution}")
    
    with st.expander(t["issue2_title"]):
        st.markdown(t["issue2_causes"])
        for cause in t["issue2_cause_list"]:
            st.markdown(f"- {cause}")
        
        st.markdown(t["issue2_solutions"])
        for solution in t["issue2_solution_list"]:
            st.markdown(f"- {solution}")
    
    with st.expander(t["issue3_title"]):
        st.markdown(t["issue3_causes"])
        for cause in t["issue3_cause_list"]:
            st.markdown(f"- {cause}")
    
    with st.expander(t["issue4_title"]):
        st.markdown(t["issue4_desc"])
        for cause in t["issue4_cause_list"]:
            st.markdown(f"- {cause}")
        
        st.markdown(t["issue4_recovery"])
        for step in t["issue4_recovery_list"]:
            st.markdown(f"- {step}")
    
    st.subheader(t["getting_help"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(t["before_help"])
        for i, item in enumerate(t["before_help_list"], 1):
            st.markdown(f"{i}. {item}")
    
    with col2:
        st.markdown(t["when_contacting"])
        for item in t["when_contacting_list"]:
            st.markdown(f"- {item}")
    
    st.markdown("---")
    
    st.subheader(t["pro_tips"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(t["excel_tips"])
        for tip in t["excel_tips_list"]:
            st.markdown(f"- {tip}")
    
    with col2:
        st.markdown(t["data_tips"])
        for tip in t["data_tips_list"]:
            st.markdown(f"- {tip}")
    
    with col3:
        st.markdown(t["system_tips"])
        for tip in t["system_tips_list"]:
            st.markdown(f"- {tip}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📧 Need more help? Contact your system administrator</p>
    <p>🔄 Last updated: JULY 2025</p>
</div>
""", unsafe_allow_html=True)