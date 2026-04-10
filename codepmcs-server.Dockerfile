FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (shared with Autoresearch)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH to include /app so imports work
ENV PYTHONPATH=/app

# Expose port (Cloud Run sets PORT env var, default 8080)
EXPOSE 8080

# Run CodePMCS Server
CMD ["python3", "bin/codepmcs-server"]
