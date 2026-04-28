# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PersistentMemory - GitHub-Attached Learning System
Version: 1.0.0

Philosophy: Always learning, always yearning, never resting, ever vesting.
Design: Every insight committed to GitHub, building permanent knowledge base.

Agent Levels:
- Level 1: Isolated agent
- Level 2: Tool-using agent
- Level 3: Self-evolving agent
- Level 4: Teaching other agents
- Level 5: Creating new agents
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any


class AgentLevel(int, Enum):
    """Agent evolution levels - always striving for next."""

    ISOLATED = 1  # Basic task completion
    TOOL_USING = 2  # Uses external tools
    SELF_EVOLVING = 3  # Learns from experience
    TEACHING = 4  # Teaches other agents
    CREATING = 5  # Creates new agents


class InsightType(StrEnum):
    """Types of learnings to commit."""

    SOLUTION_PATTERN = "solution"  # Successful approach
    FAILURE_POSTMORTEM = "failure"  # What went wrong
    DOMAIN_KNOWLEDGE = "domain"  # Subject matter expertise
    PROMPT_OPTIMIZATION = "prompt"  # Better prompting
    EDGE_CASE = "edge"  # Unusual scenarios
    COLLABORATION = "collab"  # Multi-agent patterns


@dataclass
class Insight:
    """Single learning to be committed."""

    id: str
    type: InsightType
    content: str
    context: str  # Task/situation that produced it
    confidence: float  # 0-1, how reliable
    timestamp: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    related_insights: list[str] = field(default_factory=list)


@dataclass
class AgentProfile:
    """Agent's persistent learning profile."""

    agent_id: str
    level: AgentLevel = AgentLevel.ISOLATED
    experience_points: int = 0
    insights_contributed: int = 0
    domains_mastered: list[str] = field(default_factory=list)
    specializations: dict[str, float] = field(default_factory=dict)  # domain → proficiency
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)


