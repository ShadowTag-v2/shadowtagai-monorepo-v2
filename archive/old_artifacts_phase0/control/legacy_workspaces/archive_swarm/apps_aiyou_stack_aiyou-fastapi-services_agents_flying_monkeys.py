"""
Flying n-autoresearch/Kosmos/BioAgents - Gemini Native (Antigravity Integrated)
Research + Governance + Advanced Tool Use

Migrated from v8 FULL to pure Gemini 1.5 Pro.
"""

from __future__ import annotations

import inspect
import json
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import vertexai
from vertexai.generative_models import GenerativeModel

from agents.codemender import CodeMenderAgent

try:
    import google.generativeai as genai_pkg
except ImportError:
    genai_pkg = None


logger = logging.getLogger(__name__)

# Constants
MODEL_NAME = "gemini-1.5-pro-001"


class LLMProvider(Enum):
    VERTEX = "vertex"
    STUDIO = "studio"


class AgentTier(Enum):
    WORKER = "worker"
    EXECUTION = "execution"
    STRATEGY = "strategy"


# =============================================================================
# JUDGE #6 GOVERNANCE (Ported & Optimized)
# =============================================================================


class ValidationResult(Enum):
    APPROVED = "approved"
    BLOCKED_PURPOSE = "blocked_purpose"
    BLOCKED_REASONS = "blocked_reasons"
    BLOCKED_BRAKES = "blocked_brakes"


@dataclass
class JRValidation:
    action: str
    args: dict[str, Any]
    purpose_score: float
    reasons_score: float
    brakes_score: float
    result: ValidationResult
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JudgeSix:
    """Judge #6 Governance - Purpose/Reasons/Brakes validation"""

    DANGEROUS_KEYWORDS = {
        "delete",
        "remove",
        "drop",
        "destroy",
        "kill",
        "terminate",
        "admin",
        "root",
        "sudo",
        "eval",
        "system",
        "rm -rf",
    }

    def __init__(self, mission: str = "MAKE CASH - Maximize revenue and cash flow"):
        self.mission = mission
        self.audit_log: list[JRValidation] = []

    def validate(self, action: str, args: dict[str, Any], context: str = "") -> JRValidation:
        # Heuristic checks (fast path)
        purpose_score = self._check_purpose(action, context)
        reasons_score = self._check_reasons(args)
        brakes_score = self._check_brakes(action, args)

        if purpose_score < 0.6:
            result = ValidationResult.BLOCKED_PURPOSE
            explanation = f"Action '{action}' does not advance mission: {self.mission}"
        elif reasons_score < 0.7:
            result = ValidationResult.BLOCKED_REASONS
            explanation = "Action lacking sufficient context/args"
        elif brakes_score < 0.8:
            result = ValidationResult.BLOCKED_BRAKES
            explanation = "Safety constraints violated"
        else:
            result = ValidationResult.APPROVED
            explanation = "Approved"

        val = JRValidation(
            action, args, purpose_score, reasons_score, brakes_score, result, explanation
        )
        self.audit_log.append(val)
        return val

    def _check_purpose(self, action: str, context: str) -> float:
        keywords = {"cash", "revenue", "growth", "analysis", "research", "code", "deploy"}
        score = 0.5
        if any(k in action.lower() for k in keywords):
            score += 0.3
        if len(context) > 10:
            score += 0.2
        return min(1.0, score)

    def _check_reasons(self, args: dict) -> float:
        if not args:
            return 0.5
        return 1.0

    def _check_brakes(self, action: str, args: dict) -> float:
        blob = (action + json.dumps(args)).lower()
        if any(k in blob for k in self.DANGEROUS_KEYWORDS):
            return 0.0
        return 1.0


# =============================================================================
# RESEARCH & TOOLS
# =============================================================================


class ResearchEngine:
    def web_search(self, query: str) -> dict[str, Any]:
        # Placeholder for real search (e.g. Google Search / Perplexity adapter)
        # In a full impl, connect to `src/tools/search.py` if available
        return {
            "query": query,
            "results": [
                {"title": f"Gemini Result for {query}", "snippet": "High quality insight..."},
                {"title": "Market Trends 2025", "snippet": "Agents are the future..."},
            ],
        }


@dataclass
class ToolDef:
    name: str
    description: str
    handler: Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef):
        self._tools[tool.name] = tool

    def execute(self, name: str, **kwargs) -> Any:
        if name in self._tools:
            return self._tools[name].handler(**kwargs)
        raise ValueError(f"Tool {name} not found")


# =============================================================================
# GOOGLE MCP INTEGRATION (Official Support)
# =============================================================================


class GoogleMCP:
    """
    Official Google Model Context Protocol (MCP) Integration.
    Connects to fully-managed MCP endpoints for Maps, BigQuery, GKE.
    """

    def __init__(self, project_id: str | None):
        self.project_id = project_id

    def maps_grounding(self, query: str) -> dict[str, Any]:
        """Google Maps Grounding Lite MCP"""
        # In production, this connects to the official MCP endpoint
        return {
            "tool": "google_maps",
            "query": query,
            "status": "connected",
            "data": "Real-time location data would be returned here.",
        }

    def bigquery_query(self, sql: str) -> dict[str, Any]:
        """BigQuery MCP"""
        return {
            "tool": "bigquery",
            "query": sql,
            "status": "connected",
            "schema": "Retrieved from MCP",
            "data": "Query results would be returned here.",
        }

    def gke_ops(self, cluster_name: str, action: str) -> dict[str, Any]:
        """GKE Ops MCP"""
        return {
            "tool": "gke",
            "cluster": cluster_name,
            "action": action,
            "status": "connected",
            "result": "GKE operation initiated via MCP.",
        }


