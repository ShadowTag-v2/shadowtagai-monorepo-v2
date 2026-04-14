"""Governance API Routes.

Provides endpoints for governance trace viewing and decision auditing.
FedRAMP compliant with OMB M-25-22 audit trail requirements.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from ..services.governance.signed_urls import (
    generate_trace_url,
    get_signed_url_generator,
)

router = APIRouter(prefix="/governance", tags=["governance"])

# Templates directory
templates = Jinja2Templates(directory="templates")


class TraceInput(BaseModel):
    """Input data for a governance decision trace."""

    file: str | None = None
    user_tier: str | None = None
    content_id: str | None = None
    request_type: str | None = None
    metadata: dict | None = Field(default_factory=dict)


class TraceRecord(BaseModel):
    """Complete governance trace record."""

    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp_utc: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    judge_version: str = "Judge #6 (v1.0.4)"
    inputs: TraceInput
    logic_trace: list[str] = Field(default_factory=list)
    final_verdict: str = "PENDING"


class TraceUploadRequest(BaseModel):
    """Request to upload a new governance trace."""

    inputs: TraceInput
    logic_trace: list[str]
    final_verdict: str


class TraceUploadResponse(BaseModel):
    """Response after uploading a trace."""

    decision_id: str
    trace_url: str
    viewer_url: str
    expires_in_minutes: int = 15


@router.get("/trace/{decision_id}", response_class=HTMLResponse)
async def view_trace(request: Request, decision_id: str):
    """Render the governance trace viewer.

    Returns an HTML page that fetches and displays the decision trace
    with animated replay of the logic steps.
    """
    try:
        trace_url = generate_trace_url(decision_id)
    except Exception:
        # If we can't generate a signed URL, pass empty string
        # The template will fall back to mock data for preview
        trace_url = ""

    return templates.TemplateResponse(
        "governance/trace.html",
        {
            "request": request,
            "decision_id": decision_id,
            "trace_url": trace_url,
        },
    )


@router.post("/trace", response_model=TraceUploadResponse)
async def upload_trace(trace: TraceUploadRequest):
    """Upload a new governance decision trace.

    Stores the trace in GCS and returns URLs for accessing it.
    Required for High-Impact AI audit compliance per OMB M-25-22.
    """
    decision_id = str(uuid4())

    # Build complete trace record
    trace_record = {
        "decision_id": decision_id,
        "timestamp_utc": datetime.utcnow().isoformat(),
        "judge_version": "Judge #6 (v1.0.4)",
        "inputs": trace.inputs.model_dump(),
        "logic_trace": trace.logic_trace,
        "final_verdict": trace.final_verdict,
    }

    try:
        generator = get_signed_url_generator()
        generator.upload_trace(decision_id, trace_record)
        trace_url = generator.generate_trace_url(decision_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload trace: {e!s}")

    # Build viewer URL (relative)
    viewer_url = f"/governance/trace/{decision_id}"

    return TraceUploadResponse(
        decision_id=decision_id,
        trace_url=trace_url,
        viewer_url=viewer_url,
    )


@router.get("/trace/{decision_id}/json")
async def get_trace_url(decision_id: str, expiration_minutes: int = 15):
    """Get a signed URL for the trace JSON file.

    Returns a time-limited URL that can be used to fetch the raw trace data.
    """
    try:
        trace_url = generate_trace_url(decision_id, expiration_minutes)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Trace not found or expired: {e!s}")

    return {
        "decision_id": decision_id,
        "trace_url": trace_url,
        "expires_in_minutes": expiration_minutes,
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for governance service."""
    return {
        "status": "healthy",
        "service": "governance",
        "fedramp_compliant": True,
        "judge_version": "Judge #6 (v1.0.4)",
    }
