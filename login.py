import streamlit as st
import hashlib
import sqlite3
import os
import time
import json
import pandas as pd
from datetime import datetime, timedelta
import threading
import logging

# --- Security Configuration ---
MAX_LOGIN_ATTEMPTS = 5  # Maximum failed login attempts
LOCKOUT_DURATION = 15  # Minutes to lock account after max attempts
RATE_LIMIT_WINDOW = 60  # Seconds for rate limiting
MAX_REQUESTS_PER_WINDOW = 10  # Maximum requests per window
SESSION_TIMEOUT = 24  # Hours for session timeout
MAX_CONCURRENT_SESSIONS = 3  # Maximum concurrent sessions per user

# --- Activity Tracking Configuration ---
ACTIVITY_TYPES = {
    'DATA_VERIFICATION': 'Data verification and insertion',
    'INVOICE_EDIT': 'Invoice data editing',
    'INVOICE_VOID': 'Invoice voiding',
    'INVOICE_REACTIVATE': 'Invoice reactivation',
    'INVOICE_DELETE': 'Invoice deletion',
    'DATA_AMENDMENT': 'Data amendment',
    'CONTAINER_UPDATE': 'Container information update',
    'STATUS_CHANGE': 'Status change',
    'BULK_OPERATION': 'Bulk operation'
}

# --- Storage Management Configuration ---
STORAGE_CLEANUP_CONFIG = {
    'business_activities_retention_days': 90,  # Keep detailed data for 90 days
    'security_audit_retention_days': 180,      # Keep security logs for 180 days
    'sessions_cleanup_hours': 24,              # Clean expired sessions every 24 hours
    'max_json_size_kb': 50,                    # Maximum JSON data size per record (KB)
    'auto_cleanup_enabled': True,              # Enable automatic cleanup
    'archive_old_data': True,                  # Archive old data instead of deleting
    'archive_path': 'data/archives/'           # Path for archived data
}

# --- Login System Configuration ---
ADMIN_USERNAME = "menchayheng"
ADMIN_PASSWORD_HASH = hashlib.sha256("hengh428".encode()).hexdigest()

# Database for user management
USER_DB_PATH = "data/user_database.db"

