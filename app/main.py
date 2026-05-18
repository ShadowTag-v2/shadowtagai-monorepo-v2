# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Main FastAPI application — Cloud Run compatible.

All heavy imports (DB, embedding, routes) are deferred to lifespan()
to prevent import-time crashes in containers without full env vars.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Light config import only (no I/O at import time)
from app.core.config import settings

# Configure logging
logging.basicConfig(
  level=settings.log_level,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Lifespan context manager for startup and shutdown events."""
  logger.info("Starting up CounselConduit service...")

  # Lazy-import DB and services only during startup
  db_ready = False
  try:
    from app.db.base import init_db

    logger.info("Initializing database...")
    await init_db()
    db_ready = True
  except Exception as exc:
    logger.warning("Database init skipped (non-fatal): %s", exc)

  embedding_ready = False
  try:
    from app.services import embedding_service

    logger.info("Initializing embedding service...")
    await embedding_service.initialize()
    embedding_ready = True
  except Exception as exc:
    logger.warning("Embedding service init skipped (non-fatal): %s", exc)

  # Lazy-import and register routes
  try:
    from app.api.routes import conversations, memories, projects, search

    app.include_router(conversations.router, prefix=settings.api_prefix)
    app.include_router(memories.router, prefix=settings.api_prefix)
    app.include_router(search.router, prefix=settings.api_prefix)
    app.include_router(projects.router, prefix=settings.api_prefix)
  except Exception as exc:
    logger.warning("Route registration partial: %s", exc)

  logger.info(
    "Startup complete! DB=%s, Embeddings=%s",
    "ready" if db_ready else "skipped",
    "ready" if embedding_ready else "skipped",
  )

  yield

  # Shutdown
  logger.info("Shutting down CounselConduit...")


# Create FastAPI app
app = FastAPI(
  title="CounselConduit",
  version="3.4.0",
  description="Privilege-preserving legal AI routing for law firms.",
  lifespan=lifespan,
  docs_url=None if os.getenv("DISABLE_DOCS") else "/docs",
  redoc_url=None,
)

# CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Tighten for production
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/")
async def root():
  """Root endpoint — service identity."""
  return {
    "service": "CounselConduit",
    "version": "3.4.0",
    "status": "operational",
    "docs": "disabled" if os.getenv("DISABLE_DOCS") else "/docs",
  }


async def _health_response():
  """Shared health check response."""
  return {"status": "healthy", "service": "counselconduit", "version": "3.4.0"}


@app.get("/health")
async def health_check():
  """Health check endpoint."""
  return await _health_response()


@app.get("/healthz")
async def healthz_check():
  """Health check endpoint (K8s-style alias for /health)."""
  return await _health_response()


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(
    "app.main:app",
    host=settings.host,
    port=settings.port,
    reload=settings.reload,
    log_level=settings.log_level.lower(),
  )
