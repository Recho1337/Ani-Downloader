"""
Data Models
"""
from datetime import datetime

class DownloadJob:
    """Represents a download job with progress tracking"""
    def __init__(self, job_id, anime_url, config):
        self.job_id = job_id
        self.anime_url = anime_url
        self.config = config
        self.status = "initializing"
        self.progress = 0
        self.current_episode = None
        self.total_episodes = 0
        self.completed_episodes = 0
        self.logs = []
        self.error = None
        self.downloaded_files = []
        self.merged_file = None
        self.start_time = datetime.now()
        self.end_time = None
        self.anime_title = None
        self.season = None

    def add_log(self, level, message):
        """Add a log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

    def to_dict(self):
        """Convert job to dictionary for JSON serialization"""
        elapsed = None
        if self.end_time:
            elapsed = (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()

        return {
            "job_id": self.job_id,
            "anime_url": self.anime_url,
            "anime_title": self.anime_title,
            "season": self.season,
            "status": self.status,
            "progress": self.progress,
            "current_episode": self.current_episode,
            "total_episodes": self.total_episodes,
            "completed_episodes": self.completed_episodes,
            "logs": self.logs[-20:],  # Return last 20 logs
            "error": self.error,
            "downloaded_files": self.downloaded_files,
            "merged_file": self.merged_file,
            "elapsed_seconds": int(elapsed) if elapsed else None,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