# Setup logging for security events
logging.basicConfig(
    filename='data/security.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def init_user_database():
    """Initialize the user database with admin user and security tables"""
    os.makedirs(os.path.dirname(USER_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            last_failed_attempt TIMESTAMP
        )
    ''')
    
    # Create sessions table for tracking login sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create security audit log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create rate limiting table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,  -- IP address or username
            request_count INTEGER DEFAULT 1,
            window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create business activity tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            target_invoice_ref TEXT,
            target_invoice_no TEXT,
            action_description TEXT,
            old_values TEXT,  -- JSON string of old data
            new_values TEXT,  -- JSON string of new data
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN DEFAULT 1,
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_business_activities_user 
        ON business_activities(user_id, timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_business_activities_invoice 
        ON business_activities(target_invoice_ref, timestamp)
    ''')
    
    # Insert admin user if not exists
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    ''', (ADMIN_USERNAME, ADMIN_PASSWORD_HASH, 'admin'))
    
    conn.commit()
    conn.close()

def get_client_ip():
    """Get client IP address using multiple methods"""
    try:
        # Method 1: Try to get from Streamlit session state
        if hasattr(st, 'session_state') and 'client_ip' in st.session_state:
            return st.session_state['client_ip']
        
        # Method 2: Try to get from Streamlit request object
        if hasattr(st, 'request') and st.request:
            # Check various headers for IP
            headers = st.request.headers
            for header in ['X-Forwarded-For', 'X-Real-IP', 'X-Client-IP', 'CF-Connecting-IP']:
                if header in headers:
                    ip = headers[header].split(',')[0].strip()
                    if ip and ip != 'unknown':
                        st.session_state['client_ip'] = ip
                        return ip
            
            # Try remote_ip
            if hasattr(st.request, 'remote_ip') and st.request.remote_ip:
                ip = st.request.remote_ip
                if ip and ip != 'unknown':
                    st.session_state['client_ip'] = ip
                    return ip
        
        # Method 3: Try to get from environment variables
        import os
        for env_var in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR']:
            if env_var in os.environ:
                ip = os.environ[env_var].split(',')[0].strip()
                if ip and ip != 'unknown':
                    st.session_state['client_ip'] = ip
                    return ip
        
        # Method 4: Use a simple session-based identifier
        if 'session_id' not in st.session_state:
            import secrets
            st.session_state['session_id'] = secrets.token_hex(8)
        
        # Return a session-based identifier if no IP found
        session_id = st.session_state['session_id']
        st.session_state['client_ip'] = f"session_{session_id}"
        return f"session_{session_id}"
        
    except Exception as e:
        # Fallback to session-based identifier
        if 'session_id' not in st.session_state:
            import secrets
            st.session_state['session_id'] = secrets.token_hex(8)
        return f"session_{st.session_state['session_id']}"

def get_user_agent():
    """Get user agent string using multiple methods"""
    try:
        # Method 1: Try to get from Streamlit session state
        if hasattr(st, 'session_state') and 'user_agent' in st.session_state:
            return st.session_state['user_agent']
        
        # Method 2: Try to get from Streamlit request object
        if hasattr(st, 'request') and st.request:
            headers = st.request.headers
            if 'User-Agent' in headers:
                ua = headers['User-Agent']
                if ua and ua != 'unknown':
                    st.session_state['user_agent'] = ua
                    return ua
        
        # Method 3: Try to get from environment variables
        import os
        if 'HTTP_USER_AGENT' in os.environ:
            ua = os.environ['HTTP_USER_AGENT']
            if ua and ua != 'unknown':
                st.session_state['user_agent'] = ua
                return ua
        
        # Method 4: Use a default user agent
        default_ua = "Streamlit-Client/1.0"
        st.session_state['user_agent'] = default_ua
        return default_ua
        
    except Exception as e:
        # Fallback to default user agent
        default_ua = "Streamlit-Client/1.0"
        if hasattr(st, 'session_state'):
            st.session_state['user_agent'] = default_ua
        return default_ua

def log_security_event(user_id, username, action, success, details=""):
    """Log security events for audit trail"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_audit (user_id, username, action, ip_address, user_agent, success, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, action, get_client_ip(), get_user_agent(), success, details))
        
        conn.commit()
        conn.close()
        
        # Also log to file
        log_level = logging.WARNING if not success else logging.INFO
        logging.log(log_level, f"Security Event: {action} by {username} ({get_client_ip()}) - Success: {success} - {details}")
        
    except Exception as e:
        logging.error(f"Failed to log security event: {e}")

def log_business_activity(user_id, username, activity_type, target_invoice_ref=None, target_invoice_no=None, 
                        action_description="", old_values=None, new_values=None, success=True, error_message=""):
    """Log business activities for audit trail and accountability"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Convert data to JSON strings for storage
        old_values_json = json.dumps(old_values) if old_values else None
        new_values_json = json.dumps(new_values) if new_values else None
        
        cursor.execute('''
            INSERT INTO business_activities 
            (user_id, username, activity_type, target_invoice_ref, target_invoice_no, 
             action_description, old_values, new_values, ip_address, user_agent, 
             success, error_message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, username, activity_type, target_invoice_ref, target_invoice_no,
              action_description, old_values_json, new_values_json, get_client_ip(), 
              get_user_agent(), success, error_message))
        
        conn.commit()
        conn.close()
        
        # Also log to file for backup - prioritize invoice number over reference
        invoice_identifier = target_invoice_no if target_invoice_no else target_invoice_ref
        log_level = logging.WARNING if not success else logging.INFO
        logging.log(log_level, f"Business Activity: {activity_type} by {username} - Invoice No: {invoice_identifier} - {action_description} - Success: {success}")
        
    except Exception as e:
        logging.error(f"Failed to log business activity: {e}")

