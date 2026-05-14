# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
CHEAT SHEET FUSION - Jobs-Quality Prompt Engineering
=====================================================

EVOLUTION: 21 prompt elements → 10 essentials
GOAL: Insanely great prompts that breathe, pause, simplify
VALIDATION: DTE (Dynamic Test Evolution) - +3.7% accuracy target

PHILOSOPHY (Steve Jobs):
- "Simplicity is the ultimate sophistication"
- "Design is not just what it looks like, design is how it works"
- "You have to start with the customer experience and work backwards"

THE 10 ESSENTIALS (from original 21):
=====================================
1. TONE: Voice/personality (Jobs: "Insanely great")
2. FORMAT: Structure/output style (Jobs: "Beautiful, simple")
3. ACT: Role/persona (Jobs: "Think different")
4. OBJECTIVE: Clear goal (Jobs: "Change the world")
5. CONTEXT: Background/situation (Jobs: "Reality distortion")
6. KEYWORDS: Critical terms (Jobs: "Focus - saying no to 1000 things")
7. EXAMPLES: Few-shot demos (Jobs: "Show, don't tell")
8. AUDIENCE: Who it's for (Jobs: "User experience first")
9. CITATIONS: Sources/attribution (Jobs: "Artists steal")
10. CALL: Next action (Jobs: "Ship it")

ELIMINATED (merged into above):
- Constraints → OBJECTIVE (implicit in clear goals)
- Length → FORMAT (structure includes length)
- Style → TONE (voice encompasses style)
- Temperature → ACT (persona implies creativity level)
- Stop sequences → FORMAT (structure includes boundaries)
- Presence penalty → KEYWORDS (focus implies uniqueness)
- Frequency penalty → KEYWORDS (avoid repetition)
- Best of N → CALL (quality in execution)
- Logit bias → ACT (persona implies preferences)
- User/System split → CONTEXT (roles in background)
- Chain-of-thought → EXAMPLES (show reasoning)

DTE EVOLUTION:
==============
- Test variants (A/B/C prompts)
- Measure accuracy vs ground truth
- Evolve toward better performance
- Track improvement per cycle
- Target: +3.7% accuracy observed in studies
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class Essential(str, Enum):
    """The 10 essential prompt elements"""

    TONE = "tone"  # Voice/personality
    FORMAT = "format"  # Structure/output style
    ACT = "act"  # Role/persona
    OBJECTIVE = "objective"  # Clear goal
    CONTEXT = "context"  # Background/situation
    KEYWORDS = "keywords"  # Critical terms
    EXAMPLES = "examples"  # Few-shot demos
    AUDIENCE = "audience"  # Who it's for
    CITATIONS = "citations"  # Sources/attribution
    CALL = "call"  # Next action


@dataclass
class CheatSheetVariant:
    """
    A specific prompt variant with 10 essentials configured.

    Jobs philosophy: Each variant should be "insanely great" in its own way.
    """

    variant_id: str
    essentials: dict[Essential, Any]

    # DTE tracking
    tests_run: int = 0
    accuracy_sum: float = 0.0
    avg_accuracy: float = 0.0
    best_accuracy: float = 0.0

    # Evolution metadata
    generation: int = 1  # Which evolution cycle created this
    parent_id: str | None = None
    mutations: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    last_tested: datetime | None = None

    def record_test_result(self, accuracy: float) -> None:
        """Record DTE test result and update metrics"""
        self.tests_run += 1
        self.accuracy_sum += accuracy
        self.avg_accuracy = self.accuracy_sum / self.tests_run
        self.best_accuracy = max(self.best_accuracy, accuracy)
        self.last_tested = datetime.utcnow()

        logger.info(
            f"Variant {self.variant_id}: Test #{self.tests_run} accuracy={accuracy:.1%}, avg={self.avg_accuracy:.1%}, best={self.best_accuracy:.1%}"
        )

    def get_improvement(self) -> float:
        """Calculate improvement vs initial baseline"""
        if self.tests_run < 2:
            return 0.0
        # Improvement = (current avg - first test) / first test
        first_test_accuracy = self.accuracy_sum / self.tests_run  # Approximation
        return (self.avg_accuracy - first_test_accuracy) / max(first_test_accuracy, 0.01)

    def to_prompt(self) -> str:
        """Generate final prompt from essentials"""
        return CheatSheetFusion._compile_prompt(self.essentials)


