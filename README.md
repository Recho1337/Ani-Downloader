# 🎬 AnimeKai Downloader

A powerful web-based anime downloader with a clean Flask interface for downloading anime episodes from anikai.to. Features automatic search, episode management, and a built-in library to organize your downloads.

> **Note**: This project is based on [Cinichi/Ani-Downloader](https://github.com/Cinichi/Ani-Downloader)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)

## ✨ Features

- 🔍 **Smart Search**: Search and browse anime titles from anikai.to
- 📥 **Batch Downloads**: Download single episodes or entire series
- 📚 **Library Management**: Organize and manage your anime collection
- 🎨 **Modern Web UI**: Clean, responsive interface with real-time download progress
- 🔐 **Authentication**: Secure login system (default: admin/admin)
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- ⚡ **Multi-threaded**: Fast concurrent downloads with configurable workers
- 🎞️ **Quality Control**: Automatic video processing with ffmpeg integration

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- ffmpeg
- yt-dlp

### Installation

#### Method 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Recho1337/Ani-Downloader.git
cd Ani-Downloader

# Start with Docker Compose
docker-compose up -d

# Access the application
# Open http://localhost:5000 in your browser
```

#### Method 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/Recho1337/Ani-Downloader.git
cd Ani-Downloader

# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y ffmpeg

# Install yt-dlp
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp

# Run the application
python run.py

# Or use the app directly
python app.py
```

The application will be available at `http://localhost:5000`

**Default Login Credentials:**
- Username: `admin`
- Password: `admin`

## 📖 Usage

### Web Interface

1. **Login**: Access the application and log in with your credentials
2. **Search**: Use the search bar to find anime titles
3. **Browse**: View anime details, episodes, and available quality options
4. **Download**: Select episodes or entire series to download
5. **Library**: View and manage your downloaded anime collection

### Environment Variables

Customize the application with these environment variables:

```bash
ANIME_USER=admin           # Change default username
ANIME_PASS=admin          # Change default password
SECRET_KEY=your-secret-key # Flask secret key for sessions
DOWNLOAD_FOLDER=downloads  # Download directory path
```

### Docker Configuration

```bash
# Using environment variables with Docker
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -e ANIME_USER=myusername \
  -e ANIME_PASS=mypassword \
  animekai-downloader
```

## 🏗️ Project Structure

```
Ani-Downloader/
├── app.py                  # Main Flask application
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── setup.sh               # Setup script
├── app/                   # Application package
│   ├── __init__.py
│   ├── downloader.py      # Core download logic
│   ├── models.py          # Data models
│   ├── search.py          # Search functionality
│   ├── utils.py           # Utility functions
│   └── routes/            # API routes
│       ├── auth.py        # Authentication
│       ├── download.py    # Download endpoints
│       ├── library.py     # Library management
│       ├── pages.py       # Page rendering
│       └── search.py      # Search endpoints
├── static/                # Static assets
│   ├── dashboard.js       # Dashboard JS
│   ├── library.js         # Library JS
│   └── style.css          # Styles
├── templates/             # HTML templates
│   ├── anime_detail.html
│   ├── dashboard.html
│   ├── download.html
│   ├── library.html
│   ├── login.html
│   ├── nav.html
│   └── search.html
└── downloads/             # Downloaded anime storage
```

## 🔧 Configuration

The downloader supports multiple configuration options:

- **Download Method**: Uses yt-dlp for reliable downloads
- **Max Retries**: 7 attempts per download (configurable)
- **Concurrent Workers**: Up to 15 parallel downloads
- **Timeout**: 300 seconds default
- **Max File Size**: 16GB limit

## 📦 Dependencies

- **Flask** 3.0.0 - Web framework
- **requests** 2.31.0 - HTTP library
- **beautifulsoup4** 4.12.2 - HTML parsing
- **cloudscraper** 1.2.71 - Cloudflare bypass
- **tqdm** 4.66.1 - Progress bars
- **yt-dlp** 2023.12.30 - Video downloader
- **ffmpeg** - Video processing

## 🐛 Troubleshooting

### Common Issues

**Downloads failing:**
- Ensure ffmpeg is installed and accessible
- Verify yt-dlp is up to date
- Check internet connection and firewall settings

**Port already in use:**
```bash
# Change the port in docker-compose.yml or run.py
# Docker: Change "5000:5000" to "8080:5000"
# Local: Modify port in app.run() call
```

**Permission errors:**
```bash
# Ensure downloads directory is writable
chmod -R 755 downloads/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for educational purposes. Please respect copyright laws and only download content you have the right to access.

## ⚠️ Disclaimer

This tool is for personal use only. Users are responsible for complying with their local laws and the terms of service of the content providers. The developers assume no liability for misuse of this software.

## 🙏 Acknowledgments

- Original project by [@Cinichi](https://github.com/Cinichi) - [Ani-Downloader](https://github.com/Cinichi/Ani-Downloader)
- Built with Flask and Python
- Uses yt-dlp for reliable video downloads
- Powered by anikai.to anime streaming service

---

Made with ❤️ for anime enthusiasts
