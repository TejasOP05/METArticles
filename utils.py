import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app

def save_article_file(file):
    """Save uploaded file and return filename"""
    if file and file.filename:
        # Generate a random filename to avoid conflicts
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        random_name = secrets.token_hex(16)
        filename = f"{random_name}{ext}"
        
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return filename
    return None

def get_file_size(filename):
    """Get file size in bytes"""
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'pdf'
