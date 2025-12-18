# 🎬 AnimeKai Episode Downloader & Merger

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/USERNAME/REPOSITORY/blob/main/NOTEBOOK_NAME.ipynb)

☁️ **Click the badge above to open this project directly in Google Colab (no setup required!)**

A **feature‑rich Python toolkit** for downloading anime episodes from AnimeKai, supporting **multiple download engines**, **parallel chunking**, **episode merging**, and **optional uploads** to GoFile or Google Drive. Designed primarily for **Google Colab**, but adaptable to local Linux environments.

> ⚠️ **Disclaimer**: This project is for **educational and personal archival purposes** only. Always respect copyright laws and the terms of service of the websites you access.

---

## ✨ Features

### 📥 Download Capabilities

* Download **single episodes**, **episode ranges**, or **entire seasons**
* Supports multiple download engines:

  * `yt-dlp` (recommended)
  * `aria2`
  * Parallel **HTTP chunk downloading**
  * `ffmpeg` (for `.m3u8` streams)
* Automatic retry & timeout handling
* Custom User‑Agent and headers

### 🎥 Video & Episode Handling

* Auto‑detect anime title and season
* Supports **Soft Sub**, **Hard Sub**, and **Dub** servers
* Smart server fallback logic
* Clean, filesystem‑safe filenames

### 🔗 Episode Merging

* Merge multiple episodes into **one continuous MP4**
* Fast merge (stream copy, no re‑encode)
* Optional re‑encoding (HQ or compressed)
* Automatic naming:

  ```
  Anime Title Season 01 Episodes 01-12.mp4
  ```

### 📦 ZIP Workflow (Optional)

* Download ZIP files containing episodes
* Auto‑extract and detect episode order
* Natural sorting using episode patterns (`S01E01`, `1x01`, `Episode 1`, etc.)

### ☁️ Upload Options

* Upload merged or individual files to:

  * **GoFile.io**
  * **Google Drive** (Colab only)
* Optional ZIP creation before upload

---

## 🧰 Requirements

### Runtime

* Python **3.9+**
* Linux (Ubuntu recommended)
* Google Colab (best supported)

### System Packages

```bash
sudo apt install ffmpeg aria2
```

### Python Packages

```bash
pip install requests beautifulsoup4 cloudscraper m3u8 pycryptodome tqdm yt-dlp natsort
```

---

## 🚀 Usage

This project can be used **both interactively (Colab)** and as a **CLI tool on local Linux systems**.

---

## 🖥️ CLI Usage (Local Linux)

### 1️⃣ AnimeKai Direct Download Mode

1. Open the notebook in **Google Colab**
2. Fill in the **Configuration Form**:

   * Anime URL
   * Episode selection mode
   * Quality & server preferences
   * Download engine
3. Run all cells
4. (Optional) Merge episodes and upload

Supported modes:

* All Episodes
* Episode Range
* Single Episode

---

### 2️⃣ ZIP → Merge → Upload Mode

Use this mode when you already have a ZIP file containing episodes.

Steps:

1. Provide a **Direct Download Link (DDL)** to the ZIP
2. Extract videos automatically
3. Detect episode order
4. Merge into a single MP4
5. Upload or keep locally

---

## ⚙️ Configuration Highlights

```python
video_quality = "1080p"
download_method = "yt-dlp"
merge_episodes = True
keep_individual_files = False
upload_destination = "GoFile.io Only"
```

You can fine‑tune:

* Chunk size
* Parallel workers
* Retry count
* Connection timeout

---

## 📂 Output Structure

```text
downloads/
└── Anime Title/
    ├── Episode_001.mp4
    ├── Episode_002.mp4
    └── Anime Title Season 01 Episodes 01-02.mp4
```

---

## 🧠 Episode Detection Logic

Recognized patterns include:

* `S01E01`, `S1E1`
* `1x01`
* `Episode 12`
* `Season 2 Episode 3`
* Numeric filenames

Fallback ordering uses natural filename sorting.

---

## 🛠️ Troubleshooting

**Download fails?**

* Try switching download method (`yt-dlp` ↔ `ffmpeg`)
* Increase timeout or retries

**Merge fails?**

* Ensure all files share the same codec
* Use re‑encode merge mode

**GoFile upload fails?**

* Large files may timeout
* Use Google Drive instead

---

## 📜 License

MIT License

---

## 🙌 Credits

* `yt-dlp`
* `aria2`
* `ffmpeg`
* `cloudscraper`
* `BeautifulSoup`

---

## ⭐ Notes

* Designed for **power users** and automation
* Ideal for batch workflows
* Easily extensible

If this project helped you, consider starring the repository ⭐
* 🖼️ Screenshots for README

Just tell me 😎
