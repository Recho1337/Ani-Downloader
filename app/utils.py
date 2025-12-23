"""
Utility Functions and Decorators
"""
from flask import session, redirect, url_for
from functools import wraps
import os

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def create_download_folder(folder_path):
    """Create downloads folder if it doesn't exist"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
