"""Pydantic models for Context Window Management
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AnalysisRole(StrEnum):
    """Role of the analysis session"""

    ARCHITECTURE_REVIEW = "architecture_review"
    CODE_ANALYSIS = "code_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    SECURITY_AUDIT = "security_audit"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    COST_OPTIMIZATION = "cost_optimization"
    INTEGRATION_TESTING = "integration_testing"
    GENERAL = "general"


class SessionStatus(StrEnum):
    """Status of an analysis session"""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


class AnalysisSession(BaseModel):
    """Represents a single AI analysis session

    Tracks metadata for a conversation with an AI assistant
    about a specific analysis topic (e.g., Gemini Ingestion Layer review)
    """

    session_id: str = Field(..., description="Unique session identifier")
    issue_title: str = Field(..., description="Title of the analysis issue")
    role: AnalysisRole = Field(..., description="Role/type of analysis")
    goal: str = Field(..., description="Primary goal of the session")
    constraints: str | None = Field(None, description="Constraints or limitations")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    status: SessionStatus = Field(default=SessionStatus.ACTIVE)

    # AI Model information
    model_name: str = Field(default="gemini-2.0-pro", description="AI model used")
    confidence_threshold: float = Field(
        default=0.60, ge=0.0, le=1.0, description="Minimum confidence threshold",
    )

    # Token usage tracking
    total_tokens: int = Field(default=0, description="Total tokens consumed")
    context_window_size: int = Field(default=2_000_000, description="Model context window size")

    # Related sessions
    parent_session_id: str | None = Field(None, description="Parent session for continuation")
    related_sessions: list[str] = Field(default_factory=list, description="Related session IDs")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "gemini-ingestion-2025-11-15-001",
                "issue_title": "Gemini Ingestion Layer Analysis",
                "role": "architecture_review",
                "goal": "Comprehensive pre-production analysis of ingestion pipeline",
                "constraints": "Pre-prod environment, no production telemetry available",
                "model_name": "gemini-2.0-pro",
                "confidence_threshold": 0.60,
                "total_tokens": 45000,
                "context_window_size": 2_000_000,
                "status": "active",
            },
        }


class ChatSummary(BaseModel):
    """Summary of a completed chat session

    Captures key outcomes, decisions, and insights from an AI analysis
    """

    session_id: str = Field(..., description="Reference to parent session")
    summary: str = Field(..., description="Executive summary of the chat")
    key_decisions: list[str] = Field(default_factory=list, description="Key decisions made")
    findings: list[str] = Field(default_factory=list, description="Important findings")
    recommendations: list[str] = Field(
        default_factory=list, description="Action items and recommendations",
    )
    risks_identified: list[str] = Field(
        default_factory=list, description="Risks or blockers identified",
    )

    # Metadata
    related_threads: list[str] = Field(
        default_factory=list, description="Related discussion threads or URLs",
    )
    tags: list[str] = Field(default_factory=list, description="Categorization tags")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "gemini-ingestion-2025-11-15-001",
                "summary": "Completed comprehensive analysis of Gemini Ingestion Layer. System is architecturally sound with 3 critical risks identified around source diversity and cost scaling.",
                "key_decisions": [
                    "Approved 60% confidence threshold for pre-prod",
                    "Recommended adding 2 additional sources before production launch",
                    "Flagged cost model sensitivity to Gemini API pricing changes",
                ],
                "findings": [
                    "Ethical compliance framework is robust (Green status)",
                    "Tier classification accuracy needs validation with test data",
                    "AM briefing format well-designed for Slack/email delivery",
                ],
                "recommendations": [
                    "Implement cost alerting for >$100/month spend",
                    "Add LinkedIn and academic DB sources for diversity",
                    "Set up A/B testing for briefing engagement metrics",
                ],
                "risks_identified": [
                    "Twitter API dependency (20% of items) - single point of failure",
                    "No backfill strategy if CronJob fails",
                    "GKE pod eviction could truncate ingestion run",
                ],
                "related_threads": [
                    "https://github.com/org/repo/issues/123",
                    "https://pnkln.ai/docs/ingestion-layer",
                ],
                "tags": ["ingestion", "gemini-2.0-pro", "pre-production", "architecture"],
            },
        }


class ContextIndex(BaseModel):
    """Master index of all analysis sessions

    Provides a searchable, chronological record of AI analysis activities
    """

    index_id: str = Field(default="context-index-main", description="Index identifier")
    name: str = Field(default="AI Analysis Context Index", description="Human-readable name")
    description: str | None = Field(
        "Central repository of AI analysis sessions for PNKLN Core Stack",
        description="Index description",
    )

    sessions: list[AnalysisSession] = Field(
        default_factory=list, description="All tracked sessions",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Statistics
    total_sessions: int = Field(default=0, description="Total number of sessions")
    active_sessions: int = Field(default=0, description="Currently active sessions")
    total_tokens_consumed: int = Field(default=0, description="Total tokens across all sessions")

    class Config:
        json_schema_extra = {
            "example": {
                "index_id": "context-index-main",
                "name": "PNKLN AI Analysis Context Index",
                "total_sessions": 42,
                "active_sessions": 3,
                "total_tokens_consumed": 1_250_000,
            },
        }


class CreateSessionRequest(BaseModel):
    """Request to create a new analysis session"""

    issue_title: str
    role: AnalysisRole
    goal: str
    constraints: str | None = None
    model_name: str = "gemini-2.0-pro"
    confidence_threshold: float = 0.60
    parent_session_id: str | None = None


class UpdateSessionRequest(BaseModel):
    """Request to update an existing session"""

    status: SessionStatus | None = None
    total_tokens: int | None = None
    completed_at: datetime | None = None


class CreateSummaryRequest(BaseModel):
    """Request to create a chat summary"""

    session_id: str
    summary: str
    key_decisions: list[str] = []
    findings: list[str] = []
    recommendations: list[str] = []
    risks_identified: list[str] = []
    related_threads: list[str] = []
    tags: list[str] = []
