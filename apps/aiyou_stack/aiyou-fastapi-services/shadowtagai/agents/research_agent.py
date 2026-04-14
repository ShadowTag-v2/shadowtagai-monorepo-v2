"""Gemini Research Agent

Multi-source research orchestration using native Gemini function calling.
Integrates with COR orchestrator for parallel execution and ATP_519_scan
for compliance validation.

Architecture:
- Uses GeminiFunctionCaller from src/core/gemini_function_calling.py
- Registers Drive, Gmail, Web search tools
- Executes research pipeline via shadowtagai/pipelines/research_pipeline.py
- Returns structured ResearchResult
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any

from pnkln.core.cor_orchestrator import ExecutionContext
from shadowtagai.pipelines.research_pipeline import (
    MultiSourceResearchPipeline,
    ResearchResult,
)
from src.core.gemini_function_calling import GeminiFunctionCaller
from src.core.research_router import (
    ResearchQueryRouter,
)
from src.core.research_tools import (
    check_tool_availability,
    get_research_tools,
)

logger = logging.getLogger(__name__)


# System instruction for research orchestration
RESEARCH_SYSTEM_INSTRUCTION = """You are a research orchestrator for shadowtagai.

When the user asks to research a topic, you MUST:
1. Use drive_search to find relevant internal documents
2. Use gmail_search to find related email threads
3. Use web_search to find external information

ALWAYS query ALL THREE sources for comprehensive research. Do not skip sources.

After gathering information, structure your response as:

## Research Report: [Topic]

### Executive Summary
[2-3 sentences synthesizing key findings]

### Internal Intelligence
**Drive Documents**: [List key documents found]
**Email Threads**: [List relevant email discussions and decisions]

### External Intelligence
**Web Research**: [Current public information and trends]

### Cross-Source Analysis
[Patterns across sources, gaps identified, contradictions to resolve]

### JR Assessment
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Purpose Alignment | /100 | [Does this advance mission?] |
| Technical Merit | /100 | [Quality of options found] |
| Risk Level | RA-1 to RA-4 | [Risk classification] |

### Recommended Actions
1. [Immediate action]
2. [Short-term action]
3. [Long-term consideration]

