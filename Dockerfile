# Stage 1: Build the React frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python + FFmpeg + Node.js runtime for FastAPI & yt-dlp
FROM python:3.12-slim
WORKDIR /app

# Install ffmpeg (for merging video/audio) and nodejs (for yt-dlp EJS solver)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg nodejs ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and built frontend
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure downloads go to /tmp inside container
ENV DOWNLOAD_DIR=/tmp/danfedrop_downloads

EXPOSE 10000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
