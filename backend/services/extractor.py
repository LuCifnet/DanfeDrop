import os
from typing import Dict, Any, List, Tuple
import yt_dlp
from .cookie_manager import (
    get_base_ydl_opts,
    refresh_cookies_from_browser,
    is_bot_or_auth_error,
    strip_ansi,
)
from ..utils.formatters import format_bytes, format_duration, format_views, format_upload_date
from ..utils.validators import validate_youtube_url

def classify_resolution(f: Dict[str, Any]) -> Tuple[int, str]:
    """
    Determine standard resolution tier using both width and height,
    properly supporting 16:9, vertical shorts (9:16), 21:9 ultrawide, and 4:3.
    """
    w = f.get("width") or 0
    h = f.get("height") or 0
    max_d = max(w, h)
    min_d = min(w, h) if (w and h) else (h or w or 0)

    if max_d >= 3840 or min_d >= 2160:
        return 2160, "2160p (4K Ultra HD)"
    elif max_d >= 2560 or min_d >= 1440:
        return 1440, "1440p (2K Quad HD)"
    elif max_d >= 1920 or min_d >= 1080:
        return 1080, "1080p (Full HD)"
    elif max_d >= 1280 or min_d >= 720:
        return 720, "720p (HD)"
    elif max_d >= 854 or min_d >= 480:
        return 480, "480p (SD)"
    elif max_d >= 640 or min_d >= 360:
        return 360, "360p (SD)"
    elif max_d >= 426 or min_d >= 240:
        return 240, "240p"
    else:
        return 144, "144p"

