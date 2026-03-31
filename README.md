# 🎬 AnimeKai Downloader (Archived)

> **⚠️ This project has been archived.** It has been superseded by **[月 Tsuki](https://github.com/Recho1337/Tsuki)** — a ground-up rewrite with a modern decoupled architecture.

## What was this?

A Flask-based anime downloader with a web UI for searching and downloading episodes from AnimeKai. Originally based on [Cinichi/Ani-Downloader](https://github.com/Cinichi/Ani-Downloader).

## What replaced it?

**[Tsuki](https://github.com/Recho1337/Tsuki)** keeps the same core scraping approach but splits everything into dedicated services:

- **Next.js 16 / React 19** frontend (dark/light theme, glassmorphism UI)
- **FastAPI** backend with async APIs and JWT auth
- **Redis** job queue with a standalone download **worker**
- **PostgreSQL** persistence (SQLite also supported)
- Auto-detection of **films vs TV series** with Jellyfin-compatible naming
- Searchable **library** with in-browser video playback and file management
- **VPN integration** — route the worker through Gluetun
- Real-time download progress, job recovery on restart, and more

👉 **[github.com/Recho1337/Tsuki](https://github.com/Recho1337/Tsuki)**

## License

MIT

## ⚠️ Disclaimer

This tool is for personal use only. Users are responsible for complying with their local laws and the terms of service of the content providers. The developers assume no liability for misuse of this software.

## 🙏 Acknowledgments

- Original project by [@Cinichi](https://github.com/Cinichi) - [Ani-Downloader](https://github.com/Cinichi/Ani-Downloader)
- Built with Flask and Python
- Uses yt-dlp for reliable video downloads
- Powered by anikai.to anime streaming service

---

Made with ❤️ for anime enthusiasts
