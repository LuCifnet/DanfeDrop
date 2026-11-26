import os
import json
import uuid
import time
import asyncio
import threading
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel

from ..config import TARGET_DOWNLOAD_DIR
from ..services.extractor import extract_media_info
from ..services.downloader import run_download_job
from ..services.legal import get_terms_of_service
from ..services.cookie_manager import (
    get_cookie_file,
    refresh_cookies_from_browser,
    has_valid_cookie_file,
)
from ..services.task_manager import (
    create_task,
    get_task,
    cancel_task,
)


router = APIRouter(prefix="/api")

@router.get("/terms")
async def get_terms():
    """Return the Terms of Use content and legal guidelines."""
    return {
        "success": True,
        "data": get_terms_of_service()
    }


class AnalyzeRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    type: str  # "video" or "audio"
    format_id: Optional[str] = None
    height: Optional[int] = None
    ext: str = "mp4"
    bitrate: Optional[int] = None
    title: str = "media"
    quality: str = ""

@router.get("/config")
async def get_system_config():
    """Return configured download path information."""
    return {
        "success": True,
        "target_download_dir": TARGET_DOWNLOAD_DIR,
    }

@router.get("/cookies")
async def get_cookie_status():
    """Return status of YouTube authentication cookies."""
    path = get_cookie_file()
    has_cookies = has_valid_cookie_file(path)
    return {
        "success": True,
        "has_cookies": has_cookies,
        "cookie_file": path if has_cookies else None,
    }

@router.post("/cookies/refresh")
async def trigger_cookie_refresh():
    """Attempt re-extracting YouTube cookies from installed browsers."""
    success, msg = await asyncio.to_thread(refresh_cookies_from_browser)
    return {
        "success": success,
        "message": msg,
        "cookie_file": get_cookie_file(),
    }


@router.post("/analyze")
async def analyze_video(req: AnalyzeRequest):
    try:
        data = await asyncio.to_thread(extract_media_info, req.url)
        return {"success": True, "data": data}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"success": False, "detail": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": f"Server error: {str(e)}"})

@router.post("/download")
async def start_download(req: DownloadRequest):
    task_id = str(uuid.uuid4())

    task_payload = {
        "id": task_id,
        "url": req.url,
        "type": req.type,
        "quality": req.quality,
        "ext": req.ext,
        "title": req.title,
        "status": "queued",
        "progress": 0.0,
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "downloaded_formatted": "0 B",
        "total_formatted": "Calculating...",
        "speed_formatted": "Connecting...",
        "eta_formatted": "Starting...",
        "filename": None,
        "file_path": None,
        "saved_dir": TARGET_DOWNLOAD_DIR,
        "error": None,
        "created_at": time.time(),
    }

    create_task(task_id, task_payload)

    worker = threading.Thread(
        target=run_download_job,
        args=(
            task_id,
            req.url,
            req.type,
            req.format_id,
            req.height,
            req.ext,
            req.bitrate,
            req.title,
        ),
        daemon=True,
    )
    worker.start()

    return {"success": True, "task_id": task_id, "saved_dir": TARGET_DOWNLOAD_DIR}

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "data": task}

@router.get("/progress/{task_id}")
async def stream_progress(task_id: str, request: Request):
    """Server-Sent Events endpoint to stream real-time progress updates."""
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            task = get_task(task_id)
            if not task:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            status = task["status"]
            data = {
                "id": task_id,
                "status": status,
                "progress": task.get("progress", 0.0),
                "downloaded_formatted": task.get("downloaded_formatted", ""),
                "total_formatted": task.get("total_formatted", ""),
                "speed_formatted": task.get("speed_formatted", ""),
                "eta_formatted": task.get("eta_formatted", ""),
                "quality": task.get("quality", ""),
                "ext": task.get("ext", ""),
                "filename": task.get("filename", ""),
                "saved_dir": task.get("saved_dir", TARGET_DOWNLOAD_DIR),
                "error": task.get("error"),
            }

            yield f"data: {json.dumps(data)}\n\n"

            if status in ["completed", "error", "cancelled"]:
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@router.post("/cancel/{task_id}")
async def cancel_download_task(task_id: str):
    success = cancel_task(task_id)
    return {"success": success, "message": "Cancellation requested"}

@router.get("/file/{task_id}")
async def download_file(task_id: str):
    r"""
    Files are saved directly to TARGET_DOWNLOAD_DIR.
    Browser file stream attachment is disabled to prevent duplicate files in Downloads folder.
    """

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="File is not ready yet")

    file_path = task.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return {
        "success": True,
        "saved_dir": TARGET_DOWNLOAD_DIR,
        "file_path": file_path,
        "filename": task.get("filename"),
        "message": f"File is saved exclusively in {TARGET_DOWNLOAD_DIR}",
    }