Flag any compliance concerns (GDPR, HIPAA, SOC2, security risks) for ATP 5-19 review.
"""


class GeminiResearchAgent:
    """Gemini-native research agent with multi-source orchestration.

    Capabilities:
    - Native Gemini function calling for Drive, Gmail, Web search
    - COR orchestrator integration for parallel execution
    - ATP_519_scan for compliance validation
    - Structured research report output

    Example:
        agent = GeminiResearchAgent()
        result = await agent.research("What do we know about competitor pricing?")

    """

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        api_key: str | None = None,
        max_function_calls: int = 10,
        timeout_seconds: int = 60,
        enable_atp_scan: bool = True,
    ):
        """Initialize Gemini Research Agent.

        Args:
            model_name: Gemini model (default gemini-2.0-flash-exp for speed)
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            max_function_calls: Max function calls per research (default 10)
            timeout_seconds: Total timeout (default 60s)
            enable_atp_scan: Apply ATP_519_scan to output (default True)

        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.max_function_calls = max_function_calls
        self.timeout_seconds = timeout_seconds
        self.enable_atp_scan = enable_atp_scan

        # Initialize router for intent detection
        self.router = ResearchQueryRouter()

        # Check tool availability
        self.tool_availability = check_tool_availability()
        logger.info(f"Research agent initialized. Tool availability: {self.tool_availability}")

        # Initialize Gemini function caller with research tools
        self.gemini_caller = GeminiFunctionCaller(
            model_name=self.model_name,
            tools=get_research_tools(),
            api_key=self.api_key,
            enable_automatic_calling=False,  # Manual control for validation
            system_instruction=RESEARCH_SYSTEM_INSTRUCTION,
            max_function_calls=self.max_function_calls,
            timeout_seconds=self.timeout_seconds,
        )

        # Initialize research pipeline
        self.pipeline = MultiSourceResearchPipeline(enable_atp_scan=self.enable_atp_scan)

    async def research(self, query: str, context: ExecutionContext | None = None) -> dict[str, Any]:
        """Execute research query with multi-source orchestration.

        This method:
        1. Detects research intent and recommended sources
        2. Runs Gemini function calling loop
        3. Executes parallel source queries via pipeline
        4. Applies ATP_519_scan to final output
        5. Returns structured research report

        Args:
            query: Research query
            context: Optional execution context

        Returns:
            Dict with research_output, metrics, and compliance status

        """
        datetime.utcnow()

        # Create execution context if not provided
        if context is None:
            context = ExecutionContext(
                request_id=f"research_{uuid.uuid4().hex[:8]}",
                latency_budget_ms=5000.0,  # 5s budget for research
            )

        # Detect intent
        intent = self.router.route(query)
        logger.info(f"Research intent: {intent.intent_type}, sources: {intent.recommended_sources}")

        # Execute via pipeline (parallel source queries + synthesis)
        result = await self.pipeline.execute(query, intent, context)

        # If pipeline returned results, format as report
        if result.total_results > 0:
            # Use Gemini to synthesize into natural language report
            synthesis_prompt = self._build_synthesis_prompt(query, result)

            try:
                gemini_response = self.gemini_caller.execute(
                    prompt=synthesis_prompt, validation_callback=self._validate_function_call,
                )
                research_output = gemini_response
            except Exception as e:
                logger.warning(f"Gemini synthesis failed, using structured output: {e}")
                research_output = self._format_structured_output(result)
        else:
            research_output = f"No results found for '{query}' across queried sources."

        # Get metrics
        metrics = self.gemini_caller.get_metrics()

        return {
            "query": query,
            "research_output": research_output,
            "result": result,
            "execution_metrics": metrics,
            "context_latency_ms": context.total_latency_ms,
            "sources_queried": list(result.sources_queried),
            "sources_successful": list(result.sources_successful),
            "total_results": result.total_results,
            "compliance_status": result.compliance_status,
            "risk_score": result.risk_score,
            "risk_flags": result.risk_flags,
            "sla_met": context.total_latency_ms <= context.latency_budget_ms,
        }

    def _validate_function_call(self, fn_name: str, args: dict[str, Any]) -> bool:
        """Validate function calls before execution.

        Integration point for JR Engine / Judge #6 validation.

        Args:
            fn_name: Function being called
            args: Function arguments

        Returns:
            True if call is approved, False to block

        """
        # Allow all research tool calls by default
        allowed_functions = {"drive_search", "gmail_search", "web_search"}

        if fn_name not in allowed_functions:
            logger.warning(f"Blocked unknown function call: {fn_name}")
            return False

        # Could add JR Engine validation here
        # e.g., check if query contains sensitive terms

        return True

    def _build_synthesis_prompt(self, query: str, result: ResearchResult) -> str:
        """Build prompt for Gemini synthesis of results."""
        prompt = f"""Synthesize these research findings into a comprehensive report.

Query: {query}

**Internal Findings:**
- Drive Documents ({len(result.drive_results)} found): {result.drive_results[:5]}
- Email Threads ({len(result.gmail_results)} found): {result.gmail_results[:5]}

**External Findings:**
- Web Results ({len(result.web_results)} found): {result.web_results[:5]}

**Compliance Status:** {result.compliance_status}
**Risk Score:** {result.risk_score}/100
**Risk Flags:** {result.risk_flags}

Generate a structured research report following the format in your instructions.
Focus on actionable insights and cross-source patterns.
"""
        return prompt

    def _format_structured_output(self, result: ResearchResult) -> str:
        """Format result as structured markdown when Gemini synthesis fails."""
        output = f"""## Research Report: {result.topic}

### Executive Summary
{result.executive_summary}

### Internal Intelligence

**Drive Documents** ({len(result.drive_results)} found)
"""
        for doc in result.drive_results[:5]:
            output += f"- {doc.get('name', 'Unknown')}: {doc.get('type', 'doc')}\n"

        output += f"""
**Email Threads** ({len(result.gmail_results)} found)
"""
        for email in result.gmail_results[:5]:
            output += (
                f"- {email.get('subject', 'No subject')} ({email.get('date', 'Unknown date')})\n"
            )

        output += f"""
### External Intelligence

**Web Research** ({len(result.web_results)} found)
"""
        for web in result.web_results[:5]:
            output += f"- [{web.get('title', 'Link')}]({web.get('link', '#')})\n"

        output += f"""
### Cross-Source Analysis
{result.cross_source_analysis}

### Compliance Status
- Status: {result.compliance_status}
- Risk Score: {result.risk_score}/100
- Flags: {", ".join(result.risk_flags) if result.risk_flags else "None"}

### Recommended Actions
"""
        for i, action in enumerate(result.recommended_actions, 1):
            output += f"{i}. {action}\n"

        output += f"""
---
*Research completed in {result.total_latency_ms:.1f}ms across {len(result.sources_successful)} sources*
"""
        return output


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_agent: GeminiResearchAgent | None = None


def get_research_agent() -> GeminiResearchAgent:
    """Get singleton research agent instance."""
    global _agent
    if _agent is None:
        _agent = GeminiResearchAgent()
    return _agent


async def research(query: str) -> dict[str, Any]:
    """Execute research query.

    Convenience function for quick research execution.

    Args:
        query: Research query

    Returns:
        Research results dict

    """
    agent = get_research_agent()
    return await agent.research(query)
