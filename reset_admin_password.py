#!/usr/bin/env python3
"""
Reset the admin user password
"""

import sys
sys.path.append('.')
from login import hash_password
import sqlite3

def reset_admin_password():
    """Reset the menchayheng admin password"""
    print("Resetting admin password...")
    
    # Set a known password
    new_password = "admin123"  # You can change this
    hashed_password = hash_password(new_password)
    
    try:
        conn = sqlite3.connect('data/user_database.db')
        cursor = conn.cursor()
        
        # Reset password and clear failed attempts
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, failed_attempts = 0, locked_until = NULL 
            WHERE username = 'menchayheng'
        ''', (hashed_password,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Admin password reset successfully!")
            print(f"Username: menchayheng")
            print(f"Password: {new_password}")
            print("⚠️  Please change this password after logging in!")
        else:
            print("❌ Admin user not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")

if __name__ == "__main__":
    reset_admin_password()