#!/usr/bin/env python3
"""
Test the token generation function
"""

import sys
sys.path.append('.')
from login import generate_registration_token, get_all_users

def test_token_generation():
    """Test the generate_registration_token function"""
    print("Testing token generation...")
    
    # Get a user to test with
    users = get_all_users()
    if not users:
        print("❌ No users found to test with")
        return
    
    user_id = users[0]['id']
    print(f"Testing with user ID: {user_id}")
    
    # Test the function with correct parameters
    try:
        token = generate_registration_token(
            created_by_user_id=user_id,
            max_uses=3,
            expires_hours=48  # 2 days in hours
        )
        
        if token:
            print("✅ Token generation successful!")
            print(f"Generated token: {token[:8]}...")
            print(f"Token length: {len(token)} characters")
        else:
            print("❌ Token generation failed - returned None")
            
    except Exception as e:
        print(f"❌ Error generating token: {e}")

if __name__ == "__main__":
    test_token_generation()