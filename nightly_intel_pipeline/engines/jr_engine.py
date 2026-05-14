# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
JR Engine - Purpose → Reasons → Brakes Scoring System
Evaluates content for strategic value and tier classification
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import structlog
from anthropic import Anthropic

from ..config import JR_ENGINE_CONFIG

logger = structlog.get_logger(__name__)


class Tier(Enum):
    """Tier classification for content"""

    TIER_1 = 1  # Executive review required
    TIER_2 = 2  # Auto-action approved
    TIER_3 = 3  # Archive for later
    TIER_4 = 4  # Low priority


@dataclass
class JRScore:
    """
    JR Engine scoring result

    Purpose → Reasons → Brakes framework evaluation
    """

    # Core scores (0-100)
    purpose_alignment: float  # How well does it align with MLOps/AI goals
    technical_merit: float  # Quality of implementation
    adoption_potential: float  # Community traction, growth trajectory
    risk_assessment: float  # ATP 5-19 risk level (inverse - lower risk = higher score)

    # Composite score
    total_score: float

    # Tier classification
    tier: Tier

    # ATP 5-19 risk level
    atp_risk_level: str  # RA-1, RA-2, RA-3, RA-4

    # Reasoning
    purpose_reasoning: str
    technical_reasoning: str
    adoption_reasoning: str
    risk_reasoning: str
    brakes: list[str]  # Concerns/blockers to consider

    # Metadata
    content_type: str  # "github_repo", "arxiv_paper", "web_content"
    content_id: str  # Repository name, paper ID, URL

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        d = asdict(self)
        d["tier"] = self.tier.value
        return d


