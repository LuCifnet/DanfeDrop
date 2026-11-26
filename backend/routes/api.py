import json
import uuid
import time
import asyncio
import threading
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from ..config import TARGET_DOWNLOAD_DIR
from ..services.extractor import extract_media_info
from ..services.downloader import run_download_job
from ..services.legal import get_terms_of_service
from ..services.task_manager import (
    create_task,
    get_task,
    cancel_task,
)
from ..services.api_guard import (
    acquire_analysis_slot,
    enforce_rate_limit,
    release_analysis_slot,
)
from ..utils.validators import validate_youtube_url


router = APIRouter(prefix="/api")

@router.get("/terms")
async def get_terms():
    """Return the Terms of Use content and legal guidelines."""
    return {
        "success": True,
        "data": get_terms_of_service()
    }


class AnalyzeRequest(BaseModel):
    url: str = Field(min_length=11, max_length=2048)

class DownloadRequest(BaseModel):
    url: str = Field(min_length=11, max_length=2048)
    type: Literal["video", "audio"]
    format_id: Optional[str] = Field(default=None, max_length=40, pattern=r"^[A-Za-z0-9._-]+$")
    height: Optional[int] = Field(default=None, ge=1, le=4320)
    ext: Literal["mp4", "mp3", "m4a"] = "mp4"
    bitrate: Optional[Literal[128, 192, 320]] = None
    title: str = Field(default="media", max_length=200)
    quality: str = Field(default="", max_length=80)

@router.get("/config")
async def get_system_config():
    """Health check endpoint without exposing server filesystem paths."""
    return {"success": True}

@router.post("/analyze")
async def analyze_video(req: AnalyzeRequest, request: Request):
    enforce_rate_limit(request, "analyze", 20, 60)
    if not validate_youtube_url(req.url):
        raise HTTPException(status_code=400, detail="Please provide a valid YouTube video URL.")
    if not acquire_analysis_slot():
        raise HTTPException(
            status_code=429,
            detail="Video analysis is busy. Please wait a moment and try again.",
            headers={"Retry-After": "30"},
        )
    try:
        data = await asyncio.to_thread(extract_media_info, req.url)
        return {"success": True, "data": data}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"success": False, "detail": str(e)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": "Could not analyze this video. Please try again later."},
        )
    finally:
        release_analysis_slot()

@router.post("/download")
async def start_download(req: DownloadRequest, request: Request):
    client_key = enforce_rate_limit(request, "download", 5, 3600)
    if not validate_youtube_url(req.url):
        raise HTTPException(status_code=400, detail="Please provide a valid YouTube video URL.")
    if (req.type == "video" and req.ext != "mp4") or (req.type == "audio" and req.ext not in {"mp3", "m4a"}):
        raise HTTPException(status_code=422, detail="The selected file format is not valid for this download type.")

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
        "client_key": client_key,
        "error": None,
        "created_at": time.time(),
    }

    if not create_task(task_id, task_payload):
        raise HTTPException(
            status_code=429,
            detail="The download service is busy. Please wait for a download to finish and try again.",
            headers={"Retry-After": "60"},
        )

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

    return {"success": True, "task_id": task_id}

@router.get("/status/{task_id}")
async def get_task_status(task_id: str, request: Request):
    enforce_rate_limit(request, "status", 120, 60)
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    public_fields = (
        "status",
        "progress",
        "downloaded_formatted",
        "total_formatted",
        "speed_formatted",
        "eta_formatted",
        "filename",
        "error",
    )
    return {"success": True, "data": {key: task.get(key) for key in public_fields}}

@router.get("/progress/{task_id}")
async def stream_progress(task_id: str, request: Request):
    """Server-Sent Events endpoint to stream real-time progress updates."""
    enforce_rate_limit(request, "progress", 20, 60)
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
async def cancel_download_task(task_id: str, request: Request):
    enforce_rate_limit(request, "cancel", 30, 60)
    success = cancel_task(task_id)
    return {"success": success, "message": "Cancellation requested"}

