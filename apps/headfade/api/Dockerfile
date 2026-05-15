# HeadFade API — Production Cloud Run Container
# Multi-stage build for minimal image size + security hardening.

FROM python:3.14-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

FROM python:3.14-slim

# Non-root user for Cloud Run security best practice
RUN adduser --system --no-create-home appuser

WORKDIR /app

# Copy only the installed dependencies
COPY --from=builder /deps /deps
ENV PYTHONPATH="/deps:${PYTHONPATH}"

COPY . .

# Ensure Python doesn't buffer stdout/stderr (critical for Cloud Logging)
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

USER appuser

EXPOSE 8080

# SIGTERM handler — uvicorn handles graceful shutdown by default
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
