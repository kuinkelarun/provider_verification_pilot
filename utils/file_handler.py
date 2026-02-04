"""
File handling utilities for CSV/Excel upload and validation
"""

import os
from werkzeug.utils import secure_filename
from datetime import datetime


ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'json'}


def validate_file(filename):
    """
    Validate if file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        bool: True if file extension is valid, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def handle_file_upload(file, upload_folder):
    """
    Handle file upload, save to disk with secure filename.
    
    Args:
        file: FileStorage object from Flask request
        upload_folder: Directory to save uploaded files
        
    Returns:
        str: Full path to saved file
    """
    # Create secure filename with timestamp to avoid conflicts
    original_filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{original_filename}"
    
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    return filepath


def get_file_size(filepath):
    """
    Get file size in a human-readable format.
    
    Args:
        filepath: Path to file
        
    Returns:
        str: File size in MB
    """
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    return f"{size_mb:.2f} MB"
