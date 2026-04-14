"""Compounding Engineering Integration for minion Cavalry Squadron.
Integrates 24 specialized review agents from compounding-engineering-plugin.

Maps to CHARLIE Troop (Bradley IFV) - "Zero Error Rate Review Layer"

The Compounding Engineering philosophy:
"Each unit of engineering work should make subsequent units of work easier—not harder."

Review Flow for 0% Error Rate:
1. Research Phase (4 agents) → Gather context
2. Work Phase (5 agents) → Implementation
3. Review Phase (11 agents) → Multi-perspective validation
4. Documentation Phase (1 agent) → Capture learnings
5. Design Phase (3 agents) → Visual verification

Per Kosmos Paper: All reviewers must reach UNANIMOUS CONSENSUS before approval.
"""

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class ReviewerCategory(StrEnum):
    """Categories of compounding engineering agents."""

    RESEARCH = "research"  # Context gathering
    DESIGN = "design"  # Visual/UX review
    DOCS = "docs"  # Documentation
    REVIEW = "review"  # Code review (primary)
    WORKFLOW = "workflow"  # Process automation


class Severity(StrEnum):
    """Review finding severity levels."""

    CRITICAL = "critical"  # Must fix - blocks approval
    HIGH = "high"  # Should fix - strongly recommended
    MEDIUM = "medium"  # Consider fixing
    LOW = "low"  # Optional improvement
    INFO = "info"  # Informational only


@dataclass
class ReviewFinding:
    """A single finding from a reviewer."""

    reviewer: str
    severity: Severity
    category: str
    description: str
    location: str = ""
    recommendation: str = ""


@dataclass
class ReviewerAgent:
    """Represents a single compounding engineering reviewer."""

    name: str
    description: str
    category: ReviewerCategory
    prompt_path: Path
    prompt_content: str = ""

    @property
    def summary(self) -> str:
        """Get compact agent summary."""
        return f"[{self.name}] {self.description[:150]}..."


# All 24 agents from compounding-engineering-plugin
COMPOUNDING_AGENTS: dict[str, dict] = {
    # Research Agents (4) - Context Gathering
    "framework-docs-researcher": {
        "category": ReviewerCategory.RESEARCH,
        "description": "Research framework documentation and best practices for the technology stack being used",
    },
    "best-practices-researcher": {
        "category": ReviewerCategory.RESEARCH,
        "description": "Research industry best practices and standards for code patterns and architecture",
    },
    "git-history-analyzer": {
        "category": ReviewerCategory.RESEARCH,
        "description": "Analyze git history to understand code evolution and identify patterns",
    },
    "repo-research-analyst": {
        "category": ReviewerCategory.RESEARCH,
        "description": "Deep analysis of repository structure, dependencies, and architectural patterns",
    },
    # Design Agents (3) - Visual Verification
    "figma-design-sync": {
        "category": ReviewerCategory.DESIGN,
        "description": "Ensure implementation matches Figma designs pixel-perfectly",
    },
    "design-implementation-reviewer": {
        "category": ReviewerCategory.DESIGN,
        "description": "Review code implementation against design specifications and UI/UX standards",
    },
    "design-iterator": {
        "category": ReviewerCategory.DESIGN,
        "description": "Iterate on design implementations to improve user experience",
    },
    # Documentation Agents (1)
    "ankane-readme-writer": {
        "category": ReviewerCategory.DOCS,
        "description": "Write clear, comprehensive documentation in the style of Andrew Kane",
    },
    # Review Agents (11) - Primary Code Review Layer
    "security-sentinel": {
        "category": ReviewerCategory.REVIEW,
        "description": "Security audits, vulnerability assessments, OWASP compliance checks",
    },
    "code-simplicity-reviewer": {
        "category": ReviewerCategory.REVIEW,
        "description": "YAGNI enforcement, complexity reduction, simplification recommendations",
    },
    "kieran-rails-reviewer": {
        "category": ReviewerCategory.REVIEW,
        "description": "Rails-specific code review following Kieran's patterns",
    },
    "kieran-python-reviewer": {
        "category": ReviewerCategory.REVIEW,
        "description": "Python-specific code review following Kieran's patterns",
    },
    "kieran-typescript-reviewer": {
        "category": ReviewerCategory.REVIEW,
        "description": "TypeScript-specific code review following Kieran's patterns",
    },
    "performance-oracle": {
        "category": ReviewerCategory.REVIEW,
        "description": "Performance analysis, bottleneck detection, optimization recommendations",
    },
    "pattern-recognition-specialist": {
        "category": ReviewerCategory.REVIEW,
        "description": "Identify code patterns, anti-patterns, and architectural issues",
    },
    "julik-frontend-races-reviewer": {
        "category": ReviewerCategory.REVIEW,
        "description": "Frontend race condition detection and async state management review",
    },
    "architecture-strategist": {
        "category": ReviewerCategory.REVIEW,
        "description": "System architecture review, design pattern validation, scalability assessment",
    },
    "dhh-rails-reviewer": {
        "category": ReviewerCategory.REVIEW,
        "description": "Rails review following DHH's conventions and philosophy",
    },
    "data-integrity-guardian": {
        "category": ReviewerCategory.REVIEW,
        "description": "Data validation, integrity checks, consistency verification",
    },
    # Workflow Agents (5) - Process Automation
    "every-style-editor": {
        "category": ReviewerCategory.WORKFLOW,
        "description": "Style guide enforcement and consistency checks",
    },
    "lint": {
        "category": ReviewerCategory.WORKFLOW,
        "description": "Linting and static analysis orchestration",
    },
    "pr-comment-resolver": {
        "category": ReviewerCategory.WORKFLOW,
        "description": "Resolve PR comments and implement feedback",
    },
    "bug-reproduction-validator": {
        "category": ReviewerCategory.WORKFLOW,
        "description": "Validate bug reproductions and verify fixes",
    },
    "spec-flow-analyzer": {
        "category": ReviewerCategory.WORKFLOW,
        "description": "Analyze specification flows and test coverage",
    },
}


