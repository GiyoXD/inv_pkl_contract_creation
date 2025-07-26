import streamlit as st
import json
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="User Guide",
    page_icon="📖",
    layout="wide"
)

# --- Load Translation Function ---
def load_translations(language_code):
    """Load translations from JSON files"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # The translations folder is in the same directory as this script
        root_dir = script_dir
        file_path = os.path.join(root_dir, "translations", f"{language_code}.json")
        
        if os.path.exists(file_path):
            # Check if file is not empty
            if os.path.getsize(file_path) > 0:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                st.warning(f"Translation file {language_code}.json is empty, falling back to English")
        
        # Fallback to English if file doesn't exist or is empty
        fallback_path = os.path.join(root_dir, "translations", "en.json")
        if os.path.exists(fallback_path) and os.path.getsize(fallback_path) > 0:
            with open(fallback_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            st.error("Both translation file and English fallback are missing or empty")
    except Exception as e:
        st.error(f"Error loading translations: {e}")
        return {}

# --- Language Selection ---
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    language_options = {
        "English": "en",
        "ខ្មែរ (Khmer)": "km", 
        "中文 (Chinese)": "zh"
    }
    
    selected_language = st.selectbox(
        "🌐 Language / ភាសា / 语言",
        options=list(language_options.keys()),
        index=0
    )
    
    language_code = language_options[selected_language]

# Load translations
t = load_translations(language_code)

# --- Helper function to safely get translation ---
def get_text(key_path, default=""):
    """Safely get nested translation text"""
    keys = key_path.split('.')
    value = t
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

# Main title
st.title(get_text("title", "📖 Invoice Management System - User Guide"))

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    get_text("tabs.getting_started", "🏠 Getting Started"),
    get_text("tabs.dashboard", "📊 Dashboard"), 
    get_text("tabs.adding_invoices", "➕ Adding Invoices"),
    get_text("tabs.managing_data", "✏️ Managing Data"),
    get_text("tabs.header_mapping", "🔧 Header Mapping"),
    get_text("tabs.troubleshooting", "❓ Troubleshooting")
])

with tab1:
    st.header(get_text("getting_started.welcome_title", "🏠 Welcome to the Invoice Management System"))
    
    st.markdown(get_text("getting_started.what_is_system", "### What is this system?"))
    st.markdown(get_text("getting_started.system_desc", "This is an automated invoice processing system..."))
    
    st.markdown(get_text("getting_started.what_can_do", "### What can it do for you?"))
    features = get_text("getting_started.features", [])
    for feature in features:
        st.markdown(f"- {feature}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_text("getting_started.who_for", "🎯 Who is this for?"))
        who_list = get_text("getting_started.who_list", [])
        for item in who_list:
            st.markdown(f"- {item}")
    
    with col2:
        st.subheader(get_text("getting_started.benefits", "⚡ Key Benefits"))
        benefits_list = get_text("getting_started.benefits_list", [])
        for benefit in benefits_list:
            st.markdown(f"- {benefit}")
    
    st.markdown("---")
    
    st.subheader(get_text("getting_started.quick_start", "🚀 Quick Start - 3 Simple Steps"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(get_text("getting_started.step1_title", "### Step 1: Prepare Your Excel File"))
        st.markdown(get_text("getting_started.step1_desc", "- Use your existing Excel format..."))
    
    with col2:
        st.markdown(get_text("getting_started.step2_title", "### Step 2: Upload & Process"))
        st.markdown(get_text("getting_started.step2_desc", "- Go to the appropriate page..."))
    
    with col3:
        st.markdown(get_text("getting_started.step3_title", "### Step 3: Review & Approve"))
        st.markdown(get_text("getting_started.step3_desc", "- Check the Verify page..."))

with tab2:
    st.header(get_text("dashboard.title", "📊 Understanding the Dashboard"))
    
    st.markdown(get_text("dashboard.desc", "The Dashboard is your main control center..."))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_text("dashboard.key_metrics", "📈 Key Metrics"))
        metrics_list = get_text("dashboard.metrics_list", [])
        for metric in metrics_list:
            st.markdown(f"- {metric}")
        
        st.subheader(get_text("dashboard.date_filtering", "📅 Date Filtering"))
        date_filter_list = get_text("dashboard.date_filter_list", [])
        for filter_item in date_filter_list:
            st.markdown(f"- {filter_item}")
    
    with col2:
        st.subheader(get_text("dashboard.charts_graphs", "📊 Charts & Graphs"))
        charts_list = get_text("dashboard.charts_list", [])
        for chart in charts_list:
            st.markdown(f"- {chart}")
        
        st.subheader(get_text("dashboard.what_to_look", "🔍 What to Look For"))
        look_for_list = get_text("dashboard.look_for_list", [])
        for look_item in look_for_list:
            st.markdown(f"- {look_item}")

with tab3:
    st.header(get_text("adding_invoices.title", "➕ Adding New Invoices"))
    
    st.markdown(get_text("adding_invoices.desc", "There are two ways to add invoices..."))
    
    st.subheader(get_text("adding_invoices.method1_title", "Method 1: Using the Web Forms"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(get_text("adding_invoices.high_quality_steps", "#### For High Quality Leather:"))
        high_quality_list = get_text("adding_invoices.high_quality_list", [])
        for i, step in enumerate(high_quality_list, 1):
            st.markdown(f"{i}. {step}")
    
    with col2:
        st.markdown(get_text("adding_invoices.second_layer_steps", "#### For 2nd Layer Leather:"))
        second_layer_list = get_text("adding_invoices.second_layer_list", [])
        for i, step in enumerate(second_layer_list, 1):
            st.markdown(f"{i}. {step}")
    
    st.subheader(get_text("adding_invoices.method2_title", "Method 2: Direct File Processing"))
    method2_list = get_text("adding_invoices.method2_list", [])
    for i, step in enumerate(method2_list, 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    st.subheader(get_text("adding_invoices.verification_title", "📋 Data Verification Process"))
    st.markdown(get_text("adding_invoices.verification_desc", "After processing, you'll need to verify..."))
    
    verification_steps = get_text("adding_invoices.verification_steps", [])
    for i, step in enumerate(verification_steps, 1):
        if step.startswith("-"):
            st.markdown(f"   {step}")
        else:
            st.markdown(f"{i}. {step}")
    
    st.info(get_text("adding_invoices.tip_message", "Always double-check your data..."))

with tab4:
    st.header(get_text("managing_data.title", "✏️ Managing Your Invoice Data"))
    
    st.subheader(get_text("managing_data.viewing_database", "🔍 Viewing Your Database"))
    st.markdown(get_text("managing_data.viewing_desc", "The Database page lets you..."))
    viewing_features = get_text("managing_data.viewing_features", [])
    for feature in viewing_features:
        st.markdown(f"- {feature}")
    
    st.subheader(get_text("managing_data.editing_invoices", "✏️ Editing Invoices"))
    st.markdown(get_text("managing_data.editing_desc", "To edit an existing invoice..."))
    
    editing_steps = get_text("managing_data.editing_steps", [])
    for i, step in enumerate(editing_steps, 1):
        if step.startswith("-"):
            st.markdown(f"   {step}")
        else:
            st.markdown(f"{i}. {step}")
    
    st.subheader(get_text("managing_data.voiding_invoices", "🗑️ Voiding Invoices"))
    st.markdown(get_text("managing_data.voiding_desc", "To void (cancel) an invoice..."))
    
    voiding_steps = get_text("managing_data.voiding_steps", [])
    for i, step in enumerate(voiding_steps, 1):
        st.markdown(f"{i}. {step}")
    
    st.markdown(get_text("managing_data.voiding_note", "Note: Voided invoices are not deleted..."))
    
    st.subheader(get_text("managing_data.backup_export", "💾 Backup & Export"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(get_text("managing_data.backup_title", "#### Creating Backups:"))
        backup_steps = get_text("managing_data.backup_steps", [])
        for i, step in enumerate(backup_steps, 1):
            st.markdown(f"{i}. {step}")
    
    with col2:
        st.markdown(get_text("managing_data.export_title", "#### Exporting Data:"))
        export_steps = get_text("managing_data.export_steps", [])
        for i, step in enumerate(export_steps, 1):
            st.markdown(f"{i}. {step}")

with tab5:
    st.header(get_text("header_mapping.title", "🔧 Excel Header Mapping Guide"))
    
    st.markdown(get_text("header_mapping.desc", "CRITICAL: Without proper header mapping..."))
    
    st.markdown(get_text("header_mapping.what_is_mapping", "### What is Header Mapping?"))
    st.markdown(get_text("header_mapping.mapping_desc", "The system needs to identify which columns..."))
    
    st.markdown(get_text("header_mapping.required_headers", "📋 Required Headers & Their Mappings"))
    st.markdown(get_text("header_mapping.required_headers_desc", "Your Excel file must contain these data types..."))
    
    header_mappings = get_text("header_mapping.header_mappings", [])
    for mapping in header_mappings:
        st.markdown(f"- {mapping}")
    
    st.markdown("---")
    
    st.subheader(get_text("header_mapping.common_issues_mapping", "⚠️ Common Header Issues"))
    mapping_issues = get_text("header_mapping.mapping_issues", [])
    for issue in mapping_issues:
        st.markdown(f"- {issue}")
    
    st.markdown("---")
    
    st.subheader(get_text("header_mapping.solutions_title", "✅ Solutions When Headers Don't Match"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(get_text("header_mapping.solution_option1", "#### Option 1: Edit Your Excel File (Recommended)"))
        solution1_steps = get_text("header_mapping.solution1_steps", [])
        for i, step in enumerate(solution1_steps, 1):
            st.markdown(f"{i}. {step}")
    
    with col2:
        st.markdown(get_text("header_mapping.solution_option2", "#### Option 2: Report to Administrator"))
        solution2_steps = get_text("header_mapping.solution2_steps", [])
        for i, step in enumerate(solution2_steps, 1):
            st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    st.subheader(get_text("header_mapping.example_mapping", "📝 Example Header Mapping"))
    st.markdown(get_text("header_mapping.example_desc", "Here's an example of how to map..."))
    
    example_table = get_text("header_mapping.example_table", [])
    for example in example_table:
        st.markdown(f"- {example}")
    
    st.markdown("---")
    
    st.subheader(get_text("header_mapping.best_practices_headers", "💡 Best Practices for Excel Headers"))
    header_best_practices = get_text("header_mapping.header_best_practices", [])
    for practice in header_best_practices:
        st.markdown(f"- {practice}")
    
    st.markdown("---")
    
    st.subheader(get_text("header_mapping.admin_contact", "📞 Need Help with Mapping?"))
    admin_help = get_text("header_mapping.admin_help", [])
    for help_item in admin_help:
        st.markdown(f"- {help_item}")

with tab6:
    st.header(get_text("troubleshooting.title", "❓ Troubleshooting & FAQ"))
    
    st.subheader(get_text("troubleshooting.common_issues", "🚨 Common Issues"))
    
    with st.expander(get_text("troubleshooting.issue0_title", "🔧 MOST COMMON: Headers not recognized"), expanded=True):
        st.markdown(get_text("troubleshooting.issue0_desc", "90% of problems are caused by incorrect column headers!"))
        st.markdown(get_text("troubleshooting.issue0_solution", "SOLUTION: Go to Header Mapping tab..."))
        issue0_headers = get_text("troubleshooting.issue0_headers", [])
        for header in issue0_headers:
            st.markdown(f"- {header}")
        st.info("💡 This solves 90% of processing problems!")
    
    with st.expander(get_text("troubleshooting.issue1_title", "❌ My Excel file won't process")):
        st.markdown(get_text("troubleshooting.issue1_causes", "**Possible causes:**"))
        issue1_cause_list = get_text("troubleshooting.issue1_cause_list", [])
        for cause in issue1_cause_list:
            st.markdown(f"- {cause}")
        
        st.markdown(get_text("troubleshooting.issue1_solutions", "**Solutions:**"))
        issue1_solution_list = get_text("troubleshooting.issue1_solution_list", [])
        for solution in issue1_solution_list:
            st.markdown(f"- {solution}")
    
    with st.expander(get_text("troubleshooting.issue2_title", "⏳ Processing is taking too long")):
        st.markdown(get_text("troubleshooting.issue2_causes", "**This can happen when:**"))
        issue2_cause_list = get_text("troubleshooting.issue2_cause_list", [])
        for cause in issue2_cause_list:
            st.markdown(f"- {cause}")
        
        st.markdown(get_text("troubleshooting.issue2_solutions", "**Solutions:**"))
        issue2_solution_list = get_text("troubleshooting.issue2_solution_list", [])
        for solution in issue2_solution_list:
            st.markdown(f"- {solution}")
    
    with st.expander(get_text("troubleshooting.issue3_title", "🔍 I can't find my invoice")):
        st.markdown(get_text("troubleshooting.issue3_causes", "**Check these things:**"))
        issue3_cause_list = get_text("troubleshooting.issue3_cause_list", [])
        for cause in issue3_cause_list:
            st.markdown(f"- {cause}")
    
    with st.expander(get_text("troubleshooting.issue4_title", "💾 My data disappeared")):
        st.markdown(get_text("troubleshooting.issue4_desc", "**Don't panic! Your data might be:**"))
        issue4_cause_list = get_text("troubleshooting.issue4_cause_list", [])
        for cause in issue4_cause_list:
            st.markdown(f"- {cause}")
        
        st.markdown(get_text("troubleshooting.issue4_recovery", "**Recovery steps:**"))
        issue4_recovery_list = get_text("troubleshooting.issue4_recovery_list", [])
        for step in issue4_recovery_list:
            st.markdown(f"- {step}")
    
    with st.expander(get_text("troubleshooting.issue5_title", "🚫 No data processed / Empty results")):
        st.markdown(get_text("troubleshooting.issue5_desc", "**Excel file uploads but no invoices are created:**"))
        issue5_cause_list = get_text("troubleshooting.issue5_cause_list", [])
        for cause in issue5_cause_list:
            st.markdown(f"- {cause}")
        
        st.markdown(get_text("troubleshooting.issue5_solutions", "**SOLUTION:**"))
        issue5_solution_list = get_text("troubleshooting.issue5_solution_list", [])
        for solution in issue5_solution_list:
            st.markdown(f"- {solution}")
    
    st.subheader(get_text("troubleshooting.getting_help", "📞 Getting Help"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(get_text("troubleshooting.before_help", "#### Before Asking for Help:"))
        before_help_list = get_text("troubleshooting.before_help_list", [])
        for i, item in enumerate(before_help_list, 1):
            st.markdown(f"{i}. {item}")
    
    with col2:
        st.markdown(get_text("troubleshooting.when_contacting", "#### When Contacting Support:"))
        when_contacting_list = get_text("troubleshooting.when_contacting_list", [])
        for item in when_contacting_list:
            st.markdown(f"- {item}")
    
    st.markdown("---")
    
    st.subheader(get_text("troubleshooting.pro_tips", "💡 Pro Tips for Success"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(get_text("troubleshooting.excel_tips", "#### Excel File Tips:"))
        excel_tips_list = get_text("troubleshooting.excel_tips_list", [])
        for tip in excel_tips_list:
            st.markdown(f"- {tip}")
    
    with col2:
        st.markdown(get_text("troubleshooting.data_tips", "#### Data Management:"))
        data_tips_list = get_text("troubleshooting.data_tips_list", [])
        for tip in data_tips_list:
            st.markdown(f"- {tip}")
    
    with col3:
        st.markdown(get_text("troubleshooting.system_tips", "#### System Usage:"))
        system_tips_list = get_text("troubleshooting.system_tips_list", [])
        for tip in system_tips_list:
            st.markdown(f"- {tip}")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>{get_text("footer.help_contact", "📧 Need more help? Contact your system administrator")}</p>
    <p>{get_text("footer.last_updated", "🔄 Last updated: JULY 2025")}</p>
</div>
""", unsafe_allow_html=True)