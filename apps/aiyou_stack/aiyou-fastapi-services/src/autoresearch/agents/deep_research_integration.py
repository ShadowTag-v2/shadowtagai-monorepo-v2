# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Deep Research Integration for minion Cavalry Squadron.
Integrates M2-Deep-Research multi-agent system from DAIR-AI.

Maps to AIR_CAV Troop (Aerial Reconnaissance) - Intelligence Gathering Layer

The M2 Deep Research architecture:
- SupervisorAgent: Coordinates workflow using Minimax M2 with interleaved thinking
- PlanningAgent: Generates 8-12 Exa-optimized subqueries
- WebSearchRetriever: Executes searches using Exa neural API

Research Flow:
1. Query Decomposition → PlanningAgent breaks into subqueries
2. Web Intelligence → WebSearchRetriever gathers information
3. Synthesis → SupervisorAgent produces comprehensive report

Per 0% Error Rate Architecture: Research layer provides verified intelligence
before work phase begins, ensuring all facts are sourced and validated.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class ResearchPhase(StrEnum):
    """Phases of the deep research workflow."""

    PLANNING = "planning"  # Query decomposition
    SEARCH = "search"  # Web intelligence gathering
    SYNTHESIS = "synthesis"  # Report generation
    VERIFICATION = "verification"  # Source validation


class ResearchDimension(StrEnum):
    """Research dimensions covered by subqueries."""

    CORE_CONCEPTS = "core_concepts"
    RECENT_DEVELOPMENTS = "recent_developments"
    HISTORICAL_CONTEXT = "historical_context"
    TECHNICAL_IMPLEMENTATION = "technical_implementation"
    EXPERT_OPINIONS = "expert_opinions"
    ACADEMIC_RESEARCH = "academic_research"
    MARKET_ANALYSIS = "market_analysis"
    FUTURE_IMPLICATIONS = "future_implications"
    CHALLENGES_LIMITATIONS = "challenges_limitations"
    COMPARISONS = "comparisons"


@dataclass
class ResearchSubquery:
    """A single research subquery optimized for Exa neural search."""

    query: str
    dimension: ResearchDimension
    query_type: str = "auto"  # auto, news, research paper, pdf, blog
    time_period: str = "any"  # recent, past_week, past_month, past_year, any
    priority: int = 1  # 1-5, 1=highest
    include_domains: list[str] = field(default_factory=list)
    exclude_domains: list[str] = field(default_factory=list)


@dataclass
class ResearchFinding:
    """A single finding from web search."""

    title: str
    url: str
    content: str
    source_domain: str
    dimension: ResearchDimension
    relevance_score: float = 0.0


@dataclass
class ResearchReport:
    """Complete research report structure."""

    query: str
    executive_summary: str = ""
    findings: list[ResearchFinding] = field(default_factory=list)
    analysis: str = ""
    sources: list[str] = field(default_factory=list)
    generated_at: str = ""


# Report structure template from M2
REPORT_STRUCTURE = """
## Required Report Structure:

### Executive Summary (3-5 paragraphs)
   - Overview of research scope
   - Key findings summary
   - Main conclusions and implications

### Introduction (2-3 paragraphs)
   - Context and background
   - Research objectives
   - Methodology overview

### Key Findings (Multiple detailed sections organized by theme)
   - Each major theme gets its own section with subsections
   - Include data, statistics, expert opinions
   - Cite sources inline with URLs
   - Provide examples and case studies

### Detailed Analysis (Deep dive into each area)
   - Technical details and mechanisms
   - Historical context and evolution
   - Current state of the art
   - Comparisons and contrasts
   - Strengths and limitations

### Industry/Application Analysis (if relevant)
   - Real-world applications
   - Market trends and adoption
   - Key players and institutions
   - Success stories and challenges

### Future Implications and Trends
   - Emerging developments
   - Predictions and projections
   - Challenges ahead
   - Opportunities and potential

### Critical Analysis
   - Debates and controversies
   - Limitations and challenges
   - Alternative perspectives
   - Unanswered questions

### Conclusion
   - Summary of main points
   - Broader implications
   - Recommendations (if applicable)

### Sources and Citations
   - Comprehensive list of all sources with URLs
   - Organized by category or theme
"""


