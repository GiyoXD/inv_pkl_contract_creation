import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from login import (
    get_security_events, get_business_activities, get_storage_stats,
    cleanup_old_data, optimize_database, get_storage_recommendations,
    update_storage_config, STORAGE_CLEANUP_CONFIG,
    get_all_users, create_user, update_user, delete_user, reset_user_password,
    get_active_sessions, clear_expired_sessions, unblock_user,
    generate_registration_token, get_all_registration_tokens, revoke_registration_token,
    cleanup_expired_tokens, get_token_cleanup_stats
)
from auth_wrapper import setup_page_auth, show_session_status, create_admin_check_decorator

# --- Enhanced Admin Authentication Setup ---
user_info = setup_page_auth(
    page_title="Admin Dashboard", 
    page_name="Admin Dashboard",
    admin_required=True,
    layout="wide"
)

st.title("🛡️ Admin Dashboard")
st.info("Comprehensive system monitoring, security, and storage management.")

# Show session status in sidebar
show_session_status()
show_session_status()

# --- Tab Navigation ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview", 
    "🔒 Security Monitor", 
    "📋 Activity Monitor", 
    "💾 Storage Manager",
    "👥 User Management",
    "🔑 Token Management"
])

# --- Tab 1: Overview ---
with tab1:
    st.header("📊 System Overview")
    
    # Get all statistics
    try:
        security_events = get_security_events(limit=100)
        business_activities = get_business_activities(limit=100)
        storage_stats = get_storage_stats()
        
        # System health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Security health
            if security_events:
                failed_logins = len([e for e in security_events if e.get('action') == 'LOGIN_FAILED'])
                total_logins = len([e for e in security_events if 'LOGIN' in e.get('action', '')])
                security_score = max(0, 100 - (failed_logins * 10)) if total_logins > 0 else 100
                
                if security_score >= 80:
                    st.success(f"🔒 Security: {security_score}/100")
                elif security_score >= 60:
                    st.warning(f"🔒 Security: {security_score}/100")
                else:
                    st.error(f"🔒 Security: {security_score}/100")
            else:
                st.info("🔒 Security: No data")
        
        with col2:
            # Activity health
            if business_activities:
                recent_activities = len([a for a in business_activities 
                                       if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(days=1)])
                activity_score = min(100, recent_activities * 10)
                
                if activity_score >= 50:
                    st.success(f"📋 Activity: {activity_score}/100")
                elif activity_score >= 20:
                    st.warning(f"📋 Activity: {activity_score}/100")
                else:
                    st.error(f"📋 Activity: {activity_score}/100")
            else:
                st.info("📋 Activity: No data")
        
        with col3:
            # Storage health
            if storage_stats:
                total_size = storage_stats.get('total_size_kb', 0)
                if total_size < 1000:
                    st.success("💾 Storage: Good")
                elif total_size < 5000:
                    st.warning("💾 Storage: Moderate")
                else:
                    st.error("💾 Storage: Large")
            else:
                st.info("💾 Storage: No data")
        
        with col4:
            # Overall system health
            overall_score = 0
            count = 0
            
            if security_events:
                overall_score += security_score
                count += 1
            
            if business_activities:
                overall_score += activity_score
                count += 1
            
            if storage_stats:
                storage_score = 100 if total_size < 1000 else (80 if total_size < 5000 else 60)
                overall_score += storage_score
                count += 1
            
            if count > 0:
                overall_score = overall_score // count
                
                if overall_score >= 80:
                    st.success(f"🏥 Overall: {overall_score}/100")
                elif overall_score >= 60:
                    st.warning(f"🏥 Overall: {overall_score}/100")
                else:
                    st.error(f"🏥 Overall: {overall_score}/100")
            else:
                st.info("🏥 Overall: No data")
        
        # Recent activity summary
        st.subheader("📈 Recent Activity Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if security_events:
                st.write("**Recent Security Events:**")
                recent_security = security_events[:5]
                for event in recent_security:
                    timestamp = datetime.fromisoformat(event['timestamp']).strftime('%H:%M:%S')
                    action = event.get('action', 'Unknown')
                    username = event.get('username', 'Unknown')
                    st.write(f"• {timestamp} - {username}: {action}")
            else:
                st.info("No recent security events")
        
        with col2:
            if business_activities:
                st.write("**Recent Business Activities:**")
                recent_business = business_activities[:5]
                for activity in recent_business:
                    timestamp = datetime.fromisoformat(activity['timestamp']).strftime('%H:%M:%S')
                    activity_type = activity.get('activity_type', 'Unknown')
                    username = activity.get('username', 'Unknown')
                    invoice_no = activity.get('target_invoice_no', 'N/A')
                    st.write(f"• {timestamp} - {username}: {activity_type} (INV: {invoice_no})")
            else:
                st.info("No recent business activities")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh All Data", key="refresh_all_data"):
                st.rerun()
        
        with col2:
            if st.button("🧹 Quick Cleanup", key="quick_cleanup"):
                with st.spinner("Running quick cleanup..."):
                    result = cleanup_old_data(days_back=30, force=True)
                if result['success']:
                    st.success("Quick cleanup completed!")
                    st.rerun()
                else:
                    st.error("Cleanup failed!")
        
        with col3:
            if st.button("⚡ Optimize Database", key="optimize_db_overview"):
                with st.spinner("Optimizing database..."):
                    result = optimize_database()
                if result['success']:
                    st.success("Database optimized!")
                    st.rerun()
                else:
                    st.error("Optimization failed!")
        
    except Exception as e:
        st.error(f"Error loading overview data: {e}")

# --- Tab 2: Security Monitor ---
with tab2:
    st.header("🔒 Security Monitor")
    st.info("Monitor security events, login attempts, and system access.")
    
    # Security filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        action_filter = st.selectbox(
            "Filter by Action",
            ["All", "LOGIN_SUCCESS", "LOGIN_FAILED", "LOGOUT", "ACCOUNT_LOCKED", "RATE_LIMIT_EXCEEDED"]
        )
    
    with col2:
        success_filter = st.selectbox(
            "Filter by Success",
            ["All", "Success", "Failed"]
        )
    
    with col3:
        days_filter = st.number_input(
            "Days to look back",
            min_value=1,
            max_value=30,
            value=7
        )
    
    # Get security events
    try:
        security_events = get_security_events(limit=1000)
        
        if security_events:
            # Filter events
            filtered_events = security_events
            
            if action_filter != "All":
                filtered_events = [e for e in filtered_events if e.get('action') == action_filter]
            
            if success_filter == "Success":
                filtered_events = [e for e in filtered_events if e.get('success') == True]
            elif success_filter == "Failed":
                filtered_events = [e for e in filtered_events if e.get('success') == False]
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days_filter)
            filtered_events = [e for e in filtered_events 
                             if datetime.fromisoformat(e['timestamp']) > cutoff_date]
            
            # Security summary
            st.subheader("📊 Security Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_events = len(filtered_events)
                st.metric("Total Events", total_events)
            
            with col2:
                failed_logins = len([e for e in filtered_events if e.get('action') == 'LOGIN_FAILED'])
                st.metric("Failed Logins", failed_logins)
            
            with col3:
                unique_users = len(set(e.get('username', '') for e in filtered_events if e.get('username')))
                st.metric("Unique Users", unique_users)
            
            with col4:
                unique_ips = len(set(e.get('ip_address', '') for e in filtered_events if e.get('ip_address')))
                st.metric("Unique IPs", unique_ips)
            
            # Security events table
            st.subheader("📋 Security Events")
            
            if filtered_events:
                # Prepare data for display
                display_data = []
                for event in filtered_events:
                    timestamp = datetime.fromisoformat(event['timestamp'])
                    display_data.append({
                        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Username': event.get('username', 'N/A'),
                        'Action': event.get('action', 'N/A'),
                        'IP Address': event.get('ip_address', 'N/A'),
                        'User Agent': event.get('user_agent', 'N/A')[:50] + '...' if event.get('user_agent') and len(event.get('user_agent', '')) > 50 else event.get('user_agent', 'N/A'),
                        'Success': '✅' if event.get('success') else '❌',
                        'Details': event.get('details', 'N/A')[:100] + '...' if event.get('details') and len(event.get('details', '')) > 100 else event.get('details', 'N/A')
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Export option
                if st.button("📥 Export Security Events", key="export_security_events"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"security_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No security events found with current filters.")
        else:
            st.info("No security events available.")
            
    except Exception as e:
        st.error(f"Error loading security data: {e}")

# --- Tab 3: Activity Monitor ---
with tab3:
    st.header("📋 Activity Monitor")
    st.info("Track business activities, data verification, and invoice operations.")
    
    # Activity filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        activity_type_filter = st.selectbox(
            "Filter by Activity Type",
            ["All", "DATA_VERIFICATION", "DATA_AMENDMENT", "INVOICE_EDIT", "INVOICE_VOID", "INVOICE_REACTIVATE", "INVOICE_DELETE"]
        )
    
    with col2:
        username_filter = st.text_input("Filter by Username", "")
    
    with col3:
        invoice_no_filter = st.text_input("Filter by Invoice No", "")
    
    with col4:
        activity_days_filter = st.number_input(
            "Days to look back",
            min_value=1,
            max_value=90,
            value=7
        )
    
    # Get business activities
    try:
        business_activities = get_business_activities(limit=1000)
        
        if business_activities:
            # Filter activities
            filtered_activities = business_activities
            
            if activity_type_filter != "All":
                filtered_activities = [a for a in filtered_activities if a.get('activity_type') == activity_type_filter]
            
            if username_filter:
                filtered_activities = [a for a in filtered_activities 
                                     if username_filter.lower() in a.get('username', '').lower()]
            
            if invoice_no_filter:
                filtered_activities = [a for a in filtered_activities 
                                     if invoice_no_filter.lower() in a.get('target_invoice_no', '').lower()]
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=activity_days_filter)
            filtered_activities = [a for a in filtered_activities 
                                 if datetime.fromisoformat(a['timestamp']) > cutoff_date]
            
            # Activity summary
            st.subheader("📊 Activity Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_activities = len(filtered_activities)
                st.metric("Total Activities", total_activities)
            
            with col2:
                unique_users = len(set(a.get('username', '') for a in filtered_activities if a.get('username')))
                st.metric("Active Users", unique_users)
            
            with col3:
                unique_invoices = len(set(a.get('target_invoice_no', '') for a in filtered_activities if a.get('target_invoice_no')))
                st.metric("Invoices Affected", unique_invoices)
            
            with col4:
                successful_activities = len([a for a in filtered_activities if a.get('success')])
                st.metric("Successful", successful_activities)
            
            # Activity breakdown chart
            if filtered_activities:
                activity_counts = {}
                for activity in filtered_activities:
                    activity_type = activity.get('activity_type', 'Unknown')
                    activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
                
                if activity_counts:
                    st.subheader("📈 Activity Breakdown")
                    
                    # Create pie chart
                    fig = px.pie(
                        values=list(activity_counts.values()),
                        names=list(activity_counts.keys()),
                        title="Activity Type Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Activities table
            st.subheader("📋 Business Activities")
            
            if filtered_activities:
                # Prepare data for display
                display_data = []
                for activity in filtered_activities:
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    display_data.append({
                        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'Username': activity.get('username', 'N/A'),
                        'Activity Type': activity.get('activity_type', 'N/A'),
                        'Invoice No': activity.get('target_invoice_no', 'N/A'),
                        'Invoice Ref': activity.get('target_invoice_ref', 'N/A'),
                        'Description': activity.get('action_description', 'N/A')[:100] + '...' if activity.get('action_description') and len(activity.get('action_description', '')) > 100 else activity.get('action_description', 'N/A'),
                        'Success': '✅' if activity.get('success') else '❌',
                        'IP Address': activity.get('ip_address', 'N/A')
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
                
                # Export option
                if st.button("📥 Export Business Activities", key="export_business_activities"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"business_activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No business activities found with current filters.")
        else:
            st.info("No business activities available.")
            
    except Exception as e:
        st.error(f"Error loading activity data: {e}")

# --- Tab 4: Storage Manager ---
with tab4:
    st.header("💾 Storage Manager")
    st.info("Monitor and manage database storage, cleanup old data, and optimize performance.")
    
    # Get current storage stats
    storage_stats = get_storage_stats()
    
    if storage_stats:
        # Overall database size
        st.subheader("📊 Storage Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_size = storage_stats.get('total_size_kb', 0)
            st.metric("Total Database Size", f"{total_size:.1f} KB")
        with col2:
            total_size_mb = total_size / 1024
            st.metric("Total Database Size", f"{total_size_mb:.2f} MB")
        with col3:
            tables = storage_stats.get('tables', {})
            total_records = sum(table.get('count', 0) for table in tables.values())
            st.metric("Total Records", f"{total_records:,}")
        with col4:
            # Health indicator
            if total_size < 1000:
                st.success("Health: Good")
            elif total_size < 5000:
                st.warning("Health: Moderate")
            else:
                st.error("Health: Large")
        
        # Table breakdown
        st.subheader("📋 Table Breakdown")
        
        if tables:
            table_data = []
            for table_name, table_info in tables.items():
                table_data.append({
                    'Table': table_name.replace('_', ' ').title(),
                    'Records': table_info.get('count', 0),
                    'Size (KB)': table_info.get('estimated_size_kb', 0),
                    'Size (MB)': round(table_info.get('estimated_size_kb', 0) / 1024, 2)
                })
            
            table_df = pd.DataFrame(table_data)
            st.dataframe(table_df, use_container_width=True)
            
            # Visual representation
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📈 Records by Table")
                st.bar_chart(table_df.set_index('Table')['Records'])
            
            with col2:
                st.subheader("📊 Size by Table (MB)")
                st.bar_chart(table_df.set_index('Table')['Size (MB)'])
    
    # Storage recommendations
    st.subheader("💡 Storage Recommendations")
    
    recommendations_result = get_storage_recommendations()
    
    if recommendations_result['success']:
        recommendations = recommendations_result.get('recommendations', [])
        
        if recommendations:
            for rec in recommendations:
                if rec['type'] == 'cleanup':
                    if rec['priority'] == 'high':
                        st.error(f"🔴 **{rec['title']}**: {rec['description']}")
                    elif rec['priority'] == 'medium':
                        st.warning(f"🟡 **{rec['title']}**: {rec['description']}")
                    else:
                        st.info(f"🔵 **{rec['title']}**: {rec['description']}")
                elif rec['type'] == 'optimization':
                    st.info(f"⚡ **{rec['title']}**: {rec['description']}")
                
                st.caption(f"**Recommended action:** {rec['action']}")
                st.divider()
        else:
            st.success("✅ No storage optimization recommendations at this time.")
            
        # Show database size info
        db_size_mb = recommendations_result.get('db_size_mb', 0)
        st.metric("Database Size", f"{db_size_mb:.2f} MB")
    else:
        st.error(f"❌ Error getting recommendations: {recommendations_result.get('message', 'Unknown error')}")
    
    # Storage configuration
    st.subheader("⚙️ Storage Configuration")
    
    with st.expander("Configure Storage Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Retention Periods**")
            
            business_retention = st.number_input(
                "Business Activities Retention (days)",
                min_value=7,
                max_value=365,
                value=STORAGE_CLEANUP_CONFIG.get('business_activities_retention_days', 90),
                help="How long to keep business activity records"
            )
            
            security_retention = st.number_input(
                "Security Audit Retention (days)",
                min_value=30,
                max_value=730,
                value=STORAGE_CLEANUP_CONFIG.get('security_audit_retention_days', 180),
                help="How long to keep security audit logs"
            )
        
        with col2:
            st.write("**Cleanup Settings**")
            
            auto_cleanup = st.checkbox(
                "Enable Automatic Cleanup",
                value=STORAGE_CLEANUP_CONFIG.get('auto_cleanup_enabled', True),
                help="Automatically clean old data based on retention policies"
            )
            
            archive_data = st.checkbox(
                "Archive Old Data",
                value=STORAGE_CLEANUP_CONFIG.get('archive_old_data', True),
                help="Archive old data to files instead of deleting"
            )
        
        if st.button("💾 Save Configuration", key="save_storage_config"):
            new_config = {
                'business_activities_retention_days': business_retention,
                'security_audit_retention_days': security_retention,
                'sessions_cleanup_hours': STORAGE_CLEANUP_CONFIG.get('sessions_cleanup_hours', 24),
                'auto_cleanup_enabled': auto_cleanup,
                'archive_old_data': archive_data,
                'max_json_size_kb': STORAGE_CLEANUP_CONFIG.get('max_json_size_kb', 50)
            }
            
            result = update_storage_config(new_config)
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['message'])
    
    # Manual cleanup
    st.subheader("🧹 Manual Cleanup")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Clean Old Data**")
        
        cleanup_days = st.number_input(
            "Clean data older than (days)",
            min_value=1,
            max_value=365,
            value=90,
            help="Remove data older than specified days"
        )
        
        if st.button("🗑️ Clean Old Data", key="clean_old_data"):
            with st.spinner("Cleaning old data..."):
                result = cleanup_old_data(days_back=cleanup_days, force=True)
                
            if result['success']:
                st.success(result['message'])
                if 'stats' in result:
                    stats = result['stats']
                    st.info(f"Cleaned: {stats['business_activities_cleaned']} business activities, "
                           f"{stats['security_events_cleaned']} security events, "
                           f"{stats['sessions_cleaned']} sessions, "
                           f"{stats['tokens_cleaned']} tokens")
                st.rerun()
            else:
                st.error(result['message'])
    
    with col2:
        st.write("**Database Optimization**")
        
        st.info("Optimize database performance and reclaim space")
        
        if st.button("⚡ Optimize Database", key="optimize_db_storage"):
            with st.spinner("Optimizing database..."):
                result = optimize_database()
                
            if result['success']:
                st.success(result['message'])
                st.rerun()
            else:
                st.error(result['message'])
    
    with col3:
        st.write("**Quick Actions**")
        
        if st.button("🔄 Refresh Statistics", key="refresh_storage_stats"):
            st.rerun()
        
        if st.button("📊 Export Storage Report", key="export_storage_report"):
            if storage_stats:
                # Create a comprehensive report
                report_data = {
                    'timestamp': datetime.now().isoformat(),
                    'total_size_kb': storage_stats.get('total_size_kb', 0),
                    'tables': storage_stats.get('tables', {}),
                    'recommendations': recommendations
                }
                
                report_json = json.dumps(report_data, indent=2)
                
                st.download_button(
                    label="📥 Download Storage Report (JSON)",
                    data=report_json,
                    file_name=f"storage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

# --- Tab 5: User Management ---
with tab5:
    st.header("👥 User Management")
    st.info("Manage users, their permissions, and active sessions.")
    
    # User Management Tabs
    user_tab1, user_tab2, user_tab3 = st.tabs(["📋 User List", "➕ Create New User", "🔐 Active Sessions"])
    
    with user_tab1:
        st.subheader("📋 Current Users")
        
        # Get all users
        users = get_all_users()
        
        if not users:
            st.info("No users found in the database.")
        else:
            # Display users in a nice format
            for user in users:
                with st.expander(f"👤 {user['username']} ({user['role'].title()})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Username:** {user['username']}")
                        st.write(f"**Role:** {user['role'].title()}")
                        st.write(f"**Status:** {'🟢 Active' if user['is_active'] else '🔴 Inactive'}")
                        
                        # Show lock status
                        if user.get('is_locked'):
                            st.write(f"**🔒 Lock Status:** {user['lock_status']}")
                            st.write(f"**Failed Attempts:** {user.get('failed_attempts', 0)}")
                        elif user.get('failed_attempts', 0) > 0:
                            st.write(f"**⚠️ Failed Attempts:** {user.get('failed_attempts', 0)}")
                        else:
                            st.write("**🔓 Lock Status:** Unlocked")
                        
                        st.write(f"**Created:** {user['created_at']}")
                        if user['last_login']:
                            st.write(f"**Last Login:** {user['last_login']}")
                    
                    with col2:
                        if user['username'] != 'menchayheng':  # Don't allow editing admin
                            if st.button(f"Edit {user['username']}", key=f"edit_{user['id']}"):
                                st.session_state[f"editing_user_{user['id']}"] = True
                        
                        # Add unblock button for locked users
                        if user.get('is_locked') or user.get('failed_attempts', 0) > 0:
                            if st.button(f"🔓 Unblock {user['username']}", key=f"unblock_{user['id']}"):
                                success, message = unblock_user(user['id'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                    
                    with col3:
                        if user['username'] != 'menchayheng':  # Don't allow deleting admin
                            if st.button(f"Delete {user['username']}", key=f"delete_{user['id']}"):
                                success, message = delete_user(user['id'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                    
                    # Edit form
                    if st.session_state.get(f"editing_user_{user['id']}", False):
                        with st.form(f"edit_form_{user['id']}"):
                            new_username = st.text_input("Username", value=user['username'], key=f"username_{user['id']}")
                            new_role = st.selectbox("Role", ["user", "admin"], index=0 if user['role'] == 'user' else 1, key=f"role_{user['id']}")
                            new_status = st.checkbox("Active", value=bool(user['is_active']), key=f"status_{user['id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Update User"):
                                    success, message = update_user(user['id'], new_username, new_role, new_status)
                                    if success:
                                        st.success(message)
                                        del st.session_state[f"editing_user_{user['id']}"]
                                        st.rerun()
                                    else:
                                        st.error(message)
                            
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    del st.session_state[f"editing_user_{user['id']}"]
                                    st.rerun()
                    
                    # Password reset form
                    if st.session_state.get(f"reset_password_{user['id']}", False):
                        with st.form(f"password_form_{user['id']}"):
                            new_password = st.text_input("New Password", type="password", key=f"new_pass_{user['id']}")
                            confirm_password = st.text_input("Confirm Password", type="password", key=f"confirm_pass_{user['id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Reset Password"):
                                    if new_password == confirm_password and new_password:
                                        success, message = reset_user_password(user['id'], new_password)
                                        if success:
                                            st.success(message)
                                            del st.session_state[f"reset_password_{user['id']}"]
                                            st.rerun()
                                        else:
                                            st.error(message)
                                    else:
                                        st.error("Passwords don't match or are empty!")
                            
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    del st.session_state[f"reset_password_{user['id']}"]
                                    st.rerun()
    
    with user_tab2:
        st.subheader("➕ Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username", placeholder="Enter username")
            new_password = st.text_input("Password", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            new_role = st.selectbox("Role", ["user", "admin"], help="Admin users have full access to all features")
            
            if st.form_submit_button("Create User"):
                if not new_username or not new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    success, message = create_user(new_username, new_password, new_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with user_tab3:
        st.subheader("🔐 Active Sessions")
        
        sessions = get_active_sessions()
        
        if not sessions:
            st.info("No active sessions found.")
        else:
            # Display sessions in a table
            session_data = []
            for session in sessions:
                session_data.append({
                    'Username': session['username'],
                    'Session Token': session['session_token'][:20] + '...',
                    'Created': session['created_at'],
                    'Expires': session['expires_at']
                })
            
            df = pd.DataFrame(session_data)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Clear All Expired Sessions", key="clear_sessions"):
                success, message = clear_expired_sessions()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# --- Tab 6: Token Management ---
with tab6:
    st.header("🔑 Registration Token Management")
    st.info("Generate and manage invitation tokens for user registration.")
    
    # Token Management Tabs
    token_tab1, token_tab2, token_tab3 = st.tabs(["🔑 Generate Tokens", "📋 Token List", "🧹 Token Cleanup"])
    
    with token_tab1:
        st.subheader("🔑 Generate New Registration Token")
        
        with st.form("generate_token_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                max_uses = st.number_input(
                    "Maximum Uses",
                    min_value=1,
                    max_value=10,
                    value=1,
                    help="How many times this token can be used"
                )
                
                expiry_days = st.number_input(
                    "Expiry Days",
                    min_value=1,
                    max_value=30,
                    value=7,
                    help="How many days until the token expires"
                )
            
            with col2:
                st.write("**Token Settings:**")
                st.write(f"• Max uses: {max_uses}")
                st.write(f"• Expires in: {expiry_days} days")
                st.write(f"• Created by: {user_info['username']}")
            
            if st.form_submit_button("🔑 Generate Token"):
                with st.spinner("Generating token..."):
                    # Convert days to hours for the function
                    expires_hours = expiry_days * 24
                    try:
                        result = generate_registration_token(
                            user_info['user_id'], 
                            max_uses, 
                            expires_hours
                        )
                        success = result is not None
                    except Exception as e:
                        success = False
                        result = str(e)
                
                if success:
                    st.success("✅ Token generated successfully!")
                    
                    # Display the token
                    st.subheader("📋 Generated Token")
                    st.code(result, language="text")
                    
                    # Copy button
                    st.info("⚠️ **Important:** Copy this token now! It won't be shown again for security reasons.")
                    
                    # Token info
                    expiry_date = datetime.now() + timedelta(days=expiry_days)
                    st.write(f"**Token expires:** {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Registration URL:** `http://your-domain/register`")
                    
                else:
                    st.error(f"❌ Failed to generate token: {result}")
    
    with token_tab2:
        st.subheader("📋 All Registration Tokens")
        
        tokens = get_all_registration_tokens()
        
        if not tokens:
            st.info("No registration tokens found.")
        else:
            # Process tokens to add display fields
            from datetime import datetime
            
            for token in tokens:
                # Add display_token (first 8 chars + ...)
                token['display_token'] = token['token'][:8] + "..."
                
                # Determine status
                now = datetime.now()
                expires_at = None
                
                # Parse expires_at safely
                if token['expires_at']:
                    try:
                        # Handle different datetime formats
                        expires_str = token['expires_at']
                        if 'T' in expires_str:
                            expires_at = datetime.fromisoformat(expires_str.replace('Z', ''))
                        else:
                            # Try with microseconds first, then without
                            try:
                                expires_at = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S.%f')
                            except ValueError:
                                expires_at = datetime.strptime(expires_str, '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        expires_at = None
                
                # Determine status
                if not token['is_active']:
                    token['status'] = "Inactive"
                elif token['used_count'] >= token['max_uses']:
                    token['status'] = "Used Up"
                elif expires_at and expires_at < now:
                    token['status'] = "Expired"
                else:
                    token['status'] = "Active"
            
            # Display tokens in a nice format
            for token in tokens:
                with st.expander(f"🔑 {token['display_token']} - {token['status']}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Token:** {token['display_token']}")
                        st.write(f"**Created by:** {token['created_by_username']}")
                        st.write(f"**Created:** {token['created_at']}")
                        st.write(f"**Expires:** {token['expires_at']}")
                    
                    with col2:
                        st.write(f"**Status:** {token['status']}")
                        st.write(f"**Used:** {token['used_count']}/{token['max_uses']}")
                        # Note: used_by and used_at fields don't exist in current schema
                        # These would need to be added to the database if needed
                    
                    with col3:
                        # Show different actions based on token status
                        if token['status'] == "Active":
                            if st.button(f"🚫 Revoke Token", key=f"revoke_{token['id']}"):
                                success, message = revoke_registration_token(token['id'])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        else:
                            st.info("Token already used/expired")
            
            # Summary statistics
            st.divider()
            st.subheader("📊 Token Statistics")
            
            active_tokens = len([t for t in tokens if t['status'] == "Active"])
            used_tokens = len([t for t in tokens if t['status'] == "Used/Deactivated"])
            expired_tokens = len([t for t in tokens if t['status'] == "Expired"])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Active Tokens", active_tokens)
            
            with col2:
                st.metric("Used Tokens", used_tokens)
            
            with col3:
                st.metric("Expired Tokens", expired_tokens)

    with token_tab3:
        st.subheader("🧹 Token Cleanup")
        st.info("Clean up expired and used tokens to free up database space.")
        
        # Get token cleanup statistics
        token_stats = get_token_cleanup_stats()
        
        # Display current token statistics
        st.subheader("📊 Current Token Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tokens", token_stats['total_tokens'])
        
        with col2:
            st.metric("Expired Tokens", token_stats['expired_tokens'])
        
        with col3:
            st.metric("Used Tokens", token_stats['used_tokens'])
        
        with col4:
            st.metric("Cleanup Threshold", f"{token_stats['cleanup_threshold_days']} days")
        
        # Cleanup information
        st.subheader("ℹ️ Cleanup Information")
        
        st.write("**What gets cleaned up:**")
        st.write("• Expired tokens (past their expiry date)")
        st.write("• Used tokens (already consumed)")
        st.write("• Tokens older than 30 days (configurable)")
        
        st.write("**What stays:**")
        st.write("• Active tokens (not expired, not used)")
        st.write("• Recently used tokens (within 30 days)")
        
        # Manual cleanup button
        st.subheader("🔧 Manual Cleanup")
        
        if st.button("🧹 Clean Up Expired Tokens", key="cleanup_tokens"):
            with st.spinner("Cleaning up expired tokens..."):
                success, message = cleanup_expired_tokens()
            
            if success:
                st.success(f"✅ {message}")
                st.info("Token list will be refreshed automatically.")
                st.rerun()
            else:
                st.error(f"❌ {message}")
        
        # Automatic cleanup status
        st.subheader("⚙️ Automatic Cleanup")
        
        st.info("Token cleanup is automatically included in the main storage cleanup process.")
        st.write("• Runs with regular storage cleanup")
        st.write("• Configurable retention period (currently 30 days)")
        st.write("• Logged in security audit trail")
        
        if st.button("🔄 Refresh Token Statistics", key="refresh_token_stats"):
            st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown("*Admin Dashboard - Comprehensive system monitoring and management*") 