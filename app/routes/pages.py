"""
Page Routes
Handles rendering of main pages (dashboard, download, library)
"""
from flask import Blueprint, render_template, redirect, url_for
from app.utils import login_required

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

@pages_bp.route('/search')
@login_required
def search_page():
    """Search page"""
    return render_template('search.html')

@pages_bp.route('/library')
@login_required
def library():
    """Library page showing all downloaded anime"""
    return render_template('library.html')

@pages_bp.route('/library/<anime_name>')
@login_required
def anime_detail(anime_name):
    """Detail page for a specific anime"""
    return render_template('anime_detail.html', anime_name=anime_name)