class DeepResearchIntegration:
    """Integrate M2 Deep Research system into minion.

    Maps to AIR_CAV Troop (Aerial Reconnaissance) for the
    Intelligence Gathering Layer of 0% Error Rate Architecture.

    Usage:
        integration = DeepResearchIntegration()

        # Generate research subqueries
        subqueries = integration.generate_subqueries("AI safety research")

        # Get research prompt for AIR_CAV agents
        prompt = integration.build_research_prompt("AI safety research")
    """

    def __init__(self, m2_path: str | None = None):
        """Initialize with path to m2-deep-research."""
        if m2_path:
            self.m2_path = Path(m2_path)
        else:
            self.m2_path = Path(__file__).parent.parent / "m2-deep-research"

        self.agents_path = self.m2_path / "src" / "agents"
        self.loaded = False

        # Research agent configs from M2
        self.agent_configs = {
            "supervisor": {
                "model": "minimax-m2",
                "description": "Main coordinator using Minimax M2 with interleaved thinking",
                "max_tokens": 32000,
                "max_iterations": 10,
            },
            "planning": {
                "model": "openrouter/gemini-3.1-flash-lite-preview",
                "description": "Generates 8-12 Exa-optimized subqueries",
                "max_tokens": 3000,
            },
            "search": {"model": "exa-neural", "description": "Neural web search via Exa API"},
        }

    def generate_subqueries(self, query: str, num_queries: int = 10) -> list[ResearchSubquery]:
        """Generate Exa-optimized subqueries for a research topic.

        Following M2 pattern: 8-12 subqueries across multiple dimensions.
        """
        # Map dimensions to suggested subquery patterns
        dimension_templates = {
            ResearchDimension.CORE_CONCEPTS: {
                "template": "What is {topic} and what are its fundamental concepts?",
                "type": "auto",
                "priority": 1,
            },
            ResearchDimension.RECENT_DEVELOPMENTS: {
                "template": "Latest breakthroughs and developments in {topic} 2024-2025",
                "type": "news",
                "time_period": "past_month",
                "priority": 1,
            },
            ResearchDimension.HISTORICAL_CONTEXT: {
                "template": "History and evolution of {topic} over time",
                "type": "auto",
                "priority": 3,
            },
            ResearchDimension.TECHNICAL_IMPLEMENTATION: {
                "template": "Technical implementation details and best practices for {topic}",
                "type": "auto",
                "priority": 2,
            },
            ResearchDimension.EXPERT_OPINIONS: {
                "template": "Expert analysis and opinions on {topic}",
                "type": "auto",
                "priority": 2,
            },
            ResearchDimension.ACADEMIC_RESEARCH: {
                "template": "{topic} research papers and academic studies",
                "type": "research paper",
                "include_domains": ["arxiv.org", "scholar.google.com"],
                "priority": 2,
            },
            ResearchDimension.MARKET_ANALYSIS: {
                "template": "Market trends and industry analysis for {topic}",
                "type": "auto",
                "priority": 3,
            },
            ResearchDimension.FUTURE_IMPLICATIONS: {
                "template": "Future implications and predictions for {topic}",
                "type": "auto",
                "priority": 3,
            },
            ResearchDimension.CHALLENGES_LIMITATIONS: {
                "template": "Challenges, limitations and criticisms of {topic}",
                "type": "auto",
                "priority": 2,
            },
            ResearchDimension.COMPARISONS: {
                "template": "{topic} compared to alternative approaches",
                "type": "auto",
                "priority": 4,
            },
        }

        subqueries = []

        for dimension in list(ResearchDimension)[:num_queries]:
            config = dimension_templates.get(dimension, {})
            template = config.get("template", f"Information about {{topic}} - {dimension.value}")

            subquery = ResearchSubquery(
                query=template.format(topic=query),
                dimension=dimension,
                query_type=config.get("type", "auto"),
                time_period=config.get("time_period", "any"),
                priority=config.get("priority", 3),
                include_domains=config.get("include_domains", []),
                exclude_domains=config.get("exclude_domains", []),
            )
            subqueries.append(subquery)

        return sorted(subqueries, key=lambda x: x.priority)

    def build_research_prompt(self, query: str, include_structure: bool = True) -> str:
        """Build a comprehensive research prompt for AIR_CAV agents.

        Args:
            query: Research topic/question
            include_structure: Include full report structure template

        Returns:
            Research prompt for deep investigation.

        """
        subqueries = self.generate_subqueries(query)

        prompt_parts = [
            "## DEEP RESEARCH MISSION - AIR_CAV RECONNAISSANCE",
            "",
            f"**Primary Objective:** {query}",
            "",
            "### Research Dimensions to Cover:",
            "",
        ]

        for sq in subqueries:
            prompt_parts.append(f"- **{sq.dimension.value}** (Priority {sq.priority}): {sq.query}")

        prompt_parts.extend(
            [
                "",
                "### Quality Guidelines:",
                "- Be EXTREMELY thorough and detailed",
                "- Use specific data, statistics, and concrete examples",
                "- Quote experts and authoritative sources",
                "- ALWAYS include inline citations [Source](URL) immediately after claims",
                "- Every factual claim must have a citation",
                "",
                "### Search Optimization:",
                "- Use natural language questions for neural search",
                "- Focus on recent sources (past 6 months) for developments",
                "- Include academic sources for technical depth",
                "- Cross-reference multiple sources for verification",
            ],
        )

        if include_structure:
            prompt_parts.extend(["", "### Report Format:", REPORT_STRUCTURE])

        return "\n".join(prompt_parts)

    def get_supervisor_prompt(self) -> str:
        """Get the M2 supervisor system prompt."""
        return """You are a deep research coordinator specializing in comprehensive, academic-quality research reports. Your goal is to produce thorough, well-structured, in-depth analysis.

Research Workflow:
1. Plan research strategy - decompose query into 8-12 subqueries
2. Execute web searches via Exa neural API
3. Synthesize comprehensive report (15-30 pages equivalent)

CRITICAL: Inline Citations Format
- ALWAYS include inline citations immediately after claims
- Use markdown link format: [descriptive text](URL)
- Every factual claim, statistic, or data point MUST have citation
- The final Sources section supplements but doesn't replace inline citations"""

    def get_planning_prompt(self) -> str:
        """Get the M2 planning agent prompt."""
        return """Generate 8-12 comprehensive Exa-optimized subqueries for deep research.

Cover multiple dimensions:
- Core concepts and definitions
- Latest developments and breakthroughs
- Historical context and evolution
- Technical implementations
- Expert opinions and analysis
- Academic research and papers
- Industry trends and market analysis
- Future implications and predictions
- Challenges and limitations
- Related technologies and comparisons

Output valid JSON with subqueries array containing:
- query: descriptive natural language
- type: auto|news|research paper|pdf
- time_period: recent|past_week|past_month|past_year|any
- priority: 1-5 (1=highest)"""

    def get_agents_for_troop(self, troop_name: str = "AIR_CAV") -> list[dict]:
        """Get M2 research agents mapped to cavalry troop.

        AIR_CAV Troop receives all M2 research agents.
        """
        if troop_name != "AIR_CAV":
            return []

        return [
            {
                "name": "m2_supervisor",
                "type": "supervisor",
                "model": self.agent_configs["supervisor"]["model"],
                "description": self.agent_configs["supervisor"]["description"],
            },
            {
                "name": "m2_planning",
                "type": "planning",
                "model": self.agent_configs["planning"]["model"],
                "description": self.agent_configs["planning"]["description"],
            },
            {
                "name": "m2_search",
                "type": "search",
                "model": self.agent_configs["search"]["model"],
                "description": self.agent_configs["search"]["description"],
            },
        ]

    def get_research_checklist(self) -> list[dict]:
        """Get comprehensive research quality checklist.

        Returns checklist items for research validation.
        """
        return [
            {"item": "All 10 research dimensions covered", "phase": ResearchPhase.PLANNING},
            {"item": "8-12 subqueries generated", "phase": ResearchPhase.PLANNING},
            {"item": "Neural search queries optimized", "phase": ResearchPhase.PLANNING},
            {"item": "Multiple authoritative sources found", "phase": ResearchPhase.SEARCH},
            {"item": "Recent sources (<6 months) included", "phase": ResearchPhase.SEARCH},
            {"item": "Academic sources included", "phase": ResearchPhase.SEARCH},
            {"item": "Expert opinions gathered", "phase": ResearchPhase.SEARCH},
            {"item": "Report follows required structure", "phase": ResearchPhase.SYNTHESIS},
            {"item": "All claims have inline citations", "phase": ResearchPhase.SYNTHESIS},
            {"item": "Executive summary complete", "phase": ResearchPhase.SYNTHESIS},
            {"item": "Analysis covers breadth and depth", "phase": ResearchPhase.SYNTHESIS},
            {"item": "Sources cross-referenced", "phase": ResearchPhase.VERIFICATION},
            {"item": "Facts verified from multiple sources", "phase": ResearchPhase.VERIFICATION},
            {"item": "No contradictions in findings", "phase": ResearchPhase.VERIFICATION},
        ]

    def get_stats(self) -> dict:
        """Get integration statistics."""
        return {
            "m2_path_exists": self.m2_path.exists(),
            "agent_configs": len(self.agent_configs),
            "research_dimensions": len(ResearchDimension),
            "research_phases": len(ResearchPhase),
            "report_sections": REPORT_STRUCTURE.count("###"),
        }


