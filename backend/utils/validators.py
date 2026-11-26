import re
from urllib.parse import parse_qs, urlsplit

VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
SHORT_HOSTS = {"youtu.be", "www.youtu.be"}


def validate_youtube_url(url: str) -> bool:
    """Accept supported YouTube video URLs, never arbitrary extractor URLs."""
    if not url:
        return False

    cleaned = url.strip()
    if len(cleaned) > 2048:
        return False
    if "://" not in cleaned:
        cleaned = f"https://{cleaned}"

    try:
        parsed = urlsplit(cleaned)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme.lower() not in {"http", "https"} or parsed.username or parsed.password:
            return False
        if parsed.port is not None:
            return False
    except ValueError:
        return False

    video_id = None
    if host in SHORT_HOSTS:
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) == 1:
            video_id = parts[0]
    elif host in YOUTUBE_HOSTS:
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) == 2 and parts[0] in {"shorts", "embed", "v", "live"}:
            video_id = parts[1]

    return bool(video_id and VIDEO_ID_PATTERN.fullmatch(video_id))
