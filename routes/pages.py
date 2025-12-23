"""
Page Routes
Handles rendering of main pages (dashboard, download, library)
"""
from flask import Blueprint, render_template, redirect, url_for
from utils import login_required

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
@login_required
def index():
    """Redirect to dashboard"""
    return redirect(url_for('pages.dashboard'))

@pages_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard showing downloaded anime"""
    return render_template('dashboard.html')

@pages_bp.route('/download')
@login_required
def download_page():
    """Download page"""
    return render_template('download.html')

@pages_bp.route('/library')
@login_required
def library():
    """Library page showing all downloaded files"""
    return render_template('library.html')
