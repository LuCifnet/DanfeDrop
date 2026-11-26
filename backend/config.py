import os

# Default target download folder:
# - On Windows local dev: C:\Users\Kapil\Music\newmusic
# - On Linux/cloud (Render/Docker): /tmp/danfedrop_downloads (or DOWNLOAD_DIR env var)
if os.environ.get("DOWNLOAD_DIR"):
    TARGET_DOWNLOAD_DIR = os.environ["DOWNLOAD_DIR"]
elif os.name == "nt":
    TARGET_DOWNLOAD_DIR = r"C:\Users\Kapil\Music\newmusic"
else:
    TARGET_DOWNLOAD_DIR = "/tmp/danfedrop_downloads"

# Ensure target download directory exists
os.makedirs(TARGET_DOWNLOAD_DIR, exist_ok=True)

# Server port configuration
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "127.0.0.1")

# Cookie file paths for authentication
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DEFAULT_COOKIES_FILE = os.path.join(BASE_DIR, "cookies.txt")
ROOT_COOKIES_FILE = os.path.join(PROJECT_ROOT, "cookies.txt")

# Custom cookies file path or raw Netscape cookies content via environment variable
YOUTUBE_COOKIES = os.environ.get("YOUTUBE_COOKIES", None)
YOUTUBE_COOKIES_CONTENT = os.environ.get("YOUTUBE_COOKIES_CONTENT", None)