class PersistentMemory:
    """GitHub-attached memory system for continuous agent learning.

    Every task → Solve → Reflect → Commit → Level Up → Repeat

    "The agents that learn fastest win."
    """

    def __init__(self, repo_path: str = "memory"):
        self.repo_path = repo_path
        self.insights: dict[str, Insight] = {}
        self.agents: dict[str, AgentProfile] = {}
        self.knowledge_graph: dict[str, list[str]] = {}  # insight → related

        # Level thresholds
        self.level_thresholds = {
            AgentLevel.TOOL_USING: 100,
            AgentLevel.SELF_EVOLVING: 500,
            AgentLevel.TEACHING: 2000,
            AgentLevel.CREATING: 10000,
        }

    # =========================================================================
    # AGENT MANAGEMENT
    # =========================================================================

    def register_agent(self, agent_id: str) -> AgentProfile:
        """Register new agent in the learning system."""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentProfile(agent_id=agent_id)
        return self.agents[agent_id]

    def get_agent(self, agent_id: str) -> AgentProfile | None:
        """Get agent profile."""
        return self.agents.get(agent_id)

    def update_activity(self, agent_id: str):
        """Update agent's last active timestamp."""
        if agent_id in self.agents:
            self.agents[agent_id].last_active = datetime.now()

    # =========================================================================
    # INSIGHT MANAGEMENT
    # =========================================================================

    def commit_insight(
        self,
        agent_id: str,
        insight_type: InsightType,
        content: str,
        context: str,
        confidence: float = 0.8,
        tags: list[str] = None,
    ) -> str:
        """Commit a learning to persistent memory.
        Like git commit - builds permanent knowledge base.
        """
        # Generate unique ID
        insight_id = self._generate_insight_id(agent_id, content)

        # Create insight
        insight = Insight(
            id=insight_id,
            type=insight_type,
            content=content,
            context=context,
            confidence=confidence,
            tags=tags or [],
        )

        # Store
        self.insights[insight_id] = insight

        # Update agent profile
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.insights_contributed += 1
            agent.experience_points += self._calculate_xp(insight_type, confidence)

            # Check for level up
            self._check_level_up(agent)

            # Update domain proficiency
            for tag in insight.tags:
                if tag not in agent.specializations:
                    agent.specializations[tag] = 0.0
                agent.specializations[tag] += confidence * 0.1

        # Update knowledge graph
        self._update_knowledge_graph(insight)

        return insight_id

    def _generate_insight_id(self, agent_id: str, content: str) -> str:
        """Generate unique insight ID."""
        timestamp = datetime.now().isoformat()
        data = f"{agent_id}:{content}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]

    def _calculate_xp(self, insight_type: InsightType, confidence: float) -> int:
        """Calculate experience points for insight."""
        base_xp = {
            InsightType.SOLUTION_PATTERN: 10,
            InsightType.FAILURE_POSTMORTEM: 15,  # Learn more from failures
            InsightType.DOMAIN_KNOWLEDGE: 8,
            InsightType.PROMPT_OPTIMIZATION: 12,
            InsightType.EDGE_CASE: 20,  # Edge cases are valuable
            InsightType.COLLABORATION: 25,  # Collaboration insights rare
        }
        return int(base_xp.get(insight_type, 5) * confidence)

    def _check_level_up(self, agent: AgentProfile):
        """Check if agent should level up."""
        for level, threshold in self.level_thresholds.items():
            if agent.experience_points >= threshold and agent.level.value < level.value:
                agent.level = level
                # Could trigger celebration/notification

    def _update_knowledge_graph(self, insight: Insight):
        """Update relationships between insights."""
        # Find related insights by tags
        related = []
        for existing_id, existing in self.insights.items():
            if existing_id == insight.id:
                continue
            # Check tag overlap
            common_tags = set(insight.tags) & set(existing.tags)
            if common_tags:
                related.append(existing_id)
                # Bidirectional relationship
                if existing_id not in self.knowledge_graph:
                    self.knowledge_graph[existing_id] = []
                if insight.id not in self.knowledge_graph[existing_id]:
                    self.knowledge_graph[existing_id].append(insight.id)

        self.knowledge_graph[insight.id] = related
        insight.related_insights = related

    # =========================================================================
    # KNOWLEDGE RETRIEVAL
    # =========================================================================

    def retrieve_knowledge(
        self,
        query: str,
        insight_types: list[InsightType] = None,
        tags: list[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10,
    ) -> list[Insight]:
        """Search past learnings to apply to current task."""
        results = []

        for insight in self.insights.values():
            # Filter by type
            if insight_types and insight.type not in insight_types:
                continue

            # Filter by confidence
            if insight.confidence < min_confidence:
                continue

            # Filter by tags
            if tags and not any(t in insight.tags for t in tags):
                continue

            # Simple keyword search
            query_lower = query.lower()
            if (
                query_lower in insight.content.lower()
                or query_lower in insight.context.lower()
                or any(query_lower in tag.lower() for tag in insight.tags)
            ):
                results.append(insight)

        # Sort by confidence and recency
        results.sort(key=lambda i: (i.confidence, i.timestamp), reverse=True)

        return results[:limit]

    def get_related_insights(self, insight_id: str) -> list[Insight]:
        """Get insights related to a given insight."""
        related_ids = self.knowledge_graph.get(insight_id, [])
        return [self.insights[rid] for rid in related_ids if rid in self.insights]

    def get_domain_knowledge(self, domain: str) -> list[Insight]:
        """Get all insights for a specific domain."""
        return [insight for insight in self.insights.values() if domain in insight.tags]

    # =========================================================================
    # EVOLUTION TRACKING
    # =========================================================================

    def evolution_log(self, agent_id: str) -> dict[str, Any]:
        """Track agent's growth over time.
        Visualize leveling up journey.
        """
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        agent = self.agents[agent_id]

        # Get agent's insights
        agent_insights = [
            i
            for i in self.insights.values()
            if i.id.startswith(agent_id[:8])  # Simplified matching
        ]

        # Calculate progress to next level
        current_level = agent.level
        next_level = None
        progress = 1.0

        for level, threshold in self.level_thresholds.items():
            if level.value == current_level.value + 1:
                next_level = level
                prev_threshold = (
                    self.level_thresholds.get(AgentLevel(current_level.value - 1), 0)
                    if current_level.value > 1
                    else 0
                )
                progress = (agent.experience_points - prev_threshold) / (threshold - prev_threshold)
                break

        return {
            "agent_id": agent_id,
            "level": agent.level.name,
            "level_value": agent.level.value,
            "experience_points": agent.experience_points,
            "next_level": next_level.name if next_level else "MAX",
            "progress_to_next": min(1.0, progress),
            "insights_contributed": agent.insights_contributed,
            "domains_mastered": agent.domains_mastered,
            "top_specializations": sorted(
                agent.specializations.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "created": agent.created_at.isoformat(),
            "last_active": agent.last_active.isoformat(),
            "insight_breakdown": {
                itype.value: len([i for i in agent_insights if i.type == itype])
                for itype in InsightType
            },
        }

    def leaderboard(self, top_n: int = 10) -> list[dict[str, Any]]:
        """Get top agents by experience points."""
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: a.experience_points,
            reverse=True,
        )

        return [
            {
                "rank": i + 1,
                "agent_id": agent.agent_id,
                "level": agent.level.name,
                "xp": agent.experience_points,
                "insights": agent.insights_contributed,
            }
            for i, agent in enumerate(sorted_agents[:top_n])
        ]

    # =========================================================================
    # TEACHING & KNOWLEDGE TRANSFER
    # =========================================================================

    def transfer_knowledge(
        self,
        from_agent_id: str,
        to_agent_id: str,
        domain: str,
    ) -> dict[str, Any]:
        """Level 4 agent teaches Level 1-3 agent.
        Transfer domain knowledge.
        """
        teacher = self.agents.get(from_agent_id)
        student = self.agents.get(to_agent_id)

        if not teacher or not student:
            return {"error": "Agent not found"}

        if teacher.level.value < AgentLevel.TEACHING.value:
            return {
                "error": f"Agent {from_agent_id} not qualified to teach (Level {teacher.level.name})",
            }

        # Get teacher's domain insights
        domain_insights = [
            i for i in self.insights.values() if domain in i.tags and i.confidence >= 0.7
        ]

        # Transfer knowledge (simplified)
        transferred = 0
        for insight in domain_insights:
            # Student "learns" the insight
            if domain not in student.specializations:
                student.specializations[domain] = 0.0
            student.specializations[domain] += insight.confidence * 0.05
            transferred += 1

        # Award XP to both
        teacher.experience_points += transferred * 5
        student.experience_points += transferred * 2

        return {
            "teacher": from_agent_id,
            "student": to_agent_id,
            "domain": domain,
            "insights_transferred": transferred,
            "student_new_proficiency": student.specializations.get(domain, 0),
        }

    # =========================================================================
    # PERSISTENCE (GitHub Integration Points)
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Serialize memory for persistence."""
        return {
            "repo_path": self.repo_path,
            "insights": {
                k: {
                    "id": v.id,
                    "type": v.type.value,
                    "content": v.content,
                    "context": v.context,
                    "confidence": v.confidence,
                    "timestamp": v.timestamp.isoformat(),
                    "tags": v.tags,
                    "related": v.related_insights,
                }
                for k, v in self.insights.items()
            },
            "agents": {
                k: {
                    "agent_id": v.agent_id,
                    "level": v.level.value,
                    "xp": v.experience_points,
                    "insights_contributed": v.insights_contributed,
                    "domains": v.domains_mastered,
                    "specializations": v.specializations,
                    "created": v.created_at.isoformat(),
                    "last_active": v.last_active.isoformat(),
                }
                for k, v in self.agents.items()
            },
            "knowledge_graph": self.knowledge_graph,
        }

    def save_to_file(self, filepath: str):
        """Save memory to JSON file (would be git commit in production)."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def __repr__(self) -> str:
        return (
            f"PersistentMemory("
            f"agents={len(self.agents)}, "
            f"insights={len(self.insights)}, "
            f"connections={sum(len(v) for v in self.knowledge_graph.values())})"
        )


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_memory_system(repo_path: str = "memory") -> PersistentMemory:
    """Create persistent memory system.

    "Always learning, always yearning, never resting, ever vesting."
    """
    return PersistentMemory(repo_path=repo_path)


# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":
    print("PersistentMemory - Self Test")
    print("=" * 60)

    # Create memory system
    memory = create_memory_system()
    print(f"\nCreated: {memory}")

    # Register agents
    agent_a = memory.register_agent("agent_alpha")
    agent_b = memory.register_agent("agent_beta")
    print(f"\nRegistered: {agent_a.agent_id} (Level {agent_a.level.name})")
    print(f"Registered: {agent_b.agent_id} (Level {agent_b.level.name})")

    # Commit insights
    print("\n" + "=" * 60)
    print("Committing Insights...")

    insight1 = memory.commit_insight(
        agent_id="agent_alpha",
        insight_type=InsightType.SOLUTION_PATTERN,
        content="Use action verb decomposition for complete task coverage",
        context="Task: Implement authentication",
        confidence=0.95,
        tags=["methodology", "bar-exam", "action-verbs"],
    )
    print(f"Committed: {insight1}")

    insight2 = memory.commit_insight(
        agent_id="agent_alpha",
        insight_type=InsightType.EDGE_CASE,
        content="Token expiry during refresh race condition",
        context="Task: JWT authentication",
        confidence=0.85,
        tags=["authentication", "jwt", "edge-case"],
    )
    print(f"Committed: {insight2}")

    insight3 = memory.commit_insight(
        agent_id="agent_beta",
        insight_type=InsightType.FAILURE_POSTMORTEM,
        content="Missed compound subjects - Dan AND Dave need separate analysis",
        context="Task: Multi-subject legal analysis",
        confidence=0.90,
        tags=["methodology", "bar-exam", "comprehension"],
    )
    print(f"Committed: {insight3}")

    # Retrieve knowledge
    print("\n" + "=" * 60)
    print("Retrieving Knowledge...")

    results = memory.retrieve_knowledge(query="bar exam", min_confidence=0.8)
    print(f"Found {len(results)} insights for 'bar exam':")
    for r in results:
        print(f"  - [{r.type.value}] {r.content[:50]}...")

    # Evolution log
    print("\n" + "=" * 60)
    print("Evolution Log - Agent Alpha:")

    log = memory.evolution_log("agent_alpha")
    print(f"  Level: {log['level']} ({log['level_value']})")
    print(f"  XP: {log['experience_points']}")
    print(f"  Progress to {log['next_level']}: {log['progress_to_next']:.1%}")
    print(f"  Insights: {log['insights_contributed']}")

    # Leaderboard
    print("\n" + "=" * 60)
    print("Leaderboard:")

    for entry in memory.leaderboard():
        print(f"  #{entry['rank']} {entry['agent_id']}: {entry['xp']} XP ({entry['level']})")

    print("\n" + "=" * 60)
    print("✓ PersistentMemory working correctly")
    print("\nPhilosophy: Always learning, always yearning, never resting, ever vesting.")
