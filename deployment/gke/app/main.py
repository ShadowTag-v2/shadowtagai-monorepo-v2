# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Plan Mode Service API
FastAPI service for generating plans using Plan Mode Style Guide v1.0
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Plan Mode Service", description="Generate execution-ready plans using Plan Mode Style Guide v1.0", version="1.0.0")

# Load plan mode template
TEMPLATE_PATH = os.environ.get("PLAN_MODE_TEMPLATE_PATH", "PLAN_MODE_TEMPLATE.md")
try:
    with open(TEMPLATE_PATH) as f:
        PLAN_MODE_TEMPLATE = f.read()
    logger.info(f"Plan Mode Template loaded from {TEMPLATE_PATH}")
except Exception as e:
    logger.error(f"Failed to load template: {e}")
    PLAN_MODE_TEMPLATE = ""


class PlanRequest(BaseModel):
    """Request model for plan generation"""

    task_description: str
    model: str | None = "claude-sonnet-4-5-20250929"
    max_tokens: int | None = 2048


class PlanResponse(BaseModel):
    """Response model for generated plan"""

    plan: str
    model: str
    tokens_used: int


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "plan-mode-service"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="API key not configured")
    if not PLAN_MODE_TEMPLATE:
        raise HTTPException(status_code=503, detail="Template not loaded")
    return {"status": "ready"}


@app.post("/generate-plan", response_model=PlanResponse)
async def generate_plan(request: PlanRequest):
    """
    Generate a plan using Claude with Plan Mode Style Guide

    Args:
        request: PlanRequest containing task description and options

    Returns:
        PlanResponse with generated plan
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    try:
        client = Anthropic(api_key=api_key)

        system_prompt = f"""
You are a planning assistant that strictly follows the Plan Mode Style Guide v1.0.

Rules:
- Sacrifice grammar for concision
- One action per line
- Use imperative verbs only
- Keep lines ≤60 chars
- End with 'Unresolved Qs:' section
- Use 'Impl:' if >1 module affected
- No prose explanations

Template:
{PLAN_MODE_TEMPLATE}
"""

        message = client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Generate a plan for: {request.task_description}"}],
        )

        plan_text = message.content[0].text
        tokens_used = message.usage.input_tokens + message.usage.output_tokens

        logger.info(f"Plan generated successfully. Tokens used: {tokens_used}")

        return PlanResponse(plan=plan_text, model=request.model, tokens_used=tokens_used)

    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Plan Mode Service",
        "version": "1.0.0",
        "endpoints": {"health": "/health", "ready": "/ready", "generate_plan": "/generate-plan (POST)"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
