# Security Remediation Implementation Guide

## Quick Reference: Vulnerability Fixes

### Fix 1: SQL Injection in `app.py` (Line 205)

**Before:**
```python
if csv_file_id:
    query += f" WHERE csv_file_id = '{csv_file_id}'"
```

**After (use parameterized approach):**
```python
# Don't build query string manually
# Instead, use the connector method which should be fixed
data = databricks.load_table_data(table_name, csv_file_id=csv_file_id)
```

---

### Fix 2: SQL Injection in `databricks_connector.py` (Line 183)

**Before:**
```python
def load_table_data(self, table_name: str, limit: Optional[int] = None, csv_file_id: Optional[str] = None) -> List[Dict[str, Any]]:
    # ...
    query = f"SELECT * FROM {table_name}"
    if csv_file_id:
        query += f" WHERE csv_file_id = '{csv_file_id}'"  # ❌ VULNERABLE
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
```

**After (Parameterized Query):**
```python
def load_table_data(self, table_name: str, limit: Optional[int] = None, csv_file_id: Optional[str] = None) -> List[Dict[str, Any]]:
    # ...
    query = f"SELECT * FROM {table_name}"
    params = []
    
    if csv_file_id:
        query += " WHERE csv_file_id = ?"  # ✅ Parameterized
        params.append(csv_file_id)
    
    if limit:
        query += f" LIMIT {limit}"
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
```

---

### Fix 3: SQL Injection in Catalog/Schema Filters (Lines 115-120)

**Before:**
```python
catalog_filter = ""
if self.catalogs:
    catalog_list = "', '".join(self.catalogs)
    catalog_filter = f"AND table_catalog IN ('{catalog_list}')"  # ❌ VULNERABLE

schema_filter = ""
if self.schemas:
    schema_list = "', '".join(self.schemas)
    schema_filter = f"AND table_schema IN ('{schema_list}')"  # ❌ VULNERABLE
```

**After (Safer approach - still risky if user-controlled, so validate first):**
```python
# SAFER: Validate catalog/schema names (alphanumeric + underscore only)
import re

def _validate_identifier(name):
    """Validate SQL identifier (catalog/schema/table name)."""
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        raise ValueError(f"Invalid identifier: {name}")
    return name

catalog_filter = ""
if self.catalogs:
    # Validate each catalog name
    validated_catalogs = [self._validate_identifier(c) for c in self.catalogs]
    catalog_list = ', '.join([f"'{c}'" for c in validated_catalogs])
    catalog_filter = f"AND table_catalog IN ({catalog_list})"

schema_filter = ""
if self.schemas:
    # Validate each schema name
    validated_schemas = [self._validate_identifier(s) for s in self.schemas]
    schema_list = ', '.join([f"'{s}'" for s in validated_schemas])
    schema_filter = f"AND table_schema IN ({schema_list})"
```

---

### Fix 4: Debug Mode Enabled (Line 356)

**Before:**
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # ❌ CRITICAL
```

**After:**
```python
if __name__ == '__main__':
    # Only enable debug if explicitly set to 'development'
    debug_mode = os.getenv('FLASK_ENV', 'production').lower() == 'development'
    
    if debug_mode:
        app.logger.warning("⚠️  DEBUG MODE ENABLED - DO NOT USE IN PRODUCTION")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=debug_mode,
        use_reloader=debug_mode
    )
```

**Update `.env.example`:**
```env
# Flask Environment (development or production)
# IMPORTANT: Set to 'production' for all deployments
FLASK_ENV=production
```

---

### Fix 5: Weak Secret Key (Line 19)

**Before:**
```python
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
```

**After:**
```python
# Initialize secret key with validation
secret_key = os.environ.get('FLASK_SECRET_KEY')

if not secret_key:
    if os.getenv('FLASK_ENV', 'production').lower() == 'production':
        app.logger.error("CRITICAL: FLASK_SECRET_KEY not set for production!")
        raise ValueError(
            "FLASK_SECRET_KEY environment variable must be set in production.\n"
            "Generate a secure key with:\n"
            "  python -c \"import secrets; print(secrets.token_hex(32))\"\n"
            "Then set it in your .env file."
        )
    # Development fallback (unsafe, only for local development)
    secret_key = 'dev-unsafe-key-for-local-only'
    app.logger.warning("⚠️  Using insecure development secret key")

