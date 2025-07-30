import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta

# Database path
USER_DB_PATH = "data/user_database.db"

def get_persistent_session():
    """Get session token from persistent storage"""
    try:
        # First try session state
        if 'session_token' in st.session_state:
            return st.session_state['session_token']
        
        # Try to get from database (most recent valid session)
        conn = sqlite3.connect(USER_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_token, user_id FROM sessions 
            WHERE expires_at > datetime('now')
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            session_token, user_id = result
            # Store in session state for future use
            st.session_state['session_token'] = session_token
            return session_token
        
        return None
        
    except Exception as e:
        print(f"Error getting persistent session: {e}")
        return None

def set_persistent_session(session_token, user_info):
    """Store session token in persistent storage"""
    try:
        # Store in session state
        st.session_state['session_token'] = session_token
        st.session_state['user_info'] = user_info
        
        # Also try to store in a simple file-based cache
        cache_dir = "data/session_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        cache_file = os.path.join(cache_dir, "current_session.txt")
        with open(cache_file, 'w') as f:
            f.write(f"{session_token}\n{user_info['username']}\n{user_info['role']}")
            
    except Exception as e:
        print(f"Error setting persistent session: {e}")

def clear_persistent_session():
    """Clear session from persistent storage"""
    try:
        # Clear session state
        for key in ['session_token', 'user_info']:
            if key in st.session_state:
                del st.session_state[key]
        
        # Clear file cache
        cache_file = "data/session_cache/current_session.txt"
        if os.path.exists(cache_file):
            os.remove(cache_file)
            
    except Exception as e:
        print(f"Error clearing persistent session: {e}")

def get_session_from_cache():
    """Get session from file cache"""
    try:
        cache_file = "data/session_cache/current_session.txt"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    session_token = lines[0].strip()
                    username = lines[1].strip()
                    role = lines[2].strip()
                    
                    # Validate the session token
                    conn = sqlite3.connect(USER_DB_PATH)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT user_id FROM sessions 
                        WHERE session_token = ? AND expires_at > datetime('now')
                    ''', (session_token,))
                    
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        user_info = {
                            'user_id': result[0],
                            'username': username,
                            'role': role
                        }
                        return session_token, user_info
        
        return None, None
        
    except Exception as e:
        print(f"Error getting session from cache: {e}")
        return None, None 