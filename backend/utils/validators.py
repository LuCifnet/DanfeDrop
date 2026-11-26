import re

YOUTUBE_URL_PATTERNS = [
    r'^(https?://)?(www\.)?(youtube\.com/watch\?v=[\w-]{11})',
    r'^(https?://)?(www\.)?(youtube\.com/shorts/[\w-]{11})',
    r'^(https?://)?(www\.)?(youtu\.be/[\w-]{11})',
    r'^(https?://)?(www\.)?(youtube\.com/embed/[\w-]{11})',
    r'^(https?://)?(www\.)?(youtube\.com/v/[\w-]{11})',
    r'^(https?://)?(music\.youtube\.com/watch\?v=[\w-]{11})',
    r'^(https?://)?(www\.)?(youtube\.com/live/[\w-]{11})',
]

def validate_youtube_url(url: str) -> bool:
    """Validate if the string matches recognized YouTube URL formats."""
    if not url:
        return False
    cleaned = url.strip()
    return any(re.match(p, cleaned, re.IGNORECASE) for p in YOUTUBE_URL_PATTERNS)