def extract_media_info(url: str) -> Dict[str, Any]:
    """
    Extract real YouTube metadata and formats using yt-dlp.
    Extracts all available video resolutions up to 4K/Full HD and audio formats.
    """
    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("Please provide a YouTube video URL.")
    
    if not validate_youtube_url(cleaned_url):
        raise ValueError("Invalid YouTube URL. Please enter a valid YouTube video or Shorts link.")

    info = None
    last_error = None

    # Attempt 1: Standard extraction using configured cookies + EJS solver
    base_opts = get_base_ydl_opts(for_download=False)
    base_opts.update({
        'skip_download': True,
        'extract_flat': False,
    })

    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            info = ydl.extract_info(cleaned_url, download=False)
    except Exception as e:
        last_error = e

    # Attempt 2: Auto-refresh browser cookies if bot/sign-in check occurred
    if not info and last_error and is_bot_or_auth_error(str(last_error)):
        refreshed, _ = refresh_cookies_from_browser()
        if refreshed:
            retry_opts = get_base_ydl_opts(for_download=False)
            retry_opts.update({
                'skip_download': True,
                'extract_flat': False,
            })
            try:
                with yt_dlp.YoutubeDL(retry_opts) as ydl:
                    info = ydl.extract_info(cleaned_url, download=False)
                    last_error = None
            except Exception as e:
                last_error = e

    # Attempt 3: Alternative client fallback (android/web)
    if not info and last_error and is_bot_or_auth_error(str(last_error)):
        fallback_opts = get_base_ydl_opts(for_download=False, fallback_clients=True)
        fallback_opts.update({
            'skip_download': True,
            'extract_flat': False,
        })
        try:
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = ydl.extract_info(cleaned_url, download=False)
                last_error = None
        except Exception as e:
            last_error = e

    if not info:
        err = strip_ansi(str(last_error)) if last_error else "Unknown error"
        if "Private video" in err:
            raise ValueError("This video is private and cannot be downloaded.")
        elif "Sign in to confirm your age" in err:
            raise ValueError("This video is age-restricted and requires account verification.")
        elif "Video unavailable" in err:
            raise ValueError("This video is unavailable (removed or region-locked).")
        elif is_bot_or_auth_error(err):
            raise ValueError(
                "YouTube is requiring authentication. Please ensure you are logged into YouTube in your browser or save cookies to backend/cookies.txt."
            )
        else:
            raise ValueError(f"Could not retrieve video information: {err}")

    if not info:
        raise ValueError("No video information could be found.")

    video_id = info.get("id", "")
    title = info.get("title", "YouTube Media")
    duration = info.get("duration")
    thumbnail = info.get("thumbnail") or f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
    uploader = info.get("uploader") or info.get("channel", "YouTube")
    view_count = info.get("view_count")
    upload_date = info.get("upload_date")
    webpage_url = info.get("webpage_url") or cleaned_url

    formats = info.get("formats", [])

    # Find the best audio stream for size estimation
    audio_formats = [f for f in formats if f.get("vcodec") == "none" and f.get("acodec") != "none"]
    best_audio_bitrate = 128
    best_audio_size = 0
    for af in audio_formats:
        abr = af.get("abr") or 0
        if abr > best_audio_bitrate:
            best_audio_bitrate = abr
        sz = af.get("filesize") or af.get("filesize_approx") or 0
        if sz > best_audio_size:
            best_audio_size = sz

    if not best_audio_size and duration and best_audio_bitrate:
        best_audio_size = int((best_audio_bitrate * 1000 / 8) * duration)

    # 1. Parse Video Qualities
    video_formats = [f for f in formats if f.get("vcodec") and f.get("vcodec") != "none"]

    # Group video formats by classified resolution tier
    tier_to_formats: Dict[int, List[Dict[str, Any]]] = {}
    tier_labels: Dict[int, str] = {}

    for f in video_formats:
        tier_h, label = classify_resolution(f)
        if tier_h not in tier_to_formats:
            tier_to_formats[tier_h] = []
            tier_labels[tier_h] = label
        tier_to_formats[tier_h].append(f)

    video_options: List[Dict[str, Any]] = []

    # Always add Best / Maximum Quality option at the top
    max_tier = max(tier_to_formats.keys()) if tier_to_formats else None
    if max_tier:
        max_label = tier_labels.get(max_tier, f"{max_tier}p")
        max_candidates = tier_to_formats[max_tier]
        best_cand = max(max_candidates, key=lambda x: x.get("tbr") or x.get("vbr") or 0)
        
        raw_size = best_cand.get("filesize") or best_cand.get("filesize_approx")
        est_max_size = raw_size
        if not (best_cand.get("acodec") != "none") and duration:
            est_max_size = (raw_size + best_audio_size) if raw_size else int(((best_cand.get("tbr") or 2500) * 1000 / 8) * duration)

        video_options.append({
            "id": "video_best_max",
            "quality": f"Best Quality ({max_label.split(' ')[0]})",
            "resolution": "Maximum",
            "height": None,  # Signals downloader to use 'bestvideo+bestaudio/best'
            "format": "MP4",
            "ext": "mp4",
            "format_id": None,
            "has_audio": True,
            "audio_note": "Included (Max)",
            "fps": best_cand.get("fps"),
            "filesize_approx": est_max_size,
            "filesize_formatted": format_bytes(est_max_size) if est_max_size else "—",
            "is_max": True,
        })

    # Add all individual resolution tiers in descending order
    for tier_h in sorted(tier_to_formats.keys(), reverse=True):
        candidates = tier_to_formats[tier_h]
        label = tier_labels[tier_h]

        # Prefer MP4 container if available, or best bitrate
        mp4_cands = [c for c in candidates if c.get("ext") == "mp4"]
        selected_cand = mp4_cands[0] if mp4_cands else candidates[0]

        has_audio = selected_cand.get("acodec") != "none"
        raw_size = selected_cand.get("filesize") or selected_cand.get("filesize_approx")

        estimated_size = raw_size
        if not has_audio and duration:
            v_tbr = selected_cand.get("tbr") or selected_cand.get("vbr")
            if raw_size:
                estimated_size = raw_size + best_audio_size
            elif v_tbr:
                estimated_size = int(((v_tbr + best_audio_bitrate) * 1000 / 8) * duration)
        elif not raw_size and duration:
            tbr = selected_cand.get("tbr") or (tier_h * 2)
            estimated_size = int((tbr * 1000 / 8) * duration)

        video_options.append({
            "id": f"video_{tier_h}",
            "quality": label,
            "resolution": f"{tier_h}p",
            "height": tier_h,
            "format": "MP4",
            "ext": "mp4",
            "format_id": selected_cand.get("format_id"),
            "has_audio": True,
            "audio_note": "Included",
            "fps": selected_cand.get("fps"),
            "filesize_approx": estimated_size,
            "filesize_formatted": format_bytes(estimated_size) if estimated_size else "—",
        })

    # 2. Parse Audio Qualities
    audio_options: List[Dict[str, Any]] = []
    mp3_presets = [
        {"quality": "High Quality", "bitrate": 320, "label": "320 kbps"},
        {"quality": "Standard Quality", "bitrate": 192, "label": "192 kbps"},
        {"quality": "Compact", "bitrate": 128, "label": "128 kbps"},
    ]

    for p in mp3_presets:
        kbps = p["bitrate"]
        est_size = int((kbps * 1000 / 8) * duration) if duration else 0
        audio_options.append({
            "id": f"audio_mp3_{kbps}",
            "quality": p["quality"],
            "format": "MP3",
            "ext": "mp3",
            "bitrate": p["label"],
            "bitrate_val": kbps,
            "filesize_approx": est_size,
            "filesize_formatted": format_bytes(est_size) if est_size else "—",
        })

    m4a_cands = [af for af in audio_formats if af.get("ext") == "m4a"]
    if m4a_cands:
        best_m4a = max(m4a_cands, key=lambda x: x.get("abr") or 0)
        abr = int(best_m4a.get("abr") or 128)
        m4a_size = best_m4a.get("filesize") or best_m4a.get("filesize_approx")
        if not m4a_size and duration:
            m4a_size = int((abr * 1000 / 8) * duration)
        audio_options.append({
            "id": "audio_m4a_original",
            "quality": "Original Stream",
            "format": "M4A",
            "ext": "m4a",
            "bitrate": f"{abr} kbps",
            "bitrate_val": abr,
            "format_id": best_m4a.get("format_id"),
            "filesize_approx": m4a_size,
            "filesize_formatted": format_bytes(m4a_size) if m4a_size else "—",
        })

    return {
        "id": video_id,
        "title": title,
        "duration": duration,
        "duration_formatted": format_duration(duration),
        "thumbnail": thumbnail,
        "uploader": uploader,
        "view_count_formatted": format_views(view_count),
        "upload_date_formatted": format_upload_date(upload_date),
        "webpage_url": webpage_url,
        "video_formats": video_options,
        "audio_formats": audio_options,
    }
