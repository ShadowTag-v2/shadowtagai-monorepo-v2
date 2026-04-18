"""FastAPI service for Pnkln File Search"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from pnkln_file_search.api.routes import router
from pnkln_file_search.config.mock_mode import MockCorpusManager, is_mock_mode
from pnkln_file_search.config.settings import get_settings
from pnkln_file_search.corpus.manager import CorpusManager
from pnkln_file_search.monitoring.kill_switch import KillSwitch
from pnkln_file_search.monitoring.metrics import MetricsCollector

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger(__name__)

# Global instances
corpus_manager: CorpusManager = None
kill_switch: KillSwitch = None
metrics_collector: MetricsCollector = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global corpus_manager, kill_switch, metrics_collector

    # Startup
    logger.info("service_starting", mock_mode=is_mock_mode())

    try:
        # Initialize components (use mock if MOCK_MODE=true)
        if is_mock_mode():
            logger.warning("running_in_mock_mode", message="Using mock Vertex AI responses")
            corpus_manager = MockCorpusManager()
        else:
            corpus_manager = CorpusManager()

        await corpus_manager.initialize()

        metrics_collector = MetricsCollector()
        kill_switch = KillSwitch(metrics_collector)

        # Store in app state
        app.state.corpus_manager = corpus_manager
        app.state.kill_switch = kill_switch
        app.state.metrics_collector = metrics_collector

        logger.info("service_started", version="0.1.0")

        yield

    finally:
        # Shutdown
        logger.info("service_shutting_down")


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title="Pnkln File Search Service",
    description="Google File Search Integration for Pnkln Core Stack with Judge #6",
    version="0.1.0",
    lifespan=lifespan,
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "pnkln-file-search",
        "version": "0.1.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if not app.state.corpus_manager or not app.state.kill_switch:
        raise HTTPException(status_code=503, detail="Service not initialized")

    health_check = app.state.kill_switch.check_health()

    status_code = 200
    if not health_check["healthy"]:
        status_code = 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": health_check["state"],
            "healthy": health_check["healthy"],
            "violations": health_check["violations"],
        },
    )


@app.get("/health/ready")
async def readiness():
    """Readiness check for Kubernetes"""
    if not app.state.corpus_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    return {"ready": True}


@app.get("/health/live")
async def liveness():
    """Liveness check for Kubernetes"""
    return {"alive": True}


def main():
    """Main entry point"""
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "pnkln_file_search.main:app",
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
