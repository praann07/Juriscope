# Multi-stage Dockerfile for Juriscope (FastAPI API + built React frontend)
# Compatible with Azure App Service, Docker Hub, and Render

# Stage 0: Build the React frontend into static files
FROM node:22-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 1: Build
FROM python:3.12-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first. The default Linux wheel pulls in several GB of CUDA
# libraries that a CPU host never uses. requirements.txt is satisfied by this install.
RUN pip install --user --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to include user's .local/bin
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY . .

# Copy the built frontend (served by the backend at /)
COPY --from=frontend-build /frontend/dist /app/frontend/dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT', '8000') + '/api/health', timeout=5)"]

# Default port (can be overridden by Azure's PORT env var)
ENV PORT=8000
EXPOSE 8000

# Start the application with gunicorn.
# One worker only: each worker loads the embedding model (several hundred MB) into memory,
# so two workers would not fit on a 1.75 GB App Service plan.
# Azure App Service will set PORT env var; we respect it here
CMD exec gunicorn src.app:app \
    -k uvicorn.workers.UvicornWorker \
    --workers 1 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
