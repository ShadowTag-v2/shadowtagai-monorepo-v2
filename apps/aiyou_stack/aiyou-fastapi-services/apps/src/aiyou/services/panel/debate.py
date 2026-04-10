"""
Panel Debate Architecture for Complex Content Moderation
Multi-agent consensus-building for edge cases (Gemini Powered)
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)


class DebateRole(StrEnum):
    """Roles in panel debate"""

    PROSECUTOR = "prosecutor"  # Argues for rejection
    DEFENDER = "defender"  # Argues for approval
    JUDGE = "judge"  # Makes final decision
    MODERATOR = "moderator"  # Facilitates discussion


@dataclass
class DebateArgument:
    """Single argument in the debate"""

    role: DebateRole
    model_name: str
    argument: str
    evidence: dict[str, Any]
    confidence: float  # 0.0-1.0
    timestamp: datetime


@dataclass
class DebateResult:
    """Final result of panel debate"""

    decision: str  # "APPROVE", "REJECT", "ESCALATE"
    confidence: float
    reasoning: str
    arguments_for: list[DebateArgument]
    arguments_against: list[DebateArgument]
    consensus_score: float  # 0.0-1.0, how much agreement
    duration_seconds: float
    models_used: list[str]


class PanelDebate:
    """
    Multi-agent debate system for complex moderation decisions

    Uses multiple AI perspectives:
    1. Prosecutor argues for content rejection
    2. Defender argues for content approval
    3. Judge synthesizes arguments and decides
    """

    def __init__(
        self,
        gemini_client: Any,
        claude_client: Any = None,
        confidence_threshold: float = 0.80,
        max_rounds: int = 3,
    ):
        """
        Initialize panel debate system.

        Note: claude_client is deprecated and ignored.
        """
        self.client = gemini_client  # Assumes vertexai/gemini client
        self.confidence_threshold = confidence_threshold
        self.max_rounds = max_rounds

        # We reuse one model instance if possible, or create new ones if client is just a config wrapper
        # For this implementation, we assume `gemini_client` is a ready-to-use vertexai object or we use the global vertexai
        self.model = GenerativeModel("gemini-1.5-pro-001")

    async def should_debate(self, initial_analysis: dict[str, Any]) -> bool:
        """Determine if content requires panel debate"""
        confidence = initial_analysis.get("moderation_confidence", 100) / 100.0

        if confidence < self.confidence_threshold:
            return True

        if initial_analysis.get("moderation_category") == "safe" and confidence < 0.90:
            return True

        return initial_analysis.get("creator_tier") == "premium"

    async def conduct_debate(
        self, content_analysis: dict[str, Any], content_metadata: dict[str, Any]
    ) -> DebateResult:
        """Conduct multi-round panel debate"""
        start_time = datetime.utcnow()
        arguments_for = []
        arguments_against = []

        logger.info(f"Starting panel debate for content {content_metadata.get('content_id')}")

        # Round 1: Prosecutor (Gemini)
        prosecutor_arg = await self._prosecutor_argument(content_analysis, content_metadata)
        arguments_against.append(prosecutor_arg)

        # Round 2: Defender (Gemini)
        defender_arg = await self._defender_argument(
            content_analysis, content_metadata, prosecutor_arg
        )
        arguments_for.append(defender_arg)

        # Round 3: Rebuttal (optional)
        if prosecutor_arg.confidence > 0.75:
            prosecutor_rebuttal = await self._prosecutor_rebuttal(content_analysis, defender_arg)
            arguments_against.append(prosecutor_rebuttal)

        # Judge Decision
        judge_decision = await self._judge_decision(
            content_analysis, content_metadata, arguments_for, arguments_against
        )

        consensus_score = self._calculate_consensus(arguments_for, arguments_against)
        duration = (datetime.utcnow() - start_time).total_seconds()

        result = DebateResult(
            decision=judge_decision["decision"],
            confidence=judge_decision["confidence"],
            reasoning=judge_decision["reasoning"],
            arguments_for=arguments_for,
            arguments_against=arguments_against,
            consensus_score=consensus_score,
            duration_seconds=duration,
            models_used=["gemini-1.5-pro", "gemini-1.5-pro", "gemini-1.5-pro"],
        )

        logger.info(f"Debate concluded: {result.decision} (confidence: {result.confidence:.2f})")
        return result

    async def _generate(self, prompt: str, temperature: float = 0.5) -> str:
        """Internal helper to generate content"""
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": temperature,
                },
            )
            return response.text
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return ""

    async def _prosecutor_argument(
        self, content_analysis: dict[str, Any], content_metadata: dict[str, Any]
    ) -> DebateArgument:
        prompt = f"""You are a content moderation prosecutor. Build the strongest case for REJECTING this content.

Content Analysis:
{self._format_analysis(content_analysis)}