class JREngine:
    """
    Judge #6 Governance Engine - JR Scoring System

    Implements Purpose → Reasons → Brakes framework using Claude API
    """

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or JR_ENGINE_CONFIG["api_key"]
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")

        self.model = model or JR_ENGINE_CONFIG["model"]
        self.client = Anthropic(api_key=self.api_key)
        self.config = JR_ENGINE_CONFIG

        logger.info("jr_engine_initialized", model=self.model)

    def _build_scoring_prompt(self, content: str, content_type: str, content_id: str) -> str:
        """
        Build prompt for JR scoring

        Uses Purpose → Reasons → Brakes framework
        """
        criteria = self.config["scoring_criteria"]

        prompt = f"""You are the JR Engine - a strategic evaluation system using the Purpose → Reasons → Brakes framework.

Evaluate the following {content_type} for strategic value in MLOps/AI infrastructure context.

Content ID: {content_id}
Content Type: {content_type}

CONTENT:
{content[:8000]}  # Truncate to reasonable length

---

EVALUATION FRAMEWORK:

1. PURPOSE ALIGNMENT (Weight: {criteria["purpose_alignment"] * 100}%)
   - How well does this align with MLOps/AI infrastructure goals?
   - Does it solve real problems in ML deployment, monitoring, governance?
   - Is it relevant to our strategic objectives?
   Score: 0-100

2. TECHNICAL MERIT (Weight: {criteria["technical_merit"] * 100}%)
   - Quality of implementation/research
   - Architectural soundness
   - Innovation and best practices
   - Code quality (if applicable)
   Score: 0-100

3. ADOPTION POTENTIAL (Weight: {criteria["adoption_potential"] * 100}%)
   - Community traction (stars, citations, downloads)
   - Growth trajectory
   - Industry adoption signals
   - Maintainer activity and health
   Score: 0-100

4. RISK ASSESSMENT (Weight: {criteria["risk_assessment"] * 100}%)
   Evaluate using ATP 5-19 Risk Management Framework:
   - RA-1 (Catastrophic): Critical vulnerabilities, legal issues, existential risks
   - RA-2 (Critical): Security concerns, major breaking changes, high complexity
   - RA-3 (Moderate): Minor issues, manageable risks
   - RA-4 (Low): Minimal risk, well-tested, stable

   Assign ATP Risk Level and compute risk score (RA-4=100, RA-3=75, RA-2=50, RA-1=25)

5. BRAKES (Concerns/Blockers)
   - What are the red flags?
   - What could go wrong?
   - What dependencies or constraints exist?
   - What needs careful consideration?

OUTPUT FORMAT (JSON):
{{
  "purpose_alignment": <score 0-100>,
  "purpose_reasoning": "<1-2 sentence explanation>",
  "technical_merit": <score 0-100>,
  "technical_reasoning": "<1-2 sentence explanation>",
  "adoption_potential": <score 0-100>,
  "adoption_reasoning": "<1-2 sentence explanation>",
  "risk_assessment": <score 0-100>,
  "risk_reasoning": "<1-2 sentence explanation>",
  "atp_risk_level": "<RA-1|RA-2|RA-3|RA-4>",
  "brakes": ["<concern 1>", "<concern 2>", ...],
  "recommendation": "<Executive summary in 1-2 sentences>"
}}

Respond with ONLY the JSON object, no additional text.
"""
        return prompt

    def score_content(self, content: str, content_type: str, content_id: str) -> JRScore:
        """
        Score content using JR Engine

        Args:
            content: Text content to evaluate
            content_type: Type of content ("github_repo", "arxiv_paper", "web_content")
            content_id: Identifier (repo name, paper ID, URL)

        Returns:
            JRScore object with evaluation results
        """
        try:
            logger.info("jr_scoring_started", content_type=content_type, content_id=content_id)

            # Build prompt
            prompt = self._build_scoring_prompt(content, content_type, content_id)

            # Call Claude API
            response = self.client.messages.create(model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}])

            # Parse response
            response_text = response.content[0].text.strip()

            # Extract JSON (handle code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            result = json.loads(response_text)

            # Calculate total score
            criteria = self.config["scoring_criteria"]
            total_score = (
                result["purpose_alignment"] * criteria["purpose_alignment"]
                + result["technical_merit"] * criteria["technical_merit"]
                + result["adoption_potential"] * criteria["adoption_potential"]
                + result["risk_assessment"] * criteria["risk_assessment"]
            )

            # Determine tier
            tier = self._classify_tier(total_score)

            # Create JRScore object
            jr_score = JRScore(
                purpose_alignment=result["purpose_alignment"],
                technical_merit=result["technical_merit"],
                adoption_potential=result["adoption_potential"],
                risk_assessment=result["risk_assessment"],
                total_score=total_score,
                tier=tier,
                atp_risk_level=result["atp_risk_level"],
                purpose_reasoning=result["purpose_reasoning"],
                technical_reasoning=result["technical_reasoning"],
                adoption_reasoning=result["adoption_reasoning"],
                risk_reasoning=result["risk_reasoning"],
                brakes=result["brakes"],
                content_type=content_type,
                content_id=content_id,
            )

            logger.info("jr_scoring_complete", content_id=content_id, total_score=total_score, tier=tier.value, atp_risk=result["atp_risk_level"])

            return jr_score

        except Exception as e:
            logger.error("jr_scoring_error", content_id=content_id, error=str(e))
            # Return default low score on error
            return self._create_error_score(content_type, content_id, str(e))

    def _classify_tier(self, total_score: float) -> Tier:
        """
        Classify content into tier based on total score

        Tier 1: >= 85 (Executive review)
        Tier 2: >= 70 (Auto-action)
        Tier 3: >= 50 (Archive)
        Tier 4: < 50 (Low priority)
        """
        thresholds = self.config["tier_thresholds"]

        if total_score >= thresholds["tier_1"]:
            return Tier.TIER_1
        elif total_score >= thresholds["tier_2"]:
            return Tier.TIER_2
        elif total_score >= thresholds["tier_3"]:
            return Tier.TIER_3
        else:
            return Tier.TIER_4

    def _create_error_score(self, content_type: str, content_id: str, error: str) -> JRScore:
        """Create a default error score"""
        return JRScore(
            purpose_alignment=0,
            technical_merit=0,
            adoption_potential=0,
            risk_assessment=0,
            total_score=0,
            tier=Tier.TIER_4,
            atp_risk_level="RA-1",
            purpose_reasoning=f"Error during scoring: {error}",
            technical_reasoning="N/A",
            adoption_reasoning="N/A",
            risk_reasoning="Scoring failed",
            brakes=["Scoring error occurred"],
            content_type=content_type,
            content_id=content_id,
        )

    def score_github_repo(self, flattened_content: str, repo_name: str) -> JRScore:
        """
        Score a GitHub repository

        Args:
            flattened_content: Flattened repository content
            repo_name: Repository name (owner/repo)

        Returns:
            JRScore object
        """
        return self.score_content(content=flattened_content, content_type="github_repo", content_id=repo_name)

    def score_arxiv_paper(self, paper_metadata: str, paper_id: str) -> JRScore:
        """
        Score an arXiv paper

        Args:
            paper_metadata: Paper metadata and abstract
            paper_id: arXiv paper ID

        Returns:
            JRScore object
        """
        return self.score_content(content=paper_metadata, content_type="arxiv_paper", content_id=paper_id)

    def batch_score(self, items: list[tuple[str, str, str]]) -> list[JRScore]:
        """
        Score multiple items

        Args:
            items: List of (content, content_type, content_id) tuples

        Returns:
            List of JRScore objects
        """
        scores = []

        for i, (content, content_type, content_id) in enumerate(items, 1):
            logger.info("batch_scoring", index=i, total=len(items), content_id=content_id)

            score = self.score_content(content, content_type, content_id)
            scores.append(score)

            # Rate limiting between API calls
            import time

            if i < len(items):
                time.sleep(1)  # 1 second between requests

        return scores

    def generate_tier_report(self, scores: list[JRScore]) -> str:
        """
        Generate a tier-based report of scores

        Returns:
            Markdown-formatted report
        """
        # Group by tier
        by_tier: dict[Tier, list[JRScore]] = {Tier.TIER_1: [], Tier.TIER_2: [], Tier.TIER_3: [], Tier.TIER_4: []}

        for score in scores:
            by_tier[score.tier].append(score)

        # Build report
        report_parts = [
            "# JR Engine Tier Classification Report",
            f"**Generated:** {__import__('datetime').datetime.now().isoformat()}",
            f"**Total Items Scored:** {len(scores)}",
            "",
        ]

        for tier in [Tier.TIER_1, Tier.TIER_2, Tier.TIER_3, Tier.TIER_4]:
            tier_scores = by_tier[tier]
            tier_scores.sort(key=lambda x: x.total_score, reverse=True)

            tier_desc = {
                Tier.TIER_1: "Executive Review Required",
                Tier.TIER_2: "Auto-Action Approved",
                Tier.TIER_3: "Archive for Later",
                Tier.TIER_4: "Low Priority",
            }

            report_parts.append(f"## Tier {tier.value}: {tier_desc[tier]} ({len(tier_scores)} items)")
            report_parts.append("")

            for score in tier_scores:
                report_parts.append(f"### {score.content_id}")
                report_parts.append(f"**Total Score:** {score.total_score:.1f}")
                report_parts.append(f"**ATP Risk:** {score.atp_risk_level}")
                report_parts.append(f"**Type:** {score.content_type}")
                report_parts.append("")
                report_parts.append("**Scores:**")
                report_parts.append(f"- Purpose Alignment: {score.purpose_alignment:.0f} - {score.purpose_reasoning}")
                report_parts.append(f"- Technical Merit: {score.technical_merit:.0f} - {score.technical_reasoning}")
                report_parts.append(f"- Adoption Potential: {score.adoption_potential:.0f} - {score.adoption_reasoning}")
                report_parts.append(f"- Risk Assessment: {score.risk_assessment:.0f} - {score.risk_reasoning}")
                report_parts.append("")

                if score.brakes:
                    report_parts.append("**Brakes (Concerns):**")
                    for brake in score.brakes:
                        report_parts.append(f"- {brake}")
                    report_parts.append("")

                report_parts.append("---")
                report_parts.append("")

        return "\n".join(report_parts)


# Convenience functions
def score_content(content: str, content_type: str, content_id: str) -> JRScore:
    """
    Score content using JR Engine

    Usage:
        score = score_content(repo_content, "github_repo", "owner/repo")
    """
    engine = JREngine()
    return engine.score_content(content, content_type, content_id)


def classify_tier(total_score: float) -> Tier:
    """
    Classify a score into a tier

    Usage:
        tier = classify_tier(87.5)  # Returns Tier.TIER_1
    """
    engine = JREngine()
    return engine._classify_tier(total_score)
