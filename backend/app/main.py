# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Main FastAPI application for Release Manager.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from prometheus_client import make_asgi_app, Counter, Histogram
import time

from app.core.config import settings
from app.core.logger import logger
from app.database.session import init_db, close_db
from app.api.v1.router import api_router
from app.services.feature_flags import feature_flag_service


# Prometheus metrics
REQUEST_COUNT = Counter(
  "http_requests_total",
  "Total HTTP requests",
  ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
  "http_request_duration_seconds",
  "HTTP request duration in seconds",
  ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
  """
  Application lifespan manager.

  Handles startup and shutdown events.
  """
  # Startup
  logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
  logger.info(f"Environment: {settings.APP_ENV}")

  # Initialize database
  try:
    await init_db()
    logger.info("Database initialized")
  except Exception as e:
    logger.error(f"Database initialization failed: {e}")

  # Initialize Redis for feature flags
  try:
    await feature_flag_service.init_redis()
  except Exception as e:
    logger.warning(f"Redis initialization failed: {e}")

  logger.info("Application started successfully")

  yield

  # Shutdown
  logger.info("Shutting down application")

  # Close database connections
  await close_db()
  logger.info("Database connections closed")

  # Close Redis connection
  await feature_flag_service.close_redis()
  logger.info("Redis connections closed")

  logger.info("Application shut down successfully")


# Create FastAPI application
app = FastAPI(
  title=settings.APP_NAME,
  version=settings.APP_VERSION,
  description="Release Manager API for zero-downtime deployments",
  lifespan=lifespan,
  docs_url="/docs",
  redoc_url="/redoc",
  openapi_url="/openapi.json",
)


# CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.BACKEND_CORS_ORIGINS,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
  """Log all HTTP requests."""
  start_time = time.time()

  # Log request
  logger.info(
    f"Request: {request.method} {request.url.path}",
    extra={
      "method": request.method,
      "path": request.url.path,
      "client": request.client.host if request.client else None,
    },
  )

  # Process request
  try:
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Record metrics
    REQUEST_COUNT.labels(
      method=request.method,
      endpoint=request.url.path,
      status=response.status_code,
    ).inc()

    REQUEST_DURATION.labels(
      method=request.method,
      endpoint=request.url.path,
    ).observe(duration)

    # Log response
    logger.info(
      f"Response: {response.status_code} - {duration:.3f}s",
      extra={
        "status_code": response.status_code,
        "duration": duration,
      },
    )

    return response

  except Exception as e:
    logger.error(f"Request error: {e}")
    raise


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
  """Handle validation errors."""
  logger.warning(f"Validation error: {exc}")
  return JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    content={
      "detail": exc.errors(),
      "body": exc.body,
    },
  )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
  """Handle general exceptions."""
  logger.error(f"Unhandled exception: {exc}", exc_info=True)
  return JSONResponse(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    content={
      "detail": "Internal server error",
      "message": str(exc) if settings.DEBUG else "An error occurred",
    },
  )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
  """
  Health check endpoint.

  Returns:
      Health status
  """
  return {
    "status": "healthy",
    "version": settings.APP_VERSION,
    "environment": settings.APP_ENV,
  }


# Readiness check endpoint
@app.get("/ready", tags=["health"])
async def readiness_check():
  """
  Readiness check endpoint.

  Returns:
      Readiness status
  """
  # In production, you would check database connectivity, etc.
  return {
    "status": "ready",
    "version": settings.APP_VERSION,
  }


# Include API router
app.include_router(api_router, prefix="/api")


# Prometheus metrics endpoint
if settings.PROMETHEUS_ENABLED:
  metrics_app = make_asgi_app()
  app.mount("/metrics", metrics_app)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
  """
  Root endpoint.

  Returns:
      API information
  """
  return {
    "name": settings.APP_NAME,
    "version": settings.APP_VERSION,
    "environment": settings.APP_ENV,
    "docs": "/docs",
    "redoc": "/redoc",
    "health": "/health",
    "ready": "/ready",
    "metrics": "/metrics" if settings.PROMETHEUS_ENABLED else None,
  }


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(
    "app.main:app",
    host=settings.HOST,
    port=settings.PORT,
    reload=settings.RELOAD,
    log_level=settings.LOG_LEVEL.lower(),
  )
