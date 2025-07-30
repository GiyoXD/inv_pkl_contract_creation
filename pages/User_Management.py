import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from login import check_authentication, show_logout_button, show_user_info, hash_password, init_user_database

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
    page_title="User Management",
    page_icon="👥",
    layout="wide"
)

st.title("👥 User Management")
st.info("Manage users and their permissions.")

# Show user info and logout button in sidebar
show_user_info()
show_logout_button()

# Initialize database
init_user_database()

def get_all_users():
    """Get all users from the database"""
    conn = sqlite3.connect("data/user_database.db")
    df = pd.read_sql_query('''
        SELECT id, username, role, created_at, last_login, is_active
        FROM users
        ORDER BY created_at DESC
    ''', conn)
    conn.close()
    return df

def create_user(username, password, role):
    """Create a new user"""
    try:
        conn = sqlite3.connect("data/user_database.db")
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', (username, password_hash, role))
        
        conn.commit()
        conn.close()
        return True, "User created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error creating user: {str(e)}"

def update_user(user_id, username, role, is_active):
    """Update user information"""
    try:
        conn = sqlite3.connect("data/user_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET username = ?, role = ?, is_active = ?
            WHERE id = ?
        ''', (username, role, is_active, user_id))
        
        conn.commit()
        conn.close()
        return True, "User updated successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists!"
    except Exception as e:
        return False, f"Error updating user: {str(e)}"

def delete_user(user_id):
    """Delete a user (soft delete by setting is_active to 0)"""
    try:
        conn = sqlite3.connect("data/user_database.db")
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET is_active = 0 WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return True, "User deactivated successfully!"
    except Exception as e:
        return False, f"Error deactivating user: {str(e)}"

def reset_user_password(user_id, new_password):
    """Reset a user's password"""
    try:
        conn = sqlite3.connect("data/user_database.db")
        cursor = conn.cursor()
        
        password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        conn.close()
        return True, "Password reset successfully!"
    except Exception as e:
        return False, f"Error resetting password: {str(e)}"

# --- Main Interface ---
tab1, tab2 = st.tabs(["📋 User List", "➕ Create New User"])

with tab1:
    st.header("📋 Current Users")
    
    # Get all users
    users_df = get_all_users()
    
    if users_df.empty:
        st.info("No users found in the database.")
    else:
        # Display users in a nice format
        for _, user in users_df.iterrows():
            with st.expander(f"👤 {user['username']} ({user['role'].title()})"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Username:** {user['username']}")
                    st.write(f"**Role:** {user['role'].title()}")
                    st.write(f"**Status:** {'🟢 Active' if user['is_active'] else '🔴 Inactive'}")
                    st.write(f"**Created:** {user['created_at']}")
                    if user['last_login']:
                        st.write(f"**Last Login:** {user['last_login']}")
                
                with col2:
                    if user['username'] != 'menchayheng':  # Don't allow editing admin
                        if st.button(f"Edit {user['username']}", key=f"edit_{user['id']}"):
                            st.session_state[f"editing_user_{user['id']}"] = True
                
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

with tab2:
    st.header("➕ Create New User")
    
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

# --- Session Management ---
st.header("🔐 Active Sessions")
conn = sqlite3.connect("data/user_database.db")
sessions_df = pd.read_sql_query('''
    SELECT s.session_token, u.username, s.created_at, s.expires_at
    FROM sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.expires_at > ?
    ORDER BY s.created_at DESC
''', conn, params=[datetime.now()])
conn.close()

if sessions_df.empty:
    st.info("No active sessions found.")
else:
    st.dataframe(sessions_df, use_container_width=True)
    
    if st.button("Clear All Sessions"):
        conn = sqlite3.connect("data/user_database.db")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', [datetime.now()])
        conn.commit()
        conn.close()
        st.success("All expired sessions cleared!")
        st.rerun() 