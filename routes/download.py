"""
Download API Routes
Handles anime information fetching, download job management, and execution
"""
from flask import Blueprint, jsonify, request, current_app
import threading
import os
from datetime import datetime
from utils import login_required
from anime_downloader import AnimeDownloader
from models import DownloadJob

download_bp = Blueprint('download', __name__, url_prefix='/api/download')

# Global storage for download jobs
download_jobs = {}
job_counter = 0
job_lock = threading.Lock()

def run_download_job(job: DownloadJob, download_folder):
    """Execute the download job in a separate thread"""
    try:
        # Initialize downloader
        downloader = AnimeDownloader(config={
            "download_method": job.config.get("download_method", "yt-dlp"),
            "max_retries": job.config.get("max_retries", 7),
            "timeout": job.config.get("timeout", 300),
            "max_workers": job.config.get("max_workers", 15),
        })

        # Set up callbacks
        def log_callback(level, msg):
            job.add_log(level, msg)

        downloader.set_log_callback(log_callback)

        # Get anime details
        job.status = "fetching_info"
        job.add_log("INFO", f"Fetching anime details from {job.anime_url}")
        
        anime_id, anime_title = downloader.get_anime_details(job.anime_url)
        if not anime_id:
            raise Exception("Could not extract anime ID from URL")

        job.anime_title = anime_title
        job.add_log("INFO", f"Found anime: {anime_title}")

        # Detect season
        detected_season = downloader.detect_season_from_title(anime_title)
        job.season = job.config.get("season_number", 0)
        if job.season == 0:
            job.season = detected_season
        job.add_log("INFO", f"Season: {job.season}")

        # Get episodes
        job.status = "fetching_episodes"
        episodes = downloader.get_episode_list(anime_id)
        if not episodes:
            raise Exception("No episodes found")

        job.add_log("INFO", f"Found {len(episodes)} episodes")

        # Filter episodes based on selection mode
        download_mode = job.config.get("download_mode", "All Episodes")
        if download_mode == "Single Episode":
            single_ep = job.config.get("single_episode", "1")
            selected = [ep for ep in episodes if ep["id"] == single_ep]
        elif download_mode == "Episode Range":
            start_ep = job.config.get("start_episode", "1")
            end_ep = job.config.get("end_episode", "1")
            
            def in_range(ep_id, start_id, end_id):
                start_key = downloader.safe_episode_key(start_id)
                end_key = downloader.safe_episode_key(end_id)
                key = downloader.safe_episode_key(ep_id)
                return start_key <= key <= end_key
            
            selected = [ep for ep in episodes if in_range(ep["id"], start_ep, end_ep)]
        else:  # All Episodes
            selected = episodes

        if not selected:
            raise Exception("No episodes match your selection")

        job.total_episodes = len(selected)
        job.add_log("INFO", f"Will download {job.total_episodes} episode(s)")

        # Create download directory
        download_dir = os.path.join(download_folder, anime_title)
        os.makedirs(download_dir, exist_ok=True)

        # Download episodes
        job.status = "downloading"
        downloaded_files = []
        prefer_type = job.config.get("prefer_type", "Soft Sub")
        prefer_server = job.config.get("prefer_server", "Server 1")

        for idx, ep in enumerate(selected, 1):
            ep_id = ep["id"]
            job.current_episode = ep_id
            job.add_log("INFO", f"Processing episode {ep_id} ({idx}/{job.total_episodes})")

            # Get servers
            servers = downloader.get_video_servers(ep["token"])
            if not servers:
                job.add_log("ERROR", f"No servers available for episode {ep_id}")
                continue

            # Choose server
            server = downloader.choose_server(servers, prefer_type, prefer_server)
            if not server:
                job.add_log("ERROR", f"Could not choose server for episode {ep_id}")
                continue

            job.add_log("INFO", f"Using server: {server['server_name']}")

            # Get video data
            video_data = downloader.get_video_data(server["server_id"])
            if not video_data:
                job.add_log("ERROR", f"Could not resolve video data for episode {ep_id}")
                continue

            # Generate filename
            filename = downloader.generate_episode_filename(anime_title, job.season, ep_id)
            filepath = os.path.join(download_dir, filename)

            # Download episode
            if downloader.download_episode(video_data, filepath, ep_id):
                downloaded_files.append(filepath)
                job.completed_episodes += 1
                job.progress = int((job.completed_episodes / job.total_episodes) * 100)
                job.downloaded_files.append(os.path.basename(filepath))
                job.add_log("INFO", f"✅ Successfully downloaded episode {ep_id}")
            else:
                job.add_log("ERROR", f"❌ Failed to download episode {ep_id}")

        # Merge if requested and multiple episodes
        merge_episodes = job.config.get("merge_episodes", False)
        if merge_episodes and len(downloaded_files) > 1:
            job.status = "merging"
            job.add_log("INFO", f"Merging {len(downloaded_files)} episodes...")
            
            first_ep_id = selected[0]["id"]
            last_ep_id = selected[-1]["id"]
            
            merged_file = downloader.merge_videos(
                downloaded_files,
                anime_title,
                job.season,
                first_ep_id,
                last_ep_id
            )

            if merged_file:
                job.merged_file = os.path.basename(merged_file)
                job.add_log("INFO", f"✅ Successfully merged into {job.merged_file}")
                
                # Remove individual files if requested
                if not job.config.get("keep_individual_files", False):
                    job.add_log("INFO", "Removing individual episode files...")
                    for f in downloaded_files:
                        try:
                            os.remove(f)
                            job.downloaded_files.remove(os.path.basename(f))
                        except Exception as e:
                            job.add_log("WARN", f"Could not remove {os.path.basename(f)}: {e}")
            else:
                job.add_log("ERROR", "❌ Merge failed")

        # Complete
        job.status = "completed"
        job.progress = 100
        job.end_time = datetime.now()
        job.add_log("INFO", f"🎉 Download job completed! Downloaded {job.completed_episodes}/{job.total_episodes} episodes")

    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.end_time = datetime.now()
        job.add_log("ERROR", f"Job failed: {e}")
        import traceback
        job.add_log("ERROR", traceback.format_exc())

