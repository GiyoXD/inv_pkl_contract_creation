import streamlit as st
import sqlite3
import hashlib
import secrets
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from session_helper import get_persistent_session, set_persistent_session, clear_persistent_session, get_session_from_cache

# Database paths
USER_DB_PATH = "data/user_database.db"
ACTIVITY_LOG_PATH = "data/activity_log.db"

# Session timeout (in hours)
SESSION_TIMEOUT_HOURS = 8

def init_user_database():
    """Initialize the user database with required tables"""
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Registration tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            max_uses INTEGER DEFAULT 1,
            used_count INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Security events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type TEXT NOT NULL,
            description TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Business activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS business_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            activity_type TEXT NOT NULL,
            target_invoice_ref TEXT,
            target_invoice_no TEXT,
            action_description TEXT,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN DEFAULT 1,
            error_message TEXT,
            description TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{password_hash.hex()}"

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    try:
        salt, hash_hex = password_hash.split(':')
        password_hash_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash_check.hex() == hash_hex
    except:
        return False

def log_security_event(user_id, event_type, description, ip_address=None, user_agent=None):
    """Log a security event"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Use Cambodia timezone for timestamp
        cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
        cambodia_timestamp = datetime.now(cambodia_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO security_events (user_id, event_type, description, ip_address, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, event_type, description, ip_address, user_agent, cambodia_timestamp))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging security event: {e}")

def log_business_activity(user_id, activity_type, description, details=None, **kwargs):
    """Log a business activity with extended parameters"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Get additional parameters from kwargs
        username = kwargs.get('username', '')
        target_invoice_ref = kwargs.get('target_invoice_ref', '')
        target_invoice_no = kwargs.get('target_invoice_no', '')
        action_description = kwargs.get('action_description', description)
        old_values = kwargs.get('old_values', '')
        new_values = kwargs.get('new_values', '')
        success = kwargs.get('success', True)
        error_message = kwargs.get('error_message', '')
        ip_address = kwargs.get('ip_address', get_client_ip())
        user_agent = kwargs.get('user_agent', get_user_agent())
        
        # Convert complex objects to JSON strings
        if isinstance(old_values, (list, dict)):
            old_values = json.dumps(old_values)
        if isinstance(new_values, (list, dict)):
            new_values = json.dumps(new_values)
        
        # Use Cambodia timezone for timestamp
        cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
        cambodia_timestamp = datetime.now(cambodia_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO business_activities (
                user_id, activity_type, description, details, 
                username, target_invoice_ref, target_invoice_no, 
                action_description, old_values, new_values, 
                success, error_message, ip_address, user_agent, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, activity_type, description, details,
            username, target_invoice_ref, target_invoice_no,
            action_description, old_values, new_values,
            success, error_message, ip_address, user_agent, cambodia_timestamp
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging business activity: {e}")

def create_session(user_id, ip_address=None, user_agent=None):
    """Create a new session for a user"""
    session_token = secrets.token_urlsafe(32)
    # Use Cambodia timezone for session expiry
    cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
    expires_at = datetime.now(cambodia_tz) + timedelta(hours=SESSION_TIMEOUT_HOURS)
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, session_token, expires_at, ip_address, user_agent))
    
    conn.commit()
    conn.close()
    
    return session_token

