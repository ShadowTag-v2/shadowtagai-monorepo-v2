import os
import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from middleware.app_check import app_check_middleware
from middleware.telemetry import instrument_app
from routers import (
  arbiter,
  arbiter_engine,
  b2b_refinery,
  crypto_shred,
  hdi_telemetry,
  ingestion,
  judge6,
  studio,
)

# ---------------------------------------------------------------------------
# In-memory rate limiter — sliding window, per-IP.
# Production should use Redis or Cloud Tasks, but this blocks trivial bots.
# ---------------------------------------------------------------------------
_RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX_VOTES", "30"))
_RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW_SECS", "60"))
_rate_store: dict[str, list[float]] = defaultdict(list)


app = FastAPI(
  title="HeadFade API",
  version="1.0.0",
  description="Backend for the HeadFade Global Turing Test. Ethically sourced Human Deception Index generation.",
)


@app.middleware("http")
async def rate_limit_votes(request: Request, call_next):
  """Rate-limit /api/vote to prevent HDI pollution from bot traffic."""
  if request.url.path == "/api/vote" and request.method == "POST":
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    # Prune expired entries
    _rate_store[client_ip] = [
      t for t in _rate_store[client_ip] if now - t < _RATE_LIMIT_WINDOW
    ]
    if len(_rate_store[client_ip]) >= _RATE_LIMIT_MAX:
      return JSONResponse(
        status_code=429,
        content={
          "detail": f"Rate limit exceeded. Max {_RATE_LIMIT_MAX} votes per {_RATE_LIMIT_WINDOW}s.",
        },
      )
    _rate_store[client_ip].append(now)
  return await call_next(request)


app.add_middleware(
  CORSMiddleware,
  allow_origins=os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000,https://headfade.web.app"
  ).split(","),
  allow_credentials=True,
  allow_methods=os.environ.get(
    "CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH"
  ).split(","),
  allow_headers=os.environ.get(
    "CORS_HEADERS", "Content-Type,Authorization,X-Requested-With"
  ).split(","),
)

# App Check enforcement — validates Firebase App Check tokens on /api/* routes
app.middleware("http")(app_check_middleware)

app.include_router(arbiter.router)
app.include_router(
  arbiter_engine.router, prefix="/api/arbiter-engine", tags=["arbiter-engine"]
)
app.include_router(b2b_refinery.router, prefix="/api/b2b", tags=["b2b-refinery"])
app.include_router(hdi_telemetry.router, prefix="/api", tags=["telemetry"])
app.include_router(judge6.router)
app.include_router(ingestion.router)
app.include_router(studio.router, prefix="/api/studio", tags=["studio"])
app.include_router(crypto_shred.router)

# OpenTelemetry — Cloud Trace export for latency and HDI quality monitoring
instrument_app(app)


@app.get("/health")
@app.get("/api/health")
def health_check():
  return {"status": "operational", "service": "headfade-api"}


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