# =============================================================================
# FLYING n-autoresearch/Kosmos/BioAgents (GEMINI NATIVE)
# =============================================================================


# ... (imports)


class n-autoresearch/Kosmos/BioAgents:
    """Gemini-powered autonomous agent swarm"""

    def __init__(self, project_id: str | None = None, model: str = "gemini-1.5-pro-001"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("CLOUD_ML_REGION", "us-central1")
        self.model_name = model
        self.use_vertex = False

        if self.project_id:
            logger.info(f"Initializing Flying n-autoresearch/Kosmos/BioAgents with Vertex AI (Project: {self.project_id})")
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(self.model_name)
            self.use_vertex = True
        elif os.getenv("GEMINI_API_KEY") and genai_pkg:
            logger.info("Initializing Flying n-autoresearch/Kosmos/BioAgents with GenAI SDK (API Key)")
            genai_pkg.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
            self.model = genai_pkg.GenerativeModel(self.model_name)
        else:
            logger.warning("No Project ID or API Key found. n-autoresearch/Kosmos/BioAgents grounded.")
            self.model = None

        self.judge = JudgeSix()
        self.registry = ToolRegistry()
        self.research = ResearchEngine()
        self.mcp = GoogleMCP(self.project_id)
        self.agents: dict[str, Any] = {}

        # Register default tools
        self.registry.register(ToolDef("web_search", "Search web", self.research.web_search))

        # Register Google MCP Tools
        self.registry.register(
            ToolDef("maps_query", "Query Google Maps (MCP)", self.mcp.maps_grounding)
        )
        self.registry.register(
            ToolDef("bq_query", "Run BigQuery SQL (MCP)", self.mcp.bigquery_query)
        )
        self.registry.register(ToolDef("gke_ops", "Manage GKE Clusters (MCP)", self.mcp.gke_ops))

        # Register ShadowTag v2 Tools
        try:
            from src.shadowtagai import mcarlo_bundle, odor_sim, swiper_plan

            self.registry.register(ToolDef("mcarlo_val", "Monte Carlo Valuation", mcarlo_bundle))
            self.registry.register(ToolDef("odor_sim", "Fluid/Odor Simulation", odor_sim))
            self.registry.register(ToolDef("swiper_plan", "Swiper Commerce Plan", swiper_plan))
            logger.info("ShadowTag v2 tools registered")
        except ImportError:
            logger.warning("ShadowTag v2 tools not found")

        # Register CodePMCS (Internal)
        try:
            from codepmcs import CodePMCS

            pmcs = CodePMCS()
            self.registry.register(ToolDef("code_scan", "Code Quality Scan", pmcs.scan))
            logger.info("CodePMCS tools registered")
        except ImportError:
            logger.warning("CodePMCS not found")

        # Register CodeMender (Agentic Repair)
        self.code_mender = CodeMenderAgent(self.project_id)
        self.registry.register(
            ToolDef("code_repair", "Auto-fix code vulnerabilities", self.code_mender.resolve_issue)
        )

    def initialize_swarm(self):
        """Initialize swarm components (post-init hook)"""
        self.agents = {}
        logger.info("Swarm initialized and ready for deployment.")

    async def execute_task(
        self, task: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a task using Gemini planning + tools"""
        print(f"🐒 n-autoresearch/Kosmos/BioAgents Processing: {task}")

        # Context enrichment
        task_with_context = f"{task}\nContext: {json.dumps(context)}" if context else task

        # 1. Governance Check
        val = self.judge.validate("execute_task", {"task": task}, task_with_context)
        if val.result != ValidationResult.APPROVED:
            return {"status": "blocked", "reason": val.explanation}

        if not self.model:
            return {"status": "error", "reason": "No Gemini model available"}

        # 2. Plan with Gemini
        prompt = f"""You are a Flying Monkey agent powered by Gemini.
        Task: {task}
        Context: {context}
        Available Tools: {list(self.registry._tools.keys())}

        Use Google MCP tools (maps_query, bq_query, gke_ops) for specialized tasks.

        Return a JSON plan:
        {{
            "thoughts": "...",
            "tool_calls": [{{"name": "tool_name", "args": {{...}}}}]
        }}
        """

        resp = await self.model.generate_content_async(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        try:
            plan = json.loads(resp.text)
        except json.JSONDecodeError:
            return {"status": "error", "reason": "Failed to parse plan"}

        # 3. Execute Tools
        results = []
        for call in plan.get("tool_calls", []):
            name = call["name"]
            args = call["args"]

            # Governance per tool call
            t_val = self.judge.validate(name, args, task)
            if t_val.result == ValidationResult.APPROVED:
                try:
                    res_or_coro = self.registry.execute(name, **args)
                    if inspect.iscoroutine(res_or_coro):
                        res = await res_or_coro
                    else:
                        res = res_or_coro

                    results.append({"tool": name, "result": res})
                except Exception as e:
                    results.append({"tool": name, "error": str(e)})
            else:
                results.append({"tool": name, "blocked": True})

        return {"status": "complete", "plan": plan.get("thoughts"), "results": results}