def validate_session(session_token):
    """Validate a session token and return user info"""
    if not session_token:
        return None
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.id, u.username, u.role, s.expires_at
        FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > datetime('now')
    ''', (session_token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_id, username, role, expires_at = result
        return {
            'user_id': user_id,
            'username': username,
            'role': role,
            'expires_at': expires_at
        }
    
    return None

def check_authentication():
    """Check if user is authenticated and return user info"""
    # Initialize database if it doesn't exist
    init_user_database()
    
    # Store intended page in session state
    if 'intended_page' not in st.session_state:
        # Get current page from URL or default to main
        try:
            current_page = st.query_params.get('page', 'main')
            st.session_state.intended_page = current_page
        except:
            st.session_state.intended_page = 'main'
    
    # Try to get session from various sources
    session_token = get_persistent_session()
    
    if not session_token:
        session_token, cached_user_info = get_session_from_cache()
        if session_token and cached_user_info:
            st.session_state['session_token'] = session_token
            st.session_state['user_info'] = cached_user_info
    
    if session_token:
        user_info = validate_session(session_token)
        if user_info:
            # Check for session timeout warning (1 hour before expiry)
            cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
            expires_at = datetime.fromisoformat(user_info['expires_at'])
            # Make expires_at timezone-aware by assuming it's in Cambodia time
            expires_at = expires_at.replace(tzinfo=cambodia_tz)
            time_until_expiry = expires_at - datetime.now(cambodia_tz)
            
            if time_until_expiry.total_seconds() < 3600:  # Less than 1 hour
                minutes_left = int(time_until_expiry.total_seconds() / 60)
                if minutes_left > 0:
                    st.warning(f"⚠️ Your session will expire in {minutes_left} minutes. Please save your work.")
                else:
                    st.error("🔒 Your session has expired. Please log in again.")
                    clear_persistent_session()
                    st.rerun()
            
            return user_info
        else:
            # Invalid session, clear it
            clear_persistent_session()
    
    return None

def authenticate_user(username, password):
    """Authenticate a user with username and password"""
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists and is not blocked
    cursor.execute('''
        SELECT id, password_hash, role, failed_attempts, locked_until, is_active
        FROM users 
        WHERE username = ?
    ''', (username,))
    
    result = cursor.fetchone()
    
    if not result:
        log_security_event(None, 'LOGIN_FAILED', f'Login attempt with non-existent username: {username}', 
                          ip_address=get_client_ip(), user_agent=get_user_agent())
        conn.close()
        return False, "Invalid username or password"
    
    user_id, password_hash, role, failed_attempts, locked_until, is_active = result
    
    # Check if user is active
    if not is_active:
        log_security_event(user_id, 'LOGIN_FAILED', 'Login attempt on inactive account',
                          ip_address=get_client_ip(), user_agent=get_user_agent())
        conn.close()
        return False, "Account is inactive"
    
            # Check if user is locked
        if locked_until:
            cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
            locked_until_dt = datetime.fromisoformat(locked_until)
            if datetime.now(cambodia_tz) < locked_until_dt:
                log_security_event(user_id, 'LOGIN_FAILED', 'Login attempt on locked account',
                                  ip_address=get_client_ip(), user_agent=get_user_agent())
                conn.close()
                return False, f"Account is locked until {locked_until_dt.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Verify password
    if verify_password(password, password_hash):
        # Reset failed attempts and update last login
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = 0, locked_until = NULL, last_login = datetime('now')
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        # Log successful login
        log_security_event(user_id, 'LOGIN_SUCCESS', 'Successful login',
                          ip_address=get_client_ip(), user_agent=get_user_agent())
        
        return True, {
            'user_id': user_id,
            'username': username,
            'role': role
        }
    else:
        # Increment failed attempts
        failed_attempts += 1
        
        # Lock user if too many failed attempts
        locked_until = None
        if failed_attempts >= 5:
            cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
            locked_until = datetime.now(cambodia_tz) + timedelta(minutes=30)
        
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = ?, locked_until = ?
            WHERE id = ?
        ''', (failed_attempts, locked_until, user_id))
        
        conn.commit()
        conn.close()
        
        # Log failed login
        log_security_event(user_id, 'LOGIN_FAILED', f'Failed login attempt ({failed_attempts}/5)',
                          ip_address=get_client_ip(), user_agent=get_user_agent())
        
        if locked_until:
            return False, "Too many failed attempts. Account locked for 30 minutes."
        else:
            return False, f"Invalid username or password ({failed_attempts}/5 attempts)"

def show_login_page():
    """Display the login form"""
    st.header("🔐 Login to Invoice Dashboard")
    
    # Show redirect message if user was redirected from another page
    if st.session_state.get('intended_page') and st.session_state.intended_page != 'main':
        st.info(f"🔄 Please log in to access the requested page.")
    
    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            login_button = st.form_submit_button("🚀 Login", use_container_width=True)
        
        with col2:
            remember_me = st.checkbox("Remember me", help="Keep me logged in for longer")
        
        if login_button:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                with st.spinner("Authenticating..."):
                    success, result = authenticate_user(username, password)
                
                if success:
                    user_info = result
                    
                    # Create session
                    session_token = create_session(user_info['user_id'], 
                                                 ip_address=get_client_ip(), 
                                                 user_agent=get_user_agent())
                    
                    # Store session
                    set_persistent_session(session_token, user_info)
                    
                    st.success(f"✅ Welcome back, {user_info['username']}!")
                    
                    # Redirect to intended page
                    intended_page = st.session_state.get('intended_page', 'main')
                    if intended_page != 'main':
                        st.info(f"🔄 Redirecting to your requested page...")
                    
                    # Clear intended page
                    if 'intended_page' in st.session_state:
                        del st.session_state.intended_page
                    
                    st.rerun()
                else:
                    st.error(f"❌ {result}")

