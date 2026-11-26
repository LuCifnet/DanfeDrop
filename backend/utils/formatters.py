import re
from typing import Optional

def sanitize_filename(name: str) -> str:
    """Sanitize string to be safe for filenames across operating systems."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r'[\s_]+', ' ', name).strip()
    return name[:120] if name else "media"

def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds into hh:mm:ss or mm:ss."""
    if not seconds or seconds < 0:
        return "Unknown"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def format_bytes(num_bytes: Optional[int]) -> str:
    """Convert raw byte count to readable string (e.g. 1.8 GB)."""
    if not num_bytes or num_bytes <= 0:
        return "Unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(num_bytes)
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.1f} {units[i]}"

def format_views(count: Optional[int]) -> str:
    """Convert view count into compact format (e.g. 1.5M views)."""
    if not count:
        return ""
    if count >= 1_000_000_000:
        return f"{count / 1_000_000_000:.1f}B views"
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M views"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K views"
    return f"{count:,} views"

def format_upload_date(raw_date: Optional[str]) -> str:
    """Format date string YYYYMMDD into Month Day, Year."""
    if not raw_date or len(raw_date) != 8:
        return raw_date or ""
    try:
        year = raw_date[0:4]
        month_idx = int(raw_date[4:6]) - 1
        day = int(raw_date[6:8])
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{months[month_idx]} {day}, {year}"
    except Exception:
        return raw_date
