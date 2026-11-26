import os
import time
import threading
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes.api import router as api_router
from .services.task_manager import cleanup_expired_tasks

app = FastAPI(
    title="DanfeDrop - YouTube Media Downloader",
    description="Clean, modular YouTube video and audio downloader",
    version="1.0.0",
)

# Enable CORS for development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router)


@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
async def chrome_devtools_probe():
    return Response(status_code=204)


from .services.cookie_manager import get_cookie_file

# Periodic background task to clean up old task tracking
def background_cleanup_loop():
    while True:
        try:
            time.sleep(1800)  # run every 30 minutes
            cleanup_expired_tasks()
        except Exception:
            pass


threading.Thread(target=background_cleanup_loop, daemon=True).start()



# Mount frontend build if it exists
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        response = FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

