"""
Authentication Hardening System
A security-focused authentication demonstration implementing password hashing,
rate limiting, and account lockout protections against brute-force attacks.
"""

from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# In-memory storage (in production, use a real database)
users_db = {}
failed_attempts = {}
locked_accounts = {}

# Security configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
RATE_LIMIT_WINDOW = timedelta(minutes=5)
MAX_REQUESTS_PER_WINDOW = 10


class SecurityConfig:
    """Security configuration and constants"""
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True


def validate_password_strength(password):
    """
    Validates password meets security requirements
    Returns tuple: (is_valid, error_message)
    """
    if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters"
    
    if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if SecurityConfig.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    if SecurityConfig.REQUIRE_SPECIAL and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


def is_account_locked(username):
    """Check if account is currently locked"""
    if username in locked_accounts:
        lockout_time = locked_accounts[username]
        if datetime.now() < lockout_time:
            return True, lockout_time
        else:
            # Lockout expired, remove it
            del locked_accounts[username]
            if username in failed_attempts:
                del failed_attempts[username]
    return False, None


def record_failed_attempt(username):
    """Record a failed login attempt and lock account if threshold exceeded"""
    if username not in failed_attempts:
        failed_attempts[username] = []
    
    failed_attempts[username].append(datetime.now())
    
    # Count recent attempts within the rate limit window
    recent_attempts = [
        attempt for attempt in failed_attempts[username]
        if datetime.now() - attempt < RATE_LIMIT_WINDOW
    ]
    failed_attempts[username] = recent_attempts
    
    if len(recent_attempts) >= MAX_LOGIN_ATTEMPTS:
        locked_accounts[username] = datetime.now() + LOCKOUT_DURATION
        return True
    
    return False


def clear_failed_attempts(username):
    """Clear failed attempts after successful login"""
    if username in failed_attempts:
        del failed_attempts[username]


def require_auth(f):
    """Decorator to require authentication for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Authentication Hardening System API',
        'version': '1.0.0',
        'endpoints': {
            '/register': 'POST - Register new user',
            '/login': 'POST - Login user',
            '/logout': 'POST - Logout user',
            '/profile': 'GET - Get user profile (requires auth)',
            '/security-status': 'GET - Check security status for username'
        }
    })


@app.route('/register', methods=['POST'])
def register():
    """Register a new user with secure password hashing"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    # Validate username
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if username in users_db:
        return jsonify({'error': 'Username already exists'}), 409
    
    # Validate password strength
    is_valid, message = validate_password_strength(password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # Hash password using werkzeug's secure implementation (uses pbkdf2:sha256)
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Store user (in production, use proper database)
    users_db[username] = {
        'password_hash': hashed_password,
        'created_at': datetime.now().isoformat(),
        'email': data.get('email', '')
    }
    
    return jsonify({
        'message': 'User registered successfully',
        'username': username
    }), 201


@app.route('/login', methods=['POST'])
def login():
    """Login with rate limiting and account lockout protection"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    # Check if account is locked
    is_locked, lockout_time = is_account_locked(username)
    if is_locked:
        remaining_time = (lockout_time - datetime.now()).total_seconds()
        return jsonify({
            'error': 'Account temporarily locked due to too many failed attempts',
            'lockout_remaining_seconds': int(remaining_time)
        }), 429
    
    # Check if user exists
    if username not in users_db:
        record_failed_attempt(username)
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password
    user = users_db[username]
    if not check_password_hash(user['password_hash'], password):
        was_locked = record_failed_attempt(username)
        
        if was_locked:
            return jsonify({
                'error': 'Too many failed attempts. Account locked for 15 minutes.',
                'attempts_remaining': 0
            }), 429
        
        attempts_remaining = MAX_LOGIN_ATTEMPTS - len(failed_attempts.get(username, []))
        return jsonify({
            'error': 'Invalid credentials',
            'attempts_remaining': attempts_remaining
        }), 401
    
    # Successful login
    clear_failed_attempts(username)
    session['username'] = username
    
    return jsonify({
        'message': 'Login successful',
        'username': username
    }), 200


@app.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout current user"""
    username = session.get('username')
    session.pop('username', None)
    
    return jsonify({
        'message': 'Logout successful',
        'username': username
    }), 200


@app.route('/profile', methods=['GET'])
@require_auth
def profile():
    """Get current user profile (protected route)"""
    username = session['username']
    user = users_db[username]
    
    return jsonify({
        'username': username,
        'email': user.get('email', ''),
        'created_at': user['created_at']
    }), 200


@app.route('/security-status', methods=['GET'])
def security_status():
    """Check security status for a username (for demonstration)"""
    username = request.args.get('username')
    
    if not username:
        return jsonify({'error': 'Username parameter required'}), 400
    
    is_locked, lockout_time = is_account_locked(username)
    
    status = {
        'username': username,
        'is_locked': is_locked,
        'failed_attempts': len(failed_attempts.get(username, [])),
        'max_attempts': MAX_LOGIN_ATTEMPTS,
        'lockout_duration_minutes': int(LOCKOUT_DURATION.total_seconds() / 60)
    }
    
    if is_locked:
        remaining = (lockout_time - datetime.now()).total_seconds()
        status['lockout_remaining_seconds'] = int(remaining)
    
    return jsonify(status), 200


if __name__ == '__main__':
    print("=" * 60)
    print("Authentication Hardening System")
    print("=" * 60)
    print("Security Features:")
    print(f"  - Password hashing (PBKDF2-SHA256)")
    print(f"  - Rate limiting ({MAX_LOGIN_ATTEMPTS} attempts per {RATE_LIMIT_WINDOW})")
    print(f"  - Account lockout ({LOCKOUT_DURATION} duration)")
    print(f"  - Strong password requirements")
    print(f"  - Session-based authentication")
    print("=" * 60)
    print("\nStarting server on http://localhost:5000")
    print("Use the demo script (demo.py) to test the system\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
