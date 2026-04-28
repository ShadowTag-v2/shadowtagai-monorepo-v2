# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Skills Registry

Central registry for all Pinkln reasoning skills with Glicko-2 rankings
"""

import json
from dataclasses import dataclass
from typing import Any

from .base import BenchmarkScore, Skill
from .cot import ChainOfThought
from .framework import FrameworkReasoning
from .rcr import RecursiveCritique
from .tot import TreeOfThoughts


@dataclass
class SkillRecommendation:
    """Recommendation for which skill to use"""

    skill: Skill
    reason: str
    confidence: float  # 0-1


class SkillRegistry:
    """Central registry for all reasoning skills

    Features:
    - Register/unregister skills
    - Rank by Glicko-2 rating
    - Recommend best skill for task type
    - Track benchmark performance
    - Export/import skill stats
    """

    def __init__(self):
        self.skills: dict[str, Skill] = {}
        self._init_default_skills()

    def _init_default_skills(self):
        """Initialize default skills"""
        # Core skills
        self.register(ChainOfThought())
        self.register(TreeOfThoughts())
        self.register(RecursiveCritique())
        self.register(FrameworkReasoning())

    def register(self, skill: Skill):
        """Register a skill"""
        self.skills[skill.name] = skill

    def unregister(self, name: str):
        """Unregister a skill"""
        if name in self.skills:
            del self.skills[name]

    def get(self, name: str) -> Skill | None:
        """Get skill by name"""
        return self.skills.get(name)

    def get_all(self) -> list[Skill]:
        """Get all registered skills"""
        return list(self.skills.values())

    def get_top_skills(self, n: int = 5, min_rating: float = 1400.0) -> list[Skill]:
        """Get top N skills by Glicko rating

        Args:
            n: Number of skills to return
            min_rating: Minimum conservative rating (μ - 2φ)

        Returns:
            Top skills sorted by conservative rating

        """
        eligible = [s for s in self.skills.values() if s.get_conservative_rating() >= min_rating]

        # Sort by conservative rating (μ - 2φ)
        sorted_skills = sorted(eligible, key=lambda s: s.get_conservative_rating(), reverse=True)

        return sorted_skills[:n]

    def recommend_skill(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> SkillRecommendation:
        """Recommend best skill for a task

        Uses heuristics + Glicko ratings to recommend:
        - Math/logic → ChainOfThought
        - Planning/exploration → TreeOfThoughts
        - Quality-critical → RecursiveCritique
        - Strategic/framework → FrameworkReasoning

        Args:
            task: Description of task
            context: Optional context (e.g., "prefer_speed", "prefer_quality")

        Returns:
            Skill recommendation with reasoning

        """
        # Heuristics for skill selection
        task_lower = task.lower()

        # Math/calculation → CoT
        if any(
            word in task_lower
            for word in ["calculate", "compute", "solve", "math", "number", "equation"]
        ):
            skill = self.get("ChainOfThought")
            if skill:
                return SkillRecommendation(
                    skill=skill,
                    reason="Task involves calculation/logic → Chain of Thought is optimal",
                    confidence=0.85,
                )

        # Planning/exploration → ToT
        if any(
            word in task_lower
            for word in [
                "plan",
                "strategy",
                "explore",
                "options",
                "alternatives",
                "brainstorm",
            ]
        ):
            skill = self.get("TreeOfThoughts")
            if skill:
                return SkillRecommendation(
                    skill=skill,
                    reason="Task requires exploring alternatives → Tree of Thoughts is optimal",
                    confidence=0.80,
                )

        # Quality-critical → RCR
        if any(
            word in task_lower
            for word in ["review", "critique", "improve", "refine", "quality", "perfect"]
        ):
            skill = self.get("RecursiveCritique")
            if skill:
                return SkillRecommendation(
                    skill=skill,
                    reason="Task requires high quality → Recursive Critique is optimal",
                    confidence=0.82,
                )

        # Strategic/framework → Framework
        if any(
            word in task_lower
            for word in [
                "swot",
                "analyze",
                "framework",
                "structure",
                "prioritize",
                "diagnose",
            ]
        ):
            skill = self.get("FrameworkReasoning")
            if skill:
                return SkillRecommendation(
                    skill=skill,
                    reason="Task fits structured framework → Framework Reasoning is optimal",
                    confidence=0.78,
                )

        # Default: Highest-rated skill
        top_skill = self.get_top_skills(n=1)
        if top_skill:
            return SkillRecommendation(
                skill=top_skill[0],
                reason=f"No specific match, using highest-rated skill (Glicko {top_skill[0].rating.mu:.0f})",
                confidence=0.60,
            )

        # Fallback: Chain of Thought
        cot = self.get("ChainOfThought")
        return SkillRecommendation(
            skill=cot,
            reason="Fallback to Chain of Thought (general-purpose)",
            confidence=0.50,
        )

    def update_from_benchmark(self, skill_name: str, benchmark: BenchmarkScore):
        """Update skill rating from benchmark results

        Args:
            skill_name: Name of skill
            benchmark: Benchmark results

        """
        skill = self.get(skill_name)
        if skill:
            skill.update_rating_from_benchmark(benchmark)

    def get_leaderboard(self) -> list[dict[str, Any]]:
        """Get skills leaderboard

        Returns:
            List of skills sorted by rating with stats

        """
        sorted_skills = sorted(self.skills.values(), key=lambda s: s.rating.mu, reverse=True)

        return [
            {
                "rank": i + 1,
                "name": skill.name,
                "rating": skill.rating.mu,
                "rating_deviation": skill.rating.phi,
                "conservative_rating": skill.get_conservative_rating(),
                "benchmarks": len(skill.benchmarks),
                "benchmark_avg": skill.get_benchmark_avg(),
                "total_uses": skill.total_uses,
                "success_rate": skill.success_rate(),
            }
            for i, skill in enumerate(sorted_skills)
        ]

    def export_stats(self, filepath: str):
        """Export skill stats to JSON"""
        stats = {
            "skills": {name: skill.to_dict() for name, skill in self.skills.items()},
            "leaderboard": self.get_leaderboard(),
        }

        with open(filepath, "w") as f:
            json.dump(stats, f, indent=2)

    def import_stats(self, filepath: str):
        """Import skill stats from JSON

        Note: Only updates ratings/stats, doesn't create new skills
        """
        with open(filepath) as f:
            stats = json.load(f)

        for name, skill_data in stats["skills"].items():
            skill = self.get(name)
            if skill:
                # Update rating
                rating_data = skill_data["rating"]
                skill.rating.mu = rating_data["mu"]
                skill.rating.phi = rating_data["phi"]
                skill.rating.sigma = rating_data["sigma"]

                # Update usage stats
                usage_data = skill_data["usage"]
                skill.total_uses = usage_data["total"]
                skill.successful_uses = usage_data["successful"]

    def __repr__(self) -> str:
        return f"<SkillRegistry {len(self.skills)} skills>"


# Example usage
def example():
    """Example: Skills registry with recommendations"""
    registry = SkillRegistry()

    print("=== Skills Leaderboard ===")
    for entry in registry.get_leaderboard():
        print(
            f"{entry['rank']}. {entry['name']}: {entry['rating']:.0f} "
            f"(conservative: {entry['conservative_rating']:.0f})",
        )

    print("\n=== Skill Recommendations ===")
    test_tasks = [
        "Calculate the compound interest on $10,000 at 5% for 3 years",
        "Plan a marketing strategy for a new SaaS product",
        "Review this code for bugs and suggest improvements",
        "Perform SWOT analysis for entering the European market",
    ]

    for task in test_tasks:
        rec = registry.recommend_skill(task)
        print(f"\nTask: {task[:60]}...")
        print(f"  → Recommended: {rec.skill.name}")
        print(f"  → Reason: {rec.reason}")
        print(f"  → Confidence: {rec.confidence:.0%}")

    # Export stats
    registry.export_stats("/tmp/skill_stats.json")
    print("\n✓ Stats exported to /tmp/skill_stats.json")


if __name__ == "__main__":
    example()