def get_business_activities(user_id=None, invoice_ref=None, invoice_no=None, activity_type=None, days_back=30):
    """Get business activities with optional filters - prioritize invoice number"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        
        query = '''
            SELECT ba.*, u.username as user_username
            FROM business_activities ba
            LEFT JOIN users u ON ba.user_id = u.id
            WHERE ba.timestamp >= datetime('now', '-{} days')
        '''.format(days_back)
        
        params = []
        
        if user_id:
            query += " AND ba.user_id = ?"
            params.append(user_id)
        
        # Prioritize invoice number over invoice reference
        if invoice_no:
            query += " AND ba.target_invoice_no = ?"
            params.append(invoice_no)
        elif invoice_ref:
            query += " AND ba.target_invoice_ref = ?"
            params.append(invoice_ref)
        
        if activity_type:
            query += " AND ba.activity_type = ?"
            params.append(activity_type)
        
        query += " ORDER BY ba.timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
        
    except Exception as e:
        logging.error(f"Failed to get business activities: {e}")
        return pd.DataFrame()

def check_rate_limit(identifier, max_requests=RATE_LIMIT_WINDOW, window_seconds=MAX_REQUESTS_PER_WINDOW):
    """Check if request is within rate limits"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old entries
        cursor.execute('DELETE FROM rate_limits WHERE window_start < ?', (window_start,))
        
        # Check current rate
        cursor.execute('''
            SELECT request_count FROM rate_limits 
            WHERE identifier = ? AND window_start > ?
        ''', (identifier, window_start))
        
        result = cursor.fetchone()
        
        if result:
            request_count = result[0]
            if request_count >= max_requests:
                conn.close()
                return False
            
            # Update count
            cursor.execute('''
                UPDATE rate_limits 
                SET request_count = request_count + 1, last_request = ?
                WHERE identifier = ?
            ''', (now, identifier))
        else:
            # Create new entry
            cursor.execute('''
                INSERT INTO rate_limits (identifier, request_count, window_start, last_request)
                VALUES (?, 1, ?, ?)
            ''', (identifier, now, now))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"Rate limit check failed: {e}")
        return True  # Allow request if rate limiting fails

def is_account_locked(username):
    """Check if account is locked due to failed attempts"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT failed_attempts, locked_until 
            FROM users 
            WHERE username = ?
        ''', (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            failed_attempts, locked_until = result
            
            if failed_attempts >= MAX_LOGIN_ATTEMPTS and locked_until:
                if datetime.now() < datetime.fromisoformat(locked_until):
                    return True
                else:
                    # Reset lock if expired
                    reset_failed_attempts(username)
        
        return False
        
    except Exception as e:
        logging.error(f"Account lock check failed: {e}")
        return False

def increment_failed_attempts(username):
    """Increment failed login attempts and lock account if needed"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = failed_attempts + 1,
                last_failed_attempt = ?,
                locked_until = CASE 
                    WHEN failed_attempts + 1 >= ? THEN ?
                    ELSE locked_until 
                END
            WHERE username = ?
        ''', (datetime.now(), MAX_LOGIN_ATTEMPTS, 
              datetime.now() + timedelta(minutes=LOCKOUT_DURATION), username))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Failed to increment failed attempts: {e}")

def reset_failed_attempts(username):
    """Reset failed attempts after successful login"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = 0, locked_until = NULL
            WHERE username = ?
        ''', (username,))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Failed to reset failed attempts: {e}")

