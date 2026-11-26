import os
import re
import shutil
from typing import Optional, Dict, Any, Tuple
from http.cookiejar import MozillaCookieJar
import yt_dlp
from ..config import (
    TARGET_DOWNLOAD_DIR,
    DEFAULT_COOKIES_FILE,
    ROOT_COOKIES_FILE,
    YOUTUBE_COOKIES,
    YOUTUBE_COOKIES_CONTENT,
)

SUPPORTED_BROWSERS = ["firefox", "chrome", "edge", "brave", "opera", "chromium"]

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from strings."""
    if not text:
        return ""
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]|\[[0-9;]*m", "", text).strip()

def has_valid_cookie_file(path: Optional[str]) -> bool:
    """Check if file exists and has content."""
    if not path or not os.path.exists(path):
        return False
    try:
        return os.path.getsize(path) > 100
    except OSError:
        return False

def refresh_cookies_from_browser() -> Tuple[bool, str]:
    """
    Attempt to extract YouTube/Google cookies from any installed browser
    and save them to backend/cookies.txt in standard Netscape format.
    """
    os.makedirs(os.path.dirname(DEFAULT_COOKIES_FILE), exist_ok=True)
    
    for browser_name in SUPPORTED_BROWSERS:
        try:
            cj = yt_dlp.cookies.extract_cookies_from_browser(browser_name)
            mcj = MozillaCookieJar(DEFAULT_COOKIES_FILE)
            count = 0
            for cookie in cj:
                domain = (cookie.domain or "").lower()
                if "youtube" in domain or "google" in domain:
                    mcj.set_cookie(cookie)
                    count += 1
            if count > 0:
                mcj.save(ignore_discard=True, ignore_expires=True)
                return True, f"Successfully loaded and saved {count} cookies from {browser_name.title()}."
        except Exception:
            # Browser might be locked, not installed, or have encrypted cookie storage
            continue

    return False, "Could not automatically extract cookies from installed browsers."

def get_cookie_file() -> Optional[str]:
    """
    Resolve the active cookies file.
    Checks user-specified path, root cookies.txt, backend cookies.txt,
    or auto-extracts from available browsers.
    """
    # 1. Environment variable file path
    if has_valid_cookie_file(YOUTUBE_COOKIES):
        return YOUTUBE_COOKIES

    # 1b. Environment variable raw cookies content (for hosted deployments)
    if YOUTUBE_COOKIES_CONTENT and YOUTUBE_COOKIES_CONTENT.strip():
        env_cookie_path = os.path.join(TARGET_DOWNLOAD_DIR, ".env_cookies.txt")
        try:
            with open(env_cookie_path, "w", encoding="utf-8") as f:
                f.write(YOUTUBE_COOKIES_CONTENT.strip() + "\n")
            if has_valid_cookie_file(env_cookie_path):
                return env_cookie_path
        except OSError:
            pass

    # 2. Workspace root cookies.txt
    if has_valid_cookie_file(ROOT_COOKIES_FILE):
        return ROOT_COOKIES_FILE

    # 3. backend/cookies.txt
    if has_valid_cookie_file(DEFAULT_COOKIES_FILE):
        return DEFAULT_COOKIES_FILE

    # 4. Attempt automatic browser extraction
    success, _ = refresh_cookies_from_browser()
    if success and has_valid_cookie_file(DEFAULT_COOKIES_FILE):
        return DEFAULT_COOKIES_FILE

    return None

def is_bot_or_auth_error(err_msg: str) -> bool:
    """Detect if an error is caused by YouTube bot-detection or authentication requirement."""
    lower = strip_ansi(err_msg).lower()
    patterns = [
        "sign in to confirm you’re not a bot",
        "sign in to confirm you're not a bot",
        "sign in to confirm your age",
        "confirm you’re not a bot",
        "confirm you're not a bot",
        "use --cookies-from-browser",
        "use --cookies",
        "please sign in",
        "login required",
        "bot",
    ]
    return any(p in lower for p in patterns)

def get_base_ydl_opts(for_download: bool = False, fallback_clients: bool = False) -> Dict[str, Any]:
    """
    Build optimal yt-dlp configuration with JavaScript challenge solver (EJS)
    and automated cookie management.
    """
    node_path = shutil.which("node")
    cookie_path = get_cookie_file()

    opts: Dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "retries": 10,
        "fragment_retries": 10,
        "file_access_retries": 3,
        "extractor_retries": 5,
        # Enable external JavaScript challenge solver via GitHub (solves YouTube n-challenge)
        "remote_components": ["ejs:github"],
    }

    if node_path:
        opts["js_runtimes"] = {"node": {"path": node_path}}

    if cookie_path and os.path.exists(cookie_path):
        opts["cookiefile"] = cookie_path

    # If fallback requested, use alternative client configurations to bypass bot challenges
    if fallback_clients:
        opts["extractor_args"] = {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["configs", "webpage"],
            }
        }

    return opts