def show_user_info():
    """Display user information in sidebar"""
    user_info = st.session_state.get('user_info')
    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**👤 User Information**")
        st.sidebar.write(f"**Username:** {user_info['username']}")
        st.sidebar.write(f"**Role:** {user_info['role'].title()}")
        
        # Show session expiry info
        session_token = st.session_state.get('session_token')
        if session_token:
            session_info = validate_session(session_token)
            if session_info:
                cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
                expires_at = datetime.fromisoformat(session_info['expires_at'])
                # Make expires_at timezone-aware by assuming it's in Cambodia time
                expires_at = expires_at.replace(tzinfo=cambodia_tz)
                time_until_expiry = expires_at - datetime.now(cambodia_tz)
                hours_left = int(time_until_expiry.total_seconds() / 3600)
                minutes_left = int((time_until_expiry.total_seconds() % 3600) / 60)
                
                if hours_left > 0:
                    st.sidebar.write(f"**Session expires in:** {hours_left}h {minutes_left}m")
                else:
                    st.sidebar.write(f"**Session expires in:** {minutes_left}m")

def show_logout_button():
    """Display logout button in sidebar"""
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        user_info = st.session_state.get('user_info')
        if user_info:
            log_security_event(user_info['user_id'], 'LOGOUT', 'User logged out',
                              ip_address=get_client_ip(), user_agent=get_user_agent())
        
        clear_persistent_session()
        st.success("✅ You have been logged out successfully!")
        st.rerun()

# Registration and token functions (keeping existing functionality)
def generate_registration_token(created_by_user_id, max_uses=1, expires_hours=24):
    """Generate a registration token"""
    token = secrets.token_urlsafe(32)
    cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
    expires_at = datetime.now(cambodia_tz) + timedelta(hours=expires_hours)
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Get the username of the creator
    cursor.execute('SELECT username FROM users WHERE id = ?', (created_by_user_id,))
    creator = cursor.fetchone()
    created_by_username = creator[0] if creator else 'Unknown'
    
    cursor.execute('''
        INSERT INTO registration_tokens (token, created_by, created_by_username, expires_at, max_uses)
        VALUES (?, ?, ?, ?, ?)
    ''', (token, created_by_user_id, created_by_username, expires_at, max_uses))
    
    conn.commit()
    conn.close()
    
    return token

def validate_registration_token(token):
    """Validate a registration token"""
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT rt.*, u.username as created_by_username
        FROM registration_tokens rt
        LEFT JOIN users u ON rt.created_by = u.id
        WHERE rt.token = ? AND rt.is_active = 1
    ''', (token,))
    
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return False, "Invalid token"
    
    # Get column names before closing connection
    column_names = [col[0] for col in cursor.description]
    conn.close()
    
    token_data = dict(zip(column_names, result))
    
    # Check if token is expired
    cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
    expires_at = datetime.fromisoformat(token_data['expires_at'])
    # Make expires_at timezone-aware by assuming it's in Cambodia time
    expires_at = expires_at.replace(tzinfo=cambodia_tz)
    if datetime.now(cambodia_tz) > expires_at:
        return False, "Token has expired"
    
    # Check if token has reached max uses
    if token_data['used_count'] >= token_data['max_uses']:
        return False, "Token has reached maximum uses"
    
    return True, token_data

def register_user_with_token(token, username, password):
    """Register a new user with a valid token"""
    # Validate token first
    is_valid, token_info = validate_registration_token(token)
    if not is_valid:
        return False, token_info
    
    # Check if username already exists
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists"
    
    # Create user
    password_hash = hash_password(password)
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, 'user')
    ''', (username, password_hash))
    
    user_id = cursor.lastrowid
    
    # Update token usage
    cursor.execute('''
        UPDATE registration_tokens 
        SET used_count = used_count + 1
        WHERE token = ?
    ''', (token,))
    
    conn.commit()
    conn.close()
    
    # Log the registration
    log_security_event(user_id, 'USER_REGISTERED', f'New user registered with token',
                      ip_address=get_client_ip(), user_agent=get_user_agent())
    
    # Create session for the newly registered user
    session_token = create_session(user_id, 
                                 ip_address=get_client_ip(), 
                                 user_agent=get_user_agent())
    
    # Return success with session info for automatic login
    return True, {
        "message": "User registered successfully",
        "session_token": session_token,
        "user_id": user_id,
        "username": username,
        "role": "user"
    }

