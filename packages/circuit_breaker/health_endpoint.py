# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Circuit Breaker — HTTP Health Endpoint.

Exposes circuit breaker health status via a lightweight HTTP handler
suitable for Cloud Run readiness probes and Kubernetes liveness checks.

Can be used standalone or mounted in any ASGI/WSGI application:

Standalone (for testing)::

    python -m circuit_breaker.health_endpoint --port 8081

Cloud Run readiness probe::

    # In your service.yaml:
    readinessProbe:
      httpGet:
        path: /health
        port: 8081

ASGI integration::

    from circuit_breaker.health_endpoint import health_response
    # Mount health_response() in your FastAPI/Starlette app

Design decisions:
  - Returns HTTP 200 when all breakers are CLOSED or HALF_OPEN
  - Returns HTTP 503 when ANY breaker is OPEN (service degraded)
  - Response body is the full health report JSON for diagnostics
  - No framework dependency — uses stdlib http.server for standalone
"""

from __future__ import annotations

import json
import logging
from http import HTTPStatus
from typing import Any

logger = logging.getLogger(__name__)


def health_response(
    registry: Any | None = None,
) -> tuple[int, dict[str, Any]]:
    """Generate a health check response.

    Args:
        registry: CircuitBreakerRegistry to check. Defaults to the
            global ``default_registry`` from telemetry_bridge.

    Returns:
        Tuple of (HTTP status code, response body dict).
        200 = healthy, 503 = degraded (one or more breakers OPEN).
    """
    from circuit_breaker.dashboard import get_health_report

    if registry is not None:
        # Use the provided registry instead of the default

        # Temporarily swap — dashboard uses module-level default_registry
        import circuit_breaker.dashboard as _dashboard

        original = _dashboard.default_registry
        try:
            _dashboard.default_registry = registry
            report = get_health_report()
        finally:
            _dashboard.default_registry = original
    else:
        report = get_health_report()

    summary = report.get("summary", {})
    open_count = summary.get("open", 0)

    if open_count > 0:
        status_code = HTTPStatus.SERVICE_UNAVAILABLE  # 503
        report["http_status"] = 503
        report["http_reason"] = "Service Degraded — circuit breakers open"
    else:
        status_code = HTTPStatus.OK  # 200
        report["http_status"] = 200
        report["http_reason"] = "All circuit breakers healthy"

    return int(status_code), report


def health_json(registry: Any | None = None) -> tuple[int, str]:
    """Generate health check as (status_code, JSON string).

    Convenience wrapper for HTTP handlers.
    """
    status_code, body = health_response(registry)
    return status_code, json.dumps(body, indent=2, default=str)


# --- Standalone HTTP server (for local testing / Cloud Run sidecar) ---


def _run_health_server(port: int = 8081) -> None:
    """Run a minimal HTTP server that serves /health.

    Uses stdlib http.server — no dependencies required.
    """
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health" or self.path == "/":
                status_code, body_json = health_json()
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body_json.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, fmt: str, *args: Any) -> None:
            logger.info(fmt, *args)

    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info("Circuit breaker health endpoint running on port %d", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Health endpoint shutting down")
        server.server_close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Circuit Breaker Health Endpoint")
    parser.add_argument("--port", type=int, default=8081, help="Port to listen on")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    _run_health_server(args.port)
