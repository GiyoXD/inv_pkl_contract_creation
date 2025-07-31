#!/usr/bin/env python3
"""
Script to create an initial admin user for testing
"""

import sqlite3
import os
from login import hash_password, init_user_database, USER_DB_PATH

def create_admin_user(username="admin", password="admin123"):
    """Create an initial admin user"""
    
    # Initialize database
    init_user_database()
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Check if admin user already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        print(f"❌ User '{username}' already exists!")
        conn.close()
        return False
    
    # Create admin user
    password_hash = hash_password(password)
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (?, ?, 'admin', 1)
    ''', (username, password_hash))
    
    user_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    print(f"✅ Admin user created successfully!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   User ID: {user_id}")
    print(f"   Role: admin")
    
    return True

def create_test_user(username="testuser", password="test123"):
    """Create a test regular user"""
    
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        print(f"❌ User '{username}' already exists!")
        conn.close()
        return False
    
    # Create test user
    password_hash = hash_password(password)
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, role, is_active)
        VALUES (?, ?, 'user', 1)
    ''', (username, password_hash))
    
    user_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    print(f"✅ Test user created successfully!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   User ID: {user_id}")
    print(f"   Role: user")
    
    return True

def main():
    """Create initial users for testing"""
    print("🚀 Setting up initial users for authentication testing...\n")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create admin user
    create_admin_user()
    print()
    
    # Create test user
    create_test_user()
    print()
    
    print("🎉 Setup complete! You can now test the enhanced authentication system.")
    print("\n📝 Test the following features:")
    print("   1. Login with admin/admin123 to access admin features")
    print("   2. Login with testuser/test123 for regular user experience")
    print("   3. Try accessing admin pages with regular user account")
    print("   4. Test session timeout warnings")
    print("   5. Test redirect functionality")

if __name__ == "__main__":
    main()