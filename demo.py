"""
Demo script to test the Authentication Hardening System
Shows various security features in action
"""

import requests
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_registration():
    """Test user registration with password strength validation"""
    print_section("Testing User Registration")
    
    # Test weak password
    print("\n1. Attempting registration with weak password...")
    response = requests.post(f"{BASE_URL}/register", json={
        "username": "testuser",
        "password": "weak"
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test strong password
    print("\n2. Attempting registration with strong password...")
    response = requests.post(f"{BASE_URL}/register", json={
        "username": "testuser",
        "password": "SecurePass123!",
        "email": "test@example.com"
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")


def test_failed_login_attempts():
    """Test rate limiting and account lockout"""
    print_section("Testing Failed Login Attempts & Account Lockout")
    
    for attempt in range(1, 7):
        print(f"\n{attempt}. Failed login attempt...")
        response = requests.post(f"{BASE_URL}/login", json={
            "username": "testuser",
            "password": "WrongPassword123!"
        })
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 429:
            print("\n   ⚠️  ACCOUNT LOCKED! Too many failed attempts.")
            break
        
        time.sleep(0.5)


def test_security_status():
    """Check security status"""
    print_section("Checking Security Status")
    
    response = requests.get(f"{BASE_URL}/security-status", params={
        "username": "testuser"
    })
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")


def test_successful_login():
    """Test successful login"""
    print_section("Testing Successful Login")
    
    print("\nAttempting login with correct credentials...")
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", json={
        "username": "testuser",
        "password": "SecurePass123!"
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✓ Login successful!")
        
        # Test protected route
        print("\nAccessing protected profile endpoint...")
        profile_response = session.get(f"{BASE_URL}/profile")
        print(f"Status: {profile_response.status_code}")
        print(f"Response: {profile_response.json()}")


def test_protected_route_without_auth():
    """Test accessing protected route without authentication"""
    print_section("Testing Protected Route Without Authentication")
    
    print("\nAttempting to access profile without login...")
    response = requests.get(f"{BASE_URL}/profile")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")


def main():
    print("\n" + "=" * 60)
    print("  AUTHENTICATION HARDENING SYSTEM - DEMO")
    print("=" * 60)
    print("\nMake sure the Flask app is running (python app.py)")
    input("Press Enter to start the demo...")
    
    try:
        # Check if server is running
        response = requests.get(BASE_URL)
        print(f"\n✓ Server is running")
        print(f"  {response.json()['message']}")
        
        # Run tests
        test_registration()
        time.sleep(1)
        
        test_failed_login_attempts()
        time.sleep(1)
        
        test_security_status()
        time.sleep(1)
        
        test_protected_route_without_auth()
        time.sleep(1)
        
        print("\n\n" + "=" * 60)
        print("  Waiting 2 seconds before successful login test...")
        print("=" * 60)
        time.sleep(2)
        
        test_successful_login()
        
        print("\n\n" + "=" * 60)
        print("  DEMO COMPLETED")
        print("=" * 60)
        print("\nSecurity features demonstrated:")
        print("  ✓ Password strength validation")
        print("  ✓ Secure password hashing")
        print("  ✓ Rate limiting on failed attempts")
        print("  ✓ Automatic account lockout")
        print("  ✓ Session-based authentication")
        print("  ✓ Protected route access control")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("   Please make sure the Flask app is running:")
        print("   python app.py")


if __name__ == "__main__":
    main()