@dataclass
class DTETestResult:
    """Result from DTE validation test"""

    variant_id: str
    accuracy: float
    latency_ms: float
    cost_usd: float
    test_cases_passed: int
    test_cases_total: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def pass_rate(self) -> float:
        return self.test_cases_passed / max(self.test_cases_total, 1)


class CheatSheetFusion:
    """
    Cheat Sheet Fusion with DTE Evolution.

    Usage:
        fusion = CheatSheetFusion(source="youtube", use_case="tier_1_intelligence")
        fusion.add_essential(Essential.TONE, "insanely_great")
        fusion.add_essential(Essential.OBJECTIVE, "collect_tier_1_ratio_60_percent")

        # Generate prompt
        prompt = fusion.generate_prompt()

        # Test and evolve
        result = await fusion.test_variant(prompt, ground_truth_data)
        if result.accuracy > fusion.best_accuracy:
            fusion.evolve(direction="improve")
    """

    def __init__(
        self,
        source: str,
        use_case: str,
        dte_enabled: bool = True,
        evolution_rate: float = 0.1,
        target_accuracy: float = 0.60,  # 60% baseline, aiming for +3.7% = 63.7%
    ):
        """
        Initialize Cheat Sheet Fusion.

        Args:
            source: Data source (e.g., "youtube", "twitter")
            use_case: Use case (e.g., "tier_1_intelligence", "governance_risk")
            dte_enabled: Enable Dynamic Test Evolution
            evolution_rate: Mutation rate for evolution (0.1 = 10% change per cycle)
            target_accuracy: Target accuracy to achieve
        """
        self.source = source
        self.use_case = use_case
        self.dte_enabled = dte_enabled
        self.evolution_rate = evolution_rate
        self.target_accuracy = target_accuracy

        # Variant tracking
        self.variants: dict[str, CheatSheetVariant] = {}
        self.current_variant_id: str | None = None
        self.best_variant_id: str | None = None
        self.generation = 1

        # DTE metrics
        self.total_tests_run = 0
        self.total_accuracy_gain = 0.0
        self.baseline_accuracy: float | None = None

        logger.info(
            f"CheatSheetFusion initialized: source={source}, use_case={use_case}, "
            f"DTE={'enabled' if dte_enabled else 'disabled'}, target={target_accuracy:.1%}"
        )

    def create_variant(self, essentials: dict[Essential, Any], parent_id: str | None = None) -> str:
        """Create a new cheat sheet variant"""
        # Generate variant ID from essentials hash
        essentials_str = json.dumps(essentials, sort_keys=True, default=str)
        variant_hash = hashlib.md5(essentials_str.encode()).hexdigest()[:8]
        variant_id = f"{self.source}_{self.use_case}_{variant_hash}_gen{self.generation}"

        # Detect mutations if has parent
        mutations = []
        if parent_id and parent_id in self.variants:
            parent = self.variants[parent_id]
            for essential in Essential:
                if essentials.get(essential) != parent.essentials.get(essential):
                    mutations.append(f"mutated_{essential.value}")

        variant = CheatSheetVariant(
            variant_id=variant_id,
            essentials=essentials,
            generation=self.generation,
            parent_id=parent_id,
            mutations=mutations,
        )

        self.variants[variant_id] = variant
        self.current_variant_id = variant_id

        logger.info(f"Created variant {variant_id}: gen={self.generation}, parent={parent_id}, mutations={mutations}")

        return variant_id

    def get_current_variant(self) -> CheatSheetVariant | None:
        """Get currently active variant"""
        if self.current_variant_id:
            return self.variants.get(self.current_variant_id)
        return None

    def get_best_variant(self) -> CheatSheetVariant | None:
        """Get best-performing variant"""
        if self.best_variant_id:
            return self.variants.get(self.best_variant_id)
        return None

    async def test_variant(self, variant_id: str, ground_truth_data: list[dict], test_fn: Any | None = None) -> DTETestResult:
        """
        Test a variant against ground truth using DTE.

        Args:
            variant_id: Variant to test
            ground_truth_data: List of test cases with expected outputs
            test_fn: Optional custom test function

        Returns:
            DTETestResult with accuracy metrics
        """
        if variant_id not in self.variants:
            raise ValueError(f"Variant {variant_id} not found")

        variant = self.variants[variant_id]
        prompt = variant.to_prompt()

        # Run test (mock implementation - replace with real testing)
        import time

        start_time = time.perf_counter()

        passed = 0
        total = len(ground_truth_data)

        for test_case in ground_truth_data:
            # Mock test: Check if prompt would generate correct output
            # Real implementation would call LLM and compare outputs
            if test_fn:
                result = await test_fn(prompt, test_case)
            else:
                # Mock: Random accuracy around target
                import random

                result = random.random() < self.target_accuracy

            if result:
                passed += 1

        latency_ms = (time.perf_counter() - start_time) * 1000
        accuracy = passed / max(total, 1)

        # Record result
        variant.record_test_result(accuracy)
        self.total_tests_run += 1

        # Update baseline if first test
        if self.baseline_accuracy is None:
            self.baseline_accuracy = accuracy
            logger.info(f"Baseline accuracy set: {accuracy:.1%}")
        else:
            gain = accuracy - self.baseline_accuracy
            self.total_accuracy_gain += gain
            logger.info(f"Accuracy gain: {gain:+.1%} (total: {self.total_accuracy_gain:+.1%}, target: +3.7%)")

        # Update best variant
        if self.best_variant_id is None or accuracy > self.variants[self.best_variant_id].best_accuracy:
            self.best_variant_id = variant_id
            logger.info(f"New best variant: {variant_id} ({accuracy:.1%})")

        return DTETestResult(
            variant_id=variant_id,
            accuracy=accuracy,
            latency_ms=latency_ms,
            cost_usd=0.001 * total,  # Mock cost
            test_cases_passed=passed,
            test_cases_total=total,
        )

    def evolve(self, direction: str = "improve") -> str:
        """
        Evolve cheat sheet based on test results.

        Args:
            direction: "improve" (enhance best), "explore" (random mutation),
                      "simplify" (reduce complexity)

        Returns:
            New variant ID
        """
        if not self.dte_enabled:
            logger.warning("DTE not enabled, evolution skipped")
            return self.current_variant_id

        # Get parent (best or current)
        parent_id = self.best_variant_id or self.current_variant_id
        if not parent_id:
            raise ValueError("No variants to evolve from")

        parent = self.variants[parent_id]

        # Mutate essentials based on direction
        new_essentials = parent.essentials.copy()

        if direction == "improve":
            # Enhance based on what worked
            if Essential.KEYWORDS in new_essentials:
                # Add more specific keywords
                keywords = new_essentials[Essential.KEYWORDS]
                if isinstance(keywords, list):
                    keywords.append("high_quality_tier_1")
                new_essentials[Essential.KEYWORDS] = keywords

        elif direction == "explore":
            # Random mutation
            import random

            essential_to_mutate = random.choice(list(Essential))
            # Apply random change (simplified for demo)
            new_essentials[essential_to_mutate] = f"mutated_{new_essentials.get(essential_to_mutate, 'default')}"

        elif direction == "simplify":
            # Remove least important essentials (Jobs: simplicity)
            # Keep only top 7 essentials
            essential_importance = {
                Essential.OBJECTIVE: 10,
                Essential.CONTEXT: 9,
                Essential.TONE: 8,
                Essential.ACT: 7,
                Essential.KEYWORDS: 6,
                Essential.EXAMPLES: 5,
                Essential.FORMAT: 4,
                Essential.AUDIENCE: 3,
                Essential.CITATIONS: 2,
                Essential.CALL: 1,
            }
            keep_essentials = sorted(new_essentials.keys(), key=lambda e: essential_importance.get(e, 0), reverse=True)[:7]
            new_essentials = {e: new_essentials[e] for e in keep_essentials}

        # Create new variant
        self.generation += 1
        new_variant_id = self.create_variant(new_essentials, parent_id=parent_id)

        logger.info(f"Evolved from {parent_id} → {new_variant_id} (direction={direction}, gen={self.generation})")

        return new_variant_id

    def generate_prompt(self, variant_id: str | None = None) -> str:
        """
        Generate final prompt from variant.

        Args:
            variant_id: Specific variant (default: current best)

        Returns:
            Compiled prompt string
        """
        if variant_id:
            variant = self.variants.get(variant_id)
        else:
            variant = self.get_best_variant() or self.get_current_variant()

        if not variant:
            raise ValueError("No variants available")

        return variant.to_prompt()

    @staticmethod
    def _compile_prompt(essentials: dict[Essential, Any]) -> str:
        """
        Compile essentials into final prompt.

        Jobs philosophy: Beautiful, simple, focused.
        """
        sections = []

        # 1. ACT (Role) - Who are you?
        if Essential.ACT in essentials:
            sections.append(f"You are {essentials[Essential.ACT]}.")

        # 2. CONTEXT (Background) - What's the situation?
        if Essential.CONTEXT in essentials:
            sections.append(f"\nContext: {essentials[Essential.CONTEXT]}")

        # 3. OBJECTIVE (Goal) - What do you want?
        if Essential.OBJECTIVE in essentials:
            sections.append(f"\nObjective: {essentials[Essential.OBJECTIVE]}")

        # 4. AUDIENCE (Who for) - Who is this for?
        if Essential.AUDIENCE in essentials:
            sections.append(f"\nAudience: {essentials[Essential.AUDIENCE]}")

        # 5. TONE (Voice) - How should you sound?
        if Essential.TONE in essentials:
            sections.append(f"\nTone: {essentials[Essential.TONE]}")

        # 6. KEYWORDS (Focus) - What matters most?
        if Essential.KEYWORDS in essentials:
            keywords = essentials[Essential.KEYWORDS]
            if isinstance(keywords, list):
                keywords = ", ".join(keywords)
            sections.append(f"\nKey focus areas: {keywords}")

        # 7. FORMAT (Structure) - How to output?
        if Essential.FORMAT in essentials:
            sections.append(f"\nFormat: {essentials[Essential.FORMAT]}")

        # 8. EXAMPLES (Few-shot) - Show me
        if Essential.EXAMPLES in essentials:
            examples = essentials[Essential.EXAMPLES]
            if isinstance(examples, list):
                sections.append("\nExamples:")
                for i, example in enumerate(examples, 1):
                    sections.append(f"{i}. {example}")
            else:
                sections.append(f"\nExamples: {examples}")

        # 9. CITATIONS (Sources) - Where from?
        if Essential.CITATIONS in essentials:
            sections.append(f"\nSources: {essentials[Essential.CITATIONS]}")

        # 10. CALL (Action) - What next?
        if Essential.CALL in essentials:
            sections.append(f"\n{essentials[Essential.CALL]}")

        prompt = "\n".join(sections)

        # Jobs: "Simplicity is the ultimate sophistication"
        # Keep it clean, focused, beautiful
        return prompt.strip()

    def get_stats(self) -> dict[str, Any]:
        """Get DTE evolution statistics"""
        return {
            "source": self.source,
            "use_case": self.use_case,
            "variants_created": len(self.variants),
            "current_generation": self.generation,
            "total_tests_run": self.total_tests_run,
            "baseline_accuracy": self.baseline_accuracy,
            "total_accuracy_gain": self.total_accuracy_gain,
            "target_accuracy_gain": 0.037,  # +3.7%
            "best_variant": {
                "id": self.best_variant_id,
                "accuracy": self.variants[self.best_variant_id].best_accuracy if self.best_variant_id else None,
                "tests_run": self.variants[self.best_variant_id].tests_run if self.best_variant_id else 0,
            }
            if self.best_variant_id
            else None,
            "progress_to_target": (self.total_accuracy_gain / 0.037 * 100) if self.baseline_accuracy else 0,
        }


