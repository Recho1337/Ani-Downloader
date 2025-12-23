"""
Authentication Routes
Handles login, logout, and session management
"""
from flask import Blueprint, render_template, request, redirect, url_for, session
import os

auth_bp = Blueprint('auth', __name__)

# Get credentials from environment
USERNAME = os.environ.get('ANIME_USER', 'admin')
PASSWORD = os.environ.get('ANIME_PASS', 'admin')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('pages.dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.pop('logged_in', None)
    return redirect(url_for('auth.login'))
