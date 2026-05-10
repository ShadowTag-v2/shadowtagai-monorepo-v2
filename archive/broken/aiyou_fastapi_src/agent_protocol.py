"""
Agent Message Protocol
Multi-agent communication standard for ShadowTag + ShadowTag-v4 ecosystem

Implements:
- Agent-to-Agent (A2A) message passing
- Role-based agent coordination
- Typed message payloads
- Temporal event tracking
"""

import uuid
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AgentRole(StrEnum):
    """Agent roles in the ecosystem"""

    # ShadowTag agents
    NEURAL_HASH = "neural_hash"
    WATERMARK_EMBED = "watermark_embed"
    WATERMARK_VERIFY = "watermark_verify"
    BLOCKCHAIN_RECEIPT = "blockchain_receipt"

    # ShadowTag-v4 agents
    CONTENT_INGEST = "content_ingest"
    NEURAL_RANK = "neural_rank"
    FEED_ORCHESTRATOR = "feed_orchestrator"
    CREATOR_TOOLS = "creator_tools"

    # Shared infrastructure
    DOCUMENT_OCR = "document_ocr"
    EMBEDDING_SERVICE = "embedding_service"
    STORAGE_SERVICE = "storage_service"
    ANALYTICS = "analytics"

    # Coordination
    ORCHESTRATOR = "orchestrator"
    MONITOR = "monitor"


class MessageType(StrEnum):
    """Message types for agent communication"""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    STATUS = "status"


