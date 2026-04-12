"""
Gemini MCP Bridge for minion
====================================

Bridges minion agents to Gemini CLI MCP tools with JURA cost tracking.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# Import Vertex AI SDK (Vertex-only mode)
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel as VertexModel
except ImportError:
    vertexai = None
    VertexModel = None

# Import JURA for cost tracking
try:
    from ..jura import CostTier, JuraRouter
except ImportError:
    CostTier = None
    JuraRouter = None

logger = logging.getLogger(__name__)


class MCPTool(StrEnum):
    """Available MCP tools."""

    GEMINI_PROMPT = "gemini_prompt"
    GEMINI_SUMMARIZE = "gemini_summarize"
    GEMINI_ANALYZE = "gemini_analyze"
    GEMINI_SANDBOX = "gemini_sandbox"
    GEMINI_EVAL_PLAN = "gemini_eval_plan"
    GEMINI_REVIEW_CODE = "gemini_review_code"
    GEMINI_MODELS = "gemini_models"
    GEMINI_METRICS = "gemini_metrics"


# Map tools to JURA tiers
MCP_TOOL_TIERS = {
    MCPTool.GEMINI_PROMPT: "flash",
    MCPTool.GEMINI_SUMMARIZE: "flash",
    MCPTool.GEMINI_ANALYZE: "pro",
    MCPTool.GEMINI_SANDBOX: "pro",
    MCPTool.GEMINI_EVAL_PLAN: "pro",
    MCPTool.GEMINI_REVIEW_CODE: "pro",
    MCPTool.GEMINI_MODELS: "free",
    MCPTool.GEMINI_METRICS: "free",
}

# Model mapping per tier (Vertex AI)
TIER_MODELS = {
    "free": "gemini-1.5-flash",
    "flash": "gemini-2.5-flash",  # Updated from 2.0
    "pro": "gemini-3-pro-preview",
}


@dataclass
class MCPToolRequest:
    """Request to execute an MCP tool."""

    tool: str
    args: dict[str, Any]
    agent_ids: list[str] | None = None
    cost_tier: str | None = None


@dataclass
class MCPToolResponse:
    """Response from MCP tool execution."""

    success: bool
    result: Any
    tool: str
    tier: str
    model: str
    tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    error: str | None = None
    agent_ids: list[str] | None = None


class GeminiMCPBridge:
    """
    Bridge minion agents to Gemini CLI MCP tools.

    Integrates with JURA for cost-aware routing and agent assignment.
    """

    def __init__(self, project_id: str | None = None, location: str = "us-central1"):
        """
        Initialize bridge with Vertex AI.

        Args:
            project_id: GCP project ID (default: acquired-jet-478701-b3)
            location: GCP region for Vertex AI
        """
        import os

        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "acquired-jet-478701-b3")
        self.location = location
        self._models: dict[str, VertexModel] = {}

        if vertexai and VertexModel:
            try:
                vertexai.init(project=self.project_id, location=self.location)
                logger.info(f"✅ GeminiMCPBridge initialized (Vertex AI: {self.project_id})")
            except Exception as e:
                logger.error(f"❌ Vertex AI initialization failed: {e}")
        else:
            logger.warning("⚠️  Vertex AI not available - vertexai package missing")

        # Initialize JURA router if available
        self.jura_router = JuraRouter() if JuraRouter else None

        # Metrics
        self.total_requests = 0
        self.total_cost = 0.0
        self.tool_stats: dict[str, int] = {}

    def _get_model(self, model_name: str) -> VertexModel:
        """Get or create a Vertex AI model instance."""
        if model_name not in self._models:
            self._models[model_name] = VertexModel(model_name)
        return self._models[model_name]

    async def execute_tool(
        self,
        request: MCPToolRequest,
    ) -> MCPToolResponse:
        """
        Execute an MCP tool with JURA cost tracking.

        Args:
            request: Tool request with args

        Returns:
            Tool response with results and metrics
        """
        start_time = time.time()
        self.total_requests += 1

        try:
            tool = MCPTool(request.tool)
        except ValueError:
            return MCPToolResponse(
                success=False,
                result=None,
                tool=request.tool,
                tier="unknown",
                model="unknown",
                error=f"Unknown tool: {request.tool}",
            )

        # Determine tier and model
        tier = request.cost_tier or MCP_TOOL_TIERS.get(tool, "flash")
        model = TIER_MODELS.get(tier, TIER_MODELS["flash"])

        # Track tool usage
        self.tool_stats[tool.value] = self.tool_stats.get(tool.value, 0) + 1

        try:
            # Execute based on tool type
            result = await self._execute_tool_impl(tool, request.args, model)

            latency_ms = (time.time() - start_time) * 1000
            tokens = result.get("tokens", 0)
            cost = self._estimate_cost(tier, tokens)
            self.total_cost += cost

            return MCPToolResponse(
                success=True,
                result=result.get("text", result),
                tool=tool.value,
                tier=tier,
                model=model,
                tokens=tokens,
                latency_ms=round(latency_ms, 2),
                cost_usd=cost,
                agent_ids=request.agent_ids,
            )

        except Exception as e:
            logger.error(f"❌ Tool execution failed: {e}")
            return MCPToolResponse(
                success=False,
                result=None,
                tool=tool.value,
                tier=tier,
                model=model,
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def _execute_tool_impl(
        self,
        tool: MCPTool,
        args: dict[str, Any],
        model: str,
    ) -> dict[str, Any]:
        """Execute the actual tool logic using Vertex AI."""

        if not VertexModel:
            raise RuntimeError("vertexai not installed - required for Vertex-only mode")

        model_instance = self._get_model(model)

        if tool == MCPTool.GEMINI_PROMPT:
            prompt = args.get("prompt", "")
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return {"text": response.text, "tokens": self._count_tokens(response)}

        elif tool == MCPTool.GEMINI_SUMMARIZE:
            content = args.get("content", "")
            focus = args.get("focus", "key points")
            prompt = f"Summarize this content, focusing on {focus}:\n\n{content}"
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return {"text": response.text, "tokens": self._count_tokens(response)}

        elif tool == MCPTool.GEMINI_ANALYZE:
            content = args.get("content", "")
            analysis_type = args.get("analysis_type", "comprehensive")
            prompt = f"Perform a {analysis_type} analysis:\n\n{content}"
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return {"text": response.text, "tokens": self._count_tokens(response)}

        elif tool == MCPTool.GEMINI_SANDBOX:
            code = args.get("code", "")
            language = args.get("language", "python")
            prompt = (
                f"Execute this {language} code and return the output:\n```{language}\n{code}\n```"
            )
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return {"text": response.text, "tokens": self._count_tokens(response)}

        elif tool == MCPTool.GEMINI_EVAL_PLAN:
            plan = args.get("plan", "")
            context = args.get("context", "")
            prompt = f"Evaluate this implementation plan:\n\nContext: {context}\n\nPlan:\n{plan}"
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return {"text": response.text, "tokens": self._count_tokens(response)}

        elif tool == MCPTool.GEMINI_REVIEW_CODE:
            code = args.get("code", "")
            review_type = args.get("review_type", "full")
            prompt = f"Perform a {review_type} code review:\n\n{code}"
            response = await asyncio.to_thread(model_instance.generate_content, prompt)
            return {"text": response.text, "tokens": self._count_tokens(response)}

        elif tool == MCPTool.GEMINI_MODELS:
            # Return available Vertex AI models (static list)
            return {
                "text": list(TIER_MODELS.values()),
                "tokens": 0,
            }

        elif tool == MCPTool.GEMINI_METRICS:
            return {
                "text": {
                    "total_requests": self.total_requests,
                    "total_cost_usd": f"${self.total_cost:.4f}",
                    "tool_stats": self.tool_stats,
                },
                "tokens": 0,
            }

        else:
            raise ValueError(f"Unhandled tool: {tool}")

    def _count_tokens(self, response) -> int:
        """Extract token count from response."""
        if hasattr(response, "usage_metadata"):
            return response.usage_metadata.total_token_count
        return 0

    def _estimate_cost(self, tier: str, tokens: int) -> float:
        """Estimate cost based on tier and tokens."""
        rates = {
            "free": 0.0,
            "flash": 0.00015 / 1000,  # per token
            "pro": 0.00125 / 1000,
        }
        return tokens * rates.get(tier, 0)

    def get_stats(self) -> dict[str, Any]:
        """Get bridge statistics."""
        return {
            "total_requests": self.total_requests,
            "total_cost_usd": round(self.total_cost, 4),
            "tool_stats": self.tool_stats,
            "available_tools": [t.value for t in MCPTool],
        }


# Singleton instance
_bridge: GeminiMCPBridge | None = None


def get_mcp_bridge() -> GeminiMCPBridge:
    """Get or create the global MCP bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = GeminiMCPBridge()
    return _bridge
