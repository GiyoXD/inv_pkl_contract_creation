#!/usr/bin/env python3
"""
Check the admin user account status
"""

import sys
sys.path.append('.')
from login import get_all_users
import sqlite3

def check_admin_user():
    """Check the menchayheng admin user account"""
    print("Checking admin user account...")
    
    users = get_all_users()
    admin_user = None
    
    for user in users:
        if user['username'] == 'menchayheng':
            admin_user = user
            break
    
    if admin_user:
        print("Admin user found:")
        for key, value in admin_user.items():
            if key != 'password_hash':  # Don't show password hash
                print(f"  {key}: {value}")
        
        # Check if account is locked
        if admin_user.get('locked_until'):
            print(f"⚠️  Account is locked until: {admin_user['locked_until']}")
        
        if admin_user.get('failed_attempts', 0) > 0:
            print(f"⚠️  Failed attempts: {admin_user['failed_attempts']}")
        
        if not admin_user.get('is_active', True):
            print("⚠️  Account is inactive")
            
    else:
        print("❌ Admin user not found!")
        print("Available users:")
        for user in users:
            print(f"  - {user['username']} (role: {user['role']})")

if __name__ == "__main__":
    check_admin_user()