import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from login import check_authentication, show_logout_button, show_user_info, get_security_stats, USER_DB_PATH

# --- Authentication Check ---
user_info = check_authentication()
if not user_info:
    st.stop()

# Check if user is admin
if user_info['role'] != 'admin':
    st.error("Access denied. Admin privileges required.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="Security Monitor", layout="wide")
st.title("🛡️ Security Monitor (Simple Version)")
st.info("Monitor security events, failed login attempts, and system threats.")

# Show user info and logout button in sidebar
show_user_info()
show_logout_button()

# Show current session info
st.sidebar.markdown("---")
st.sidebar.markdown("**🌐 Current Session Info:**")
from login import get_client_ip, get_user_agent
current_ip = get_client_ip()
current_ua = get_user_agent()
st.sidebar.markdown(f"**IP/ID**: {current_ip}")
st.sidebar.markdown(f"**User Agent**: {current_ua[:30]}...")
st.sidebar.markdown("---")

# --- Security Statistics Dashboard ---
st.header("📊 Security Statistics")

# Get security stats
stats = get_security_stats()

# Display key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Failed Logins (24h)",
        value=stats.get('failed_logins_24h', 0),
        delta=None
    )

with col2:
    st.metric(
        label="Locked Accounts",
        value=stats.get('locked_accounts', 0),
        delta=None
    )

with col3:
    st.metric(
        label="Active Sessions",
        value=stats.get('active_sessions', 0),
        delta=None
    )

with col4:
    st.metric(
        label="Rate Limited (1h)",
        value=stats.get('rate_limited_1h', 0),
        delta=None
    )

# --- Security Audit Log ---
st.header("📋 Security Audit Log")

# Date range filter
col1, col2 = st.columns(2)
with col1:
    days_back = st.selectbox("Show events from last:", [1, 7, 30, 90], index=1)
with col2:
    action_filter = st.selectbox("Filter by action:", ["All", "LOGIN_FAILED", "LOGIN_SUCCESS", "LOGIN_RATE_LIMITED", "LOGOUT", "ACCOUNT_LOCKED"])

