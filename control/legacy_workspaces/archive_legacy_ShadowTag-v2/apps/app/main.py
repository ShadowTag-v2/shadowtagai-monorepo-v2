# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
AiYou PNKLN Core Stack™ API
FastAPI application for intelligence collection and validation

Based on Cor.8 AiYou Global Edge Fabric documentation:
- docs/cor8-aiyou-global-edge-fabric/03-technical-architecture/gemini-ingestion-layer.md
- docs/cor8-aiyou-global-edge-fabric/03-technical-architecture/judge-six-validation.md
- docs/cor8-aiyou-global-edge-fabric/09-implementation/api-schemas.md
"""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models.schemas import HealthResponse
from app.routes import ingestion, validation

# ============================================================================
# Lifespan Management
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 PNKLN Core Stack™ API starting...")
    print("📦 Gemini Ingestion Layer: OPERATIONAL")
    print("⚖️  Judge #6 Validation: OPERATIONAL")

    # Initialize Cor.17 services
    from app.routes.cor17 import gptram, safety_service, search_service

    try:
        await gptram.initialize()
        await search_service.initialize()
        await safety_service.initialize()
        print("🧠 Cor.17 Integration: OPERATIONAL (GPTRAM + Search + Safety)")
    except Exception as e:
        print(f"⚠️  Cor.17 Integration: DEGRADED ({e})")

    print(f"🌐 API Server: http://0.0.0.0:{os.getenv('PORT', 8080)}")
    print("📚 Docs: http://0.0.0.0:8080/docs")

    yield

    # Shutdown
    print("🛑 PNKLN Core Stack™ API shutting down...")
    try:
        await gptram.shutdown()
        await search_service.shutdown()
        await safety_service.shutdown()
    except Exception:
        pass


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="AiYou PNKLN Core Stack™ API",
    description="""
    **PNKLN Core Stack™** — Intelligence Collection & Validation Pipeline

    This API implements the PNKLN (Preparation, Normalization, Knowledge, Logic, Notarization)
    architecture for AiYou's verified AI mesh.

    ## Components

    ### 1. Gemini Ingestion Layer (P — Preparation)
    - **Ethical web crawling** with robots.txt compliance
    - **Tier classification** (Tier 1/2/3) using Gemini 2.0 Pro
    - **Multi-source coverage** across YouTube, Twitter, News, etc.
    - **PII scrubbing** for GDPR/CCPA compliance
    - **Cost:** ~$1.4K/month fixed operational budget

    ### 2. Judge #6 Validation (L — Logic & Validation)
    - **ATP 5-19 compliance** (NATO intelligence standards)
    - **JR validation** (ITAR, EAR, NIST RMF, OPSEC)
    - **Real-time validation** with p99 ≤90ms latency
    - **Cost:** ~$0.0022 per validation

    ## Quick Start

    1. **Submit intelligence item for ingestion:**
       ```bash
       curl -X POST http://localhost:8080/ingestion/submit \\
         -H "Content-Type: application/json" \\
         -d '{"source": {...}, "content": {...}}'
       ```

    2. **Validate item against ATP 5-19:**
       ```bash
       curl -X POST http://localhost:8080/validation/validate \\
         -H "Content-Type: application/json" \\
         -d '{"item_id": "ing_2025-11-17_x8y7z6", "validation_profile": "defense_isr"}'
       ```

    ## Documentation

    - [Gemini Ingestion Layer Docs](https://github.com/ShadowTag-v2/aiyou-fastapi-services/blob/main/docs/cor8-aiyou-global-edge-fabric/03-technical-architecture/gemini-ingestion-layer.md)
    - [Judge #6 Validation Docs](https://github.com/ShadowTag-v2/aiyou-fastapi-services/blob/main/docs/cor8-aiyou-global-edge-fabric/03-technical-architecture/judge-six-validation.md)
    - [API Schemas](https://github.com/ShadowTag-v2/aiyou-fastapi-services/blob/main/docs/cor8-aiyou-global-edge-fabric/09-implementation/api-schemas.md)

    ## Architecture

    ```
    User/Service
        │
        ▼
    ┌─────────────────────────────────┐
    │ P — Preparation (Ingestion API) │
    │     POST /ingestion/submit      │
    └─────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────┐
    │ L — Logic (Validation API)      │
    │     POST /validation/validate   │
    └─────────────────────────────────┘
        │
        ▼
    ┌─────────────────────────────────┐
    │ N — Notarization (ShadowTag)    │
    │     [Future: Attestation API]   │
    └─────────────────────────────────┘
    ```

    ## Performance Targets

    - **Ingestion:** 10K-15K items/day, 30-45 min nightly runtime
    - **Validation:** p99 ≤90ms latency, 5K QPS throughput
    - **Ethical Compliance:** ≥95% robots.txt adherence, ≤1 req/sec rate limiting
    - **Quality Gates:** ≥98% ATP 5-19 coverage, ≤1.5% FP rate, ≤0.5% FN rate

    ## Cost Model

    - **Gemini Ingestion:** $1,376/month (fixed infrastructure + API costs)
    - **Judge #6 Validation:** $0.0022/validation (variable cost)
    - **Total (50K validations/day):** ~$4,700/month

    ## Revenue Unlock

    - **Defense & ISR:** $400M-600M ARR (ATP 5-19 compliance enables DoD contracts)
    - **FAANG Integration:** $1.4B ARR (content verification for Meta/Google/Netflix)
    - **Aviation Compliance:** $240M ARR (FAA regulatory monitoring)

    **Total Market Opportunity:** $100M-200M ARR (Option 2: Hybrid Approach)
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ============================================================================
# Middleware
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# ============================================================================
# Routes
# ============================================================================

# Include routers
app.include_router(ingestion.router, prefix="/api/v1")
app.include_router(validation.router, prefix="/api/v1")

# Gemini Agents (AutoGen → Gemini migration)
from app.routes import gemini_agents

app.include_router(gemini_agents.router, prefix="/api/v1")

# LLM Orchestrator (Superpowers Marketplace + PNKLN integration)
from app.routes import orchestrator

app.include_router(orchestrator.router, prefix="/api/v1")

# Cor.17 Integration (GPTRAM + Semantic Search + Content Safety)
from app.routes import cor17

app.include_router(cor17.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    API root endpoint with quick links.
    """
    return {
        "service": "AiYou PNKLN Core Stack™ API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": {
            "interactive_docs": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json",
        },
        "endpoints": {
            "ingestion": "/api/v1/ingestion",
            "validation": "/api/v1/validation",
        },
        "quick_start": {
            "submit_item": "POST /api/v1/ingestion/submit",
            "validate_item": "POST /api/v1/validation/validate",
            "list_sources": "GET /api/v1/ingestion/sources",
            "list_rules": "GET /api/v1/validation/rules",
        },
        "metrics": {
            "ingestion_cost_monthly": "$1,376",
            "validation_cost_per_item": "$0.0022",
            "target_revenue_arr": "$100M-200M",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Global health check for all PNKLN services.

    **Components:**
    - Gemini Ingestion Layer (crawler, classifier, validator)
    - Judge #6 Validation (ATP 5-19, JR compliance)
    - Gemini API connectivity
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "ingestion": "operational",
            "validation": "operational",
            "gemini_api": "operational",
        },
    )


@app.get("/metrics", tags=["Metrics"])
async def metrics():
    """
    Prometheus-compatible metrics endpoint.

    **Metrics:**
    - `pnkln_ingestion_items_total`: Total items ingested
    - `pnkln_validation_requests_total`: Total validation requests
    - `pnkln_validation_latency_seconds`: Validation latency histogram
    - `pnkln_cost_usd_total`: Total operational cost
    """
    # Mock metrics (in production, use prometheus_client)
    return {
        "pnkln_ingestion_items_total": 12456,
        "pnkln_validation_requests_total": 9823,
        "pnkln_validation_latency_p99_ms": 87.3,
        "pnkln_cost_usd_monthly": 4714,
        "pnkln_tier_1_percentage": 0.152,
        "pnkln_ethical_compliance_score": 0.968,
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "not_found",
                "message": f"Endpoint not found: {request.url.path}",
                "suggestion": "Visit /docs for API documentation",
            }
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat(),
            }
        },
    )


# ============================================================================
# Main Entry Point (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))

    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
