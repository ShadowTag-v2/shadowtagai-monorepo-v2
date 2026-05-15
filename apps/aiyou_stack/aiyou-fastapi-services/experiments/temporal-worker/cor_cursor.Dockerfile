# ----------------------------------------------------------------------
# Cor.Cursor VDI Worker Environment
# ----------------------------------------------------------------------
FROM python:3.11-slim

# Install system dependencies (Cinematic VDI Stack)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    xvfb \
    x11vnc \
    fluxbox \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install isolated Playwright deps
COPY requirements.txt .
# Mock requirements install to get playwright
RUN pip install "playwright==1.42.0" "google-generativeai==0.4.1" "temporalio==1.5.1"
RUN playwright install --with-deps chromium

COPY . .

# Expose invisible monitor buffer to the Python orchestrator
ENV DISPLAY=:99

# Boot Temporal worker wrapped in Virtual Display
CMD Xvfb :99 -screen 0 1920x1080x24 & fluxbox & python worker.py
