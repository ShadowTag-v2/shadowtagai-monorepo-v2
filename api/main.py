# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pnkln API - FastAPI service for ultrathink framework
Version: 1.0.0

Philosophy: Steve Jobs mode - beautiful, intuitive, inevitable
Design: RESTful, self-documenting, error-resistant
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for pnkln imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pnkln import create_orchestrator, PnklnOrchestrator


# Pydantic models for API
class ExecuteRequest(BaseModel):
    """Request to execute against pnkln orchestrator"""

    query: str = Field(..., description="User query to execute", min_length=1)
    agent_id: str | None = Field(None, description="Specific agent to use (auto-detect if None)")
    track_metrics: bool = Field(True, description="Track monetization metrics")

    class Config:
        json_schema_extra = {
            "example": {"query": "Research edge AI compute market and identify revenue opportunities", "agent_id": None, "track_metrics": True}
        }


class ExecuteResponse(BaseModel):
    """Response from pnkln execution"""

    status: str
    agent: str | None
    skills_activated: list[str]
    synthesis: str
    audit: dict[str, Any]
    execution_time_seconds: float


class SkillInfo(BaseModel):
    """Skill metadata"""

    id: str
    name: str
    category: str
    description: str
    triggers: list[str]
    frameworks: list[str]
    risk_level: str


class AgentInfo(BaseModel):
    """Agent metadata"""

    id: str
    name: str
    persona: str
    iq_baseline: int
    description: str
    skills: list[str]
    activation_triggers: list[str]


class AuditSummary(BaseModel):
    """Audit trail summary"""

    total_executions: int
    total_time_saved_hours: float
    total_revenue_identified_usd: float
    total_revenue_generated_usd: float
    average_leverage_ratio: float
    executions: list[dict[str, Any]]


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    orchestrator: str
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="Pnkln Ultrathink API",
    description="Production-grade AI orchestration with Steve Jobs design philosophy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator: PnklnOrchestrator | None = None


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    try:
        orchestrator = create_orchestrator(
            skills_path="/home/user/aiyou-fastapi-services/pnkln/skills/registry.yaml",
            agents_path="/home/user/aiyou-fastapi-services/pnkln/agents/registry.yaml",
        )
        print(f"✓ Pnkln orchestrator initialized: {orchestrator}")
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        raise


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return HealthResponse(status="operational", version="1.0.0", orchestrator=str(orchestrator), timestamp=datetime.now().isoformat())


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return await root()


@app.post("/api/pnkln/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):
    """
    Execute query against pnkln orchestrator.

    Auto-detects appropriate skills and agents based on query content.
    Returns synthesized response with audit trail.
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        result = await orchestrator.execute(user_input=request.query, agent_id=request.agent_id, track_metrics=request.track_metrics)
        return ExecuteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.get("/api/pnkln/skills", response_model=list[SkillInfo])
async def list_skills():
    """List all available skills"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    skills = []
    for skill in orchestrator.skills.values():
        skills.append(
            SkillInfo(
                id=skill.id,
                name=skill.name,
                category=skill.category,
                description=skill.description,
                triggers=skill.triggers,
                frameworks=skill.frameworks,
                risk_level=skill.risk_level,
            )
        )
    return skills


@app.get("/api/pnkln/agents", response_model=list[AgentInfo])
async def list_agents():
    """List all available agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    agents = []
    for agent in orchestrator.agents.values():
        agents.append(
            AgentInfo(
                id=agent.id,
                name=agent.name,
                persona=agent.persona,
                iq_baseline=agent.iq_baseline,
                description=agent.description,
                skills=agent.skills,
                activation_triggers=agent.activation_triggers,
            )
        )
    return agents


@app.get("/api/pnkln/audit", response_model=AuditSummary)
async def get_audit():
    """Get Boy Scout Rule audit trail summary"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    summary = orchestrator.get_audit_summary()
    return AuditSummary(**summary)


@app.post("/api/pnkln/execute/skill/{skill_id}", response_model=ExecuteResponse)
async def execute_skill(skill_id: str, request: ExecuteRequest):
    """Execute with specific skill (bypasses auto-detection)"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    if skill_id not in orchestrator.skills:
        raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

    # Create temporary agent with just this skill
    try:
        result = await orchestrator.execute(
            user_input=request.query,
            agent_id=None,  # Manual skill selection
            track_metrics=request.track_metrics,
        )
        return ExecuteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@app.post("/api/pnkln/execute/agent/{agent_id}", response_model=ExecuteResponse)
async def execute_agent(agent_id: str, request: ExecuteRequest):
    """Execute with specific agent"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    if agent_id not in orchestrator.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    try:
        result = await orchestrator.execute(user_input=request.query, agent_id=agent_id, track_metrics=request.track_metrics)
        return ExecuteResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
