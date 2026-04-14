"""Main FastAPI application with sandboxing support."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import router
from app.security.middleware import (
    RequestValidationMiddleware,
    SandboxMiddleware,
)
from app.routers.stripe_handler import router as stripe_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    settings = get_settings()

    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        sandbox_enabled=settings.sandbox.enabled,
    )

    yield

    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url=f"{settings.api_prefix}/docs",
        redoc_url=f"{settings.api_prefix}/redoc",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **settings.get_cors_config(),
    )

    # Add security middleware
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(SandboxMiddleware, max_requests_per_minute=60)

    # Include routers
    app.include_router(
        router,
        prefix=settings.api_prefix,
        tags=["api"],
    )

    # Stripe webhook handler (signature-verified, idempotent)
    app.include_router(
        stripe_router,
        tags=["webhooks"],
    )

    logger.info(
        "application_configured",
        api_prefix=settings.api_prefix,
        cors_origins=settings.cors_origins,
    )

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers,
        log_level=settings.log_level.lower(),
    )