class CompoundingIntegration:
    """Integrate 24 compounding engineering agents into minion.

    Maps to CHARLIE Troop (Bradley IFV) for the 0% Error Rate Review Layer.

    Usage:
        integration = CompoundingIntegration()
        integration.load_all_agents()

        # Get all review agents for multi-perspective validation
        reviewers = integration.get_review_agents()

        # Execute unanimous consensus review
        result = integration.execute_review_panel(code_context)
    """

    def __init__(self, plugin_path: str | None = None):
        """Initialize with path to compounding-engineering-plugin."""
        if plugin_path:
            self.plugin_path = Path(plugin_path)
        else:
            self.plugin_path = (
                Path(__file__).parent.parent
                / "compounding-engineering-plugin"
                / "plugins"
                / "compounding-engineering"
            )

        self.agents_path = self.plugin_path / "agents"
        self.agents: dict[str, ReviewerAgent] = {}
        self.agents_by_category: dict[ReviewerCategory, list[ReviewerAgent]] = {
            cat: [] for cat in ReviewerCategory
        }
        self.loaded = False

    def _parse_frontmatter(self, content: str) -> tuple[str, str, str]:
        """Parse YAML frontmatter from agent .md file."""
        name = ""
        description = ""
        body = content

        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
            frontmatter = match.group(1)
            body = match.group(2)

            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip().strip("\"'")

            desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
            if desc_match:
                description = desc_match.group(1).strip().strip("\"'")

        return name, description, body

    def load_agent(self, agent_name: str) -> ReviewerAgent | None:
        """Load a single agent from the plugin."""
        # Get category from our mapping
        agent_info = COMPOUNDING_AGENTS.get(agent_name)
        if not agent_info:
            return None

        category = agent_info["category"]

        # Find the agent file
        agent_file = self.agents_path / category.value / f"{agent_name}.md"

        if not agent_file.exists():
            # Try without category subfolder
            agent_file = self.agents_path / f"{agent_name}.md"
            if not agent_file.exists():
                return None

        try:
            content = agent_file.read_text(encoding="utf-8")
            name, description, body = self._parse_frontmatter(content)

            agent = ReviewerAgent(
                name=name or agent_name,
                description=description or agent_info["description"],
                category=category,
                prompt_path=agent_file,
                prompt_content=body[:10000],  # Limit content
            )

            return agent

        except Exception as e:
            print(f"Error loading agent {agent_name}: {e}")
            return None

    def load_all_agents(self) -> int:
        """Load all 24 compounding engineering agents.

        Returns:
            Number of agents loaded successfully.

        """
        loaded_count = 0

        for agent_name in COMPOUNDING_AGENTS:
            agent = self.load_agent(agent_name)

            if agent:
                self.agents[agent.name] = agent
                self.agents_by_category[agent.category].append(agent)
                loaded_count += 1

        self.loaded = True
        return loaded_count

    def get_review_agents(self) -> list[ReviewerAgent]:
        """Get the 11 primary review agents."""
        return self.agents_by_category.get(ReviewerCategory.REVIEW, [])

    def get_research_agents(self) -> list[ReviewerAgent]:
        """Get the 4 research agents."""
        return self.agents_by_category.get(ReviewerCategory.RESEARCH, [])

    def get_workflow_agents(self) -> list[ReviewerAgent]:
        """Get the 5 workflow agents."""
        return self.agents_by_category.get(ReviewerCategory.WORKFLOW, [])

    def get_all_agents_for_troop(self, troop_name: str = "CHARLIE") -> list[ReviewerAgent]:
        """Get all agents mapped to a cavalry troop.

        CHARLIE Troop (Bradley IFV) receives all compounding agents
        for the 0% Error Rate Review Layer.
        """
        if troop_name == "CHARLIE":
            return list(self.agents.values())
        return []

    def build_review_panel_prompt(self, task_description: str) -> str:
        """Build a multi-reviewer prompt for unanimous consensus.

        Following Kosmos paper: All reviewers must agree before approval.
        """
        review_agents = self.get_review_agents()

        prompt_parts = [
            "## 0% ERROR RATE REVIEW PANEL",
            "",
            f"**Task Under Review:** {task_description}",
            "",
            "### Active Reviewers (Unanimous Consensus Required)",
            "",
        ]

        for i, agent in enumerate(review_agents, 1):
            prompt_parts.append(f"{i}. **{agent.name}**: {agent.description[:100]}...")

        prompt_parts.extend(
            [
                "",
                "### Review Protocol",
                "1. Each reviewer evaluates independently",
                "2. Findings are categorized by severity (CRITICAL/HIGH/MEDIUM/LOW/INFO)",
                "3. All CRITICAL findings must be resolved",
                "4. HIGH findings require justification if not addressed",
                "5. UNANIMOUS CONSENSUS required for approval",
                "",
                "### Consensus Voting",
                "- APPROVE: No critical issues, acceptable quality",
                "- REVISE: Issues found, changes required",
                "- REJECT: Fundamental issues, requires rework",
                "",
                "Begin review...",
            ],
        )

        return "\n".join(prompt_parts)

    def get_review_checklist(self) -> list[dict]:
        """Get a comprehensive review checklist combining all reviewer perspectives.

        Returns checklist items with reviewer attribution.
        """
        checklist = [
            # Security Sentinel
            {"reviewer": "security-sentinel", "item": "All inputs validated and sanitized"},
            {"reviewer": "security-sentinel", "item": "No hardcoded secrets or credentials"},
            {"reviewer": "security-sentinel", "item": "SQL queries use parameterization"},
            {"reviewer": "security-sentinel", "item": "XSS protection implemented"},
            {"reviewer": "security-sentinel", "item": "OWASP Top 10 compliance verified"},
            # Code Simplicity Reviewer
            {"reviewer": "code-simplicity-reviewer", "item": "YAGNI principle followed"},
            {"reviewer": "code-simplicity-reviewer", "item": "No unnecessary abstractions"},
            {"reviewer": "code-simplicity-reviewer", "item": "Code is self-documenting"},
            {"reviewer": "code-simplicity-reviewer", "item": "No dead or commented-out code"},
            # Performance Oracle
            {"reviewer": "performance-oracle", "item": "No N+1 queries"},
            {"reviewer": "performance-oracle", "item": "Appropriate indexing"},
            {"reviewer": "performance-oracle", "item": "No memory leaks"},
            {"reviewer": "performance-oracle", "item": "Efficient algorithms used"},
            # Architecture Strategist
            {"reviewer": "architecture-strategist", "item": "Design patterns correctly applied"},
            {"reviewer": "architecture-strategist", "item": "Separation of concerns maintained"},
            {"reviewer": "architecture-strategist", "item": "Dependencies properly managed"},
            # Data Integrity Guardian
            {"reviewer": "data-integrity-guardian", "item": "Data validation complete"},
            {"reviewer": "data-integrity-guardian", "item": "Referential integrity maintained"},
            {"reviewer": "data-integrity-guardian", "item": "Edge cases handled"},
            # Pattern Recognition Specialist
            {"reviewer": "pattern-recognition-specialist", "item": "No anti-patterns detected"},
            {"reviewer": "pattern-recognition-specialist", "item": "Consistent coding style"},
            {"reviewer": "pattern-recognition-specialist", "item": "Best practices followed"},
        ]

        return checklist

    def get_full_agent_prompt(self, agent_name: str) -> str:
        """Get the full prompt content for a specific agent."""
        agent = self.agents.get(agent_name)
        if not agent:
            return ""

        try:
            return agent.prompt_path.read_text(encoding="utf-8")
        except Exception:
            return agent.prompt_content

    def get_stats(self) -> dict:
        """Get integration statistics."""
        return {
            "total_agents": len(self.agents),
            "loaded": self.loaded,
            "agents_by_category": {
                cat.value: len(agents) for cat, agents in self.agents_by_category.items()
            },
            "review_agents": len(self.get_review_agents()),
            "research_agents": len(self.get_research_agents()),
            "workflow_agents": len(self.get_workflow_agents()),
        }


