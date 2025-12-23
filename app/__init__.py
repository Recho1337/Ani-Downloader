"""
AnimeKai Downloader Application Package
"""
from flask import Flask
import os

def create_app():
    """Application factory pattern"""
    # Get the parent directory (Ani-Downloader) for templates and static files
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    # Configuration
    download_folder = os.environ.get('DOWNLOAD_FOLDER', os.path.join(base_dir, 'downloads'))
    app.config['DOWNLOAD_FOLDER'] = download_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024  # 16GB max
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Create downloads folder
    from app.utils import create_download_folder
    create_download_folder(app.config['DOWNLOAD_FOLDER'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.pages import pages_bp
    from app.routes.library import library_bp
    from app.routes.download import download_bp
    from app.routes.search import search_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(download_bp)
    app.register_blueprint(search_bp)
    
    return app