class Priority(StrEnum):
    """Message priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AgentMessage(BaseModel):
    """
    Standard message format for agent-to-agent communication

    Example:
        message = AgentMessage(
            message_type=MessageType.REQUEST,
            from_agent=AgentRole.CONTENT_INGEST,
            to_agent=AgentRole.NEURAL_HASH,
            data={"media_url": "https://example.com/video.mp4"},
            correlation_id="upload_session_123"
        )
    """

    # Message metadata
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique message identifier"
    )
    message_type: MessageType = Field(..., description="Type of message")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Message creation timestamp"
    )

    # Agent routing
    from_agent: AgentRole = Field(..., description="Sending agent role")
    to_agent: AgentRole = Field(..., description="Receiving agent role")

    # Message payload
    data: dict[str, Any] = Field(default_factory=dict, description="Message payload data")

    # Coordination
    correlation_id: str | None = Field(
        None, description="ID linking related messages (e.g., request/response)"
    )
    parent_message_id: str | None = Field(
        None, description="Parent message ID for chained workflows"
    )
    priority: Priority = Field(default=Priority.NORMAL, description="Message priority")

    # Metadata
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional context metadata"
    )

    # Error handling
    error: str | None = Field(None, description="Error message if message_type is ERROR")

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_abc123",
                "message_type": "request",
                "timestamp": "2025-11-29T10:00:00Z",
                "from_agent": "content_ingest",
                "to_agent": "neural_hash",
                "data": {
                    "media_url": "https://example.com/video.mp4",
                    "media_type": "video/mp4",
                    "uploaded_by": "user_123",
                },
                "correlation_id": "upload_session_456",
                "priority": "normal",
                "metadata": {"session_id": "web_session_789", "client_ip": "192.168.1.1"},
            }
        }


class AgentState(BaseModel):
    """Agent state tracking"""

    agent_role: AgentRole
    status: str = Field(..., description="Agent status: idle, processing, error")
    current_task: str | None = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowStep(BaseModel):
    """Single step in a multi-agent workflow"""

    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_role: AgentRole
    action: str = Field(..., description="Action to perform")
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] | None = None
    status: str = "pending"  # pending, processing, completed, failed
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


class AgentWorkflow(BaseModel):
    """
    Multi-agent workflow definition

    Example - ShadowTag Upload Workflow:
        workflow = AgentWorkflow(
            workflow_id="shadowtag_upload",
            steps=[
                WorkflowStep(agent_role=DOCUMENT_OCR, action="extract_text"),
                WorkflowStep(agent_role=NEURAL_HASH, action="generate_fingerprint"),
                WorkflowStep(agent_role=WATERMARK_EMBED, action="embed_watermark"),
                WorkflowStep(agent_role=BLOCKCHAIN_RECEIPT, action="record_blockchain"),
            ]
        )
    """

    workflow_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique workflow identifier"
    )
    name: str = Field(..., description="Workflow name")
    description: str | None = None
    steps: list[WorkflowStep] = Field(default_factory=list, description="Ordered workflow steps")
    current_step_index: int = 0
    status: str = "pending"  # pending, running, completed, failed
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    def get_current_step(self) -> WorkflowStep | None:
        """Get the current workflow step"""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance_step(self) -> bool:
        """Advance to next step, return True if more steps remain"""
        self.current_step_index += 1
        return self.current_step_index < len(self.steps)

    def mark_step_completed(self, output_data: dict[str, Any]) -> None:
        """Mark current step as completed"""
        step = self.get_current_step()
        if step:
            step.status = "completed"
            step.output_data = output_data
            step.completed_at = datetime.utcnow()

    def mark_step_failed(self, error: str) -> None:
        """Mark current step as failed"""
        step = self.get_current_step()
        if step:
            step.status = "failed"
            step.error = error
            step.completed_at = datetime.utcnow()
        self.status = "failed"


class MediaAsset(BaseModel):
    """Media asset data structure"""

    asset_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    asset_type: str = Field(..., description="image, video, audio, document")
    url: str | None = None
    local_path: str | None = None

    # Content
    title: str | None = None
    description: str | None = None
    extracted_text: str | None = None

    # ShadowTag fields
    neural_fingerprint: dict[str, Any] | None = None
    watermark_embedded: bool = False
    watermark_data: dict[str, Any] | None = None
    blockchain_receipt: str | None = None

    # ShadowTag-v4 fields
    ai_cognition_score: float | None = None
    engagement_score: int | None = None
    ranking_tier: str | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    creator_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Pre-defined Workflows
# ============================================================================


def create_shadowtag_upload_workflow(asset: MediaAsset) -> AgentWorkflow:
    """
    Create ShadowTag upload workflow

    Flow: OCR → Neural Hash → Watermark → Blockchain
    """
    return AgentWorkflow(
        name="ShadowTag Upload",
        description="Process and authenticate uploaded media",
        steps=[
            WorkflowStep(
                agent_role=AgentRole.DOCUMENT_OCR,
                action="extract_text",
                input_data={"asset_id": asset.asset_id, "url": asset.url},
            ),
            WorkflowStep(
                agent_role=AgentRole.NEURAL_HASH,
                action="generate_fingerprint",
                input_data={"asset_id": asset.asset_id},
            ),
            WorkflowStep(
                agent_role=AgentRole.WATERMARK_EMBED,
                action="embed_watermark",
                input_data={"asset_id": asset.asset_id},
            ),
            WorkflowStep(
                agent_role=AgentRole.BLOCKCHAIN_RECEIPT,
                action="record_blockchain",
                input_data={"asset_id": asset.asset_id},
            ),
        ],
        metadata={"asset_id": asset.asset_id},
    )


def create_ShadowTag-v2_content_workflow(content: dict[str, Any]) -> AgentWorkflow:
    """
    Create ShadowTag-v4 content ingestion workflow

    Flow: Ingest → Embed → Rank → Feed
    """
    content_id = content.get("id", str(uuid.uuid4()))

    return AgentWorkflow(
        name="ShadowTag-v4 Content Ingestion",
        description="Ingest and rank content for AI-cognition feed",
        steps=[
            WorkflowStep(
                agent_role=AgentRole.CONTENT_INGEST, action="ingest_content", input_data=content
            ),
            WorkflowStep(
                agent_role=AgentRole.EMBEDDING_SERVICE,
                action="generate_embeddings",
                input_data={"content_id": content_id},
            ),
            WorkflowStep(
                agent_role=AgentRole.NEURAL_RANK,
                action="compute_ai_cognition_score",
                input_data={"content_id": content_id},
            ),
            WorkflowStep(
                agent_role=AgentRole.FEED_ORCHESTRATOR,
                action="add_to_feed",
                input_data={"content_id": content_id},
            ),
        ],
        metadata={"content_id": content_id},
    )


# ============================================================================
# Message Utilities
# ============================================================================


def create_request_message(
    from_agent: AgentRole,
    to_agent: AgentRole,
    data: dict[str, Any],
    correlation_id: str | None = None,
    priority: Priority = Priority.NORMAL,
) -> AgentMessage:
    """Helper to create a request message"""
    return AgentMessage(
        message_type=MessageType.REQUEST,
        from_agent=from_agent,
        to_agent=to_agent,
        data=data,
        correlation_id=correlation_id,
        priority=priority,
    )


def create_response_message(
    request_message: AgentMessage, response_data: dict[str, Any]
) -> AgentMessage:
    """Helper to create a response to a request message"""
    return AgentMessage(
        message_type=MessageType.RESPONSE,
        from_agent=request_message.to_agent,
        to_agent=request_message.from_agent,
        data=response_data,
        correlation_id=request_message.correlation_id,
        parent_message_id=request_message.message_id,
    )


def create_error_message(request_message: AgentMessage, error: str) -> AgentMessage:
    """Helper to create an error response"""
    return AgentMessage(
        message_type=MessageType.ERROR,
        from_agent=request_message.to_agent,
        to_agent=request_message.from_agent,
        data={},
        error=error,
        correlation_id=request_message.correlation_id,
        parent_message_id=request_message.message_id,
    )
