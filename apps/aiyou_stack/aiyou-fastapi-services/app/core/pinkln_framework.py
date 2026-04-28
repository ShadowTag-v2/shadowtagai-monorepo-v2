# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pinkln Ultrathink Framework
Jobs-inspired multi-agent ecosystem with DTE evolution, Glicko ratings, and wealth acceleration

Persona: Ultrathink Jobs—breathe/urgency/beauty/details/simplify/Boy Scout
Frameworks: CoT/ToT/RCR/RTF-TAG-BAB-CARE-RISE fused
Evolution: DTE (Dynamic Test Evolution) with GRPO/PPO comparison
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class UltrathinkPersona(StrEnum):
    """Ultrathink Jobs persona modes"""

    PAUSE_BREATHE = "pause_breathe"  # Take a moment to think
    URGENCY = "urgency"  # Ship it, make it happen
    BEAUTY = "beauty"  # Insanely great design
    DETAILS = "details"  # Sweat the details
    SIMPLIFY = "simplify"  # Remove everything unnecessary
    BOY_SCOUT = "boy_scout"  # Leave it better than you found it


class ReasoningFramework(StrEnum):
    """Reasoning frameworks for ultrathink"""

    COT = "chain_of_thought"  # Step-by-step reasoning
    TOT = "tree_of_thoughts"  # Explore multiple paths
    RCR = "reason_critique_refine"  # Self-improvement loop
    RTF = "reason_then_fix"  # Identify and correct
    TAG = "think_act_gather"  # Plan, execute, learn
    BAB = "build_analyze_build"  # Iterative construction
    CARE = "context_analyze_respond_evaluate"  # Comprehensive approach
    RISE = "reason_iterate_synthesize_elevate"  # Progressive enhancement


@dataclass
class CheatSheetEssentials:
    """10 Essential Elements (evolved from 21)
    For maximum prompt effectiveness
    """

    tone: str = "professional"  # Voice and style
    format: str = "structured"  # Output structure
    act: str = "expert"  # Role to assume
    objective: str = ""  # Clear goal
    context: str = ""  # Background information
    keywords: list[str] = field(default_factory=list)  # Key terms to use
    examples: list[str] = field(default_factory=list)  # Sample outputs
    audience: str = "technical"  # Target reader
    citations: bool = True  # Include sources
    call_to_action: str = ""  # Next steps

    def to_prompt(self) -> str:
        """Convert to structured prompt"""
        prompt_parts = [
            f"Act as: {self.act}",
            f"Objective: {self.objective}",
            f"Context: {self.context}",
            f"Tone: {self.tone}",
            f"Format: {self.format}",
            f"Audience: {self.audience}",
        ]

        if self.keywords:
            prompt_parts.append(f"Keywords: {', '.join(self.keywords)}")

        if self.examples:
            prompt_parts.append("Examples:")
            for i, ex in enumerate(self.examples, 1):
                prompt_parts.append(f"  {i}. {ex}")

        if self.citations:
            prompt_parts.append("Include citations and sources")

        if self.call_to_action:
            prompt_parts.append(f"Next step: {self.call_to_action}")

        return "\n".join(prompt_parts)


@dataclass
class WealthLeakDetection:
    """Wealth-Planning Model: Spot leaks, redesign funnels
    Structure: Hard truth / Plan / Challenge
    """

    leak_type: str  # "conversion", "retention", "upsell", "viral"
    severity: float  # 0.0 to 1.0
    current_rate: float
    target_rate: float
    hard_truth: str  # Honest assessment
    plan: str  # Concrete redesign steps
    challenge: str  # What makes this hard

    @property
    def potential_gain(self) -> float:
        """Calculate potential revenue gain"""
        return (self.target_rate - self.current_rate) * self.severity


@dataclass
class TrustValidation:
    """Trust Structure: Security, memory compounding, validations
    Boy Scout improvements, Reality Distortion for impossibles
    """

    security_score: float  # 0.0 to 1.0
    memory_compounds: bool
    critique: str  # Self-critique
    assumptions: list[str]  # Stated assumptions
    boy_scout_improvements: list[str]  # How we left it better
    reality_distortion: str | None = None  # For "impossible" challenges

    def validate(self) -> bool:
        """Validate trust structure"""
        return (
            self.security_score >= 0.8
            and self.memory_compounds
            and len(self.critique) > 0
            and len(self.assumptions) > 0
        )


