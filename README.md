# DanfeDrop — YouTube Video & Audio Downloader

A modern, fast, and human-designed web application for downloading YouTube videos and audio in high quality, inspired by utility tools like Y2Mate, but built with a clean, uncluttered, professional UI/UX.

---

## Key Features

- **Clean & Human-Designed UI/UX**: Restrained, elegant typography and neutral color palette without aggressive ads, neon gradients, or artificial dashboards.
- **Light & Dark Mode**: Instant theme switching in the header with full CSS variable theming and persistence.
- **Modern Vector Identity**: Custom geometric logo mark and clean brand naming.
- **Terms of Use & API**: Built-in modal and REST API endpoint (`GET /api/terms`) providing structured usage policies.
- **Real Media Analysis**: Uses `yt-dlp` to extract genuine streams and available qualities (resolutions 2160p 4K down to 144p; MP3 320/192/128 kbps; original M4A streams).
- **Smooth Real-Time Progress Indicator**: Real-time Server-Sent Events (SSE) stream percentage, downloaded vs total byte sizes, download speed (MB/s), and ETA time remaining.
- **Automatic Output Target**: Downloaded media is saved directly into:
  ```
  C:\Users\Kapil\Music\newmusic
  ```
  Files can also be saved directly through the browser at any time.
- **Robust Error Handling**: Friendly notifications for age-restricted, private, or invalid YouTube links.
- **Cancellation Support**: Safely cancel downloads mid-stream.
- **Clean Architecture (KISS & DRY)**:
  - Decomposed into focused services, validators, formatters, and reusable React components.

---

## Project Structure

```
videodownloader/
├── backend/
│   ├── config.py              # Configuration & TARGET_DOWNLOAD_DIR
│   ├── main.py                # FastAPI entry point & static file mount
│   ├── routes/
│   │   └── api.py             # REST API & Server-Sent Events routes
│   ├── services/
│   │   ├── cookie_manager.py  # Automated browser cookie extraction & EJS setup
│   │   ├── downloader.py      # yt-dlp & FFmpeg execution worker
│   │   ├── extractor.py       # Stream manifest & format extractor
│   │   └── task_manager.py    # Download state & cancellation manager
│   └── utils/
│       ├── formatters.py      # Byte, duration, views & text formatters
│       └── validators.py      # YouTube URL patterns & validators

├── frontend/
│   ├── dist/                  # Built production assets (ready to serve)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Alert.jsx
│   │   │   ├── AnalyzingSkeleton.jsx
│   │   │   ├── DownloadProgress.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── FormatTable.jsx
│   │   │   ├── FormatTabs.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── UrlInput.jsx
│   │   │   └── VideoInfoCard.jsx
│   │   ├── hooks/
│   │   │   └── useDownloadProgress.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx            # Lean coordinator component
│   │   ├── index.css          # Refined design system & typography
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── run.py                     # Single-command application launcher
```

---

## Quick Start

### 1. YouTube Cookie Authentication (Required)

YouTube may require authentication to prevent bot detection. You need to provide cookies:

**Option A: Using a cookies.txt file (Recommended)**
1. Export your YouTube cookies from your browser
2. Save them as `cookies.txt` in the project root or any location
3. Update `backend/config.py`:
```python
YOUTUBE_COOKIES = r"C:\path\to\your\cookies.txt"
```

**Option B: Using environment variable**
```powershell
$env:YOUTUBE_COOKIES="C:\path\to\your\cookies.txt"
python run.py
```

**How to export cookies:**
- **Chrome/Edge:** Use the [EditThisCookie](https://www.editthiscookie.com/) extension to export as Netscape format
- **Firefox:** Use the [Cookie-Editor](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/) extension
- **Manual:** yt-dlp supports browser cookie export: see [yt-dlp cookie documentation](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

> **Note:** Make sure you're signed into YouTube in your browser before exporting cookies.

### 2. Launch the Application
Run the launcher from the project root:
```powershell
python run.py
```

Open your browser at:
```
http://127.0.0.1:8000
```

### 3. Frontend Development (Optional)
If you want to edit frontend components live with hot reloading:
```powershell
cd frontend
npm run dev
```
(Vite automatically proxies `/api` requests to `http://127.0.0.1:8000`)

---

## Troubleshooting

### "Sign in to confirm you're not a bot" Error

This error occurs when YouTube detects automated traffic. To fix it:

1. **Ensure cookies are properly configured** (see Step 1 above)
2. **Verify your cookies file exists** at the path specified in `YOUTUBE_COOKIES`
3. **Check cookie file format** - It should be in Netscape HTTP cookie format
4. **Make sure you're signed in** to YouTube in the browser where you exported cookies
5. **Cookies may expire** - Re-export cookies periodically (every few weeks)

### Common Issues

**Age-restricted videos:**
- Make sure your cookies include a signed-in YouTube account that can view age-restricted content
- The error will say "Sign in to confirm your age"

**Private videos:**
- Private videos cannot be downloaded, even with cookies

**Region-locked content:**
- Your cookies must be from a region where the content is available

**Cookie file not found:**
- Double-check the path in `backend/config.py`
- Use raw string notation: `r"C:\path\to\cookies.txt"`
- Or use forward slashes: `"C:/path/to/cookies.txt"`