try:
    conn = sqlite3.connect(USER_DB_PATH)
    
    # Build query based on filters
    query = '''
        SELECT 
            timestamp,
            username,
            action,
            ip_address,
            user_agent,
            success,
            details
        FROM security_audit
        WHERE timestamp > datetime('now', '-{} days')
    '''.format(days_back)
    
    if action_filter != "All":
        query += f" AND action = '{action_filter}'"
    
    query += " ORDER BY timestamp DESC LIMIT 1000"
    
    df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        # Format timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
        
        # Display the audit log
        st.dataframe(
            df[['date', 'time', 'username', 'action', 'ip_address', 'success', 'details']],
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Audit Log",
            data=csv,
            file_name=f"security_audit_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # --- Simple Security Analytics ---
        st.header("📈 Security Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Failed login attempts summary
            failed_logins = df[df['action'] == 'LOGIN_FAILED']
            if not failed_logins.empty:
                st.subheader("Failed Login Attempts")
                st.write(f"Total failed attempts: {len(failed_logins)}")
                
                # Show by hour
                failed_logins['hour'] = failed_logins['timestamp'].dt.hour
                hourly_failed = failed_logins.groupby('hour').size()
                st.write("Failed attempts by hour:")
                st.dataframe(hourly_failed.reset_index().rename(columns={0: 'Count', 'hour': 'Hour'}))
        
        with col2:
            # Success vs Failed summary
            login_attempts = df[df['action'].isin(['LOGIN_SUCCESS', 'LOGIN_FAILED'])]
            if not login_attempts.empty:
                st.subheader("Login Success vs Failed")
                success_count = len(login_attempts[login_attempts['success'] == True])
                failed_count = len(login_attempts[login_attempts['success'] == False])
                total_count = len(login_attempts)
                
                st.write(f"Total login attempts: {total_count}")
                st.write(f"Successful logins: {success_count}")
                st.write(f"Failed logins: {failed_count}")
                
                if total_count > 0:
                    success_rate = (success_count / total_count) * 100
                    st.write(f"Success rate: {success_rate:.1f}%")
        
        # IP Address Analysis
        st.subheader("🌐 Suspicious IP Addresses")
        ip_analysis = df.groupby('ip_address').agg({
            'action': 'count',
            'success': lambda x: (x == False).sum()
        }).reset_index()
        ip_analysis.columns = ['IP Address', 'Total Requests', 'Failed Requests']
        ip_analysis['Success Rate'] = ((ip_analysis['Total Requests'] - ip_analysis['Failed Requests']) / ip_analysis['Total Requests'] * 100).round(2)
        
        # Highlight suspicious IPs
        suspicious_ips = ip_analysis[
            (ip_analysis['Failed Requests'] > 5) | 
            (ip_analysis['Success Rate'] < 20)
        ].sort_values('Failed Requests', ascending=False)
        
        if not suspicious_ips.empty:
            st.warning("🚨 Suspicious IP addresses detected:")
            st.dataframe(suspicious_ips, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No suspicious IP addresses detected")
    
    else:
        st.info("No security events found for the selected time period.")
    
    conn.close()
    
except Exception as e:
    st.error(f"Error loading security data: {e}")

# --- User Account Status ---
st.header("👥 User Account Status")

try:
    conn = sqlite3.connect(USER_DB_PATH)
    
    # Get user account status
    user_status_query = '''
        SELECT 
            username,
            role,
            created_at,
            last_login,
            failed_attempts,
            CASE 
                WHEN locked_until > datetime('now') THEN 'Locked'
                WHEN failed_attempts >= 3 THEN 'Warning'
                ELSE 'Active'
            END as status,
            locked_until
        FROM users
        ORDER BY failed_attempts DESC, last_login DESC
    '''
    
    user_df = pd.read_sql_query(user_status_query, conn)
    
    if not user_df.empty:
        # Format timestamps
        user_df['created_at'] = pd.to_datetime(user_df['created_at'])
        user_df['last_login'] = pd.to_datetime(user_df['last_login'])
        user_df['locked_until'] = pd.to_datetime(user_df['locked_until'])
        
        # Display user status
        st.dataframe(
            user_df[['username', 'role', 'status', 'failed_attempts', 'last_login']],
            use_container_width=True,
            hide_index=True
        )
        
        # Account management actions
        st.subheader("🔧 Account Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 Unlock All Accounts"):
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users 
                    SET failed_attempts = 0, locked_until = NULL
                    WHERE locked_until > datetime('now')
                ''')
                conn.commit()
                st.success("All locked accounts have been unlocked!")
                st.rerun()
        
        with col2:
            if st.button("🧹 Reset Failed Attempts"):
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET failed_attempts = 0')
                conn.commit()
                st.success("All failed attempt counters have been reset!")
                st.rerun()
    
    conn.close()
    
except Exception as e:
    st.error(f"Error loading user data: {e}")

# --- System Health Check ---
st.header("💚 System Health Check")

try:
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Check database integrity
    cursor.execute("PRAGMA integrity_check")
    integrity_result = cursor.fetchone()
    
    # Check for orphaned sessions
    cursor.execute('''
        SELECT COUNT(*) FROM sessions s
        LEFT JOIN users u ON s.user_id = u.id
        WHERE u.id IS NULL
    ''')
    orphaned_sessions = cursor.fetchone()[0]
    
    # Check for expired sessions
    cursor.execute('''
        SELECT COUNT(*) FROM sessions
        WHERE expires_at < datetime('now')
    ''')
    expired_sessions = cursor.fetchone()[0]
    
    conn.close()
    
    # Display health status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if integrity_result[0] == "ok":
            st.success("✅ Database Integrity: OK")
        else:
            st.error("❌ Database Integrity: FAILED")
    
    with col2:
        if orphaned_sessions == 0:
            st.success("✅ Orphaned Sessions: None")
        else:
            st.warning(f"⚠️ Orphaned Sessions: {orphaned_sessions}")
    
    with col3:
        if expired_sessions == 0:
            st.success("✅ Expired Sessions: None")
        else:
            st.info(f"ℹ️ Expired Sessions: {expired_sessions}")
    
    # Cleanup actions
    if st.button("🧹 Cleanup System"):
        try:
            conn = sqlite3.connect(USER_DB_PATH)
            cursor = conn.cursor()
            
            # Remove expired sessions
            cursor.execute('DELETE FROM sessions WHERE expires_at < datetime("now")')
            
            # Remove orphaned sessions
            cursor.execute('''
                DELETE FROM sessions WHERE user_id IN (
                    SELECT s.user_id FROM sessions s
                    LEFT JOIN users u ON s.user_id = u.id
                    WHERE u.id IS NULL
                )
            ''')
            
            # Clean old rate limit entries
            cursor.execute('DELETE FROM rate_limits WHERE window_start < datetime("now", "-1 hour")')
            
            # Clean old audit logs (keep last 90 days)
            cursor.execute('DELETE FROM security_audit WHERE timestamp < datetime("now", "-90 days")')
            
            conn.commit()
            conn.close()
            
            st.success("System cleanup completed!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Cleanup failed: {e}")
    
except Exception as e:
    st.error(f"Health check failed: {e}")

# --- Security Recommendations ---
st.header("💡 Security Recommendations")

with st.expander("View Security Recommendations"):
    st.markdown("""
    ### 🔒 Security Best Practices:
    
    1. **Password Policy**
       - Enforce strong passwords (minimum 8 characters, mix of letters, numbers, symbols)
       - Implement password expiration
       - Prevent password reuse
    
    2. **Access Control**
       - Regular review of user permissions
       - Implement least privilege principle
       - Monitor admin account usage
    
    3. **Monitoring**
       - Set up alerts for suspicious activities
       - Regular review of security logs
       - Monitor for unusual login patterns
    
    4. **System Hardening**
       - Keep software updated
       - Use HTTPS in production
       - Implement IP whitelisting if needed
    
    5. **Backup & Recovery**
       - Regular database backups
       - Test recovery procedures
       - Secure backup storage
    """)

# --- Real-time Monitoring ---
st.header("⏱️ Real-time Monitoring")

if st.button("🔄 Refresh Security Data"):
    st.rerun()

st.info("🔄 Click the refresh button above to get the latest security data.")

# --- Quick Login Test ---
st.header("🔐 Quick Login Test")

st.info("""
**Test the security features:**

1. **Try logging in with wrong password 5 times** - Account should be locked
2. **Try rapid form submissions** - Should trigger rate limiting  
3. **Check the Security Monitor** - View all security events
4. **Admin credentials**: menchayheng / hengh428
""")

if st.button("🔓 Unlock Admin Account (Emergency)"):
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = 0, locked_until = NULL
            WHERE username = 'menchayheng'
        ''')
        conn.commit()
        conn.close()
        st.success("Admin account unlocked! You can now login.")
    except Exception as e:
        st.error(f"Failed to unlock account: {e}") 