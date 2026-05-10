# ShadowTag Omega V7: The Sovereign Sentinel
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for the Relay server
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install (Stub - no requirements.txt yet, assuming standard libs)
# COPY requirements.txt .
# RUN pip install -r requirements.txt
RUN pip install fastapi uvicorn playwright websockets
RUN playwright install chromium

# Copy application source
COPY . .

# Expose Relay port
EXPOSE 8080

# Start combined services (Simulated via script)
CMD ["bash", "-c", "node src/relay/server.js & python3 scripts/sentinel_loop.py"]
