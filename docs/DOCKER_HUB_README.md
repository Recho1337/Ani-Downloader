# AnimeKai Downloader

A web-based anime downloader for AnimeKai with a modern interface, real-time progress tracking, and automatic subtitle embedding.

## Features

- 🎨 **Modern Web UI** - Clean, dark-themed interface with real-time updates
- 📥 **Multiple Download Modes** - Single episode, episode range, or entire seasons
- 💬 **Subtitle Support** - Automatic embedding for Soft Sub and Dub options
- 🔗 **Episode Merging** - Combine multiple episodes into one file
- 📊 **Live Progress Tracking** - Real-time download status and logs
- 🎯 **Quality Options** - Choose between different servers and subtitle types
- 📦 **Built-in Tools** - Includes ffmpeg and yt-dlp for seamless downloading

## Quick Start

### Basic Usage

```bash
docker run -d \
  --name animekai-downloader \
  -p 5000:5000 \
  -v /path/to/downloads:/app/downloads \
  recho1235/animekai-downloader:latest
```

Then open `http://localhost:5000` in your browser.

### Docker Compose (Recommended)

```yaml
services:
  anime-downloader:
    image: recho1235/animekai-downloader:latest
    container_name: animekai-downloader
    ports:
      - "5000:5000"
    volumes:
      - ./downloads:/app/downloads
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

### With VPN (Gluetun)

```yaml
services:
  gluetun:
    image: qmcgaw/gluetun
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    ports:
      - "5000:5000"
    environment:
      - VPN_SERVICE_PROVIDER=your_provider
      # Add your VPN configuration here
    restart: unless-stopped

  anime-downloader:
    image: recho1235/animekai-downloader:latest
    container_name: animekai-downloader
    network_mode: "container:gluetun"
    volumes:
      - ./downloads:/app/downloads
    depends_on:
      - gluetun
    restart: unless-stopped
```

## Configuration

### Volumes

| Path | Description |
|------|-------------|
| `/app/downloads` | Downloaded anime files are stored here |

### Ports

| Port | Description |
|------|-------------|
| `5000` | Web interface |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment mode |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

## Usage

1. **Access the web interface** at `http://localhost:5000`

2. **Enter AnimeKai URL** (e.g., `https://animekai.to/watch/your-anime`)

3. **Configure download settings:**
   - Download mode (All Episodes, Range, or Single)
   - Subtitle type (Soft Sub, Hard Sub, or Dub)
   - Server preference
   - Optional episode merging

4. **Click "Start Download"** and monitor progress in real-time

5. **Download completed files** directly from the web interface

## Download Options

### Subtitle Types
- **Soft Sub** - External subtitles embedded in video (recommended)
- **Hard Sub** - Burned-in subtitles
- **Dub** - Dubbed audio with optional subtitles

### Download Modes
- **All Episodes** - Download complete season
- **Episode Range** - Download specific episode range (e.g., 1-12)
- **Single Episode** - Download one episode

### Advanced Features
- **Episode Merging** - Combine multiple episodes into one file
- **Multiple Servers** - Automatic fallback if primary server fails
- **Retry Logic** - Automatic retry on download failures
- **Concurrent Downloads** - Track multiple downloads simultaneously

## System Requirements

- Docker 20.10+
- 2GB RAM minimum
- Sufficient storage for downloads

## Notes

- Downloaded files are saved to the mounted volume
- Each anime gets its own subdirectory
- Web interface updates every 2 seconds
- Supports concurrent downloads

## Troubleshooting

**Can't access web interface:**
- Verify port 5000 is not in use: `netstat -tulpn | grep 5000`
- Check container logs: `docker logs animekai-downloader`

**Downloads failing:**
- Verify internet connection
- Check AnimeKai URL is correct
- Try different server in advanced settings
- Review logs in web interface

**Permission errors:**
- Ensure download directory is writable
- Check volume mount permissions

## Disclaimer

This tool is for **educational and personal archival purposes** only. Always respect copyright laws and the terms of service of the websites you access.

## Source Code

GitHub: [Your GitHub Repository URL]

## Support

For issues and feature requests, please visit the GitHub repository.
