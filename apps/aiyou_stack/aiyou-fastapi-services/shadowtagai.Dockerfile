FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    git \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONPATH="/app"
ENV PORT=8000

# Expose port
EXPOSE 8000

# Run ShadowTagAI API
CMD ["uvicorn", "src.aiyou.main:app", "--host", "0.0.0.0", "--port", "8000"]