# Global singleton instance
_integration_instance: CompoundingIntegration | None = None


def get_compounding_integration() -> CompoundingIntegration:
    """Get or create the global compounding integration instance."""
    global _integration_instance

    if _integration_instance is None:
        _integration_instance = CompoundingIntegration()
        _integration_instance.load_all_agents()

    return _integration_instance


def get_review_panel_for_mission(task_description: str) -> str:
    """Convenience function to get review panel prompt for a mission.

    Args:
        task_description: Description of the task to review

    Returns:
        Multi-reviewer prompt for unanimous consensus.

    """
    integration = get_compounding_integration()
    return integration.build_review_panel_prompt(task_description)


def get_review_checklist() -> list[dict]:
    """Get the comprehensive review checklist."""
    integration = get_compounding_integration()
    return integration.get_review_checklist()


# Quick test when run directly
if __name__ == "__main__":
    integration = CompoundingIntegration()
    count = integration.load_all_agents()

    print(f"\n{'=' * 60}")
    print("COMPOUNDING ENGINEERING INTEGRATION - minion Phase 3")
    print(f"{'=' * 60}")
    print(f"\nLoaded {count} compounding engineering agents")

    stats = integration.get_stats()

    print("\nAgents by Category:")
    for cat, count in stats["agents_by_category"].items():
        if count > 0:
            print(f"  {cat}: {count}")

    print(f"\n{'=' * 60}")
    print("Review Panel for CHARLIE Troop:")
    print(f"{'=' * 60}")

    review_agents = integration.get_review_agents()
    for i, agent in enumerate(review_agents[:5], 1):
        print(f"  {i}. {agent.name}: {agent.description[:60]}...")

    print(f"\n  ... and {len(review_agents) - 5} more review agents")

    print(f"\n{'=' * 60}")
    print("Sample Review Checklist Items:")
    print(f"{'=' * 60}")

    checklist = integration.get_review_checklist()
    for item in checklist[:5]:
        print(f"  [{item['reviewer']}] {item['item']}")