Platform Policy:
- Zero tolerance for violence, hate speech, illegal content
- Protect brand safety
- Prioritize user safety

Your task:
1. Identify every policy violation
2. Consider worst-case interpretations
3. Cite specific policy sections

Provide output in JSON format:
{{
  "reasoning": "...",
  "violations": {{ "violation": "explanation" }},
  "confidence": 85
}}
"""
        response_text = await self._generate(prompt, temperature=0.7)
        parsed = self._parse_json_safe(response_text)

        return DebateArgument(
            role=DebateRole.PROSECUTOR,
            model_name="gemini-1.5-pro",
            argument=parsed.get("reasoning", "Error generating argument"),
            evidence=parsed.get("violations", {}),
            confidence=parsed.get("confidence", 50) / 100.0,
            timestamp=datetime.utcnow(),
        )

    async def _defender_argument(
        self,
        content_analysis: dict[str, Any],
        content_metadata: dict[str, Any],
        prosecutor_arg: DebateArgument,
    ) -> DebateArgument:
        prompt = f"""You are a content moderation defender. Build the case for APPROVING this content.

Content Analysis:
{self._format_analysis(content_analysis)}

Prosecutor's Argument:
{prosecutor_arg.argument}

Platform Values:
- Creator freedom
- Context matters (educational/artistic)
- Avoid over-moderation

Provide output in JSON format:
{{
  "reasoning": "...",
  "counter_arguments": {{ "point": "counter" }},
  "confidence": 80
}}
"""
        response_text = await self._generate(prompt, temperature=0.7)
        parsed = self._parse_json_safe(response_text)

        return DebateArgument(
            role=DebateRole.DEFENDER,
            model_name="gemini-1.5-pro",
            argument=parsed.get("reasoning", "Error generating defense"),
            evidence=parsed.get("counter_arguments", {}),
            confidence=parsed.get("confidence", 50) / 100.0,
            timestamp=datetime.utcnow(),
        )

    async def _prosecutor_rebuttal(
        self, content_analysis: dict[str, Any], defender_arg: DebateArgument
    ) -> DebateArgument:
        prompt = f"""Prosecutor rebuttal.

Defender argued:
{defender_arg.argument}

Counter these points. Focus on why context doesn't excuse violations.

Provide output in JSON format:
{{
  "reasoning": "...",
  "confidence": 85
}}
"""
        response_text = await self._generate(prompt, temperature=0.7)
        parsed = self._parse_json_safe(response_text)

        return DebateArgument(
            role=DebateRole.PROSECUTOR,
            model_name="gemini-1.5-pro",
            argument=parsed.get("reasoning", "Maintain rejection recommendation"),
            evidence={},
            confidence=parsed.get("confidence", 60) / 100.0,
            timestamp=datetime.utcnow(),
        )

    async def _judge_decision(
        self,
        content_analysis: dict[str, Any],
        content_metadata: dict[str, Any],
        arguments_for: list[DebateArgument],
        arguments_against: list[DebateArgument],
    ) -> dict[str, Any]:
        prompt = f"""You are the judge.

Content Analysis:
{self._format_analysis(content_analysis)}

Arguments FOR Approval:
{self._format_arguments(arguments_for)}

Arguments AGAINST (Rejection):
{self._format_arguments(arguments_against)}

Make FINAL decision: APPROVE, REJECT, or ESCALATE.

Provide output in JSON format:
{{
  "decision": "APPROVE|REJECT|ESCALATE",
  "confidence": 90,
  "reasoning": "...",
  "conditions": ["cond1"]
}}
"""
        response_text = await self._generate(prompt, temperature=0.1)
        parsed = self._parse_json_safe(response_text)

        return {
            "decision": parsed.get("decision", "ESCALATE"),
            "confidence": parsed.get("confidence", 50) / 100.0,
            "reasoning": parsed.get("reasoning", "Unable to decide"),
            "conditions": parsed.get("conditions", []),
        }

    def _calculate_consensus(
        self,
        arguments_for: list[DebateArgument],
        arguments_against: list[DebateArgument],
    ) -> float:
        if not arguments_for and not arguments_against:
            return 0.5

        total_for = sum(arg.confidence for arg in arguments_for)
        total_against = sum(arg.confidence for arg in arguments_against)

        if total_for + total_against == 0:
            return 0.5

        max_side = max(total_for, total_against)
        total = total_for + total_against
        return max_side / total

    def _format_analysis(self, analysis: dict[str, Any]) -> str:
        return json.dumps(analysis, indent=2)

    def _format_arguments(self, arguments: list[DebateArgument]) -> str:
        return "\n".join([f"{arg.role}: {arg.argument}" for arg in arguments])

    def _parse_json_safe(self, text: str) -> dict[str, Any]:
        """Attempt to parse JSON from text, handling code blocks"""
        try:
            clean = text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            return {}