if len(secret_key) < 32:
    app.logger.warning("⚠️  FLASK_SECRET_KEY is less than 32 characters")

app.secret_key = secret_key
```

---

### Fix 6: Add Input Validation

**Add to `app.py` (near imports):**
```python
import re
from uuid import UUID

def validate_csv_file_id(csv_file_id):
    """
    Validate csv_file_id format.
    
    Args:
        csv_file_id: String to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If invalid format
    """
    if csv_file_id == 'all':
        return True
    
    # Assuming UUIDs based on folder structure
    try:
        UUID(csv_file_id)
        return True
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid csv_file_id format: {csv_file_id}")
```

**Update routes to use validation:**
```python
@app.route('/dashboard')
def dashboard():
    csv_file_id = request.args.get('csv_file_id', 'all')
    
    try:
        validate_csv_file_id(csv_file_id)
    except ValueError as e:
        return render_template('error.html', error=str(e)), 400
    
    # ... rest of function
```

---

### Fix 7: Fix Exception Handling

**Before:**
```python
for table_info in all_tables:
    # ...
    try:
        data = databricks.load_table_data(table_name, csv_file_id=csv_file_id, limit=1)
        if data and len(data) > 0:
            target_table = table_name
            table_data = databricks.load_table_data(target_table, csv_file_id=csv_file_id)
            break
    except:  # ❌ Bare except clause
        continue
```

**After:**
```python
for table_info in all_tables:
    # ...
    try:
        data = databricks.load_table_data(table_name, csv_file_id=csv_file_id, limit=1)
        if data and len(data) > 0:
            target_table = table_name
            table_data = databricks.load_table_data(target_table, csv_file_id=csv_file_id)
            break
    except Exception as e:  # ✅ Specific exception
        app.logger.debug(f"Table {table_name} does not contain csv_file_id {csv_file_id}: {str(e)}")
        continue
```

---

### Fix 8: Add Security Headers

**Add to `app.py` (before `@app.route` decorators):**
```python
@app.after_request
def set_security_headers(response):
    """
    Set security headers for all responses.
    
    Mitigates XSS, clickjacking, MIME sniffing, and other attacks.
    """
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection in older browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy - don't leak referrer info
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy - limit browser features
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Content Security Policy (strict)
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "  # Unsafe-inline needed for inline scripts
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers['Content-Security-Policy'] = csp
    
    # HSTS header (if using HTTPS - recommended 1 year)
    # Uncomment when HTTPS is enabled:
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    return response
```

---

### Fix 9: Temporary File Cleanup

**Before:**
```python
# Create temporary file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_path = os.path.join(temp_dir, filename)
df.to_csv(output_path, index=False)

return send_file(output_path, as_attachment=True, download_name=filename)
# ❌ File never deleted
```

**After:**
```python
import tempfile
import atexit

@app.route('/export')
def export_results():
    # ... validation code ...
    
    try:
        # Create temporary file with automatic cleanup
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            delete=False,
            prefix='provider_export_'
        ) as tmp_file:
            csv_path = tmp_file.name
        
        # Write CSV data
        df.to_csv(csv_path, index=False)
        
        # Log export for audit
        app.logger.info(f"CSV exported by {session.get('user_id', 'unknown')} to {csv_path}")
        
        # Send file to client
        return send_file(
            csv_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        app.logger.error(f"Export failed: {str(e)}", exc_info=True)
        return jsonify({'error': 'Export failed'}), 500
    
    finally:
        # Ensure temporary file is deleted
        try:
            if os.path.exists(csv_path):
                os.remove(csv_path)
                app.logger.debug(f"Cleaned up temporary file: {csv_path}")
        except Exception as e:
            app.logger.warning(f"Failed to cleanup temp file {csv_path}: {str(e)}")
```

---

### Fix 10: Add Audit Logging

**Add to `app.py` (after imports):**
```python
import logging
from logging.handlers import RotatingFileHandler
import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
log_formatter = logging.Formatter(
    '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler - rotate logs
file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.WARNING)

# Add handlers to app logger
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)

