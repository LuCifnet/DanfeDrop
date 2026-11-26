import os
import re
from typing import Optional, Dict, Any
import yt_dlp

from ..config import TARGET_DOWNLOAD_DIR
from ..utils.formatters import sanitize_filename, format_bytes
from .task_manager import update_task, is_cancelled
from .cookie_manager import (
    get_base_ydl_opts,
    refresh_cookies_from_browser,
    is_bot_or_auth_error,
    strip_ansi,
)


def run_download_job(
    task_id: str,
    url: str,
    media_type: str,
    format_id: Optional[str],
    height: Optional[int],
    ext: str,
    bitrate: Optional[int],
    title: str,
):
    r"""
    Downloads and converts media using yt-dlp directly into TARGET_DOWNLOAD_DIR.
    """

    os.makedirs(TARGET_DOWNLOAD_DIR, exist_ok=True)
    safe_title = sanitize_filename(title)

    # Progress hook callback
    def progress_hook(d: Dict[str, Any]):
        if is_cancelled(task_id):
            raise Exception("Download cancelled by user.")

        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            speed = d.get("speed") or 0.0
            eta = d.get("eta") or 0

            percent = 0.0
            if total > 0:
                percent = round((downloaded / total) * 100.0, 1)
            elif d.get("_percent_str"):
                try:
                    cleaned_p = re.sub(r"[^0-9.]", "", d.get("_percent_str", ""))
                    percent = float(cleaned_p) if cleaned_p else 0.0
                except Exception:
                    pass

            speed_str = f"{speed / (1024 * 1024):.1f} MB/s" if speed else "—"
            if eta and eta > 60:
                eta_str = f"~{int(eta // 60)}m {int(eta % 60)}s remaining"
            elif eta:
                eta_str = f"{int(eta)}s remaining"
            else:
                eta_str = "Calculating..."

            update_task(
                task_id,
                status="downloading",
                progress=min(percent, 99.0),
                downloaded_bytes=downloaded,
                total_bytes=total,
                speed=speed,
                eta=eta,
                downloaded_formatted=format_bytes(downloaded),
                total_formatted=format_bytes(total) if total else "Unknown",
                speed_formatted=speed_str,
                eta_formatted=eta_str,
            )

        elif status == "finished":
            update_task(
                task_id,
                status="processing",
                progress=99.0,
                speed_formatted="Merging / Converting...",
                eta_formatted="Finishing up...",
            )

    # Clean filename using actual YouTube title without random task_id tags
    final_title = safe_title
    expected_file = os.path.join(TARGET_DOWNLOAD_DIR, f"{final_title}.{ext}")
    counter = 1
    while os.path.exists(expected_file):
        final_title = f"{safe_title} ({counter})"
        expected_file = os.path.join(TARGET_DOWNLOAD_DIR, f"{final_title}.{ext}")
        counter += 1

    outtmpl = os.path.join(TARGET_DOWNLOAD_DIR, f"{final_title}.%(ext)s")

    def build_download_opts(fallback_clients: bool = False) -> Dict[str, Any]:

        opts = get_base_ydl_opts(for_download=True, fallback_clients=fallback_clients)
        opts["outtmpl"] = outtmpl
        opts["progress_hooks"] = [progress_hook]

        if media_type == "video":
            if format_id:
                opts["format"] = f"{format_id}+bestaudio/best"
            elif height:
                opts["format"] = (
                    f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
                )
            else:
                opts["format"] = "bestvideo+bestaudio/best"

            opts["merge_output_format"] = ext
            opts["postprocessors"] = [
                {
                    "key": "FFmpegVideoRemuxer",
                    "preferedformat": ext,
                }
            ]

        elif media_type == "audio":
            if ext == "mp3":
                opts["format"] = "bestaudio/best"
                target_kbps = str(bitrate or 192)
                opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": target_kbps,
                    }
                ]
            elif ext == "m4a" and format_id:
                opts["format"] = format_id
            else:
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": ext,
                    }
                ]
        return opts

    ydl_opts = build_download_opts(fallback_clients=False)

    download_success = False
    last_exc = None

    # Attempt 1: Standard download
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        download_success = True
    except Exception as e:
        last_exc = e

    # Attempt 2: Auto-refresh cookies and retry if bot/auth check encountered
    if not download_success and last_exc and is_bot_or_auth_error(str(last_exc)):
        update_task(task_id, speed_formatted="Refreshing YouTube authentication...")
        refreshed, _ = refresh_cookies_from_browser()
        if refreshed:
            try:
                retry_opts = build_download_opts(fallback_clients=False)
                with yt_dlp.YoutubeDL(retry_opts) as ydl:
                    ydl.download([url])
                download_success = True
                last_exc = None
            except Exception as e:
                last_exc = e

    # Attempt 3: Client fallback if still encountering bot checks
    if not download_success and last_exc and is_bot_or_auth_error(str(last_exc)):
        try:
            fallback_opts = build_download_opts(fallback_clients=True)
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                ydl.download([url])
            download_success = True
            last_exc = None
        except Exception as e:
            last_exc = e

    try:
        if not download_success and last_exc:
            raise last_exc

        if is_cancelled(task_id):
            raise Exception("Download cancelled by user.")

        # Find the output file in TARGET_DOWNLOAD_DIR
        actual_file = None
        output_filename = None

        if os.path.exists(expected_file):
            actual_file = expected_file
            output_filename = os.path.basename(expected_file)
        else:
            for fname in os.listdir(TARGET_DOWNLOAD_DIR):
                if (
                    fname.startswith(final_title)
                    and not fname.endswith(".part")
                    and not fname.endswith(".ytdl")
                ):
                    actual_file = os.path.join(TARGET_DOWNLOAD_DIR, fname)
                    output_filename = fname
                    break

        if not actual_file or not os.path.exists(actual_file):
            raise Exception(
                f"File was processed but could not be located in {TARGET_DOWNLOAD_DIR}."
            )

        file_size = os.path.getsize(actual_file)

        update_task(
            task_id,
            status="completed",
            progress=100.0,
            filename=output_filename,
            file_path=actual_file,
            saved_dir=TARGET_DOWNLOAD_DIR,
            total_bytes=file_size,
            total_formatted=format_bytes(file_size),
            downloaded_bytes=file_size,
            downloaded_formatted=format_bytes(file_size),
            speed_formatted="Completed",
            eta_formatted="Done",
        )

    except Exception as e:
        raw_msg = str(e)
        cleaned_msg = strip_ansi(raw_msg)
        if is_cancelled(task_id) or "cancelled" in cleaned_msg.lower():
            update_task(task_id, status="cancelled", error="Download was cancelled.")
        elif is_bot_or_auth_error(cleaned_msg):
            update_task(
                task_id,
                status="error",
                error="YouTube requested sign-in confirmation. Please keep Firefox logged into YouTube or export cookies into backend/cookies.txt.",
            )
        else:
            update_task(task_id, status="error", error=cleaned_msg)

        # Cleanup incomplete/part files
        try:
            for fname in os.listdir(TARGET_DOWNLOAD_DIR):
                if fname.startswith(final_title) and (fname.endswith(".part") or fname.endswith(".ytdl")):
                    os.remove(os.path.join(TARGET_DOWNLOAD_DIR, fname))
        except Exception:
            pass


