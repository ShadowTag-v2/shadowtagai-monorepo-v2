FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application source (not the full monorepo)
COPY app/ ./app/
COPY src/ ./src/
COPY packages/ ./packages/
COPY configs/ ./configs/ 

# Expose port (Cloud Run injects PORT=8080)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# Run the application — use PORT env var (Cloud Run sets PORT=8080)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
