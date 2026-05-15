import os

"""Innovation Lab Service - Main Application

import os
FastAPI application for AI-powered innovation, experimentation, and tech exploration.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .config import config
from .routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_innovation_app() -> FastAPI:
    """Create and configure the Innovation Lab FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance

    """
    app = FastAPI(
        title=config.service_name,
        version=config.version,
        description=config.description,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.environ.get(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
        ).split(","),
        allow_credentials=True,
        allow_methods=os.environ.get("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(
            ","
        ),
        allow_headers=os.environ.get(
            "CORS_HEADERS", "Content-Type,Authorization,X-Requested-With"
        ).split(","),
    )

    # Include routers
    app.include_router(router, prefix="/v1", tags=["innovation-lab"])

    # Root redirect to docs
    @app.get("/", include_in_schema=False)
    async def redirect_to_docs():
        """Redirect root to API documentation"""
        return RedirectResponse(url="/docs")

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        logger.info(f"Starting {config.service_name} v{config.version}")
        logger.info(f"Innovation focus areas: {', '.join(config.innovation_focus_areas)}")
        logger.info(f"Experimental features enabled: {config.enable_experimental_features}")

    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info(f"Shutting down {config.service_name}")

    return app


# Create app instance
app = create_innovation_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.innovation_lab.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,
        log_level=config.log_level.lower(),
    )
