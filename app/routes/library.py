"""
Library API Routes
Handles listing and serving downloaded anime files
"""
from flask import Blueprint, jsonify, send_file, current_app
from datetime import datetime
import os
from app.utils import login_required

library_bp = Blueprint('library', __name__, url_prefix='/api/library')

def collect_media_files(base_path):
    """Recursively collect media files under a directory."""
    media_files = []

    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.isfile(file_path):
                continue

            relative_path = os.path.relpath(file_path, base_path).replace(os.sep, "/")
            media_files.append({
                "absolute_path": file_path,
                "relative_path": relative_path,
            })

    media_files.sort(key=lambda item: item["relative_path"])
    return media_files

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
                    media_files = collect_media_files(anime_path)
                    file_count = len(media_files)
                    total_size = sum(os.path.getsize(file["absolute_path"]) for file in media_files)
                    seasons = sorted({
                        file["relative_path"].split("/", 1)[0]
                        for file in media_files
                        if "/" in file["relative_path"]
                    })
                    
                    library.append({
                        "name": anime_dir,
                        "total_files": file_count,
                        "total_size_mb": round(total_size / (1024 * 1024), 2),
                        "seasons": seasons,
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
        for media_file in collect_media_files(anime_path):
            file_path = media_file["absolute_path"]
            size = os.path.getsize(file_path)
            relative_path = media_file["relative_path"]
            season_folder = relative_path.split("/", 1)[0] if "/" in relative_path else None
            files.append({
                "name": os.path.basename(file_path),
                "relative_path": relative_path,
                "season_folder": season_folder,
                "size": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "size_gb": round(size / (1024 * 1024 * 1024), 2),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
        
        return jsonify({
            "anime_name": anime_name,
            "files": files,
            "total_files": len(files),
            "total_size_mb": round(sum(f['size'] for f in files) / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/file/<path:relative_path>', methods=['GET'])
@login_required
def download_file(relative_path):
    """Download a completed file"""
    try:
        download_folder = current_app.config['DOWNLOAD_FOLDER']

        filepath = os.path.abspath(os.path.join(download_folder, relative_path))
        download_root = os.path.abspath(download_folder)

        if not filepath.startswith(download_root + os.sep):
            return jsonify({"error": "Invalid file path"}), 400

        if os.path.isfile(filepath):
            return send_file(
                filepath,
                as_attachment=True,
                download_name=os.path.basename(filepath),
                mimetype='video/mp4'
            )

        return jsonify({"error": f"File not found: {relative_path}"}), 404
    except Exception as e:
        print(f"Error downloading file '{relative_path}': {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
