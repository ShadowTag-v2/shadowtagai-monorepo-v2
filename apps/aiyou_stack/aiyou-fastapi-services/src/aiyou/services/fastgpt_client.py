"""
FastGPT Client - Wire contract for FastGPT knowledge console.

Implements GPTRAM (Retrieval-Augmented Memory) pattern:
1. Retrieve from Context Index + BigQuery + Sonar history
2. Augment with pre-context bundle
3. Generate via Gemini/minion

Usage:
    client = FastGPTClient()
    results = await client.search_org_knowledge(
        session_id="ac_01H...",
        query="JWT middleware issues",
        tags=["auth"]
    )
"""

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx


@dataclass
class KnowledgeResult:
    """A single result from FastGPT knowledge search."""

    content: str
    source: str
    relevance_score: float
    metadata: dict[str, Any]


@dataclass
class ContextBundle:
    """Pre-context bundle for GPTRAM augmentation."""

    context_notes: list[dict]
    intel_briefing: dict
    sonar_issues: list[dict]
    total_tokens: int


class FastGPTClient:
    """
    Client for FastGPT knowledge console.

    Provides:
    - Organization knowledge search
    - GPTRAM context retrieval + augmentation
    - Intel briefing integration
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        """
        Initialize FastGPT client.

        Args:
            base_url: FastGPT API URL. Defaults to localhost:3001
            api_key: Optional API key for authentication
        """
        self.base_url = base_url or os.getenv("FASTGPT_URL", "http://localhost:3001")
        self.api_key = api_key or os.getenv("FASTGPT_API_KEY", "")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
        )

    async def search_org_knowledge(
        self,
        session_id: str,
        query: str,
        tags: list[str] | None = None,
        project: str = "ShadowTag-v2-fastapi-services",
        limit: int = 5,
    ) -> list[KnowledgeResult]:
        """
        Search organization knowledge base.

        POST https://fastgpt.yourdomain/api/chat
        Body:
        {
          "session_id": "ac_01H...",
          "query": "What prior JWT incidents have we had?",
          "metadata": {
            "tags": ["auth"],
            "project": "ShadowTag-v2-fastapi-services"
          }
        }

        Args:
            session_id: Atomic chat session ID
            query: Search query
            tags: Optional tag filters
            project: Project scope
            limit: Maximum results

        Returns:
            List of KnowledgeResult objects
        """
        try:
            response = await self._client.post(
                "/api/chat",
                json={
                    "session_id": session_id,
                    "query": query,
                    "metadata": {"tags": tags or [], "project": project, "limit": limit},
                },
            )
            response.raise_for_status()
            data = response.json()

            return [
                KnowledgeResult(
                    content=item.get("content", ""),
                    source=item.get("source", "unknown"),
                    relevance_score=item.get("score", 0.0),
                    metadata=item.get("metadata", {}),
                )
                for item in data.get("results", [])
            ]

        except httpx.HTTPError as e:
            # Fallback: return empty results if FastGPT unavailable
            print(f"FastGPT search failed: {e}")
            return []

    async def get_context_for_task(
        self, task_id: str, query: str | None = None, limit: int = 8
    ) -> ContextBundle:
        """
        GPTRAM: Retrieve + Augment for a task.

        1. GET /api/context/search?query=...&limit=8
        2. GET /api/intel/briefing/today
        3. Merge into pre-context bundle

        Args:
            task_id: Task identifier
            query: Optional search query for context
            limit: Maximum context items

        Returns:
            ContextBundle with all retrieved context
        """
        context_notes = []
        intel_briefing = {}
        sonar_issues = []

        # 1. Fetch context notes
        if query:
            try:
                response = await self._client.get(
                    "/api/context/search", params={"query": query, "limit": limit}
                )
                if response.status_code == 200:
                    context_notes = response.json().get("notes", [])
            except httpx.HTTPError:
                pass

        # 2. Fetch today's intel briefing
        try:
            response = await self._client.get("/api/intel/briefing/today")
            if response.status_code == 200:
                intel_briefing = response.json()
        except httpx.HTTPError:
            intel_briefing = {
                "date": datetime.now(UTC).isoformat(),
                "summary": "No intel briefing available",
                "items": [],
            }

        # 3. Fetch relevant Sonar issues (optional)
        try:
            response = await self._client.get(
                "/api/quality/issues", params={"severity": "BLOCKER,CRITICAL", "limit": 5}
            )
            if response.status_code == 200:
                sonar_issues = response.json().get("issues", [])
        except httpx.HTTPError:
            pass

        # Calculate approximate token count
        total_tokens = self._estimate_tokens(context_notes, intel_briefing, sonar_issues)

        return ContextBundle(
            context_notes=context_notes,
            intel_briefing=intel_briefing,
            sonar_issues=sonar_issues,
            total_tokens=total_tokens,
        )

    def _estimate_tokens(
        self, context_notes: list[dict], intel_briefing: dict, sonar_issues: list[dict]
    ) -> int:
        """Rough token estimation (4 chars ~ 1 token)."""
        total_chars = 0
        for note in context_notes:
            total_chars += len(str(note))
        total_chars += len(str(intel_briefing))
        for issue in sonar_issues:
            total_chars += len(str(issue))
        return total_chars // 4

    async def format_pre_context(self, bundle: ContextBundle) -> str:
        """
        Format ContextBundle as pre-context string for LLM.

        Returns:
            Formatted markdown string for system/user message prefix
        """
        lines = ["# Pre-Context (GPTRAM)", ""]

        if bundle.context_notes:
            lines.append("## Relevant Context Notes")
            for note in bundle.context_notes[:5]:
                lines.append(f"- {note.get('content', '')[:200]}")
            lines.append("")

        if bundle.intel_briefing.get("items"):
            lines.append("## Today's Intel")
            for item in bundle.intel_briefing["items"][:3]:
                lines.append(f"- {item.get('summary', '')}")
            lines.append("")

        if bundle.sonar_issues:
            lines.append("## Active Code Issues (Blocker/Critical)")
            for issue in bundle.sonar_issues[:3]:
                lines.append(f"- [{issue.get('severity')}] {issue.get('message', '')[:100]}")
            lines.append("")

        lines.append(f"*{bundle.total_tokens} tokens retrieved*")
        return "\n".join(lines)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()


# Singleton instance
_fastgpt_client: FastGPTClient | None = None


def get_fastgpt_client() -> FastGPTClient:
    """Get the global FastGPT client instance."""
    global _fastgpt_client
    if _fastgpt_client is None:
        _fastgpt_client = FastGPTClient()
    return _fastgpt_client
