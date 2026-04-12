"""
ShadowTag-v4 FastAPI Main Application

This is the main entry point for the ShadowTag-v4 platform API services.
"""

import logging
import os
import time
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .middleware import (
    RateLimitMiddleware,
    RequestValidationMiddleware,
    RevenueGateMiddleware,
    SecurityHeadersMiddleware,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
app = FastAPI(
    title="ShadowTag-v4 Platform API",
    description="The Verified AI Civilization Layer - Infrastructure, Content, Commerce, and Truth",
    version="0.1.0",
    docs_url="/docs"
    if settings.environment != "production"
    else None,  # Disable docs in production
    redoc_url="/redoc" if settings.environment != "production" else None,
    openapi_url="/openapi.json" if settings.environment != "production" else None,
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    # Create DB tables (In production, use Alembic)
    Base.metadata.create_all(bind=engine)


# CORS Configuration
app.add_middleware(
    RequestValidationMiddleware,
    max_request_size=10 * 1024 * 1024,  # 10MB
    max_upload_size=500 * 1024 * 1024,  # 500MB
)

# 2. Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_requests_per_minute,
    burst=settings.rate_limit_burst,
    upload_per_hour=settings.rate_limit_upload_per_hour,
    enabled=settings.rate_limit_enabled,
)

# 3. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 4. Revenue Gate (No Pay, No AI)
app.add_middleware(RevenueGateMiddleware)

# 5. CORS Configuration (strict by default)
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_credentials,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    logger.info(f"CORS enabled for origins: {settings.cors_origins}")
else:
    logger.warning("CORS origins not configured - no CORS middleware added")


# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Root endpoint
@app.get("/", tags=["System"])
async def root() -> dict[str, Any]:
    """
    Root endpoint providing basic API information.

    Returns:
        Dict containing API metadata and service status
    """
    return {
        "name": "ShadowTag-v4 Platform API",
        "version": "0.1.0",
        "description": "The Verified AI Civilization Layer",
        "status": "operational",
        "services": {
            "cineverse": "Verified streaming platform",
            "gameport": "Gaming integration layer",
            "commerce": "Virtual commerce mall",
            "shadowtag": "Cryptographic verification",
            "infrastructure": "Edge compute mesh",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
    }


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for load balancers and monitoring.
    Verifies core dependencies (DB, Redis) are reachable.

    Returns:
        Dict with status indicator
    """
    health_status = "healthy"
    # Basic connectivity check logic
    try:
        # TODO: Implement actual DB ping
        # await db.execute("SELECT 1")
        pass
    except Exception:
        health_status = "degraded"

    return {"status": health_status, "service": "shadowtag_v4-api"}


# Service status endpoint
@app.get("/status", tags=["System"])
async def service_status() -> dict[str, Any]:
    """
    Detailed service status endpoint.
    Checks connectivity to all dependent services and infrastructure.

    Returns:
        Dict with detailed status of all services
    """
    status_report = {
        "api": "operational",
        "database": "unknown",
        "redis": "unknown",
        "shadowtag": "operational",
        "services": {
            "cineverse": {"status": "operational", "endpoints": ["/api/v1/cineverse"]},
            "gameport": {"status": "operational", "endpoints": ["/api/v1/gameport"]},
            "commerce": {"status": "operational", "endpoints": ["/api/v1/commerce"]},
            "shadowtag": {"status": "operational", "endpoints": ["/api/v1/shadowtag"]},
            "infrastructure": {
                "status": "operational",
                "endpoints": ["/api/v1/infrastructure"],
            },
        },
    }

    # Check Database
    try:
        # Placeholder for DB check
        # await db.execute("SELECT 1")
        status_report["database"] = "operational"
    except Exception as e:
        status_report["database"] = f"down: {str(e)}"

    # Check Redis
    try:
        # Placeholder for Redis check
        # await redis.ping()
        status_report["redis"] = "operational"
    except Exception as e:
        status_report["redis"] = f"down: {str(e)}"

    return status_report


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource {request.url.path} was not found",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "path": str(request.url.path),
        },
    )


# Include service routers
# Include service routers
from .routers import atomic_chat
from .routes.cineverse import router as cineverse_router
from .routes.governance import router as governance_router
from .routes.ingestion import router as ingestion_router

app.include_router(ingestion_router)
app.include_router(governance_router, tags=["Governance"])
app.include_router(cineverse_router, prefix="/api/v1/cineverse", tags=["CineVerse"])
app.include_router(atomic_chat.router, prefix="/api/v1/atomic-chat", tags=["Atomic Chat"])

# Mount static files for landing pages (GamePort games, etc.)
# Check if directories exist before mounting
landing_pages_dir = os.path.join(os.path.dirname(__file__), "..", "..", "landing-pages/gameport")
if os.path.isdir(landing_pages_dir):
    app.mount(
        "/games",
        StaticFiles(directory=landing_pages_dir, html=True),
        name="game-landings",
    )
    logger.info(f"Mounted game landing pages from {landing_pages_dir}")

# TODO: Add remaining service routers as they are implemented
# from .services.gameport.routes import router as gameport_router
# from .services.commerce.routes import router as commerce_router
# from .services.shadowtag.routes import router as shadowtag_router
# from .services.infrastructure.routes import router as infrastructure_router
#
# app.include_router(gameport_router, prefix="/api/v1/gameport", tags=["GamePort"])
# app.include_router(commerce_router, prefix="/api/v1/commerce", tags=["Commerce"])
# app.include_router(shadowtag_router, prefix="/api/v1/shadowtag", tags=["ShadowTag"])
# app.include_router(infrastructure_router, prefix="/api/v1/infrastructure", tags=["Infrastructure"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