# Audit logger (separate file for compliance)
audit_logger = logging.getLogger('audit')
audit_file_handler = RotatingFileHandler(
    'logs/audit.log',
    maxBytes=10485760,  # 10MB
    backupCount=20  # Keep more audit logs
)
audit_file_handler.setFormatter(log_formatter)
audit_logger.addHandler(audit_file_handler)
audit_logger.setLevel(logging.INFO)
```

**Add audit logging to routes:**
```python
@app.route('/dashboard')
def dashboard():
    csv_file_id = request.args.get('csv_file_id', 'all')
    user_id = session.get('user_id', 'unknown')
    
    # Audit log: DATA ACCESS
    audit_logger.info(
        f"DATA_ACCESS | user={user_id} | csv_file_id={csv_file_id} | "
        f"ip={request.remote_addr} | user_agent={request.user_agent}"
    )
    
    # ... rest of function
```

---

### Fix 11: Add Rate Limiting

**Add to requirements.txt:**
```
Flask-Limiter==3.5.0
```

**Add to `app.py` (after Flask import):**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # In-memory storage (use Redis for production)
)

# Apply to sensitive endpoints
@app.route('/dashboard')
@limiter.limit("30 per minute")
def dashboard():
    # ... code

@app.route('/export')
@limiter.limit("10 per minute")  # Stricter limit on exports
def export_results():
    # ... code

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Strict for login attempts
def login():
    # ... code
```

---

## Updated Configuration Files

### `.env.example` - UPDATED

```env
# Flask Configuration
# CRITICAL: Set to 'production' for deployments
FLASK_ENV=production

# Secret Key for session management
# IMPORTANT: Generate a strong key with:
#   python -c "import secrets; print(secrets.token_hex(32))"
# Must be at least 32 characters for production
FLASK_SECRET_KEY=your-64-character-hex-string-here

# Databricks Connection
DATABRICKS_HOST=your-workspace-url.databricks.com
DATABRICKS_TOKEN=dapi...  # Never commit real tokens!
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_CATALOGS=databricks_poc
DATABRICKS_SCHEMAS=default

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_ENABLED=true

# Security
ENABLE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### `.gitignore` - UPDATED

```gitignore
# Environment variables (CRITICAL - never commit)
.env
.env.local
.env.*.local