# Additional utility functions for admin dashboard
def get_security_events(limit=100):
    """Get recent security events"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT se.*, u.username
            FROM security_events se
            LEFT JOIN users u ON se.user_id = u.id
            ORDER BY se.timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        events = []
        for row in cursor.fetchall():
            event = dict(zip([col[0] for col in cursor.description], row))
            events.append(event)
        
        conn.close()
        return events
    except Exception as e:
        print(f"Error getting security events: {e}")
        return []

def get_business_activities(limit=100, days_back=7):
    """Get recent business activities"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                ba.id,
                ba.user_id,
                ba.activity_type,
                ba.username,
                ba.target_invoice_ref,
                ba.target_invoice_no,
                ba.action_description,
                COALESCE(ba.old_values, '') as old_values,
                COALESCE(ba.new_values, '') as new_values,
                COALESCE(ba.ip_address, '127.0.0.1') as ip_address,
                COALESCE(ba.user_agent, 'Streamlit/1.0') as user_agent,
                COALESCE(ba.success, 1) as success,
                COALESCE(ba.error_message, '') as error_message,
                ba.timestamp
            FROM business_activities ba
            WHERE ba.timestamp > datetime('now', '-{} days')
            ORDER BY ba.timestamp DESC
            LIMIT ?
        '''.format(days_back), (limit,))
        
        activities = []
        for row in cursor.fetchall():
            activity = dict(zip([col[0] for col in cursor.description], row))
            activities.append(activity)
        
        conn.close()
        return activities
    except Exception as e:
        print(f"Error getting business activities: {e}")
        return []

def get_storage_stats():
    """Get storage statistics"""
    try:
        stats = {}
        
        # Get database file sizes
        if os.path.exists(USER_DB_PATH):
            stats['user_db_size_kb'] = os.path.getsize(USER_DB_PATH) / 1024
        
        invoice_db_path = "data/Invoice Record/master_invoice_data.db"
        if os.path.exists(invoice_db_path):
            stats['invoice_db_size_kb'] = os.path.getsize(invoice_db_path) / 1024
        
        stats['total_size_kb'] = stats.get('user_db_size_kb', 0) + stats.get('invoice_db_size_kb', 0)
        
        return stats
    except Exception as e:
        print(f"Error getting storage stats: {e}")
        return {}

# Additional admin functions (stubs for compatibility)
def get_all_users():
    """Get all users (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, role, created_at, last_login, is_active, failed_attempts, locked_until
            FROM users
            ORDER BY created_at DESC
        ''')
        
        users = []
        for row in cursor.fetchall():
            user = dict(zip([col[0] for col in cursor.description], row))
            users.append(user)
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []

