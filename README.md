# Authentication Hardening System

A security-focused authentication demonstration implementing password hashing, rate limiting, and account lockout protections against brute-force attacks.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![Security](https://img.shields.io/badge/Security-Hardened-red.svg)

## 🔒 Security Features

- **Secure Password Hashing**: Uses PBKDF2-SHA256 algorithm via Werkzeug
- **Password Strength Validation**: Enforces strong password requirements
- **Rate Limiting**: Tracks failed login attempts per user
- **Account Lockout**: Automatically locks accounts after 5 failed attempts for 15 minutes
- **Session-Based Authentication**: Secure session management for logged-in users
- **Protected Routes**: Decorator-based route protection

## 📋 Requirements

- Python 3.8 or higher
- Flask 3.0.0
- Werkzeug 3.0.1

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/auth-hardening-system.git
cd auth-hardening-system
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Starting the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### Running the Demo

In a separate terminal, run the demo script to see all security features in action:

```bash
python demo.py
```

The demo will:
- Test password strength validation
- Attempt multiple failed logins
- Demonstrate account lockout
- Show successful authentication
- Test protected route access

## 🔐 API Endpoints

### Public Endpoints

#### `GET /`
Get API information

**Response:**
```json
{
  "message": "Authentication Hardening System API",
  "version": "1.0.0",
  "endpoints": {...}
}
```

#### `POST /register`
Register a new user

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123!",
  "email": "test@example.com"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "username": "testuser"
}
```

#### `POST /login`
Login with credentials

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123!"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "username": "testuser"
}
```

**Failed Response (401):**
```json
{
  "error": "Invalid credentials",
  "attempts_remaining": 3
}
```

**Locked Account Response (429):**
```json
{
  "error": "Account temporarily locked due to too many failed attempts",
  "lockout_remaining_seconds": 847
}
```

#### `GET /security-status?username=testuser`
Check security status for a username

**Response:**
```json
{
  "username": "testuser",
  "is_locked": false,
  "failed_attempts": 2,
  "max_attempts": 5,
  "lockout_duration_minutes": 15
}
```

### Protected Endpoints (Requires Authentication)

#### `GET /profile`
Get current user profile

**Response:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-02-08T12:34:56"
}
```

#### `POST /logout`
Logout current user

**Response:**
```json
{
  "message": "Logout successful",
  "username": "testuser"
}
```

## 🛡️ Security Implementation Details

### Password Hashing
- Algorithm: PBKDF2-SHA256
- Implementation: Werkzeug's `generate_password_hash` and `check_password_hash`
- Passwords are never stored in plain text

### Rate Limiting
- Tracks failed login attempts per username
- Maximum 5 failed attempts within 5-minute window
- Automatic account lockout for 15 minutes after threshold exceeded

### Account Lockout
- Triggered after 5 consecutive failed login attempts
- Lockout duration: 15 minutes
- Failed attempts counter resets after successful login
- Lockout expires automatically after duration

### Session Security
- Flask's secure session management
- Session-based authentication for protected routes
- Logout clears session data

## 🧪 Testing with cURL

### Register a User
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123!","email":"test@example.com"}'
```

### Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123!"}'
```

### Check Security Status
```bash
curl "http://localhost:5000/security-status?username=testuser"
```

## 📊 Configuration

Security settings can be modified in `app.py`:

```python
# Security configuration
MAX_LOGIN_ATTEMPTS = 5                      # Failed attempts before lockout
LOCKOUT_DURATION = timedelta(minutes=15)    # Lockout duration
RATE_LIMIT_WINDOW = timedelta(minutes=5)    # Time window for counting attempts
```

Password requirements in `SecurityConfig` class:
```python
class SecurityConfig:
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
```

## ⚠️ Important Notes

### For Production Use

This is a demonstration project. For production deployment:

1. **Use a real database** instead of in-memory storage
   - PostgreSQL, MySQL, or MongoDB recommended
   - Implement proper database models and migrations

2. **Set a secure SECRET_KEY**
   ```python
   app.secret_key = os.environ.get('SECRET_KEY')  # Set in environment variables
   ```

3. **Use HTTPS** for all communications
   - Deploy behind a reverse proxy (nginx, Apache)
   - Implement SSL/TLS certificates

4. **Add additional security measures**
   - CSRF protection (Flask-WTF)
   - Rate limiting per IP address (Flask-Limiter)
   - Two-factor authentication (2FA)
   - Email verification
   - Password reset functionality
   - Captcha for registration/login

5. **Implement proper logging**
   - Log all authentication attempts
   - Monitor for suspicious activity
   - Set up alerts for security events

6. **Use environment variables**
   - Never hardcode sensitive information
   - Use tools like python-dotenv

## 🎯 Learning Outcomes

This project demonstrates:
- ✅ Secure password storage and verification
- ✅ Protection against brute-force attacks
- ✅ Rate limiting implementation
- ✅ Session management
- ✅ RESTful API design
- ✅ Security best practices in web applications

## 📝 License

MIT License - feel free to use this project for learning and demonstration purposes.

## 👨‍💻 Author

Ethan Lynn
- GitHub: [@XoTtic809](https://github.com/XoTtic809)
- Portfolio: [ethanlynn.dev](https://ethanlynn.dev)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

**Disclaimer**: This project is for educational purposes. Always consult security professionals for production authentication systems.