# Logs (contain sensitive data)
logs/
logs/*.log
*.log

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
venv/
env/
ENV/
.venv

# Flask
instance/
.webassets-cache

# Uploads
uploads/
/tmp/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Distribution
dist/
build/
*.egg-info/

# Temporary files
*.tmp
*.bak
~*

# Data files (if any contain PII)
data_storage/*.json
data_storage/*.csv
```

### `requirements.txt` - UPDATED

```
# Provider Verification Dashboard - Python Dependencies

# Core Web Framework
Flask==3.0.0
Werkzeug==3.0.1

# Data Processing
pandas==2.1.4

# Configuration
python-dotenv==1.0.0

# Databricks Integration
databricks-sql-connector>=3.0.0

# Security
Flask-Limiter==3.5.0

# Logging (built-in, but documenting)
# - logging (built-in)
# - RotatingFileHandler (built-in)

# Optional for production:
# gunicorn==21.2.0  # Production WSGI server
# python-dotenv==1.0.0  # Environment variable management
```

---

## Step-by-Step Remediation Process

### Step 1: Immediate (TODAY)
```bash
# 1. Create security branch
git checkout -b security/fix-critical-vulnerabilities

# 2. Verify .gitignore
cat .gitignore | grep .env  # Should show .env is ignored

# 3. Backup current .env
cp .env .env.backup.$(date +%Y%m%d)
```

### Step 2: Critical Fixes (ASAP)
```bash
# 1. Fix SQL injections
# Edit databricks_connector.py and app.py
# (See code examples above)

# 2. Disable debug mode
# Update app.py line 356 and .env.example

# 3. Generate strong secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Copy output to .env as FLASK_SECRET_KEY

# 4. Test locally
export FLASK_ENV=development
python app.py
```

### Step 3: Add Input Validation
```bash
# 1. Add validate_csv_file_id function to app.py
# 2. Update routes to use validation
# 3. Test with invalid inputs
curl "http://localhost:8080/dashboard?csv_file_id=invalid'"
# Should return 400 error
```

### Step 4: Add Logging & Headers
```bash
# 1. Create logs directory
mkdir -p logs
echo "logs/" >> .gitignore

# 2. Add logging configuration to app.py
# 3. Add set_security_headers function
# 4. Test headers
curl -I http://localhost:8080/
# Should show X-Frame-Options, X-Content-Type-Options, etc.
```

### Step 5: Testing & Validation
```bash
# Run security tests
python -m pytest tests/security_tests.py  # Create these!

# Check for SQL injection vulnerabilities
# Test endpoint: /dashboard?csv_file_id=x' OR '1'='1
# Should return error, not data

# Verify no debug mode
# Should not see debugger at /__debugger__
```

### Step 6: Commit & Deploy
```bash
git add .
git commit -m "Security: Fix CRITICAL vulnerabilities (SQL injection, debug mode, auth)"
git push origin security/fix-critical-vulnerabilities

# Create pull request for review
```

---

## Security Testing Script

```python
# tests/security_tests.py
import unittest
from app import app

class SecurityTests(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_debug_mode_disabled(self):
        """Verify debug mode is disabled in production."""
        # Debug should not be enabled
        import os
        self.assertNotEqual(os.getenv('FLASK_ENV'), 'development')
    
    def test_secret_key_not_default(self):
        """Verify secret key is not the default weak key."""
        self.assertNotEqual(
            app.secret_key,
            'dev-secret-key-change-in-production'
        )
    
    def test_security_headers_present(self):
        """Verify security headers are set."""
        response = self.client.get('/')
        
        headers = {
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Content-Security-Policy'
        }
        
        for header in headers:
            self.assertIn(header, response.headers)
    
    def test_sql_injection_dashboard(self):
        """Verify SQL injection attempt is blocked."""
        response = self.client.get(
            "/dashboard?csv_file_id=x' OR '1'='1"
        )
        # Should return 400, not 200
        self.assertEqual(response.status_code, 400)
    
    def test_invalid_csv_file_id_rejected(self):
        """Verify invalid csv_file_id is rejected."""
        response = self.client.get(
            "/dashboard?csv_file_id=invalid!!!"
        )
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
```

---

## Checklist for Deployment

- [ ] All SQL injections fixed (4 locations)
- [ ] Debug mode disabled
- [ ] Strong secret key generated and set
- [ ] Input validation implemented
- [ ] Security headers added
- [ ] Exception handling improved
- [ ] Temporary files cleaned up
- [ ] Audit logging implemented
- [ ] Rate limiting configured
- [ ] Dependencies updated
- [ ] Security headers verified
- [ ] Tests pass
- [ ] Code review completed
- [ ] HTTPS configured
- [ ] .env file properly secured (0600 permissions)
- [ ] Logging directory created and in .gitignore

---

## Production Deployment Notes

1. **Set environment variables securely:**
   ```bash
   # Use environment variable management (not .env in production)
   export FLASK_ENV=production
   export FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   export DATABRICKS_TOKEN=your-secure-token
   ```

2. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 app:app
   ```

3. **Enable HTTPS:**
   - Use reverse proxy (nginx, Apache)
   - Get SSL certificate (Let's Encrypt, Azure Certificates)
   - Force HTTPS redirect

4. **Monitor logs:**
   ```bash
   tail -f logs/app.log
   tail -f logs/audit.log
   ```

5. **Regular security updates:**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

---

This guide provides actionable steps to fix all identified vulnerabilities before healthcare deployment.
