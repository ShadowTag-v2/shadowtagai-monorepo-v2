FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Install system deps
RUN apt-get update && apt-get install -y wget unzip && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install fastapi uvicorn playwright-stealth

# Copy Code
WORKDIR /app
COPY browser_subagent.py .

# Expose Sidecar Port
EXPOSE 3000

# Run
CMD ["python", "browser_subagent.py"]
