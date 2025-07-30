#!/usr/bin/env python3
"""
IP and User Agent Detection Test
This script tests the IP and user agent detection methods
"""

import streamlit as st
import os

def test_ip_detection():
    """Test IP detection methods"""
    st.title("🌐 IP and User Agent Detection Test")
    
    st.header("🔍 IP Detection Methods")
    
    # Method 1: Environment variables
    st.subheader("Environment Variables")
    env_vars = ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR']
    for var in env_vars:
        value = os.environ.get(var, 'Not found')
        st.write(f"**{var}**: {value}")
    
    # Method 2: Streamlit request object
    st.subheader("Streamlit Request Object")
    if hasattr(st, 'request') and st.request:
        st.write(f"**Request object exists**: Yes")
        if hasattr(st.request, 'remote_ip'):
            st.write(f"**Remote IP**: {st.request.remote_ip}")
        if hasattr(st.request, 'headers'):
            st.write("**Headers found**:")
            for key, value in st.request.headers.items():
                if 'ip' in key.lower() or 'forward' in key.lower():
                    st.write(f"  {key}: {value}")
    else:
        st.write("**Request object exists**: No")
    
    # Method 3: Session-based identifier
    st.subheader("Session-based Identifier")
    if 'session_id' not in st.session_state:
        import secrets
        st.session_state['session_id'] = secrets.token_hex(8)
    
    session_id = st.session_state['session_id']
    st.write(f"**Session ID**: {session_id}")
    st.write(f"**Session-based IP**: session_{session_id}")
    
    # Test the actual functions
    st.header("🧪 Function Test Results")
    
    try:
        from login import get_client_ip, get_user_agent
        
        detected_ip = get_client_ip()
        detected_ua = get_user_agent()
        
        st.success(f"**Detected IP**: {detected_ip}")
        st.success(f"**Detected User Agent**: {detected_ua}")
        
        # Store in session state for comparison
        if 'test_ip' not in st.session_state:
            st.session_state['test_ip'] = detected_ip
            st.session_state['test_ua'] = detected_ua
        
        st.info("**Session State Storage**:")
        st.write(f"IP: {st.session_state.get('test_ip', 'Not stored')}")
        st.write(f"UA: {st.session_state.get('test_ua', 'Not stored')}")
        
    except Exception as e:
        st.error(f"Error testing functions: {e}")
    
    # Refresh button
    if st.button("🔄 Refresh Test"):
        st.rerun()
    
    st.header("📝 Notes")
    st.info("""
    **Why IP detection might show 'session_xxx':**
    
    1. **Streamlit Limitations**: Streamlit doesn't always provide direct access to client IP
    2. **Local Development**: When running locally, IP detection is limited
    3. **Proxy/Cloud**: If behind a proxy or cloud service, real IP might be hidden
    
    **Session-based tracking is still secure because:**
    - Each browser session gets a unique identifier
    - We can still track suspicious activity patterns
    - Rate limiting and account lockout still work
    - All security features remain functional
    """)

if __name__ == "__main__":
    test_ip_detection() 