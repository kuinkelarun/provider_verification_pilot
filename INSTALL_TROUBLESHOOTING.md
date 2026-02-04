# 🔧 Installation Troubleshooting

## Issue: pip install fails with build dependencies error

You're getting this error because some packages (especially pandas) need compilation tools.

---

## ✅ Solution 1: Update pip first (Recommended)

```bash
# Update pip to latest version
python -m pip install --upgrade pip

# Then try installing requirements again
pip install -r requirements.txt
```

---

## ✅ Solution 2: Install packages one by one

If updating pip doesn't work, install packages individually:

```bash
# Install Flask first (usually no issues)
pip install Flask==3.0.0
pip install Werkzeug==3.0.1

# Install pandas (this is the one that usually causes issues)
pip install pandas==2.1.4

# Install Excel support
pip install openpyxl==3.1.2
pip install xlrd==2.0.1

# Install environment variables support
pip install python-dotenv==1.0.0
```

---

## ✅ Solution 3: Use pre-built wheels (Fastest)

Install packages without requiring compilation:

```bash
# Update pip and wheel
python -m pip install --upgrade pip wheel setuptools

# Install with pre-built binaries
pip install --only-binary :all: Flask pandas openpyxl xlrd python-dotenv Werkzeug
```

---

## ✅ Solution 4: Install without pandas version lock

If pandas 2.1.4 specifically is causing issues:

```bash
pip install Flask==3.0.0 Werkzeug==3.0.1 openpyxl==3.1.2 xlrd==2.0.1 python-dotenv==1.0.0
pip install pandas  # Install latest compatible version
```

---

## ✅ Solution 5: Minimal installation (Test quickly)

Install only essential packages to test the app:

```bash
pip install Flask pandas openpyxl
```

This skips version locks and gets you running quickly.

---

## 🎯 Recommended Quick Fix

Try this command sequence:

```bash
# 1. Update pip
python -m pip install --upgrade pip

# 2. Install wheel and setuptools
pip install --upgrade wheel setuptools

# 3. Install packages with pre-built wheels
pip install Flask Werkzeug pandas openpyxl xlrd python-dotenv

# 4. Verify installation
python -c "import flask; import pandas; import openpyxl; print('✓ All packages installed!')"
```

---

## 🔍 Check what's installed

After installation, verify:

```bash
pip list | findstr "Flask pandas openpyxl"
```

You should see:
- Flask (any version 3.x)
- pandas (any version 2.x)
- openpyxl (any version 3.x)

---

## 🚀 Test the app immediately

Once any of the above solutions work, test:

```bash
python app.py
```

If it starts without errors, you're good to go!

---

## 💡 Alternative: Skip dependencies check

If you just want to test quickly and some packages fail:

1. **Comment out** problematic imports in app.py temporarily
2. **Test** if Flask works
3. **Add back** packages one by one

---

## 📝 Common Error Messages & Solutions

### "Microsoft Visual C++ 14.0 or greater is required"
**Solution**: Install pre-built wheels (Solution 3 above)

### "No matching distribution found"
**Solution**: Use latest versions without version locks (Solution 4)

### "externally-managed-environment"
**Solution**: Use virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## ✅ Working? Start the app!

Once packages install successfully:

```bash
python app.py
```

Then go to: **http://localhost:5000**

---

**Still having issues?** Try the minimal installation (Solution 5) - it gets you running fastest!