@download_bp.route('/anime/info', methods=['POST'])
@login_required
def get_anime_info():
    """Get anime information from URL"""
    try:
        data = request.json
        anime_url = data.get('anime_url')
        
        if not anime_url:
            return jsonify({"error": "No URL provided"}), 400

        downloader = AnimeDownloader()
        anime_id, anime_title = downloader.get_anime_details(anime_url)
        
        if not anime_id:
            return jsonify({"error": "Could not fetch anime information"}), 400

        episodes = downloader.get_episode_list(anime_id)
        season = downloader.detect_season_from_title(anime_title)

        return jsonify({
            "anime_id": anime_id,
            "title": anime_title,
            "season": season,
            "total_episodes": len(episodes),
            "episodes": [{"id": ep["id"], "title": ep["title"]} for ep in episodes]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@download_bp.route('/start', methods=['POST'])
@login_required
def start_download():
    """Start a new download job"""
    global job_counter
    
    try:
        data = request.json
        anime_url = data.get('anime_url')
        
        if not anime_url:
            return jsonify({"error": "No URL provided"}), 400

        # Create new job
        with job_lock:
            job_counter += 1
            job_id = job_counter

        config = {
            "download_mode": data.get("download_mode", "All Episodes"),
            "single_episode": data.get("single_episode", "1"),
            "start_episode": data.get("start_episode", "1"),
            "end_episode": data.get("end_episode", "1"),
            "prefer_type": data.get("prefer_type", "Soft Sub"),
            "prefer_server": data.get("prefer_server", "Server 1"),
            "download_method": data.get("download_method", "yt-dlp"),
            "max_retries": data.get("max_retries", 7),
            "timeout": data.get("timeout", 300),
            "max_workers": data.get("max_workers", 15),
            "merge_episodes": data.get("merge_episodes", False),
            "season_number": data.get("season_number", 0),
            "keep_individual_files": data.get("keep_individual_files", False),
        }

        job = DownloadJob(job_id, anime_url, config)
        download_jobs[job_id] = job

        # Start download in background thread
        thread = threading.Thread(
            target=run_download_job, 
            args=(job, current_app.config['DOWNLOAD_FOLDER'])
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            "job_id": job_id,
            "message": "Download job started"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@download_bp.route('/status/<int:job_id>', methods=['GET'])
@login_required
def get_download_status(job_id):
    """Get status of a download job"""
    job = download_jobs.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job.to_dict())

@download_bp.route('/list', methods=['GET'])
@login_required
def list_downloads():
    """List all download jobs"""
    jobs = [job.to_dict() for job in download_jobs.values()]
    # Sort by start time, newest first
    jobs.sort(key=lambda x: x['start_time'], reverse=True)
    return jsonify(jobs)

@download_bp.route('/clear/<int:job_id>', methods=['DELETE'])
@login_required
def clear_download_job(job_id):
    """Clear a completed/failed job from history"""
    if job_id in download_jobs:
        job = download_jobs[job_id]
        if job.status in ["completed", "failed"]:
            del download_jobs[job_id]
            return jsonify({"message": "Job cleared"})
        else:
            return jsonify({"error": "Cannot clear active job"}), 400
    return jsonify({"error": "Job not found"}), 404
