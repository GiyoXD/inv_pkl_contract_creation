import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from login import check_authentication, show_logout_button, show_user_info, get_business_activities, ACTIVITY_TYPES

# --- Authentication Check ---
user_info = check_authentication()
if not user_info:
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="Activity Monitor", layout="wide")
st.title("Activity Monitor 📊")
st.info("Track all user activities and data changes for accountability and audit purposes.")

# Show user info and logout button in sidebar
show_user_info()
show_logout_button()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Activity Filters")

# Date range filter
days_back = st.sidebar.slider("Days to look back:", 1, 90, 30, help="How many days of activity to display")

# Activity type filter
activity_types = ["All"] + list(ACTIVITY_TYPES.keys())
selected_activity = st.sidebar.selectbox("Activity Type:", activity_types)

# User filter (if admin)
if user_info['role'] == 'admin':
    # Get unique users from activities
    try:
        all_activities = get_business_activities(days_back=days_back)
        unique_users = ["All"] + sorted(all_activities['username'].unique().tolist()) if not all_activities.empty else ["All"]
        selected_user = st.sidebar.selectbox("User:", unique_users)
    except:
        selected_user = "All"
else:
    selected_user = user_info['username']

# Invoice filters - prioritize invoice number
invoice_no_filter = st.sidebar.text_input("Invoice Number:", placeholder="Filter by invoice number")
invoice_ref_filter = st.sidebar.text_input("Invoice Reference:", placeholder="Filter by invoice reference")

# Success status filter
success_filter = st.sidebar.selectbox("Status:", ["All", "Success", "Failed"])

# --- Main Content ---
st.header("📈 Activity Summary")

# Get activities based on filters
try:
    activities_df = get_business_activities(
        user_id=None if selected_user == "All" else None,  # We'll filter by username instead
        invoice_ref=invoice_ref_filter if invoice_ref_filter else None,
        invoice_no=invoice_no_filter if invoice_no_filter else None,
        activity_type=selected_activity if selected_activity != "All" else None,
        days_back=days_back
    )
    
    if not activities_df.empty:
        # Apply additional filters
        if selected_user != "All":
            activities_df = activities_df[activities_df['username'] == selected_user]
        
        if success_filter != "All":
            success_bool = success_filter == "Success"
            activities_df = activities_df[activities_df['success'] == success_bool]
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Activities", len(activities_df))
        
        with col2:
            successful = len(activities_df[activities_df['success'] == True])
            st.metric("Successful", successful)
        
        with col3:
            failed = len(activities_df[activities_df['success'] == False])
            st.metric("Failed", failed)
        
        with col4:
            # Count unique invoices - prioritize invoice number over reference
            unique_invoices = activities_df['target_invoice_no'].nunique() if 'target_invoice_no' in activities_df.columns else activities_df['target_invoice_ref'].nunique()
            st.metric("Invoices Affected", unique_invoices)
        
        # Activity type breakdown
        st.subheader("📊 Activity Breakdown")
        activity_counts = activities_df['activity_type'].value_counts()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.bar_chart(activity_counts)
        
        with col2:
            st.write("**Activity Types:**")
            for activity_type, count in activity_counts.items():
                st.write(f"• {ACTIVITY_TYPES.get(activity_type, activity_type)}: {count}")
        
        # Recent activities table
        st.subheader("🕒 Recent Activities")
        
        # Format the dataframe for display
        display_df = activities_df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['activity_type'] = display_df['activity_type'].map(lambda x: ACTIVITY_TYPES.get(x, x))
        display_df['success'] = display_df['success'].map({True: '✅', False: '❌'})
        
        # Select columns to display - prioritize invoice number
        columns_to_show = ['timestamp', 'username', 'activity_type', 'target_invoice_no', 'target_invoice_ref', 'action_description', 'success']
        display_df = display_df[columns_to_show]
        
        # Rename columns for better display
        display_df.columns = ['Timestamp', 'User', 'Activity Type', 'Invoice No', 'Invoice Ref', 'Description', 'Status']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Detailed view for selected activity
        st.subheader("🔍 Activity Details")
        
        if len(activities_df) > 0:
            # Create a selectbox for detailed view
            activity_options = []
            for idx, row in activities_df.iterrows():
                timestamp = pd.to_datetime(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                activity_type = ACTIVITY_TYPES.get(row['activity_type'], row['activity_type'])
                # Prioritize invoice number over reference
                invoice_identifier = row['target_invoice_no'] if pd.notna(row['target_invoice_no']) else row['target_invoice_ref']
                option_text = f"{timestamp} - {row['username']} - {activity_type} - {invoice_identifier}"
                activity_options.append((option_text, idx))
            
            selected_option, selected_idx = st.selectbox(
                "Select activity for detailed view:",
                options=activity_options,
                format_func=lambda x: x[0]
            )
            
            if selected_idx is not None:
                selected_activity = activities_df.iloc[selected_idx]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Activity Information:**")
                    st.write(f"**User:** {selected_activity['username']}")
                    st.write(f"**Activity Type:** {ACTIVITY_TYPES.get(selected_activity['activity_type'], selected_activity['activity_type'])}")
                    st.write(f"**Invoice Reference:** {selected_activity['target_invoice_ref']}")
                    st.write(f"**Invoice Number:** {selected_activity['target_invoice_no']}")
                    st.write(f"**Timestamp:** {pd.to_datetime(selected_activity['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Status:** {'✅ Success' if selected_activity['success'] else '❌ Failed'}")
                    st.write(f"**IP Address:** {selected_activity['ip_address']}")
                    st.write(f"**User Agent:** {selected_activity['user_agent']}")
                
                with col2:
                    st.write("**Action Description:**")
                    st.write(selected_activity['action_description'])
                    
                    if selected_activity['error_message']:
                        st.write("**Error Message:**")
                        st.error(selected_activity['error_message'])
                
                # Show old and new values if available
                if selected_activity['old_values'] or selected_activity['new_values']:
                    st.subheader("📋 Data Changes")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if selected_activity['old_values']:
                            st.write("**Previous Values:**")
                            try:
                                old_data = json.loads(selected_activity['old_values'])
                                st.json(old_data)
                            except:
                                st.code(selected_activity['old_values'])
                    
                    with col2:
                        if selected_activity['new_values']:
                            st.write("**New Values:**")
                            try:
                                new_data = json.loads(selected_activity['new_values'])
                                st.json(new_data)
                            except:
                                st.code(selected_activity['new_values'])
        
        # Export functionality
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export to CSV", use_container_width=True):
                csv = activities_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📋 Export to JSON", use_container_width=True):
                json_data = activities_df.to_json(orient='records', indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    else:
        st.info("No activities found for the selected filters.")
        st.write("Try adjusting the filters or increasing the time range.")

except Exception as e:
    st.error(f"Error loading activities: {e}")
    st.write("Please check if the database is accessible and try again.")

# --- Footer ---
st.markdown("---")
st.markdown("*Activity Monitor - Track all user actions for accountability and audit purposes*") 