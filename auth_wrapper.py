import streamlit as st
from login import check_authentication, show_user_info, show_logout_button

def require_authentication(page_name=None, admin_required=False):
    """
    Authentication wrapper that provides enhanced redirect functionality
    
    Args:
        page_name: Name of the current page for better redirect messages
        admin_required: Whether admin privileges are required
    
    Returns:
        user_info if authenticated, None otherwise (and stops execution)
    """
    # Store the current page name for better redirect messages
    if page_name and 'current_page_name' not in st.session_state:
        st.session_state.current_page_name = page_name
    
    # Check authentication
    user_info = check_authentication()
    
    if not user_info:
        # Show custom redirect message based on page
        if page_name:
            st.error(f"🔒 Authentication required to access {page_name}")
            st.info("👆 Please log in using the main page to continue.")
        else:
            st.error("🔒 Authentication required")
            st.info("👆 Please log in to continue.")
        
        # Provide a link back to main page
        if st.button("🏠 Go to Login Page", use_container_width=True):
            st.switch_page("app.py")
        
        st.stop()
    
    # Check admin privileges if required
    if admin_required and user_info.get('role') != 'admin':
        st.error("🛡️ Admin privileges required to access this page")
        st.info("Contact your administrator if you need access to this feature.")
        
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.switch_page("app.py")
        
        st.stop()
    
    return user_info

def setup_page_auth(page_title, page_name=None, admin_required=False, layout="wide"):
    """
    Complete page setup with authentication, user info, and logout button
    
    Args:
        page_title: Title for the page configuration
        page_name: Display name for the page (for redirect messages)
        admin_required: Whether admin privileges are required
        layout: Streamlit page layout
    
    Returns:
        user_info if authenticated
    """
    # Set page config
    st.set_page_config(page_title=page_title, layout=layout)
    
    # Require authentication
    user_info = require_authentication(page_name, admin_required)
    
    # Show user info and logout button in sidebar
    show_user_info()
    show_logout_button()
    
    return user_info

def show_session_status():
    """Show session status and warnings in the sidebar"""
    user_info = st.session_state.get('user_info')
    session_token = st.session_state.get('session_token')
    
    if user_info and session_token:
        from login import validate_session
        from datetime import datetime
        
        session_info = validate_session(session_token)
        if session_info:
            from zoneinfo import ZoneInfo
            cambodia_tz = ZoneInfo("Asia/Phnom_Penh")
            expires_at = datetime.fromisoformat(session_info['expires_at'])
            # Make expires_at timezone-aware by assuming it's in Cambodia time
            expires_at = expires_at.replace(tzinfo=cambodia_tz)
            time_until_expiry = expires_at - datetime.now(cambodia_tz)
            
            # Show different warnings based on time left
            total_minutes = int(time_until_expiry.total_seconds() / 60)
            
            if total_minutes <= 0:
                st.sidebar.error("🔒 Session expired!")
            elif total_minutes <= 15:
                st.sidebar.error(f"⚠️ Session expires in {total_minutes} minutes!")
                if st.sidebar.button("🔄 Extend Session"):
                    st.rerun()
            elif total_minutes <= 60:
                st.sidebar.warning(f"⏰ Session expires in {total_minutes} minutes")
            else:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                st.sidebar.success(f"✅ Session active ({hours}h {minutes}m left)")

def create_admin_check_decorator(func):
    """Decorator to check admin privileges for specific functions"""
    def wrapper(*args, **kwargs):
        user_info = st.session_state.get('user_info')
        if not user_info or user_info.get('role') != 'admin':
            st.error("🛡️ Admin privileges required for this action")
            return None
        return func(*args, **kwargs)
    return wrapper