def check_concurrent_sessions(user_id):
    """Check if user has too many concurrent sessions"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE user_id = ? AND expires_at > ?
        ''', (user_id, datetime.now()))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count >= MAX_CONCURRENT_SESSIONS
        
    except Exception as e:
        logging.error(f"Concurrent session check failed: {e}")
        return False

def cleanup_old_sessions(user_id):
    """Remove oldest sessions if user has too many"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM sessions 
            WHERE user_id = ? AND id NOT IN (
                SELECT id FROM sessions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            )
        ''', (user_id, user_id, MAX_CONCURRENT_SESSIONS - 1))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Session cleanup failed: {e}")

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

def create_session(user_id):
    """Create a new session for a user with security features"""
    import secrets
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=SESSION_TIMEOUT)
    
    # Check concurrent sessions
    if check_concurrent_sessions(user_id):
        cleanup_old_sessions(user_id)
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, session_token, expires_at, get_client_ip(), get_user_agent()))
    
    conn.commit()
    conn.close()
    
    return session_token

def validate_session(session_token):
    """Validate a session token and return user info if valid"""
    if not session_token:
        return None
    
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.role, s.expires_at, s.id as session_id
            FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = 1
        ''', (session_token, datetime.now()))
        
        result = cursor.fetchone()
        
        if result:
            user_id, username, role, expires_at, session_id = result
            
            # Update last activity
            cursor.execute('''
                UPDATE sessions SET last_activity = ? WHERE id = ?
            ''', (datetime.now(), session_id))
            
            conn.commit()
            conn.close()
            
            return {
                'user_id': user_id,
                'username': username,
                'role': role,
                'expires_at': expires_at
            }
        
        conn.close()
        return None
        
    except Exception as e:
        logging.error(f"Session validation failed: {e}")
        return None

