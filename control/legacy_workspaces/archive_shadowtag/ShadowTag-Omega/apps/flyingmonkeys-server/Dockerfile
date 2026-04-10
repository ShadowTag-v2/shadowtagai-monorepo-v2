FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY apps/n-autoresearch/Kosmos/BioAgentss-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/n-autoresearch/Kosmos/BioAgentss-server/src/ src/
COPY libs/ libs/
COPY pyproject.toml .

# Environment variables
ENV PORT 8080
ENV PYTHONPATH=/app:/app/libs

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
