import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from login import (
    check_authentication, show_logout_button, show_user_info,
    get_storage_stats, cleanup_old_data, optimize_database,
    get_storage_recommendations, update_storage_config,
    STORAGE_CLEANUP_CONFIG
)

# --- Authentication Check ---
user_info = check_authentication()
if not user_info:
    st.stop()

# Check if user is admin
if user_info['role'] != 'admin':
    st.error("Access denied. Admin privileges required.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Storage Manager",
    page_icon="💾",
    layout="wide"
)

st.title("💾 Storage Manager")
st.info("Monitor and manage database storage, cleanup old data, and optimize performance.")

# Show user info and logout button in sidebar
show_user_info()
show_logout_button()

# --- Storage Statistics ---
st.header("📊 Storage Statistics")

# Get current storage stats
storage_stats = get_storage_stats()

if storage_stats:
    # Overall database size
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
        # Calculate growth rate (placeholder for now)
        st.metric("Growth Rate", "N/A")
    
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
else:
    st.error("Could not retrieve storage statistics.")

# --- Storage Recommendations ---
st.header("💡 Storage Recommendations")

recommendations = get_storage_recommendations()

if recommendations:
    for rec in recommendations:
        if rec['type'] == 'warning':
            st.warning(f"⚠️ {rec['message']}")
            st.info(f"**Action:** {rec['action']}")
        elif rec['type'] == 'info':
            st.info(f"ℹ️ {rec['message']}")
            st.info(f"**Action:** {rec['action']}")
else:
    st.success("✅ No storage optimization recommendations at this time.")

# --- Storage Configuration ---
st.header("⚙️ Storage Configuration")

