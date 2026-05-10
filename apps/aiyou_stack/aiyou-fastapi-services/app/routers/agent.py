"""Claude Agent SDK Router"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.claude_agent import ClaudeAgentService

router = APIRouter()
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    """Request model for agent queries"""

    prompt: str
    system_prompt: str | None = None
    use_claude_code_preset: bool = False
    max_tokens: int | None = None
    temperature: float | None = 1.0


class QueryResponse(BaseModel):
    """Response model for agent queries"""

    response: str
    metadata: dict[str, Any] | None = None


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Query the Claude Agent

    - **prompt**: The query or task to send to the agent
    - **system_prompt**: Optional custom system prompt
    - **use_claude_code_preset**: Use Claude Code preset system prompt
    - **max_tokens**: Maximum tokens in response
    - **temperature**: Sampling temperature (0-1)
    """
    try:
        service = ClaudeAgentService()
        response = await service.query(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            use_claude_code_preset=request.use_claude_code_preset,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        return QueryResponse(response=response["content"], metadata=response.get("metadata"))

    except Exception as e:
        logger.error(f"Error querying agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/models")
async def list_models():
    """List available Claude models"""
    return {
        "models": [
            {
                "id": "claude-sonnet-4-5-20250929",
                "name": "Claude Sonnet 4.5",
                "description": "Most recent frontier Claude model",
            },
            {
                "id": "claude-opus-4-20250514",
                "name": "Claude Opus 4",
                "description": "Most intelligent model",
            },
            {
                "id": "claude-3-5-sonnet-20241022",
                "name": "Claude 3.5 Sonnet",
                "description": "Fast and capable",
            },
        ],
    }