class PinklnFramework:
    """Pinkln Ultrathink Framework Orchestrator

    Integrates:
    - Multi-agent reasoning (debates, code crafters)
    - DTE self-evolution
    - Glicko ratings
    - Cheat sheet fusion
    - Wealth acceleration
    """

    def __init__(self, persona_iq: int = 160):
        self.persona_iq = persona_iq
        self.active_persona = UltrathinkPersona.PAUSE_BREATHE
        self.reasoning_stack: list[ReasoningFramework] = []
        logger.info(f"Pinkln Framework initialized at IQ {persona_iq}")

    def set_persona(self, persona: UltrathinkPersona):
        """Switch ultrathink persona mode"""
        self.active_persona = persona
        logger.info(f"Switched to {persona.value} mode")

    def apply_reasoning(self, framework: ReasoningFramework) -> dict[str, Any]:
        """Apply reasoning framework"""
        self.reasoning_stack.append(framework)

        return {
            "framework": framework.value,
            "persona": self.active_persona.value,
            "iq": self.persona_iq,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def fuse_cheat_sheet(self, essentials: CheatSheetEssentials) -> str:
        """Fuse cheat sheet with current reasoning framework
        Returns evolved prompt
        """
        base_prompt = essentials.to_prompt()

        # Apply ultrathink enhancement
        enhancement = f"\nUltrathink Mode: {self.active_persona.value} (IQ {self.persona_iq})"

        # Apply reasoning framework
        if self.reasoning_stack:
            frameworks = " → ".join([f.value for f in self.reasoning_stack])
            enhancement += f"\nReasoning Path: {frameworks}"

        return base_prompt + enhancement

    def detect_wealth_leak(
        self,
        leak_type: str,
        current_rate: float,
        target_rate: float,
    ) -> WealthLeakDetection:
        """Detect and diagnose wealth leaks
        Running at IQ {self.persona_iq} for maximum foresight
        """
        severity = min(1.0, (target_rate - current_rate) / target_rate)

        # Generate hard truth
        hard_truth = self._generate_hard_truth(leak_type, current_rate, target_rate)

        # Generate plan
        plan = self._generate_plan(leak_type, severity)

        # Generate challenge
        challenge = self._generate_challenge(leak_type, severity)

        return WealthLeakDetection(
            leak_type=leak_type,
            severity=severity,
            current_rate=current_rate,
            target_rate=target_rate,
            hard_truth=hard_truth,
            plan=plan,
            challenge=challenge,
        )

    def _generate_hard_truth(self, leak_type: str, current: float, target: float) -> str:
        """Generate honest assessment"""
        gap = target - current
        gap_pct = (gap / target) * 100

        truths = {
            "conversion": f"Your conversion rate is {gap_pct:.1f}% below target. You're leaving money on the table every day.",
            "retention": f"Retention is bleeding {gap_pct:.1f}%. Fix this or growth becomes a leaky bucket.",
            "upsell": f"You're missing {gap_pct:.1f}% of upsell opportunities. Your customers want to pay more—let them.",
            "viral": f"Viral coefficient is {gap_pct:.1f}% short. Without organic growth, CAC will kill you.",
        }

        return truths.get(leak_type, f"{gap_pct:.1f}% gap between current and target")

    def _generate_plan(self, leak_type: str, severity: float) -> str:
        """Generate concrete redesign plan"""
        plans = {
            "conversion": "1. A/B test CTA placement, 2. Reduce form friction, 3. Add social proof above fold, 4. Implement exit-intent offers",
            "retention": "1. Build onboarding sequence, 2. Identify churn signals, 3. Create re-engagement campaigns, 4. Add usage analytics",
            "upsell": "1. Segment by usage, 2. Create tiered pricing, 3. Build upgrade prompts at friction points, 4. Add premium features",
            "viral": "1. Built-in sharing incentives, 2. Referral program, 3. Social proof mechanics, 4. Content worth sharing",
        }

        base_plan = plans.get(
            leak_type,
            "1. Diagnose root cause, 2. Test solutions, 3. Scale what works",
        )

        if severity > 0.5:
            base_plan = "URGENT: " + base_plan

        return base_plan

    def _generate_challenge(self, leak_type: str, severity: float) -> str:
        """Generate honest challenge assessment"""
        challenges = {
            "conversion": "Need to test without breaking current funnel. Data takes time. Engineers are busy.",
            "retention": "Requires product changes, not just marketing. Long feedback loops. Hard to isolate causes.",
            "upsell": "Risk alienating existing customers. Pricing psychology is hard. Needs new features to justify tiers.",
            "viral": "Can't force virality. Requires product excellence. May need fundamental redesign.",
        }

        return challenges.get(
            leak_type,
            "Execution is hard. Resources are constrained. Must prove ROI first.",
        )

    def validate_trust(
        self,
        security_score: float,
        memory_compounds: bool,
        critique: str,
        assumptions: list[str],
    ) -> TrustValidation:
        """Validate trust structure with Boy Scout improvements"""
        # Generate Boy Scout improvements
        improvements = [
            "Added explicit security validation",
            "Documented all assumptions",
            "Self-critique integrated into process",
            "Memory compounding enabled for learning",
        ]

        # Add reality distortion for high-IQ impossible challenges
        reality_distortion = None
        if self.persona_iq >= 160:
            reality_distortion = "At IQ 160: What looks impossible is just a design constraint to overcome. Ship anyway."

        validation = TrustValidation(
            security_score=security_score,
            memory_compounds=memory_compounds,
            critique=critique,
            assumptions=assumptions,
            boy_scout_improvements=improvements,
            reality_distortion=reality_distortion,
        )

        if not validation.validate():
            logger.warning("Trust validation failed - security or memory issues")

        return validation