def create_user(username, password, role='user'):
    """Create a new user (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, is_active, created_at, failed_attempts)
            VALUES (?, ?, ?, 1, datetime('now'), 0)
        ''', (username, hashed_password, role))
        
        conn.commit()
        conn.close()
        
        return True, f"User '{username}' created successfully"
        
    except Exception as e:
        print(f"Error creating user: {e}")
        return False, f"Error creating user: {e}"

def update_user(user_id, new_username=None, new_role=None, new_status=None):
    """Update user information (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found"
        
        old_username = user[0]
        
        # Build update query dynamically
        updates = []
        params = []
        
        if new_username and new_username != old_username:
            # Check if new username already exists
            cursor.execute('SELECT id FROM users WHERE username = ? AND id != ?', (new_username, user_id))
            if cursor.fetchone():
                conn.close()
                return False, "Username already exists"
            updates.append("username = ?")
            params.append(new_username)
        
        if new_role:
            updates.append("role = ?")
            params.append(new_role)
        
        if new_status is not None:
            updates.append("is_active = ?")
            params.append(1 if new_status == "Active" else 0)
        
        if not updates:
            conn.close()
            return False, "No changes to update"
        
        # Perform update
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return True, f"User '{old_username}' updated successfully"
        
    except Exception as e:
        print(f"Error updating user: {e}")
        return False, f"Error updating user: {e}"

def delete_user(user_id):
    """Delete a user (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # First check if user exists
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found"
        
        username = user[0]
        
        # Don't allow deleting the admin user
        if username == 'menchayheng':
            conn.close()
            return False, "Cannot delete admin user"
        
        # Delete the user
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return False, "User not found or already deleted"
        
        conn.commit()
        conn.close()
        
        return True, f"User '{username}' deleted successfully"
        
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False, f"Error deleting user: {e}"

def reset_user_password(user_id, new_password):
    """Reset user password (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found"
        
        username = user[0]
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update password and reset failed attempts
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, failed_attempts = 0, locked_until = NULL 
            WHERE id = ?
        ''', (hashed_password, user_id))
        
        conn.commit()
        conn.close()
        
        return True, f"Password reset successfully for user '{username}'"
        
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False, f"Error resetting password: {e}"

def get_active_sessions():
    """Get active sessions (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, s.user_id, u.username, s.session_token, s.created_at, s.expires_at, s.ip_address, s.user_agent
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.expires_at > datetime('now')
            ORDER BY s.created_at DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            session = dict(zip([col[0] for col in cursor.description], row))
            sessions.append(session)
        
        conn.close()
        return sessions
        
    except Exception as e:
        print(f"Error getting active sessions: {e}")
        return []

def clear_expired_sessions():
    """Clear expired sessions (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Count expired sessions before deletion
        cursor.execute('SELECT COUNT(*) FROM sessions WHERE expires_at < datetime("now")')
        expired_count = cursor.fetchone()[0]
        
        # Delete expired sessions
        cursor.execute('DELETE FROM sessions WHERE expires_at < datetime("now")')
        
        conn.commit()
        conn.close()
        
        return True, f"Cleared {expired_count} expired sessions"
        
    except Exception as e:
        print(f"Error clearing expired sessions: {e}")
        return False, f"Error clearing expired sessions: {e}"

def unblock_user(user_id):
    """Unblock a user (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return False, "User not found"
        
        username = user[0]
        
        # Reset failed attempts and unlock user
        cursor.execute('''
            UPDATE users 
            SET failed_attempts = 0, locked_until = NULL 
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return True, f"User '{username}' has been unblocked successfully"
        
    except Exception as e:
        print(f"Error unblocking user: {e}")
        return False, f"Error unblocking user: {e}"

def get_all_registration_tokens():
    """Get all registration tokens (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, token, created_by_username, created_at, expires_at, max_uses, used_count, is_active
            FROM registration_tokens
            ORDER BY created_at DESC
        ''')
        
        tokens = []
        for row in cursor.fetchall():
            token = dict(zip([col[0] for col in cursor.description], row))
            tokens.append(token)
        
        conn.close()
        return tokens
        
    except Exception as e:
        print(f"Error getting all registration tokens: {e}")
        return []

def revoke_registration_token(token_id):
    """Revoke a registration token (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Check if token exists
        cursor.execute('SELECT token FROM registration_tokens WHERE id = ?', (token_id,))
        token_row = cursor.fetchone()
        
        if not token_row:
            conn.close()
            return False, "Token not found"
        
        token_display = token_row[0][:8] + "..."
        
        # Revoke the token by setting is_active to 0
        cursor.execute('UPDATE registration_tokens SET is_active = 0 WHERE id = ?', (token_id,))
        
        conn.commit()
        conn.close()
        
        return True, f"Token {token_display} has been revoked"
        
    except Exception as e:
        print(f"Error revoking token: {e}")
        return False, f"Error revoking token: {e}"

def cleanup_expired_tokens():
    """Clean up expired tokens (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Count expired tokens before cleanup
        cursor.execute('SELECT COUNT(*) FROM registration_tokens WHERE expires_at < datetime("now")')
        expired_count = cursor.fetchone()[0]
        
        # Delete expired tokens
        cursor.execute('DELETE FROM registration_tokens WHERE expires_at < datetime("now")')
        
        # Count fully used tokens
        cursor.execute('SELECT COUNT(*) FROM registration_tokens WHERE used_count >= max_uses')
        used_count = cursor.fetchone()[0]
        
        # Delete fully used tokens
        cursor.execute('DELETE FROM registration_tokens WHERE used_count >= max_uses')
        
        conn.commit()
        conn.close()
        
        total_cleaned = expired_count + used_count
        return True, f"Cleaned up {total_cleaned} tokens ({expired_count} expired, {used_count} fully used)"
        
    except Exception as e:
        print(f"Error cleaning up expired tokens: {e}")
        return False, f"Error: {e}"

def get_token_cleanup_stats():
    """Get token cleanup statistics (admin function)"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Get total tokens
        cursor.execute('SELECT COUNT(*) FROM registration_tokens')
        total_tokens = cursor.fetchone()[0]
        
        # Get expired tokens
        cursor.execute('SELECT COUNT(*) FROM registration_tokens WHERE expires_at < datetime("now")')
        expired_tokens = cursor.fetchone()[0]
        
        # Get used tokens
        cursor.execute('SELECT COUNT(*) FROM registration_tokens WHERE used_count >= max_uses')
        used_tokens = cursor.fetchone()[0]
        
        # Get active tokens
        cursor.execute('''
            SELECT COUNT(*) FROM registration_tokens 
            WHERE expires_at > datetime("now") AND used_count < max_uses AND is_active = 1
        ''')
        active_tokens = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_tokens': total_tokens,
            'expired_tokens': expired_tokens,
            'used_tokens': used_tokens,
            'active_tokens': active_tokens,
            'cleanup_threshold_days': 30  # Default cleanup threshold
        }
        
    except Exception as e:
        print(f"Error getting token cleanup stats: {e}")
        return {
            'total_tokens': 0,
            'expired_tokens': 0,
            'used_tokens': 0,
            'active_tokens': 0,
            'cleanup_threshold_days': 30  # Default cleanup threshold
        }

def cleanup_old_data():
    """Clean up old data (admin function)"""
    pass

def optimize_database():
    """Optimize database (admin function)"""
    pass

def get_storage_recommendations():
    """Get storage recommendations (admin function)"""
    pass

def update_storage_config(config):
    """Update storage configuration (admin function)"""
    pass

# Storage cleanup configuration (for compatibility)
STORAGE_CLEANUP_CONFIG = {
    'security_events_days': 90,
    'business_activities_days': 365,
    'expired_sessions_days': 7,
    'expired_tokens_days': 30
}

# Activity types (for compatibility)
ACTIVITY_TYPES = {
    'INVOICE_CREATED': 'Invoice Created',
    'INVOICE_UPDATED': 'Invoice Updated',
    'INVOICE_DELETED': 'Invoice Deleted',
    'DATA_EXPORT': 'Data Export',
    'BACKUP_CREATED': 'Backup Created',
    'BACKUP_RESTORED': 'Backup Restored'
}

def get_security_stats():
    """Get security statistics for dashboard"""
    try:
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        # Failed logins in last 24 hours
        cursor.execute('''
            SELECT COUNT(*) FROM security_events 
            WHERE event_type = 'LOGIN_FAILED' 
            AND timestamp > datetime('now', '-1 day')
        ''')
        failed_logins_24h = cursor.fetchone()[0]
        
        # Locked accounts
        cursor.execute('''
            SELECT COUNT(*) FROM users 
            WHERE locked_until > datetime('now')
        ''')
        locked_accounts = cursor.fetchone()[0]
        
        # Active sessions
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE expires_at > datetime('now')
        ''')
        active_sessions = cursor.fetchone()[0]
        
        # Rate limited in last hour (placeholder - would need rate_limits table)
        rate_limited_1h = 0
        
        conn.close()
        
        return {
            'failed_logins_24h': failed_logins_24h,
            'locked_accounts': locked_accounts,
            'active_sessions': active_sessions,
            'rate_limited_1h': rate_limited_1h
        }
        
    except Exception as e:
        print(f"Error getting security stats: {e}")
        return {
            'failed_logins_24h': 0,
            'locked_accounts': 0,
            'active_sessions': 0,
            'rate_limited_1h': 0
        }

def get_client_ip():
    """Get client IP address from Streamlit session state or request"""
    try:
        # Try to get IP from Streamlit session state
        if hasattr(st, 'session_state') and 'client_ip' in st.session_state:
            return st.session_state.client_ip
        
        # Try to get from request headers (if available)
        if hasattr(st, 'request') and hasattr(st.request, 'headers'):
            # Check common IP headers
            for header in ['X-Forwarded-For', 'X-Real-IP', 'CF-Connecting-IP']:
                if header in st.request.headers:
                    ip = st.request.headers[header].split(',')[0].strip()
                    if ip and ip != 'unknown':
                        return ip
            
            # Fallback to remote address
            if hasattr(st.request, 'remote_ip'):
                return st.request.remote_ip
        
        # Default fallback
        return "127.0.0.1"
    except:
        return "127.0.0.1"

def get_user_agent():
    """Get user agent from Streamlit request"""
    try:
        # Try to get from request headers
        if hasattr(st, 'request') and hasattr(st.request, 'headers'):
            if 'User-Agent' in st.request.headers:
                return st.request.headers['User-Agent']
        
        # Default fallback
        return "Streamlit/1.0"
    except:
        return "Streamlit/1.0"

# Initialize database on import
init_user_database()