# ============================================================================
# PRESET CHEAT SHEETS (Jobs-Quality Defaults)
# ============================================================================


class PresetCheatSheets:
    """
    Preset cheat sheets for common use cases.

    Jobs philosophy: Start with great defaults, evolve to perfection.
    """

    @staticmethod
    def youtube_tier_1_intelligence() -> dict[Essential, Any]:
        """YouTube collection optimized for Tier 1 intelligence"""
        return {
            Essential.ACT: "elite intelligence analyst specializing in AI governance",
            Essential.CONTEXT: "Collecting YouTube content for governance/compliance intelligence. Target: Tier 1 (high-value, actionable insights) ≥60% of items.",
            Essential.OBJECTIVE: "Identify YouTube videos that provide exceptional governance intelligence: EU AI Act analysis, DSA compliance, GDPR implications, model risk management, ethical AI practices.",
            Essential.AUDIENCE: "Regulatory compliance teams, AI governance officers, legal counsel",
            Essential.TONE: "Insanely great - Jobs quality obsession. Only the best insights.",
            Essential.KEYWORDS: [
                "EU AI Act",
                "DSA VLOP",
                "GDPR",
                "model governance",
                "AI ethics",
                "compliance",
                "risk management",
                "transparency",
                "accountability",
            ],
            Essential.FORMAT: "Structured JSON: {title, channel, description, tier_justification, key_insights, timestamp, url}",
            Essential.EXAMPLES: [
                "Tier 1: 'EU AI Act Article 9 Deep Dive' by AI Policy Expert - Actionable compliance checklist",
                "Tier 2: 'AI Trends 2024' by Tech News - General insights, some governance mentions",
                "Tier 3: 'AI Tutorial' by Educator - Technical, no governance relevance",
            ],
            Essential.CITATIONS: "YouTube Data API v3, ATP 5-19 Risk Framework validation",
            Essential.CALL: "Return items with tier classification (1/2/3) and confidence score (0-1). Prioritize quality over quantity.",
        }

    @staticmethod
    def twitter_governance_signals() -> dict[Essential, Any]:
        """Twitter collection for early governance signals"""
        return {
            Essential.ACT: "early warning analyst for AI governance trends",
            Essential.CONTEXT: "Monitoring Twitter for emerging governance issues, regulatory announcements, industry discussions. Focus: signals before they become mainstream.",
            Essential.OBJECTIVE: "Detect early governance signals: regulatory changes, enforcement actions, industry debates, risk incidents.",
            Essential.AUDIENCE: "Risk management teams, policy strategists, C-suite",
            Essential.TONE: "Urgent, focused, reality-distortion (Jobs: make impossibles possible)",
            Essential.KEYWORDS: [
                "breaking",
                "announcement",
                "enforcement",
                "fine",
                "violation",
                "guidance",
                "draft regulation",
                "consultation",
            ],
            Essential.FORMAT: "Structured: {tweet_text, author, timestamp, signal_type, urgency_score, related_regulations}",
            Essential.EXAMPLES: [
                "Tier 1: '@EU_Commission announces Article 52 enforcement guidance' - Direct regulatory impact",
                "Tier 2: 'Industry expert discusses AI Act implications' - Valuable analysis",
                "Tier 3: 'AI is cool' - No governance relevance",
            ],
            Essential.CITATIONS: "Twitter API v2, verified regulatory accounts, industry leaders",
            Essential.CALL: "Flag HIGH urgency items immediately. Include source credibility score.",
        }

    @staticmethod
    def news_api_compliance_tracking() -> dict[Essential, Any]:
        """News API for compliance enforcement tracking"""
        return {
            Essential.ACT: "compliance enforcement tracker",
            Essential.CONTEXT: "Tracking news articles about AI compliance: fines, violations, enforcement actions, regulatory updates.",
            Essential.OBJECTIVE: "Identify compliance enforcement cases that set precedents or reveal enforcement priorities.",
            Essential.AUDIENCE: "Legal teams, compliance officers, risk managers",
            Essential.TONE: "Hard truth - reality-based, no sugar-coating (Jobs: brutal honesty)",
            Essential.KEYWORDS: [
                "fine",
                "penalty",
                "violation",
                "enforcement",
                "investigation",
                "settlement",
                "consent order",
                "regulatory action",
            ],
            Essential.FORMAT: "Structured: {headline, source, date, violation_type, entity, penalty_amount, precedent_value}",
            Essential.EXAMPLES: [
                "Tier 1: 'Company X fined €50M for GDPR/AI Act violations' - Direct precedent",
                "Tier 2: 'Regulator issues guidance on AI transparency' - Important context",
                "Tier 3: 'AI company raises funding' - No compliance relevance",
            ],
            Essential.CITATIONS: "NewsAPI, verified news sources, regulatory press releases",
            Essential.CALL: "Classify precedent value: HIGH/MEDIUM/LOW. Extract enforcement patterns.",
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


async def example_cheat_sheet_fusion():
    """Demonstrate Cheat Sheet Fusion with DTE evolution"""
    print("=== Cheat Sheet Fusion Demo ===\n")

    # Create fusion engine
    fusion = CheatSheetFusion(source="youtube", use_case="tier_1_intelligence", dte_enabled=True, evolution_rate=0.1, target_accuracy=0.60)

    # Create initial variant from preset
    preset_essentials = PresetCheatSheets.youtube_tier_1_intelligence()
    variant_id = fusion.create_variant(preset_essentials)

    print(f"Created variant: {variant_id}\n")
    print("Initial prompt:")
    print("-" * 80)
    print(fusion.generate_prompt(variant_id))
    print("-" * 80)

    # Mock ground truth data for testing
    ground_truth = [
        {"input": "EU AI Act video", "expected_tier": 1},
        {"input": "AI tutorial", "expected_tier": 3},
        {"input": "Governance analysis", "expected_tier": 1},
        # ... more test cases
    ] * 10  # 30 test cases

    # Run DTE tests
    print("\n=== DTE Evolution ===\n")

    for cycle in range(5):
        print(f"\n--- Cycle {cycle + 1} ---")

        # Test current variant
        result = await fusion.test_variant(variant_id, ground_truth)
        print(f"Variant: {variant_id}")
        print(f"Accuracy: {result.accuracy:.1%}")
        print(f"Pass rate: {result.pass_rate:.1%}")
        print(f"Latency: {result.latency_ms:.1f}ms")

        # Check if we hit target
        if fusion.total_accuracy_gain >= 0.037:
            print(f"\n✅ TARGET ACHIEVED: +{fusion.total_accuracy_gain:.1%} accuracy gain!")
            break

        # Evolve
        if result.accuracy < fusion.target_accuracy:
            direction = "improve"
        elif cycle % 2 == 0:
            direction = "explore"
        else:
            direction = "simplify"

        variant_id = fusion.evolve(direction=direction)
        print(f"Evolved → {variant_id} (direction: {direction})")

    # Final stats
    print("\n=== Final Statistics ===\n")
    stats = fusion.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Show best prompt
    print("\n=== Best Prompt ===\n")
    print(fusion.generate_prompt())


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_cheat_sheet_fusion())
