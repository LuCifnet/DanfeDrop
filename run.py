"""
Application Launcher for YouTube Video & Audio Downloader
"""
import os
import sys
import uvicorn
from backend.config import HOST, PORT, TARGET_DOWNLOAD_DIR
from backend.services.cookie_manager import get_cookie_file

def main():
    cookie_file = get_cookie_file()
    cookie_status = f"Loaded ({os.path.basename(cookie_file)})" if cookie_file else "Auto-extract on demand"
    print("=" * 60)
    print(" DanfeDrop — YouTube Video & Audio Downloader")
    print(f" Download Directory: {TARGET_DOWNLOAD_DIR}")
    print(f" YouTube Auth:       {cookie_status}")
    print(f" Backend API URL:   http://{HOST}:{PORT}")
    print("=" * 60)


    # Ensure target directory exists
    os.makedirs(TARGET_DOWNLOAD_DIR, exist_ok=True)

    # Start FastAPI server
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)

if __name__ == "__main__":
    main()
