"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .database import get_db_context, init_db
from .routes import agent_router, growth_router
from .services import AgentService

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Initialize agents in database
    logger.info("Initializing agents...")
    with get_db_context() as db:
        service = AgentService(db)
        service.initialize_agents_in_db()

    logger.info(f"Application started successfully - {settings.app_name} v{settings.app_version}")

    if settings.use_vertex:
        logger.info(f"Using Vertex AI in project: {settings.google_cloud_project}")
    else:
        msg = "Use Vertex AI enabled" if settings.use_vertex else "Running in Pure Gemini Mode"
        logger.info(msg)

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    AI You - FastAPI Agent Services

    This service provides AI agents for growth engineering, product strategy, and data analysis.

    ## Features

    - **Growth Engineer Agent**: Implements viral mechanics and growth loops
    - **Analytics Tools**: Metrics analysis, A/B testing, viral coefficients
    - **Retention Analysis**: Cohort analysis and retention optimization
    - **Funnel Optimization**: Conversion funnel analysis and recommendations

    ## Agents

    ### Growth Engineer
    Finds where users get hooked in your app and builds viral loops that actually work.

    Key capabilities:
    - Viral mechanics design
    - User hook identification
    - Growth loop implementation
    - A/B testing framework
    - Analytics tracking
    - Engagement features
    """,
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "vertex_ai": settings.use_vertex,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "description": "AI You - FastAPI Agent Services",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_url": "/health",
        "agents": {
            "list": f"{settings.api_prefix}/agents/",
            "growth_engineer": f"{settings.api_prefix}/agents/growth_engineer",
        },
        "growth_endpoints": {
            "analyze": f"{settings.api_prefix}/growth/analyze",
            "ab_test": f"{settings.api_prefix}/growth/ab-test/design",
            "viral_loop": f"{settings.api_prefix}/growth/viral-loop/analyze",
            "retention": f"{settings.api_prefix}/growth/retention/analyze",
            "funnel": f"{settings.api_prefix}/growth/funnel/analyze",
            "hooks": f"{settings.api_prefix}/growth/hooks/identify",
            "experiments": f"{settings.api_prefix}/growth/experiment/recommend",
        },
    }


# Include routers
app.include_router(agent_router, prefix=settings.api_prefix)
app.include_router(growth_router, prefix=settings.api_prefix)


# WEALTH LEAK PLUG: Monetization Middleware
from .pnkln.api.monetization import monetization


class MonetizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip health/root/docs endpoints
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # 1. Capture API Key
        api_key = request.headers.get("X-ShadowTag-v2-API-KEY")

        # 2. Enforce Auth for API routes
        if request.url.path.startswith(settings.api_prefix):
            if not api_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing X-ShadowTag-v2-API-KEY header"},
                )

            # 3. Track Usage & Billing
            try:
                monetization.track_request(api_key, request.url.path)
            except ValueError as e:
                return JSONResponse(
                    status_code=402,
                    content={"error": str(e)},
                )  # Payment Required / Quota Exceeded

        response = await call_next(request)
        return response


app.add_middleware(MonetizationMiddleware)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
    )
