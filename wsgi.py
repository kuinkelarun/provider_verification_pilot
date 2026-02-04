"""
WSGI entry point for the Flask application
This file ensures proper path handling in Databricks Apps environment
"""

import sys
import os

# Ensure the application directory is in the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Debug: Print what's in the directory
print("=" * 80)
print(f"Current working directory: {os.getcwd()}")
print(f"App directory: {app_dir}")
print(f"Python path: {sys.path}")
print(f"\nFiles in app directory:")
for item in os.listdir(app_dir):
    item_path = os.path.join(app_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR]  {item}/")
        # List files in subdirectories
        try:
            for subitem in os.listdir(item_path):
                print(f"         - {subitem}")
        except:
            pass
    else:
        print(f"  [FILE] {item}")
print("=" * 80)

# Now import the Flask app
try:
    from app import app
    print("✅ Successfully imported Flask app!")
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    print(f"Looking for utils folder at: {os.path.join(app_dir, 'utils')}")
    print(f"Utils folder exists: {os.path.exists(os.path.join(app_dir, 'utils'))}")
    raise

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
