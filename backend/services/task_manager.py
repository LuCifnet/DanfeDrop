import os
import time
import threading
from typing import Dict, Any, Optional

# Active tasks store: task_id -> dict
tasks: Dict[str, Dict[str, Any]] = {}
tasks_lock = threading.Lock()

# Thread cancel events: task_id -> threading.Event
cancel_events: Dict[str, threading.Event] = {}
MAX_ACTIVE_DOWNLOADS = 2
MAX_ACTIVE_DOWNLOADS_PER_CLIENT = 1

def create_task(task_id: str, data: Dict[str, Any]) -> bool:
    event = threading.Event()
    with tasks_lock:
        active_tasks = [
            task for task in tasks.values()
            if task.get("status") in {"queued", "downloading", "processing"}
        ]
        if len(active_tasks) >= MAX_ACTIVE_DOWNLOADS:
            return False

        client_key = data.get("client_key")
        if client_key and sum(task.get("client_key") == client_key for task in active_tasks) >= MAX_ACTIVE_DOWNLOADS_PER_CLIENT:
            return False

        cancel_events[task_id] = event
        tasks[task_id] = data
    return True

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    with tasks_lock:
        task = tasks.get(task_id)
        return dict(task) if task else None

def update_task(task_id: str, **kwargs) -> None:
    with tasks_lock:
        if task_id in tasks:
            tasks[task_id].update(kwargs)

def cancel_task(task_id: str) -> bool:
    with tasks_lock:
        task = tasks.get(task_id)
        event = cancel_events.get(task_id)
        if not task or not event or task.get("status") not in {"queued", "downloading", "processing"}:
            return False
        # Keep the task active until its worker exits, so cancellation cannot
        # be used to bypass the concurrent-download limit.
        event.set()
        task["cancellation_requested"] = True
        task["error"] = "Cancellation requested."
        return True

def is_cancelled(task_id: str) -> bool:
    event = cancel_events.get(task_id)
    return bool(event and event.is_set())

def cleanup_expired_tasks(max_age_seconds: int = 3600):
    """Clean up stale task records and their completed output files."""
    now = time.time()
    cutoff = now - max_age_seconds
    with tasks_lock:
        expired = [
            tid for tid, t in tasks.items()
            if t.get("created_at", 0) < cutoff
            and t.get("status") not in {"queued", "downloading", "processing"}
        ]
        for tid in expired:
            task = tasks.pop(tid)
            file_path = task.get("file_path")
            if task.get("status") == "completed" and file_path and os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            if tid in cancel_events:
                del cancel_events[tid]