def login_user(username, password):
    """Attempt to login a user with security checks"""
    # Check rate limiting
    client_ip = get_client_ip()
    if not check_rate_limit(client_ip):
        log_security_event(None, username, "LOGIN_RATE_LIMITED", False, f"IP: {client_ip}")
        return None
    
    # Check if account is locked
    if is_account_locked(username):
        log_security_event(None, username, "LOGIN_ACCOUNT_LOCKED", False, f"IP: {client_ip}")
        return None
    
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role
            FROM users
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and verify_password(password, result[2]):
            user_id, username, _, role = result
            
            # Reset failed attempts on successful login
            reset_failed_attempts(username)
            
            # Create session
            session_token = create_session(user_id)
            
            # Update last login
            conn = sqlite3.connect(USER_DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET last_login = ? WHERE id = ?
            ''', (datetime.now(), user_id))
            conn.commit()
            conn.close()
            
            # Log successful login
            log_security_event(user_id, username, "LOGIN_SUCCESS", True, f"IP: {client_ip}")
            
            return {
                'user_id': user_id,
                'username': username,
                'role': role,
                'session_token': session_token
            }
        else:
            # Increment failed attempts
            increment_failed_attempts(username)
            
            # Log failed login
            log_security_event(None, username, "LOGIN_FAILED", False, f"IP: {client_ip}")
            
            return None
            
    except Exception as e:
        logging.error(f"Login failed: {e}")
        log_security_event(None, username, "LOGIN_ERROR", False, f"Error: {str(e)}")
        return None

def logout_user(session_token):
    """Logout a user by removing their session"""
    if not session_token:
        return
    
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Get user info before deleting session
        cursor.execute('''
            SELECT u.username FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.session_token = ?
        ''', (session_token,))
        
        result = cursor.fetchone()
        username = result[0] if result else "unknown"
        
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
        
        # Log logout
        log_security_event(None, username, "LOGOUT", True, f"IP: {get_client_ip()}")
        
    except Exception as e:
        logging.error(f"Logout failed: {e}")

def cleanup_expired_sessions():
    """Remove expired sessions from the database"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now(),))
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Session cleanup failed: {e}")

def show_login_page():
    """Display the login page with security features"""
    st.set_page_config(
        page_title="Login - Invoice Dashboard",
        page_icon="🔐",
        layout="centered"
    )
    
    # Initialize database
    init_user_database()
    
    # Cleanup expired sessions
    cleanup_expired_sessions()
    
    st.title("🔐 Login")
    st.markdown("---")
    
    # Check if user is already logged in
    session_token = st.session_state.get('session_token')
    if session_token:
        user_info = validate_session(session_token)
        if user_info:
            st.success(f"Welcome back, {user_info['username']}!")
            st.info("You are already logged in. Redirecting to dashboard...")
            st.rerun()
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                # Check if account is locked
                if is_account_locked(username):
                    st.error(f"Account is temporarily locked due to too many failed attempts. Please try again later.")
                else:
                    user_info = login_user(username, password)
                    if user_info:
                        # Store session token using persistent helper
                        from session_helper import set_persistent_session
                        
                        user_info_dict = {
                            'user_id': user_info['user_id'],
                            'username': user_info['username'],
                            'role': user_info['role']
                        }
                        
                        set_persistent_session(user_info['session_token'], user_info_dict)
                        
                        st.success(f"Welcome, {user_info['username']}!")
                        st.info("Login successful! Redirecting to dashboard...")
                        st.rerun()
                    else:
                        # Check if account is now locked
                        if is_account_locked(username):
                            st.error(f"Account locked due to too many failed attempts. Please try again in {LOCKOUT_DURATION} minutes.")
                        else:
                            st.error("Invalid username or password.")
    
    # Security information
    with st.expander("🔒 Security Information"):
        st.info("**Security Features:**")
        st.info("• Rate limiting: Maximum 10 requests per minute")
        st.info(f"• Account lockout: {MAX_LOGIN_ATTEMPTS} failed attempts = {LOCKOUT_DURATION} minute lockout")
        st.info(f"• Session timeout: {SESSION_TIMEOUT} hours")
        st.info(f"• Maximum concurrent sessions: {MAX_CONCURRENT_SESSIONS}")
        st.info("• All login attempts are logged for security audit")
    
    # Admin credentials hint (you can remove this in production)
    with st.expander("Admin Login Info"):
        st.info("Admin Username: menchayheng")
        st.info("Admin Password: hengh428")

def check_authentication():
    """Check if user is authenticated, redirect to login if not"""
    try:
        from session_helper import get_persistent_session, get_session_from_cache
        
        # Try to get session token from multiple sources
        session_token = None
        
        # First try session state
        if 'session_token' in st.session_state:
            session_token = st.session_state['session_token']
        
        # If not in session state, try persistent storage
        if not session_token:
            session_token = get_persistent_session()
        
        # If still no token, try file cache
        if not session_token:
            session_token, user_info = get_session_from_cache()
            if session_token and user_info:
                st.session_state['session_token'] = session_token
                st.session_state['user_info'] = user_info
        
        if not session_token:
            st.switch_page("pages/login.py")
            return None
        
        user_info = validate_session(session_token)
        if not user_info:
            # Session expired or invalid
            from session_helper import clear_persistent_session
            clear_persistent_session()
            st.switch_page("pages/login.py")
            return None
        
        # Store user info in session state if not already there
        if 'user_info' not in st.session_state:
            st.session_state['user_info'] = user_info
        
        return user_info
        
    except Exception as e:
        print(f"Authentication error: {e}")
        st.switch_page("pages/login.py")
        return None

def show_logout_button():
    """Display logout button in sidebar"""
    if st.sidebar.button("🚪 Logout"):
        session_token = st.session_state.get('session_token')
        if session_token:
            logout_user(session_token)
        
        # Clear persistent session
        from session_helper import clear_persistent_session
        clear_persistent_session()
        
        st.rerun()

def show_user_info():
    """Display current user information in sidebar"""
    user_info = st.session_state.get('user_info')
    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👤 Logged in as:** {user_info['username']}")
        st.sidebar.markdown(f"**🔑 Role:** {user_info['role'].title()}")
        st.sidebar.markdown("---")

def get_security_stats():
    """Get security statistics for admin dashboard"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Get failed login attempts in last 24 hours
        cursor.execute('''
            SELECT COUNT(*) FROM security_audit 
            WHERE action = 'LOGIN_FAILED' 
            AND timestamp > datetime('now', '-1 day')
        ''')
        failed_logins_24h = cursor.fetchone()[0]
        
        # Get locked accounts
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE locked_until > datetime('now')
        ''')
        locked_accounts = cursor.fetchone()[0]
        
        # Get active sessions
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE expires_at > datetime('now')
        ''')
        active_sessions = cursor.fetchone()[0]
        
        # Get rate limited requests in last hour
        cursor.execute('''
            SELECT COUNT(*) FROM security_audit 
            WHERE action = 'LOGIN_RATE_LIMITED' 
            AND timestamp > datetime('now', '-1 hour')
        ''')
        rate_limited_1h = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'failed_logins_24h': failed_logins_24h,
            'locked_accounts': locked_accounts,
            'active_sessions': active_sessions,
            'rate_limited_1h': rate_limited_1h
        }
        
    except Exception as e:
        logging.error(f"Failed to get security stats: {e}")
        return {}

# Initialize the database when this module is imported
init_user_database()

# --- Storage Management Functions ---

def get_storage_stats():
    """Get storage statistics for the database"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Get table sizes
        tables = ['users', 'sessions', 'security_audit', 'business_activities']
        table_stats = {}
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                
                # Estimate size (rough calculation)
                cursor.execute(f'PRAGMA table_info({table})')
                columns = cursor.fetchall()
                avg_row_size = sum(1 for col in columns) * 50  # Rough estimate
                estimated_size_kb = (count * avg_row_size) / 1024
                
                table_stats[table] = {
                    'count': count,
                    'estimated_size_kb': round(estimated_size_kb, 2)
                }
            except sqlite3.OperationalError:
                table_stats[table] = {'count': 0, 'estimated_size_kb': 0}
        
        # Get total database size
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        total_size_kb = (page_count * page_size) / 1024
        
        conn.close()
        
        return {
            'total_size_kb': round(total_size_kb, 2),
            'tables': table_stats
        }
        
    except Exception as e:
        logging.error(f"Failed to get storage stats: {e}")
        return {}

def cleanup_old_data(days_back=None, force=False):
    """Clean up old data based on retention policies"""
    try:
        config = STORAGE_CLEANUP_CONFIG
        if not config['auto_cleanup_enabled'] and not force:
            return {"success": False, "message": "Auto cleanup is disabled"}
        
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Create archive directory if needed
        if config['archive_old_data']:
            os.makedirs(config['archive_path'], exist_ok=True)
        
        cleanup_stats = {
            'business_activities_cleaned': 0,
            'security_audit_cleaned': 0,
            'sessions_cleaned': 0,
            'archived_files': []
        }
        
        # Clean business activities
        retention_days = days_back or config['business_activities_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        if config['archive_old_data']:
            # Archive old business activities
            cursor.execute('''
                SELECT * FROM business_activities 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            old_activities = cursor.fetchall()
            
            if old_activities:
                archive_file = f"{config['archive_path']}business_activities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(archive_file, 'w') as f:
                    json.dump(old_activities, f, indent=2)
                cleanup_stats['archived_files'].append(archive_file)
        
        cursor.execute('''
            DELETE FROM business_activities 
            WHERE timestamp < ?
        ''', (cutoff_date,))
        cleanup_stats['business_activities_cleaned'] = cursor.rowcount
        
        # Clean security audit logs
        retention_days = days_back or config['security_audit_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        if config['archive_old_data']:
            # Archive old security audit logs
            cursor.execute('''
                SELECT * FROM security_audit 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            old_audit = cursor.fetchall()
            
            if old_audit:
                archive_file = f"{config['archive_path']}security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(archive_file, 'w') as f:
                    json.dump(old_audit, f, indent=2)
                cleanup_stats['archived_files'].append(archive_file)
        
        cursor.execute('''
            DELETE FROM security_audit 
            WHERE timestamp < ?
        ''', (cutoff_date,))
        cleanup_stats['security_audit_cleaned'] = cursor.rowcount
        
        # Clean expired sessions
        cursor.execute('DELETE FROM sessions WHERE expires_at < datetime("now")')
        cleanup_stats['sessions_cleaned'] = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        # Log cleanup activity
        logging.info(f"Storage cleanup completed: {cleanup_stats}")
        
        return {
            "success": True,
            "message": f"Cleanup completed. {cleanup_stats['business_activities_cleaned']} business activities, {cleanup_stats['security_audit_cleaned']} security logs, {cleanup_stats['sessions_cleaned']} sessions cleaned.",
            "stats": cleanup_stats
        }
        
    except Exception as e:
        logging.error(f"Failed to cleanup old data: {e}")
        return {"success": False, "message": f"Cleanup failed: {str(e)}"}

def optimize_database():
    """Optimize database performance and reduce size"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Vacuum database to reclaim space
        cursor.execute("VACUUM")
        
        # Analyze tables for better query performance
        cursor.execute("ANALYZE")
        
        # Rebuild indexes
        cursor.execute("REINDEX")
        
        conn.close()
        
        return {"success": True, "message": "Database optimized successfully"}
        
    except Exception as e:
        logging.error(f"Failed to optimize database: {e}")
        return {"success": False, "message": f"Optimization failed: {str(e)}"}

def get_storage_recommendations():
    """Get storage optimization recommendations"""
    try:
        stats = get_storage_stats()
        recommendations = []
        
        if not stats:
            return recommendations
        
        total_size = stats.get('total_size_kb', 0)
        tables = stats.get('tables', {})
        
        # Check if database is getting large
        if total_size > 10000:  # 10MB
            recommendations.append({
                'type': 'warning',
                'message': f'Database size is {total_size:.1f} KB. Consider enabling auto-cleanup.',
                'action': 'Enable automatic cleanup in storage settings'
            })
        
        # Check business activities table
        ba_stats = tables.get('business_activities', {})
        if ba_stats.get('count', 0) > 10000:
            recommendations.append({
                'type': 'info',
                'message': f'Business activities table has {ba_stats["count"]} records. Consider reducing retention period.',
                'action': 'Reduce business activities retention period'
            })
        
        # Check security audit table
        sa_stats = tables.get('security_audit', {})
        if sa_stats.get('count', 0) > 50000:
            recommendations.append({
                'type': 'info',
                'message': f'Security audit table has {sa_stats["count"]} records. Consider reducing retention period.',
                'action': 'Reduce security audit retention period'
            })
        
        return recommendations
        
    except Exception as e:
        logging.error(f"Failed to get storage recommendations: {e}")
        return []

def update_storage_config(new_config):
    """Update storage cleanup configuration"""
    try:
        global STORAGE_CLEANUP_CONFIG
        STORAGE_CLEANUP_CONFIG.update(new_config)
        
        # Save to file for persistence
        config_file = 'data/storage_config.json'
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(STORAGE_CLEANUP_CONFIG, f, indent=2)
        
        return {"success": True, "message": "Storage configuration updated successfully"}
        
    except Exception as e:
        logging.error(f"Failed to update storage config: {e}")
        return {"success": False, "message": f"Failed to update config: {str(e)}"}

def load_storage_config():
    """Load storage configuration from file"""
    try:
        config_file = 'data/storage_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                global STORAGE_CLEANUP_CONFIG
                STORAGE_CLEANUP_CONFIG.update(loaded_config)
    except Exception as e:
        logging.error(f"Failed to load storage config: {e}")

# Load storage configuration on module import
load_storage_config()

# --- Automatic Cleanup Scheduling ---
def schedule_automatic_cleanup():
    """Schedule automatic cleanup if enabled"""
    try:
        config = STORAGE_CLEANUP_CONFIG
        if not config['auto_cleanup_enabled']:
            return
        
        # Check if cleanup is needed (simple time-based check)
        # In a production environment, you might want to use a proper scheduler
        # For now, we'll just log that cleanup should be considered
        logging.info("Automatic cleanup check - consider running cleanup_old_data()")
        
    except Exception as e:
        logging.error(f"Failed to schedule automatic cleanup: {e}")

# Schedule cleanup on module import (for demonstration)
# In production, you'd want to use a proper scheduler like APScheduler
schedule_automatic_cleanup() 