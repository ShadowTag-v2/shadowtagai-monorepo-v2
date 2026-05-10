# Google Cloud Run optimized Dockerfile
FROM python:3.11-slim-bookworm AS builder

# DeepMind infrastructure requirements
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Ensure google-genai and vertexai are preferred over openai
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim-bookworm

# Playwright dependencies for the Nexus API
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libx11-xcb1 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

# Install browser binaries
RUN playwright install chromium
RUN playwright install-deps

COPY src/ ./src/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "src.api.nexus:app", "--host", "0.0.0.0", "--port", "8080"]
