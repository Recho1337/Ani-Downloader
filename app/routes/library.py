"""
Library API Routes
Handles listing and serving downloaded anime files
"""
from flask import Blueprint, jsonify, send_file, current_app
from datetime import datetime
import os
from app.utils import login_required

library_bp = Blueprint('library', __name__, url_prefix='/api/library')

@library_bp.route('/list', methods=['GET'])
@login_required
def list_library():
    """List all downloaded anime titles"""
    try:
        library = []
        download_folder = current_app.config['DOWNLOAD_FOLDER']
        
        if os.path.exists(download_folder):
            for anime_dir in os.listdir(download_folder):
                anime_path = os.path.join(download_folder, anime_dir)
                if os.path.isdir(anime_path):
                    files = os.listdir(anime_path)
                    file_count = len([f for f in files if os.path.isfile(os.path.join(anime_path, f))])
                    
                    total_size = 0
                    for file in files:
                        file_path = os.path.join(anime_path, file)
                        if os.path.isfile(file_path):
                            total_size += os.path.getsize(file_path)
                    
                    library.append({
                        "name": anime_dir,
                        "total_files": file_count,
                        "total_size_mb": round(total_size / (1024 * 1024), 2)
                    })
        
        # Sort by name
        library.sort(key=lambda x: x['name'])
        return jsonify(library)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/anime/<path:anime_name>', methods=['GET'])
@login_required
def get_anime_files(anime_name):
    """Get all files for a specific anime"""
    try:
        download_folder = current_app.config['DOWNLOAD_FOLDER']
        anime_path = os.path.join(download_folder, anime_name)
        
        if not os.path.exists(anime_path) or not os.path.isdir(anime_path):
            return jsonify({"error": "Anime not found"}), 404
        
        files = []
        for file in os.listdir(anime_path):
            file_path = os.path.join(anime_path, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                files.append({
                    "name": file,
                    "size": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "size_gb": round(size / (1024 * 1024 * 1024), 2),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })
        
        # Sort by filename
        files.sort(key=lambda x: x['name'])
        
        return jsonify({
            "anime_name": anime_name,
            "files": files,
            "total_files": len(files),
            "total_size_mb": round(sum(f['size'] for f in files) / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/file/<path:filename>', methods=['GET'])
@login_required
def download_file(filename):
    """Download a completed file"""
    try:
        download_folder = current_app.config['DOWNLOAD_FOLDER']
        
        # Search for file in downloads directory
        for root, dirs, files in os.walk(download_folder):
            if filename in files:
                filepath = os.path.join(root, filename)
                if os.path.isfile(filepath):
                    return send_file(
                        filepath, 
                        as_attachment=True,
                        download_name=filename,
                        mimetype='video/mp4'
                    )
        
        return jsonify({"error": f"File not found: {filename}"}), 404
    except Exception as e:
        print(f"Error downloading file '{filename}': {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
