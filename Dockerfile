# Multi-stage build for CONTEXT video evidence workstation
FROM node:22-alpine AS frontend-builder
WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app

# Install system dependencies (ffmpeg, ffprobe, and OpenCV requirements)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application and static assets
COPY backend/ ./backend/
COPY --from=frontend-builder /app/web/dist ./web/dist

# Setup default runtime environment
COPY .env.example .env

EXPOSE 8000
CMD ["uvicorn", "context_core.api:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]
