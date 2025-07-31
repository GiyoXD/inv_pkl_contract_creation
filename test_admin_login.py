#!/usr/bin/env python3
"""
Test the admin login
"""

import sys
sys.path.append('.')
from login import authenticate_user

def test_admin_login():
    """Test the admin login with the reset password"""
    print("Testing admin login...")
    
    username = "menchayheng"
    password = "admin123"
    
    try:
        result = authenticate_user(username, password)
        success = result[0]
        
        if success:
            user_info = result[1]
            print("✅ Admin login successful!")
            print(f"User ID: {user_info['user_id']}")
            print(f"Username: {user_info['username']}")
            print(f"Role: {user_info['role']}")
        else:
            message = result[1]
            print(f"❌ Admin login failed: {message}")
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")

if __name__ == "__main__":
    test_admin_login()