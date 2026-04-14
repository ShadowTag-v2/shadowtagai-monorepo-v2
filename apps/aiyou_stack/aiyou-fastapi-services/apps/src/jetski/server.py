"""JETSKI SIDECAR SERVICE
Exposes browser automation as REST API
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from src.jetski.browser_engine import get_jetski

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jetski-sidecar")

app = FastAPI(
    title="Jetski Reality Validator",
    description="Browser automation sidecar for n-autoresearch/Kosmos/BioAgents",
    version="2.0.0",
)


# Request models
class EndpointCheck(BaseModel):
    url: HttpUrl
    expected_status: int = 200


class PageRenderCheck(BaseModel):
    url: HttpUrl
    selector: str  # CSS selector to verify


class InterceptionConfig(BaseModel):
    url: HttpUrl
    block_pattern: str | None = None
    modify_headers: dict[str, str] | None = None


# Health check
@app.get("/health")
def health_check():
    """Cloud Run health check."""
    return {"status": "healthy", "service": "jetski-sidecar"}


# Core endpoints
@app.post("/verify/endpoint")
def verify_endpoint(check: EndpointCheck):
    """Verify an API endpoint is accessible and returns expected status.

    Example:
    POST /verify/endpoint
    {
      "url": "https://n-autoresearch/Kosmos/BioAgents-server-s2its66sea-uc.a.run.app/health",
      "expected_status": 200
    }

    """
    try:
        jetski = get_jetski()
        result = jetski.verify_endpoint(str(check.url), check.expected_status)

        if not result["success"]:
            logger.warning(f"Endpoint check failed: {result}")

        return result
    except Exception as e:
        logger.error(f"Jetski error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify/render")
def verify_render(check: PageRenderCheck):
    """Verify a page renders and element exists.
    Returns screenshot as base64.

    Example:
    POST /verify/render
    {
      "url": "https://example.com",
      "selector": "h1.title"
    }

    """
    try:
        jetski = get_jetski()
        result = jetski.verify_page_render(str(check.url), check.selector)

        return result
    except Exception as e:
        logger.error(f"Render check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/intercept")
def intercept_traffic(config: InterceptionConfig):
    """Advanced: Modify network traffic in-flight.
    Use for testing error handling.
    """
    try:
        jetski = get_jetski()
        result = jetski.intercept_and_modify(
            str(config.url),
            {
                "block_pattern": config.block_pattern,
                "modify_headers": config.modify_headers,
            },
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on container shutdown."""
    jetski = get_jetski()
    jetski.cleanup()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
