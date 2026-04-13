FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY src/ ./src/

# Cloud Run expects PORT env
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "api.fastapi_kovel_enclave:app", "--host", "0.0.0.0", "--port", "8080"]
