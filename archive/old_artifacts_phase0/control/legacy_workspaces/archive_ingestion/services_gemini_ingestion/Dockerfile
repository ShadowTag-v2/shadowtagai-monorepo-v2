# Gemini Ingestion Layer - CronJob Container
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 ingestionuser && chown -R ingestionuser:ingestionuser /app
USER ingestionuser

# Run ingestion pipeline
CMD ["python", "cron_job.py"]
