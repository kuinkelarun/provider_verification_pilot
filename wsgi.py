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

# Import the Flask app
from app import app

if __name__ == "__main__":
    # Databricks Apps sets the PORT environment variable automatically
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

