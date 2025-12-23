"""
Library API Routes
Handles listing and serving downloaded anime files
"""
from flask import Blueprint, jsonify, send_file, current_app
from datetime import datetime
import os
from utils import login_required

library_bp = Blueprint('library', __name__, url_prefix='/api/library')

@library_bp.route('/list', methods=['GET'])
@login_required
def list_library():
    """List all downloaded anime and their files"""
    try:
        library = {}
        download_folder = current_app.config['DOWNLOAD_FOLDER']
        
        if os.path.exists(download_folder):
            for anime_dir in os.listdir(download_folder):
                anime_path = os.path.join(download_folder, anime_dir)
                if os.path.isdir(anime_path):
                    files = []
                    total_size = 0
                    for file in os.listdir(anime_path):
                        file_path = os.path.join(anime_path, file)
                        if os.path.isfile(file_path):
                            size = os.path.getsize(file_path)
                            total_size += size
                            files.append({
                                "name": file,
                                "size": size,
                                "size_mb": round(size / (1024 * 1024), 2),
                                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                    
                    library[anime_dir] = {
                        "files": sorted(files, key=lambda x: x['name']),
                        "total_files": len(files),
                        "total_size_mb": round(total_size / (1024 * 1024), 2)
                    }
        
        return jsonify(library)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/file/<path:filename>', methods=['GET'])
@login_required
def download_file(filename):
    """Download a completed file"""
    try:
        # Search for file in downloads directory
        for root, dirs, files in os.walk(current_app.config['DOWNLOAD_FOLDER']):
            if filename in files:
                filepath = os.path.join(root, filename)
                return send_file(filepath, as_attachment=True)
        
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
