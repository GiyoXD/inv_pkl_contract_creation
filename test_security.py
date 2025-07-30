#!/usr/bin/env python3
"""
Security Test Script
This script demonstrates the security features implemented in the login system.
Use this to test brute force protection, rate limiting, and account lockout.
"""

import requests
import time
import json
from datetime import datetime

def test_login_attempt(username, password, base_url="http://localhost:8501"):
    """Test a single login attempt"""
    try:
        # Simulate login form submission
        # Note: This is a simplified test - actual Streamlit forms work differently
        print(f"Testing login: {username} / {password}")
        
        # In a real scenario, you would use Selenium or similar to interact with Streamlit
        # For demonstration, we'll just show what would happen
        
        return {
            'username': username,
            'password': password,
            'timestamp': datetime.now().isoformat(),
            'status': 'attempted'
        }
    except Exception as e:
        return {
            'username': username,
            'password': password,
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }

def test_brute_force_protection():
    """Test brute force protection by attempting multiple failed logins"""
    print("🔒 Testing Brute Force Protection")
    print("=" * 50)
    
    # Test with wrong passwords
    test_cases = [
        ("menchayheng", "wrong_password_1"),
        ("menchayheng", "wrong_password_2"),
        ("menchayheng", "wrong_password_3"),
        ("menchayheng", "wrong_password_4"),
        ("menchayheng", "wrong_password_5"),
        ("menchayheng", "wrong_password_6"),  # This should trigger lockout
    ]
    
    print("Attempting 6 failed login attempts...")
    print("After 5 attempts, the account should be locked for 15 minutes.")
    print()
    
    for i, (username, password) in enumerate(test_cases, 1):
        result = test_login_attempt(username, password)
        print(f"Attempt {i}: {result['status']}")
        
        if i == 5:
            print("⚠️  Account should now be locked!")
            print("⏰ Lockout duration: 15 minutes")
        
        time.sleep(1)  # Small delay between attempts
    
    print()
    print("✅ Brute force protection test completed!")
    print("Check the Security Monitor page to see the failed attempts logged.")

def test_rate_limiting():
    """Test rate limiting by making rapid requests"""
    print("\n🚦 Testing Rate Limiting")
    print("=" * 50)
    
    print("Making 12 rapid login attempts (rate limit: 10 per minute)...")
    print("The last 2 attempts should be rate limited.")
    print()
    
    for i in range(12):
        result = test_login_attempt("testuser", "testpass")
        print(f"Request {i+1}: {result['status']}")
        
        if i >= 9:
            print("⚠️  This request should be rate limited!")
        
        time.sleep(0.1)  # Very rapid requests
    
    print()
    print("✅ Rate limiting test completed!")
    print("Check the Security Monitor page to see rate limited requests.")

def test_security_features():
    """Test various security features"""
    print("\n🛡️ Security Features Overview")
    print("=" * 50)
    
    features = [
        "✅ Account Lockout: 5 failed attempts = 15 minute lockout",
        "✅ Rate Limiting: 10 requests per minute per IP",
        "✅ Session Management: 24-hour sessions with activity tracking",
        "✅ Concurrent Session Limit: Maximum 3 sessions per user",
        "✅ Security Audit Logging: All events logged with IP and user agent",
        "✅ Password Hashing: SHA-256 encryption",
        "✅ Session Cleanup: Automatic cleanup of expired sessions",
        "✅ IP Tracking: All login attempts tracked by IP address",
        "✅ User Agent Logging: Browser/client information logged",
        "✅ Admin Monitoring: Security dashboard for threat detection"
    ]
    
    for feature in features:
        print(feature)
    
    print()
    print("📊 Security Monitoring Dashboard Features:")
    monitoring_features = [
        "• Real-time security statistics",
        "• Failed login attempt tracking",
        "• Suspicious IP address detection",
        "• User account status monitoring",
        "• Security audit log with filtering",
        "• System health checks",
        "• Automated cleanup tools",
        "• Security recommendations"
    ]
    
    for feature in monitoring_features:
        print(f"  {feature}")

def main():
    """Main test function"""
    print("🛡️ Security System Test Suite")
    print("=" * 60)
    print("This script demonstrates the security features implemented.")
    print("To run actual tests, you need to:")
    print("1. Start the Streamlit app: streamlit run app.py")
    print("2. Open the Security Monitor page")
    print("3. Manually test the login system")
    print()
    
    test_security_features()
    test_brute_force_protection()
    test_rate_limiting()
    
    print("\n" + "=" * 60)
    print("🎯 How to Test the Security Features:")
    print("=" * 60)
    print()
    print("1. 🔐 Login System Testing:")
    print("   • Try logging in with correct credentials: menchayheng / hengh428")
    print("   • Try logging in with wrong password multiple times")
    print("   • Observe account lockout after 5 failed attempts")
    print()
    print("2. 🚦 Rate Limiting Testing:")
    print("   • Rapidly submit login forms")
    print("   • Try refreshing pages quickly")
    print("   • Observe rate limiting messages")
    print()
    print("3. 📊 Security Monitoring:")
    print("   • Go to 'Security Monitor' page (admin only)")
    print("   • View security statistics and audit logs")
    print("   • Check for suspicious IP addresses")
    print("   • Monitor user account status")
    print()
    print("4. 🔧 Admin Features:")
    print("   • Create new users via 'User Management'")
    print("   • Unlock locked accounts")
    print("   • Reset failed attempt counters")
    print("   • View security recommendations")
    print()
    print("5. 🧹 System Maintenance:")
    print("   • Use cleanup tools in Security Monitor")
    print("   • Check system health status")
    print("   • Review security audit logs")
    print()
    print("🔍 Security Log Location: data/security.log")
    print("🗄️  Database Location: data/user_database.db")

if __name__ == "__main__":
    main() 