with st.expander("Configure Storage Settings"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retention Periods")
        
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
        
        session_cleanup = st.number_input(
            "Session Cleanup Interval (hours)",
            min_value=1,
            max_value=168,
            value=STORAGE_CLEANUP_CONFIG.get('sessions_cleanup_hours', 24),
            help="How often to clean expired sessions"
        )
    
    with col2:
        st.subheader("Cleanup Settings")
        
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
        
        max_json_size = st.number_input(
            "Maximum JSON Size per Record (KB)",
            min_value=1,
            max_value=1000,
            value=STORAGE_CLEANUP_CONFIG.get('max_json_size_kb', 50),
            help="Maximum size for JSON data in activity records"
        )
    
    if st.button("💾 Save Configuration"):
        new_config = {
            'business_activities_retention_days': business_retention,
            'security_audit_retention_days': security_retention,
            'sessions_cleanup_hours': session_cleanup,
            'auto_cleanup_enabled': auto_cleanup,
            'archive_old_data': archive_data,
            'max_json_size_kb': max_json_size
        }
        
        result = update_storage_config(new_config)
        if result['success']:
            st.success(result['message'])
            st.rerun()
        else:
            st.error(result['message'])

# --- Manual Cleanup ---
st.header("🧹 Manual Cleanup")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Clean Old Data")
    
    cleanup_days = st.number_input(
        "Clean data older than (days)",
        min_value=1,
        max_value=365,
        value=90,
        help="Remove data older than specified days"
    )
    
    if st.button("🗑️ Clean Old Data"):
        with st.spinner("Cleaning old data..."):
            result = cleanup_old_data(days_back=cleanup_days, force=True)
            
        if result['success']:
            st.success(result['message'])
            if 'stats' in result:
                stats = result['stats']
                st.info(f"Cleaned: {stats['business_activities_cleaned']} business activities, "
                       f"{stats['security_audit_cleaned']} security logs, "
                       f"{stats['sessions_cleaned']} sessions")
                if stats['archived_files']:
                    st.info(f"Archived to: {', '.join(stats['archived_files'])}")
            st.rerun()
        else:
            st.error(result['message'])

with col2:
    st.subheader("Database Optimization")
    
    st.info("Optimize database performance and reclaim space")
    
    if st.button("⚡ Optimize Database"):
        with st.spinner("Optimizing database..."):
            result = optimize_database()
            
        if result['success']:
            st.success(result['message'])
            st.rerun()
        else:
            st.error(result['message'])

with col3:
    st.subheader("Quick Actions")
    
    if st.button("🔄 Refresh Statistics"):
        st.rerun()
    
    if st.button("📊 Export Storage Report"):
        if storage_stats:
            # Create a comprehensive report
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'total_size_kb': storage_stats.get('total_size_kb', 0),
                'tables': storage_stats.get('tables', {}),
                'recommendations': recommendations
            }
            
            import json
            report_json = json.dumps(report_data, indent=2)
            
            st.download_button(
                label="📥 Download Storage Report (JSON)",
                data=report_json,
                file_name=f"storage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# --- Archive Management ---
st.header("📁 Archive Management")

# Check for existing archives
import os
archive_path = STORAGE_CLEANUP_CONFIG.get('archive_path', 'data/archives/')

if os.path.exists(archive_path):
    archive_files = [f for f in os.listdir(archive_path) if f.endswith('.json')]
    
    if archive_files:
        st.subheader("📋 Existing Archives")
        
        archive_data = []
        for file in archive_files:
            file_path = os.path.join(archive_path, file)
            file_size = os.path.getsize(file_path)
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            archive_data.append({
                'File': file,
                'Size (KB)': round(file_size / 1024, 2),
                'Date': file_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        archive_df = pd.DataFrame(archive_data)
        st.dataframe(archive_df, use_container_width=True)
        
        # Archive actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete All Archives"):
                if st.checkbox("I confirm I want to delete all archive files"):
                    deleted_count = 0
                    for file in archive_files:
                        try:
                            os.remove(os.path.join(archive_path, file))
                            deleted_count += 1
                        except Exception as e:
                            st.error(f"Failed to delete {file}: {e}")
                    
                    st.success(f"Deleted {deleted_count} archive files")
                    st.rerun()
        
        with col2:
            if st.button("📥 Download All Archives"):
                import zipfile
                import io
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for file in archive_files:
                        file_path = os.path.join(archive_path, file)
                        zip_file.write(file_path, file)
                
                st.download_button(
                    label="📥 Download Archives (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"archives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
    else:
        st.info("No archive files found.")
else:
    st.info("Archive directory does not exist yet.")

# --- Storage Health Monitor ---
st.header("🏥 Storage Health Monitor")

# Create a simple health score
if storage_stats:
    total_size = storage_stats.get('total_size_kb', 0)
    tables = storage_stats.get('tables', {})
    
    # Calculate health score (0-100)
    health_score = 100
    
    # Deduct points for large database
    if total_size > 10000:  # 10MB
        health_score -= 20
    elif total_size > 5000:  # 5MB
        health_score -= 10
    
    # Deduct points for large tables
    for table_name, table_info in tables.items():
        count = table_info.get('count', 0)
        if table_name == 'business_activities' and count > 10000:
            health_score -= 15
        elif table_name == 'security_audit' and count > 50000:
            health_score -= 15
    
    # Ensure score doesn't go below 0
    health_score = max(0, health_score)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if health_score >= 80:
            st.success(f"🏥 Health Score: {health_score}/100")
        elif health_score >= 60:
            st.warning(f"🏥 Health Score: {health_score}/100")
        else:
            st.error(f"🏥 Health Score: {health_score}/100")
    
    with col2:
        if total_size < 1000:
            st.success("📊 Database Size: Good")
        elif total_size < 5000:
            st.warning("📊 Database Size: Moderate")
        else:
            st.error("📊 Database Size: Large")
    
    with col3:
        if len(recommendations) == 0:
            st.success("💡 Recommendations: None")
        elif len(recommendations) <= 2:
            st.warning(f"💡 Recommendations: {len(recommendations)}")
        else:
            st.error(f"💡 Recommendations: {len(recommendations)}")

# --- Footer ---
st.markdown("---")
st.markdown("*Storage Manager - Monitor and optimize your database storage efficiently*") 