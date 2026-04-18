"""Multi-Source Research Pipeline

COR-based orchestration for parallel research across Drive, Gmail, Web.
Integrates with ATP_519_scan for compliance validation on output.

Architecture:
    Stage 1 (Concurrent): drive_search + gmail_search + web_search
    Stage 2 (Sequential): Aggregate → MCP compress → ATP_519_scan → Synthesize

SLA Target: p99 < 2000ms for complete research cycle
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from pnkln.core.cor_orchestrator import (
    ExecutionContext,
)
from src.core.research_router import ResearchIntent, ResearchSourceType
from src.core.research_tools import (
    check_tool_availability,
    drive_search_impl,
    gmail_search_impl,
    web_search_impl,
)

logger = logging.getLogger(__name__)


@dataclass
class SourceResult:
    """Result from a single source search."""

    source: str
    status: str
    results: list[dict[str, Any]]
    count: int
    latency_ms: float
    error: str | None = None


@dataclass
class ResearchResult:
    """Aggregated research results with synthesis."""

    query: str
    topic: str
    sources_queried: list[str]
    sources_successful: list[str]

    # Results by source
    drive_results: list[dict[str, Any]] = field(default_factory=list)
    gmail_results: list[dict[str, Any]] = field(default_factory=list)
    web_results: list[dict[str, Any]] = field(default_factory=list)
    memory_results: list[dict[str, Any]] = field(default_factory=list)
    codebase_results: list[dict[str, Any]] = field(default_factory=list)

    # Synthesis
    executive_summary: str = ""
    cross_source_analysis: str = ""
    recommended_actions: list[str] = field(default_factory=list)

    # Compliance
    compliance_status: str = "pending"
    risk_score: int = 0
    risk_flags: list[str] = field(default_factory=list)

    # Metrics
    total_results: int = 0
    total_latency_ms: float = 0
    stage_latencies: dict[str, float] = field(default_factory=dict)


class MultiSourceResearchPipeline:
    """Multi-source research orchestration using COR patterns.

    ARCHITECTURE:
    Stage 1 (Concurrent): Query all sources in parallel
        - drive_search()
        - gmail_search()
        - web_search()

    Stage 2 (Sequential): Process results
        - Aggregate results
        - Apply MCP semantic compression
        - ATP_519_scan for compliance
        - Synthesize final report

    SLA: p99 < 2000ms for complete research cycle
    """

    def __init__(
        self,
        latency_budget_ms: float = 2000.0,
        enable_mcp_compression: bool = True,
        enable_atp_scan: bool = True,
    ):
        """Initialize research pipeline.

        Args:
            latency_budget_ms: Total latency budget (default 2000ms)
            enable_mcp_compression: Apply MCP semantic compression
            enable_atp_scan: Apply ATP_519_scan compliance check

        """
        self.latency_budget_ms = latency_budget_ms
        self.enable_mcp_compression = enable_mcp_compression
        self.enable_atp_scan = enable_atp_scan

        # Check available tools
        self.tool_availability = check_tool_availability()

    async def execute(
        self,
        query: str,
        intent: ResearchIntent,
        context: ExecutionContext | None = None,
    ) -> ResearchResult:
        """Execute complete multi-source research workflow.

        Args:
            query: Research query
            intent: ResearchIntent with recommended sources
            context: Optional execution context

        Returns:
            ResearchResult with aggregated and synthesized findings

        """
        start_time = time.time()

        # Create execution context if not provided
        if context is None:
            context = ExecutionContext(
                request_id=f"research_{uuid.uuid4().hex[:8]}",
                latency_budget_ms=self.latency_budget_ms,
            )

        # Initialize result
        result = ResearchResult(
            query=query,
            topic=intent.extracted_topic,
            sources_queried=[],
            sources_successful=[],
        )

        # =========================================
        # Stage 1: Concurrent Source Queries
        # =========================================
        stage1_start = time.time()

        source_tasks = []
        source_names = []

        # Build tasks for each recommended source
        if ResearchSourceType.DRIVE in intent.recommended_sources:
            if self.tool_availability.get("drive_search"):
                source_tasks.append(self._search_drive(intent.extracted_topic))
                source_names.append("drive")
                result.sources_queried.append("drive")

        if ResearchSourceType.GMAIL in intent.recommended_sources:
            if self.tool_availability.get("gmail_search"):
                source_tasks.append(self._search_gmail(intent.extracted_topic))
                source_names.append("gmail")
                result.sources_queried.append("gmail")

        if ResearchSourceType.WEB in intent.recommended_sources:
            source_tasks.append(self._search_web(intent.extracted_topic))
            source_names.append("web")
            result.sources_queried.append("web")

        # Execute all sources in parallel
        if source_tasks:
            try:
                source_results = await asyncio.wait_for(
                    asyncio.gather(*source_tasks, return_exceptions=True),
                    timeout=1.5,  # 1.5s timeout for source queries
                )
            except TimeoutError:
                logger.warning(f"Source queries timed out for: {query}")
                source_results = []

            # Process results
            for name, res in zip(source_names, source_results, strict=False):
                if isinstance(res, Exception):
                    logger.error(f"Source {name} failed: {res}")
                    continue

                if res.get("status") == "success":
                    result.sources_successful.append(name)

                    if name == "drive":
                        result.drive_results = res.get("results", [])
                    elif name == "gmail":
                        result.gmail_results = res.get("results", [])
                    elif name == "web":
                        result.web_results = res.get("results", [])

        stage1_latency = (time.time() - stage1_start) * 1000
        result.stage_latencies["source_queries"] = stage1_latency
        context.record_stage_latency("source_queries", stage1_latency)

        # =========================================
        # Stage 2: Aggregate Results
        # =========================================
        stage2_start = time.time()

        result.total_results = (
            len(result.drive_results)
            + len(result.gmail_results)
            + len(result.web_results)
            + len(result.memory_results)
            + len(result.codebase_results)
        )

        stage2_latency = (time.time() - stage2_start) * 1000
        result.stage_latencies["aggregation"] = stage2_latency
        context.record_stage_latency("aggregation", stage2_latency)

        # =========================================
        # Stage 3: MCP Compression (optional)
        # =========================================
        if self.enable_mcp_compression:
            stage3_start = time.time()
            # MCP compression would happen here
            # For now, just track latency
            stage3_latency = (time.time() - stage3_start) * 1000
            result.stage_latencies["mcp_compression"] = stage3_latency
            context.record_stage_latency("mcp_compression", stage3_latency)

        # =========================================
        # Stage 4: ATP_519_scan (optional)
        # =========================================
        if self.enable_atp_scan:
            stage4_start = time.time()
            compliance = self._apply_atp_scan(result)
            result.compliance_status = compliance.get("status", "approved")
            result.risk_score = compliance.get("risk_score", 0)
            result.risk_flags = compliance.get("flags", [])
            stage4_latency = (time.time() - stage4_start) * 1000
            result.stage_latencies["atp_scan"] = stage4_latency
            context.record_stage_latency("atp_scan", stage4_latency)

        # =========================================
        # Stage 5: Synthesis
        # =========================================
        stage5_start = time.time()
        result.executive_summary = self._generate_summary(result)
        result.cross_source_analysis = self._analyze_cross_source(result)
        result.recommended_actions = self._generate_actions(result)
        stage5_latency = (time.time() - stage5_start) * 1000
        result.stage_latencies["synthesis"] = stage5_latency
        context.record_stage_latency("synthesis", stage5_latency)

        # =========================================
        # Finalize
        # =========================================
        result.total_latency_ms = (time.time() - start_time) * 1000

        # Log SLA compliance
        if result.total_latency_ms > self.latency_budget_ms:
            logger.warning(
                f"Research pipeline exceeded SLA: {result.total_latency_ms:.1f}ms > {self.latency_budget_ms}ms",
            )
        else:
            logger.info(
                f"Research complete: {result.total_results} results in {result.total_latency_ms:.1f}ms",
            )

        return result

    async def _search_drive(self, topic: str) -> dict[str, Any]:
        """Execute Drive search."""
        start = time.time()
        result = drive_search_impl(query=topic, max_results=10)
        result["latency_ms"] = (time.time() - start) * 1000
        return result

    async def _search_gmail(self, topic: str) -> dict[str, Any]:
        """Execute Gmail search."""
        start = time.time()
        result = gmail_search_impl(query=topic, max_results=10)
        result["latency_ms"] = (time.time() - start) * 1000
        return result

    async def _search_web(self, topic: str) -> dict[str, Any]:
        """Execute Web search."""
        start = time.time()
        result = web_search_impl(query=topic, max_results=10)
        result["latency_ms"] = (time.time() - start) * 1000
        return result

    def _apply_atp_scan(self, result: ResearchResult) -> dict[str, Any]:
        """Apply ATP 5-19 compliance scan to research output.

        Checks for:
        - PII exposure in results
        - Compliance domain mentions (GDPR, HIPAA, etc.)
        - Security-sensitive content
        """
        flags = []
        risk_score = 0

        # Simple heuristic checks
        all_text = str(result.drive_results) + str(result.gmail_results) + str(result.web_results)
        all_text_lower = all_text.lower()

        # PII detection
        if any(
            term in all_text_lower for term in ["ssn", "social security", "credit card", "password"]
        ):
            flags.append("PII_DETECTED")
            risk_score += 30

        # Compliance domain detection
        for domain in ["gdpr", "hipaa", "soc2", "pci", "ccpa"]:
            if domain in all_text_lower:
                flags.append(f"COMPLIANCE_MENTION_{domain.upper()}")
                risk_score += 5

        # Security content
        if any(term in all_text_lower for term in ["vulnerability", "exploit", "breach", "attack"]):
            flags.append("SECURITY_CONTENT")
            risk_score += 15

        return {
            "status": "review_required" if risk_score > 50 else "approved",
            "risk_score": min(risk_score, 100),
            "flags": flags,
        }

    def _generate_summary(self, result: ResearchResult) -> str:
        """Generate executive summary from results."""
        source_counts = []
        if result.drive_results:
            source_counts.append(f"{len(result.drive_results)} Drive docs")
        if result.gmail_results:
            source_counts.append(f"{len(result.gmail_results)} email threads")
        if result.web_results:
            source_counts.append(f"{len(result.web_results)} web results")

        if source_counts:
            return f"Research on '{result.topic}' found {', '.join(source_counts)} across {len(result.sources_successful)} sources."
        return f"No results found for '{result.topic}' across queried sources."

    def _analyze_cross_source(self, result: ResearchResult) -> str:
        """Analyze patterns across sources."""
        analysis = []

        if result.drive_results and result.web_results:
            analysis.append(
                "Internal documentation and external sources both available - cross-reference recommended.",
            )

        if result.gmail_results:
            analysis.append("Email context found - check for relevant decisions or discussions.")

        if not result.drive_results and result.web_results:
            analysis.append(
                "Gap: External information available but no internal documentation found.",
            )

        return " ".join(analysis) if analysis else "Cross-source analysis pending."

    def _generate_actions(self, result: ResearchResult) -> list[str]:
        """Generate recommended actions from results."""
        actions = []

        if result.total_results > 0:
            actions.append(f"Review {result.total_results} results for relevance")

        if result.drive_results:
            actions.append("Examine internal documents for prior decisions")

        if result.gmail_results:
            actions.append("Check email threads for stakeholder context")

        if result.web_results:
            actions.append("Validate external information currency")

        if result.risk_flags:
            actions.append(f"Address compliance flags: {', '.join(result.risk_flags)}")

        return actions or ["No specific actions identified"]


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_pipeline: MultiSourceResearchPipeline | None = None


def get_pipeline() -> MultiSourceResearchPipeline:
    """Get singleton pipeline instance."""
    global _pipeline
    if _pipeline is None:
        _pipeline = MultiSourceResearchPipeline()
    return _pipeline


async def execute_research(
    query: str,
    intent: ResearchIntent,
    context: ExecutionContext | None = None,
) -> ResearchResult:
    """Execute research query with multi-source orchestration.

    Args:
        query: Research query
        intent: ResearchIntent from router
        context: Optional execution context

    Returns:
        ResearchResult with findings and synthesis

    """
    pipeline = get_pipeline()
    return await pipeline.execute(query, intent, context)