# Global singleton instance
_integration_instance: DeepResearchIntegration | None = None


def get_deep_research_integration() -> DeepResearchIntegration:
    """Get or create the global deep research integration instance."""
    global _integration_instance

    if _integration_instance is None:
        _integration_instance = DeepResearchIntegration()

    return _integration_instance


def get_research_prompt_for_mission(topic: str) -> str:
    """Convenience function to get research prompt for a mission.

    Args:
        topic: Research topic/question

    Returns:
        Comprehensive research prompt for AIR_CAV troop.

    """
    integration = get_deep_research_integration()
    return integration.build_research_prompt(topic)


def get_research_subqueries(topic: str) -> list[ResearchSubquery]:
    """Get research subqueries for a topic."""
    integration = get_deep_research_integration()
    return integration.generate_subqueries(topic)


# Quick test when run directly
if __name__ == "__main__":
    integration = DeepResearchIntegration()

    print(f"\n{'=' * 60}")
    print("DEEP RESEARCH INTEGRATION - minion Phase 3")
    print(f"{'=' * 60}")

    stats = integration.get_stats()
    print(f"\nM2 Path exists: {stats['m2_path_exists']}")
    print(f"Agent configs: {stats['agent_configs']}")
    print(f"Research dimensions: {stats['research_dimensions']}")
    print(f"Research phases: {stats['research_phases']}")

    print(f"\n{'=' * 60}")
    print("Sample Subqueries for 'AI Safety Research':")
    print(f"{'=' * 60}")

    subqueries = integration.generate_subqueries("AI Safety Research", num_queries=5)
    for sq in subqueries:
        print(f"\n  [{sq.dimension.value}] (P{sq.priority})")
        print(f"    Query: {sq.query}")
        print(f"    Type: {sq.query_type}, Period: {sq.time_period}")

    print(f"\n{'=' * 60}")
    print("AIR_CAV Troop Agents:")
    print(f"{'=' * 60}")

    agents = integration.get_agents_for_troop("AIR_CAV")
    for agent in agents:
        print(f"  - {agent['name']}: {agent['description'][:50]}...")

    print(f"\n{'=' * 60}")
    print("Research Checklist Sample:")
    print(f"{'=' * 60}")

    checklist = integration.get_research_checklist()
    for item in checklist[:5]:
        print(f"  [{item['phase'].value}] {item['item']}")
