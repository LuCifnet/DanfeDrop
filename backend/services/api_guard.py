"""Small single-process abuse controls for the public API."""

from collections import OrderedDict, deque
from ipaddress import ip_address
import threading
import time

from fastapi import HTTPException, Request


_MAX_CLIENT_BUCKETS = 4096
_buckets = OrderedDict()
_lock = threading.Lock()
_analysis_slots = threading.BoundedSemaphore(4)


def get_client_key(request: Request) -> str:
    """Use the rightmost appended proxy IP, or the direct peer locally."""
    forwarded_for = request.headers.get("x-forwarded-for", "")
    for candidate in reversed(forwarded_for.split(",")):
        try:
            return str(ip_address(candidate.strip()))
        except ValueError:
            continue

    peer = request.client.host if request.client else "unknown"
    try:
        return str(ip_address(peer))
    except ValueError:
        return peer[:128] or "unknown"


def enforce_rate_limit(request: Request, action: str, limit: int, window_seconds: int) -> str:
    """Allow at most `limit` requests for a client during a sliding time window."""
    client_key = get_client_key(request)
    bucket_key = (client_key, action)
    now = time.monotonic()
    cutoff = now - window_seconds

    with _lock:
        bucket = _buckets.get(bucket_key)
        if bucket is None:
            if len(_buckets) >= _MAX_CLIENT_BUCKETS:
                _buckets.popitem(last=False)
            bucket = deque()
            _buckets[bucket_key] = bucket
        else:
            _buckets.move_to_end(bucket_key)

        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= limit:
            retry_after = max(1, int(window_seconds - (now - bucket[0])))
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait before trying again.",
                headers={"Retry-After": str(retry_after)},
            )

        bucket.append(now)

    return client_key


def acquire_analysis_slot() -> bool:
    return _analysis_slots.acquire(blocking=False)


def release_analysis_slot() -> None:
    _analysis_slots.release()
