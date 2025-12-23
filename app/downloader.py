"""
AnimeKai Downloader Core Module
Extracted from the Jupyter notebook for use in web applications
"""

import requests
import re
import json
import os
import time
import subprocess
from typing import List, Optional, Tuple, Dict, Any
from bs4 import BeautifulSoup
import cloudscraper
from urllib.parse import urlparse
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class AnimeDownloader:
    def __init__(self, config: Dict[str, Any] = None):
        self.BASE_URL = "https://anikai.to"
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True}
        )
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": self.BASE_URL,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        
        # Default configuration
        self.config = {
            "download_method": "yt-dlp",
            "max_retries": 7,
            "sleep_between": 3,
            "timeout": 300,
            "max_workers": 15,
            "chunk_size_mb": 15,
        }
        if config:
            self.config.update(config)
        
        self.progress_callback = None
        self.log_callback = None

    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback

    def set_log_callback(self, callback):
        """Set callback for log messages"""
        self.log_callback = callback

    def log(self, level: str, msg: str):
        """Log message"""
        message = f"[{level}] {msg}"
        print(message)
        if self.log_callback:
            self.log_callback(level, msg)

    def call_enc_dec_api(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call enc-dec.app API"""
        base = "https://enc-dec.app/api"
        url = f"{base}/{endpoint}"
        try:
            if endpoint.startswith("enc-"):
                text = payload.get("text", "")
                resp = self.scraper.get(f"{url}?text={text}", headers=self.HEADERS, timeout=15)
            else:
                resp = self.scraper.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                    timeout=30,
                )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.log("ERROR", f"enc-dec API '{endpoint}' failed: {e}")
            return None

    def enc_kai(self, text: str) -> Optional[str]:
        data = self.call_enc_dec_api("enc-kai", {"text": text})
        if not data or "result" not in data:
            self.log("ERROR", "Failed to get enc-kai result.")
            return None
        return data["result"]

    def dec_kai(self, text: str) -> Optional[Dict[str, Any]]:
        data = self.call_enc_dec_api("dec-kai", {"text": text})
        if not data or "result" not in data:
            self.log("ERROR", "Failed to decode dec-kai payload.")
            return None
        return data["result"]

    def dec_mega(self, text: str, agent: str) -> Optional[Dict[str, Any]]:
        data = self.call_enc_dec_api("dec-mega", {"text": text, "agent": agent})
        if not data or "result" not in data:
            self.log("ERROR", "Failed to decode dec-mega payload.")
            return None
        return data["result"]

    def get_anime_details(self, url: str) -> Tuple[Optional[str], str]:
        """Get anime ID and title from URL"""
        try:
            r = self.scraper.get(url, headers=self.HEADERS, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            anime_div = soup.select_one("div[data-id]")
            anime_id = anime_div.get("data-id") if anime_div else None

            title_elem = (
                soup.select_one("div.title-wrapper h1.title span")
                or soup.select_one("h1.title")
                or soup.select_one(".anime-title")
            )
            title = title_elem.get("title") if title_elem and title_elem.get("title") else (
                title_elem.text.strip() if title_elem else "Unknown"
            )
            title = re.sub(r'[<>:"/\\|?*]', "", title)
            return anime_id, title
        except Exception as e:
            self.log("ERROR", f"Error getting anime details: {e}")
            return None, "Unknown"

    def detect_season_from_title(self, title: str) -> int:
        """Auto-detect season number from title"""
        patterns = [
            r"[Ss]eason\s+(\d+)",
            r"[Ss](\d+)",
            r"(\d+)(?:st|nd|rd|th)\s+[Ss]eason",
            r"\s+(\d+)$",
            r"Part\s+(\d+)",
            r"Cour\s+(\d+)",
        ]
        for p in patterns:
            m = re.search(p, title)
            if m:
                return int(m.group(1))
        return 1

    def safe_episode_key(self, ep_id: str) -> Tuple[int, float]:
        """Convert episode ID to sortable key"""
        m = re.match(r"(\d+)(?:\.(\d+))?", ep_id)
        if m:
            main = int(m.group(1))
            frac = float(f"0.{m.group(2)}") if m.group(2) else 0.0
            return main, frac
        return (10**9, 0.0)

    def get_episode_list(self, anime_id: str) -> List[Dict[str, Any]]:
        """Get list of available episodes"""
        try:
            enc = self.enc_kai(anime_id)
            if not enc:
                return []
            url = f"{self.BASE_URL}/ajax/episodes/list?ani_id={anime_id}&_={enc}"
            r = self.scraper.get(url, headers=self.HEADERS, timeout=30)
            r.raise_for_status()
            data = r.json()
            html = data.get("result", "")
            if not html:
                return []

            soup = BeautifulSoup(html, "html.parser")
            episodes: List[Dict[str, Any]] = []
            for ep in soup.select("div.eplist a"):
                token = ep.get("token", "")
                ep_id = ep.get("num", "").strip()
                langs = ep.get("langs", "0")
                try:
                    langs_int = int(langs)
                except ValueError:
                    langs_int = 0
                if langs_int == 1:
                    subdub = "Sub"
                elif langs_int == 3:
                    subdub = "Dub & Sub"
                else:
                    subdub = ""

                episodes.append({
                    "id": ep_id,
                    "sort_key": self.safe_episode_key(ep_id),
                    "token": token,
                    "subdub": subdub,
                    "title": f"Episode {ep_id}",
                })
            episodes.sort(key=lambda e: e["sort_key"])
            return episodes
        except Exception as e:
            self.log("ERROR", f"Error getting episodes: {e}")
            return []

    def get_video_servers(self, token: str) -> List[Dict[str, str]]:
        """Get available video servers for episode"""
        try:
            enc = self.enc_kai(token)
            if not enc:
                return []
            url = f"{self.BASE_URL}/ajax/links/list?token={token}&_={enc}"
            r = self.scraper.get(url, headers=self.HEADERS, timeout=30)
            r.raise_for_status()
            data = r.json()
            html = data.get("result", "")
            if not html:
                return []
            soup = BeautifulSoup(html, "html.parser")
            servers: List[Dict[str, str]] = []
            for type_div in soup.select("div.server-items[data-id]"):
                type_id = type_div.get("data-id", "")
                for server in type_div.select("span.server[data-lid]"):
                    server_id = server.get("data-lid", "")
                    server_name = server.text.strip()
                    servers.append({
                        "type": type_id,
                        "server_id": server_id,
                        "server_name": server_name
                    })
            return servers
        except Exception as e:
            self.log("ERROR", f"Error getting servers: {e}")
            return []

    def choose_server(self, servers: List[Dict[str, str]], prefer_type: str, prefer_server: str) -> Optional[Dict[str, str]]:
        """Choose best server based on preferences"""
        type_map = {
            "Hard Sub": "sub",
            "Soft Sub": "softsub",
            "Dub (with subs)": "dub",
        }
        prefer_type_id = type_map.get(prefer_type, "softsub")

        if not servers:
            return None

        # Try exact match
        for s in servers:
            if s["type"] == prefer_type_id and prefer_server.lower() in s["server_name"].lower():
                return s

        # Try server name match
        for s in servers:
            if prefer_server.lower() in s["server_name"].lower():
                return s

        # Try type match
        for s in servers:
            if s["type"] == prefer_type_id:
                return s

        # Return first available
        return servers[0] if servers else None

    def get_video_data(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get video URL and subtitle tracks"""
        try:
            enc = self.enc_kai(server_id)
            if not enc:
                return None
            url = f"{self.BASE_URL}/ajax/links/view?id={server_id}&_={enc}"
            r = self.scraper.get(url, headers=self.HEADERS, timeout=30)
            r.raise_for_status()
            data = r.json()
            encoded_link = data.get("result", "")
            if not encoded_link:
                return None

            dec = self.dec_kai(encoded_link)
            if not dec:
                return None
            iframe_url = dec.get("url", "")
            if not iframe_url:
                return None

            parsed = urlparse(iframe_url)
            token = parsed.path.split("/")[-1]
            media_url = f"{parsed.scheme}://{parsed.netloc}/media/{token}"
            r2 = self.scraper.get(media_url, headers=self.HEADERS, timeout=30)
            r2.raise_for_status()
            j2 = r2.json()
            mega_token = j2.get("result", "")
            if not mega_token:
                return None

            mega = self.dec_mega(mega_token, self.HEADERS["User-Agent"])
            if not mega:
                return None

            sources = mega.get("sources", [])
            if not sources:
                return None

            video_url = sources[0].get("file", "")

            # Extract subtitle tracks
            subtitle_tracks = []
            tracks = mega.get("tracks", [])
            for track in tracks:
                if track.get("kind") == "captions" and track.get("file", "").endswith(".vtt"):
                    subtitle_tracks.append({
                        "url": track["file"],
                        "lang": track.get("label", "Unknown")
                    })

            return {
                "video_url": video_url,
                "subtitles": subtitle_tracks
            }
        except Exception as e:
            self.log("ERROR", f"Error getting video data: {e}")
            return None

    def generate_episode_filename(self, anime_title: str, season_num: int, ep_id: str) -> str:
        """Generate proper episode filename"""
        try:
            ep_num = float(ep_id)
            if ep_num == int(ep_num):
                ep_formatted = f"{int(ep_num):02d}"
            else:
                ep_formatted = ep_id
        except ValueError:
            ep_formatted = ep_id

        filename = f"{anime_title} Season {season_num:02d} Episode {ep_formatted}.mp4"
        filename = re.sub(r'[<>:"/\\|?*]', "", filename)
        return filename

    def download_with_ytdlp(self, url: str, output_file: str, episode_label: str, subtitles: List[Dict] = None) -> bool:
        """Download with yt-dlp, optionally embedding subtitles"""
        try:
            self.log("INFO", f"Downloading episode {episode_label} with yt-dlp")

            cmd = [
                "yt-dlp",
                url,
                "-o", output_file,
                "--no-warnings",
                "--no-check-certificate",
                "--concurrent-fragments", str(self.config["max_workers"]),
                "--retries", str(self.config["max_retries"]),
                "--fragment-retries", str(self.config["max_retries"]),
                "--socket-timeout", str(self.config["timeout"]),
                "--user-agent", self.HEADERS["User-Agent"],
                "--referer", self.BASE_URL,
                "--newline",
            ]

            if subtitles:
                self.log("INFO", f"Found {len(subtitles)} subtitle track(s)")
                temp_video = output_file.replace(".mp4", "_temp.mp4")
                cmd_copy = cmd.copy()
                cmd_copy[cmd_copy.index("-o") + 1] = temp_video

                # Download video
                result = subprocess.run(cmd_copy, capture_output=True, text=True)
                if result.returncode != 0 or not os.path.exists(temp_video):
                    self.log("ERROR", "Video download failed")
                    return False

                # Download subtitles
                sub_files = []
                for idx, sub in enumerate(subtitles):
                    sub_path = output_file.replace(".mp4", f"_sub{idx}.vtt")
                    try:
                        r = self.scraper.get(sub['url'], headers=self.HEADERS, timeout=30)
                        r.raise_for_status()
                        with open(sub_path, 'wb') as f:
                            f.write(r.content)
                        sub_files.append((sub_path, sub['lang']))
                    except Exception as e:
                        self.log("WARN", f"Failed to download subtitle {sub['lang']}: {e}")

                # Merge with ffmpeg
                if sub_files:
                    ffmpeg_cmd = ["ffmpeg", "-i", temp_video]
                    for sub_file, _ in sub_files:
                        ffmpeg_cmd.extend(["-i", sub_file])
                    ffmpeg_cmd.extend(["-map", "0:v", "-map", "0:a"])
                    for idx, (_, lang) in enumerate(sub_files, 1):
                        ffmpeg_cmd.extend([
                            "-map", f"{idx}:0",
                            f"-metadata:s:s:{idx-1}", f"language={lang[:3].lower()}",
                            f"-metadata:s:s:{idx-1}", f"title={lang}"
                        ])
                    ffmpeg_cmd.extend([
                        "-c:v", "copy",
                        "-c:a", "copy",
                        "-c:s", "mov_text",
                        "-y",
                        output_file
                    ])
                    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                    
                    # Cleanup
                    try:
                        os.remove(temp_video)
                        for sub_file, _ in sub_files:
                            os.remove(sub_file)
                    except Exception:
                        pass

                    if result.returncode == 0 and os.path.exists(output_file):
                        return True
                    else:
                        if os.path.exists(temp_video):
                            shutil.move(temp_video, output_file)
                        return os.path.exists(output_file)
                else:
                    shutil.move(temp_video, output_file)
                    return True
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0 and os.path.exists(output_file)

        except Exception as e:
            self.log("ERROR", f"yt-dlp error: {e}")
            return False

    def download_episode(self, video_data: Dict[str, Any], output_file: str, episode_label: str) -> bool:
        """Download a single episode"""
        url = video_data["video_url"]
        subtitles = video_data.get("subtitles", [])

        for attempt in range(1, self.config["max_retries"] + 1):
            if os.path.exists(output_file):
                os.remove(output_file)
            if attempt > 1:
                self.log("INFO", f"Retry {attempt}/{self.config['max_retries']} for episode {episode_label}")
            
            if self.download_with_ytdlp(url, output_file, episode_label, subtitles):
                self.log("INFO", f"✅ Successfully downloaded episode {episode_label}")
                return True
            
            time.sleep(self.config["sleep_between"])
        
        return False

    def merge_videos(self, file_list: List[str], anime_title: str, season_num: int, 
                    first_ep_id: str, last_ep_id: str) -> Optional[str]:
        """Merge multiple video files into one"""
        if not file_list:
            self.log("ERROR", "No files to merge")
            return None

        valid_files = [f for f in file_list if os.path.exists(f)]
        if len(valid_files) != len(file_list):
            self.log("ERROR", "Some input files for merging are missing")
            return None

        merged_filename = f"{anime_title} Season {season_num:02d} Episodes {first_ep_id}-{last_ep_id}.mp4"
        merged_filename = re.sub(r'[<>:"/\\|?*]', "", merged_filename)
        merged_path = os.path.join(os.path.dirname(file_list[0]), merged_filename)

        self.log("INFO", f"Merging {len(valid_files)} files into {merged_filename}")

        list_file = os.path.join(os.path.dirname(file_list[0]), "filelist_merge.txt")
        try:
            with open(list_file, "w", encoding="utf-8") as f:
                for vf in valid_files:
                    f.write(f"file '{os.path.abspath(vf)}'\n")

            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c:v", "copy",
                "-c:a", "copy",
                "-c:s", "copy",
                "-y",
                "-loglevel", "info",
                merged_path,
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0 or not os.path.exists(merged_path):
                self.log("ERROR", "ffmpeg merge failed")
                return None

            self.log("INFO", f"✅ Successfully merged: {merged_filename}")
            return merged_path
        except Exception as e:
            self.log("ERROR", f"Merge error: {e}")
            return None
        finally:
            try:
                if os.path.exists(list_file):
                    os.remove(list_file)
            except Exception:
                pass
