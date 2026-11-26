import os
import time
import threading
from typing import Dict, Any, Optional

# Active tasks store: task_id -> dict
tasks: Dict[str, Dict[str, Any]] = {}
tasks_lock = threading.Lock()

# Thread cancel events: task_id -> threading.Event
cancel_events: Dict[str, threading.Event] = {}

def create_task(task_id: str, data: Dict[str, Any]) -> None:
    event = threading.Event()
    cancel_events[task_id] = event
    with tasks_lock:
        tasks[task_id] = data

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    with tasks_lock:
        task = tasks.get(task_id)
        return dict(task) if task else None

def update_task(task_id: str, **kwargs) -> None:
    with tasks_lock:
        if task_id in tasks:
            tasks[task_id].update(kwargs)

def cancel_task(task_id: str) -> bool:
    event = cancel_events.get(task_id)
    if event:
        event.set()
    with tasks_lock:
        if task_id in tasks:
            tasks[task_id]["status"] = "cancelled"
            tasks[task_id]["error"] = "Download was cancelled."
            return True
    return False

def is_cancelled(task_id: str) -> bool:
    event = cancel_events.get(task_id)
    return bool(event and event.is_set())

def cleanup_expired_tasks(max_age_seconds: int = 7200):
    """Clean up memory and cancel events for tasks older than max_age_seconds."""
    now = time.time()
    cutoff = now - max_age_seconds
    with tasks_lock:
        expired = [
            tid for tid, t in tasks.items()
            if t.get("created_at", 0) < cutoff
        ]
        for tid in expired:
            del tasks[tid]
            if tid in cancel_events:
                del cancel_events[tid]
