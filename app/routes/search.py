"""
Search API Routes
Handles anime search on AnimeKai
"""
from flask import Blueprint, jsonify, request
from app.utils import login_required
from app.search import search_anime

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/anime', methods=['GET'])
@login_required
def search_anime_api():
    """Search for anime by keyword"""
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400
    
    try:
        results = search_anime(query)
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
