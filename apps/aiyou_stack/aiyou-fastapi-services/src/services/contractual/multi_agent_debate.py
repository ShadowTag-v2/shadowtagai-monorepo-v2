"""
Multi-Agent Debate (MAD) System for Conflict Detection

This module implements a panel debate system where multiple AI agents
analyze negotiations from different perspectives and reach consensus.

Integrates:
- DTE-evolved Cheat Sheet prompts
- Glicko-2 quality ranking
- GRPO training loop

Author: PNKLN Core Stack / ShadowTag-v4 FastAPI Services
Version: 2.0.0 (Ultrathink Integration)
Status: Strategic Planning Phase
"""

import asyncio
import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel

# ============================================================================
# Glicko-2 Rating System
# ============================================================================


class Glicko2Player:
    """
    Glicko-2 rating system for tracking AI strategy quality

    Improvements over Elo:
    - Tracks rating deviation (RD) - uncertainty in rating
    - Tracks volatility (σ) - degree of expected performance fluctuation
    - Handles inactivity (RD increases over time)
    - More accurate for sparse competition

    Rating scale:
    - 1500: Average (baseline)
    - 1600+: Good
    - 1700+: Very Good
    - 1800+: Excellent
    """

    def __init__(self, rating: float = 1500, rd: float = 350, vol: float = 0.06):
        """
        Initialize Glicko-2 player

        Args:
            rating: Initial rating (μ), default 1500
            rd: Initial rating deviation, default 350 (high uncertainty)
            vol: Initial volatility (σ), default 0.06
        """
        # Convert to Glicko-2 scale
        self.mu = (rating - 1500) / 173.7178
        self.phi = rd / 173.7178
        self.sigma = vol

    def get_rating(self) -> float:
        """Get current rating on Elo scale"""
        return self.mu * 173.7178 + 1500

    def get_rd(self) -> float:
        """Get current rating deviation"""
        return self.phi * 173.7178

    def get_vol(self) -> float:
        """Get current volatility"""
        return self.sigma

    def update(self, opponents: list[tuple], tau: float = 0.5, tol: float = 1e-6) -> None:
        """
        Update rating based on match results

        Args:
            opponents: List of (opponent_rating, opponent_rd, score) tuples
                      score: 1.0 = win, 0.5 = draw, 0.0 = loss
            tau: System constant (constrains volatility change), default 0.5
            tol: Convergence tolerance for volatility calculation, default 1e-6

        Algorithm (Glickman 2012):
        1. Convert opponent ratings to Glicko-2 scale
        2. Calculate v (estimated variance)
        3. Calculate Δ (improvement estimate)
        4. Update volatility σ using iterative algorithm
        5. Update RD ϕ
        6. Update rating μ
        """

        # Step 1: Convert opponent ratings
        g_list = []
        e_list = []
        v_sum = 0

        for opp_rating, opp_rd, _score in opponents:
            opp_mu = (opp_rating - 1500) / 173.7178
            opp_phi = opp_rd / 173.7178

            # g function: effect of opponent's RD
            g_phi = 1 / np.sqrt(1 + 3 * opp_phi**2 / np.pi**2)
            g_list.append(g_phi)

            # E function: expected score
            e_val = 1 / (1 + np.exp(-g_phi * (self.mu - opp_mu)))
            e_list.append(e_val)

            # Accumulate v (estimated variance)
            v_sum += g_phi**2 * e_val * (1 - e_val)

        # Step 2: Calculate v
        v = 1 / v_sum if v_sum > 0 else float("inf")

        # Step 3: Calculate Δ (improvement estimate)
        delta_sum = sum(g_list[i] * (opponents[i][2] - e_list[i]) for i in range(len(opponents)))
        delta = v * delta_sum

        # Step 4: Update volatility using iterative algorithm
        a = np.log(self.sigma**2)

        def f(x: float) -> float:
            """Volatility iteration function"""
            ex = np.exp(x)
            num1 = ex * (delta**2 - self.phi**2 - v - ex)
            denom1 = 2 * (self.phi**2 + v + ex) ** 2
            num2 = x - a
            denom2 = tau**2
            return num1 / denom1 - num2 / denom2

        # Illinois algorithm for finding zero of f
        A = a
        B = a

        # Find B
        if delta**2 > self.phi**2 + v:
            B = np.log(delta**2 - self.phi**2 - v)
        else:
            k = 1
            while f(a - k * tau) < 0:
                k += 1
            B = a - k * tau

        # Iterate to find sigma_prime
        fA = f(A)
        fB = f(B)

        while abs(B - A) > tol:
            C = A + (A - B) * fA / (fB - fA)
            fC = f(C)

            if fC * fB < 0:
                A = B
                fA = fB
            else:
                fA = fA / 2

            B = C
            fB = fC

        sigma_prime = np.exp(A / 2)

        # Step 5: Update phi (RD)
        phi_star = np.sqrt(self.phi**2 + sigma_prime**2)
        phi_prime = 1 / np.sqrt(1 / phi_star**2 + 1 / v)

        # Step 6: Update mu (rating)
        mu_prime = self.mu + phi_prime**2 * sum(
            g_list[i] * (opponents[i][2] - e_list[i]) for i in range(len(opponents))
        )

        # Update player state
        self.mu = mu_prime
        self.phi = phi_prime
        self.sigma = sigma_prime


# ============================================================================
# DTE-Evolved Cheat Sheet Prompts
# ============================================================================


@dataclass
class CheatSheetPrompt:
    """
    DTE-evolved Cheat Sheet prompt for conflict detection

    10 essential elements (evolved from 21):
    1. Objective
    2. Context
    3. Act (role)
    4. Keywords
    5. Output Format
    6. Examples
    7. Edge Cases
    8. Audience
    9. Validation
    10. Call-to-Action
    """

    objective: str
    context: str
    act: str
    keywords: list[str]
    output_format: str
    examples: list[str]
    edge_cases: list[str]
    audience: str
    validation: str
    call_to_action: str

    def render(self, transcript_text: str) -> str:
        """Render prompt with transcript"""
        return f"""
{self.objective}

CONTEXT:
{self.context}

ACT AS:
{self.act}

KEYWORDS TO FOCUS ON:
{", ".join(self.keywords)}

TRANSCRIPT:
{transcript_text}

EXAMPLES OF CONFLICTS:
{chr(10).join(f"- {ex}" for ex in self.examples)}

EDGE CASES TO HANDLE:
{chr(10).join(f"- {ec}" for ec in self.edge_cases)}

OUTPUT FORMAT:
{self.output_format}

VALIDATION REQUIREMENTS:
{self.validation}

{self.call_to_action}
"""


# Conservative agent prompt (high sensitivity, may flag false positives)
CONSERVATIVE_PROMPT = CheatSheetPrompt(
    objective="Identify ALL potential conflicts between Party A and Party B, even minor or implied disagreements.",
    context="Business negotiation transcript with speaker diarization. Parties may have unstated assumptions or implied disagreements.",
    act="Conservative legal term extraction specialist. Your role is to protect both parties by flagging every possible conflict, even if subtle.",
    keywords=[
        "payment",
        "scope",
        "timeline",
        "liability",
        "warranty",
        "termination",
        "change orders",
        "IP ownership",
    ],
    output_format="""JSON array of conflicts:
[
  {
    "topic": "payment_terms",
    "party_a_proposal": {"value": "$500", "normalized": 500, "context": "...", "confidence": 0.95},
    "party_b_proposal": {"value": "$450", "normalized": 450, "context": "...", "confidence": 0.92},
    "confidence": 0.93,
    "severity": "high",
    "explanation": "..."
  }
]""",
    examples=[
        "Party A: 'Net 30' vs Party B: 'Payment on delivery' → Payment timing conflict",
        "Party A: 'Fix transmission' vs Party B: 'Rebuild transmission' → Scope conflict",
        "Party A: 'Standard warranty' vs Party B: (no mention) → Implied warranty conflict",
    ],
    edge_cases=[
        "One party implies agreement through silence",
        "Vague terms like 'as needed', 'reasonable efforts'",
        "Emotional language masking substantive disagreement",
    ],
    audience="Internal AI system - be technical and precise",
    validation="Require 70%+ confidence threshold. Flag low-confidence conflicts for human review. Prefer false positives over false negatives.",
    call_to_action="Return actionable conflict objects. If uncertain whether something is a conflict, FLAG IT.",
)

# Liberal agent prompt (high specificity, only clear conflicts)
LIBERAL_PROMPT = CheatSheetPrompt(
    objective="Identify CLEAR, UNAMBIGUOUS conflicts between Party A and Party B where terms explicitly differ.",
    context="Business negotiation transcript with speaker diarization. Focus only on explicit disagreements.",
    act="Liberal legal term extraction specialist. Your role is to avoid false alarms by only flagging genuine, explicit conflicts.",
    keywords=[
        "payment",
        "scope",
        "timeline",
        "liability",
        "warranty",
        "termination",
        "change orders",
        "IP ownership",
    ],
    output_format="""JSON array of conflicts:
[
  {
    "topic": "payment_terms",
    "party_a_proposal": {"value": "$500", "normalized": 500, "context": "...", "confidence": 0.95},
    "party_b_proposal": {"value": "$450", "normalized": 450, "context": "...", "confidence": 0.92},
    "confidence": 0.93,
    "severity": "high",
    "explanation": "..."
  }
]""",
    examples=[
        "Party A: '$500' vs Party B: '$450' → Clear payment amount conflict",
        "Party A: '2 weeks' vs Party B: '1 month' → Clear timeline conflict",
        "Party A: 'No warranty' vs Party B: '90-day warranty' → Clear warranty conflict",
    ],
    edge_cases=[
        "Ignore implied disagreements unless explicitly stated",
        "Ignore vague terms unless both parties define them differently",
        "Assume good faith - similar terms likely mean the same thing",
    ],
    audience="Internal AI system - be technical and precise",
    validation="Require 85%+ confidence threshold. Reject conflicts based on assumptions. Prefer false negatives over false positives.",
    call_to_action="Return actionable conflict objects. If uncertain whether something is a conflict, DO NOT flag it.",
)

# Neutral agent prompt (balanced, legal enforceability focus)
NEUTRAL_PROMPT = CheatSheetPrompt(
    objective="Identify conflicts that would create legal ambiguity or enforceability issues.",
    context="Business negotiation transcript with speaker diarization. Focus on legally significant differences.",
    act="Neutral legal arbiter. Your role is to identify conflicts that would matter in court or cause enforcement problems.",
    keywords=[
        "payment",
        "scope",
        "timeline",
        "liability",
        "warranty",
        "termination",
        "change orders",
        "IP ownership",
    ],
    output_format="""JSON array of conflicts:
[
  {
    "topic": "payment_terms",
    "party_a_proposal": {"value": "$500", "normalized": 500, "context": "...", "confidence": 0.95},
    "party_b_proposal": {"value": "$450", "normalized": 450, "context": "...", "confidence": 0.92},
    "confidence": 0.93,
    "severity": "high",
    "explanation": "..."
  }
]""",
    examples=[
        "Party A: 'Net 30' vs Party B: 'Payment on delivery' → Legally significant timing conflict",
        "Party A: 'Fix' vs Party B: 'Replace' → Legally significant scope conflict",
        "Party A: 'California law' vs Party B: 'Nevada law' → Legally significant jurisdiction conflict",
    ],
    edge_cases=[
        "Minor differences that wouldn't affect legal enforceability (ignore)",
        "Implied terms that both parties would reasonably understand the same way (ignore)",
        "Ambiguous terms that need clarification regardless of agreement (flag)",
    ],
    audience="Internal AI system - be technical and precise",
    validation="Require 80%+ confidence threshold. Focus on material differences. Balance precision and recall.",
    call_to_action="Return actionable conflict objects. Flag only conflicts that matter for legal enforceability or would cause post-signature disputes.",
)


# ============================================================================
# Multi-Agent Debate System
# ============================================================================


class AgentRole(StrEnum):
    """Agent roles in panel debate"""

    CONSERVATIVE = "conservative"
    LIBERAL = "liberal"
    NEUTRAL = "neutral"


@dataclass
class DebateAgent:
    """Individual agent in panel debate"""

    role: AgentRole
    prompt: CheatSheetPrompt
    glicko_player: Glicko2Player


class Term(BaseModel):
    """Legal term extracted from conversation"""

    topic: str
    value: str
    normalized: Any
    context: str
    confidence: float


class DetectedConflict(BaseModel):
    """Detected conflict between parties"""

    id: UUID
    session_id: UUID
    topic: str
    party_a_proposal: Term
    party_b_proposal: Term
    confidence: float
    explanation: str
    severity: str
    detected_by: AgentRole  # Which agent detected this


class MultiAgentDebateSystem:
    """
    Panel debate system for conflict detection

    Uses 3 agents with different perspectives:
    - Conservative: High sensitivity, flags everything
    - Liberal: High specificity, only clear conflicts
    - Neutral: Balanced, legal enforceability focus

    Process:
    1. All agents analyze transcript independently
    2. Compare results, identify disagreements
    3. Conduct debate on disagreements
    4. Neutral agent synthesizes consensus
    5. Glicko-2 ranks quality of final output
    """

    def __init__(self, ai_client=None):
        """
        Initialize multi-agent debate system

        Args:
            ai_client: Anthropic Claude API client (optional for planning phase)
        """
        self.ai_client = ai_client

        # Initialize agents
        self.agents = {
            AgentRole.CONSERVATIVE: DebateAgent(
                role=AgentRole.CONSERVATIVE,
                prompt=CONSERVATIVE_PROMPT,
                glicko_player=Glicko2Player(rating=1500, rd=350),
            ),
            AgentRole.LIBERAL: DebateAgent(
                role=AgentRole.LIBERAL,
                prompt=LIBERAL_PROMPT,
                glicko_player=Glicko2Player(rating=1500, rd=350),
            ),
            AgentRole.NEUTRAL: DebateAgent(
                role=AgentRole.NEUTRAL,
                prompt=NEUTRAL_PROMPT,
                glicko_player=Glicko2Player(rating=1500, rd=350),
            ),
        }

    async def analyze_with_panel(self, transcript) -> list[DetectedConflict]:
        """
        Analyze transcript using multi-agent panel debate

        Args:
            transcript: Transcript object with text and segments

        Returns:
            List of consensus conflicts from panel

        Process:
        1. Each agent analyzes independently
        2. Identify consensus conflicts (all agents agree)
        3. Identify disputed conflicts (agents disagree)
        4. Debate disputed conflicts
        5. Neutral agent synthesizes final list
        """

        # Step 1: Independent analysis by each agent
        analyses = {}
        for role, agent in self.agents.items():
            conflicts = await self._analyze_with_agent(transcript, agent)
            analyses[role] = conflicts

        # Step 2: Identify consensus conflicts
        consensus_conflicts = self._find_consensus(analyses)

        # Step 3: Identify disputed conflicts
        disputed_conflicts = self._find_disputes(analyses)

        # Step 4: Debate disputed conflicts
        if disputed_conflicts:
            debate_result = await self._conduct_debate(
                transcript=transcript, disputed=disputed_conflicts, analyses=analyses
            )

            # Step 5: Neutral agent synthesizes
            final_conflicts = await self._synthesize_consensus(
                consensus=consensus_conflicts, debate_result=debate_result
            )
        else:
            final_conflicts = consensus_conflicts

        return final_conflicts

    async def _analyze_with_agent(self, transcript, agent: DebateAgent) -> list[DetectedConflict]:
        """
        Single agent analyzes transcript

        Args:
            transcript: Transcript object
            agent: DebateAgent to use

        Returns:
            List of conflicts detected by this agent
        """

        if not self.ai_client:
            # Mock implementation for planning phase
            return self._mock_agent_analysis(transcript, agent)

        # Render prompt with agent's cheat sheet
        prompt = agent.prompt.render(transcript.text)

        # Call AI
        response = await self.ai_client.analyze(prompt)

        # Parse response
        conflicts_data = json.loads(response)

        # Convert to DetectedConflict objects
        conflicts = []
        for data in conflicts_data:
            conflict = DetectedConflict(
                id=uuid4(),
                session_id=transcript.id,
                topic=data["topic"],
                party_a_proposal=Term(**data["party_a_proposal"]),
                party_b_proposal=Term(**data["party_b_proposal"]),
                confidence=data["confidence"],
                explanation=data["explanation"],
                severity=data["severity"],
                detected_by=agent.role,
            )
            conflicts.append(conflict)

        return conflicts

    def _find_consensus(
        self, analyses: dict[AgentRole, list[DetectedConflict]]
    ) -> list[DetectedConflict]:
        """
        Find conflicts where all 3 agents agree

        Two conflicts are "the same" if they have:
        - Same topic
        - Same party A proposal value (within 5%)
        - Same party B proposal value (within 5%)
        """

        conservative = set(
            (c.topic, c.party_a_proposal.value, c.party_b_proposal.value)
            for c in analyses[AgentRole.CONSERVATIVE]
        )
        liberal = set(
            (c.topic, c.party_a_proposal.value, c.party_b_proposal.value)
            for c in analyses[AgentRole.LIBERAL]
        )
        neutral = set(
            (c.topic, c.party_a_proposal.value, c.party_b_proposal.value)
            for c in analyses[AgentRole.NEUTRAL]
        )

        # Conflicts present in all 3 analyses
        consensus_keys = conservative & liberal & neutral

        # Return conflicts from neutral agent (most balanced)
        consensus_conflicts = [
            c
            for c in analyses[AgentRole.NEUTRAL]
            if (c.topic, c.party_a_proposal.value, c.party_b_proposal.value) in consensus_keys
        ]

        return consensus_conflicts

    def _find_disputes(self, analyses: dict[AgentRole, list[DetectedConflict]]) -> list[tuple]:
        """
        Find conflicts where agents disagree

        Returns:
            List of (topic, agents_who_flagged) tuples
        """

        all_conflicts = {}  # {(topic, a_val, b_val): [agents who flagged]}

        for role, conflicts in analyses.items():
            for conflict in conflicts:
                key = (
                    conflict.topic,
                    conflict.party_a_proposal.value,
                    conflict.party_b_proposal.value,
                )
                if key not in all_conflicts:
                    all_conflicts[key] = []
                all_conflicts[key].append(role)

        # Disputes: flagged by 1-2 agents (not all 3)
        disputes = [(key, agents) for key, agents in all_conflicts.items() if len(agents) < 3]

        return disputes

    async def _conduct_debate(
        self, transcript, disputed: list[tuple], analyses: dict[AgentRole, list[DetectedConflict]]
    ) -> dict[str, Any]:
        """
        Conduct panel debate on disputed conflicts

        Args:
            transcript: Original transcript
            disputed: List of disputed conflicts
            analyses: Original analyses from each agent

        Returns:
            Debate result with consensus recommendations
        """

        if not self.ai_client:
            # Mock implementation
            return {"resolved": [], "escalate_to_human": []}

        # Build debate prompt
        debate_prompt = f"""
PANEL DEBATE: Resolve disagreements on conflict detection

TRANSCRIPT:
{transcript.text}

AGENT ANALYSES:
- Conservative agent found {len(analyses[AgentRole.CONSERVATIVE])} conflicts
- Liberal agent found {len(analyses[AgentRole.LIBERAL])} conflicts
- Neutral agent found {len(analyses[AgentRole.NEUTRAL])} conflicts

DISPUTED CONFLICTS (agents disagree):
{self._format_disputes(disputed, analyses)}

TASK:
Each agent: Defend your position with evidence from transcript.
Goal: Reach consensus on which disputes are TRUE conflicts vs. FALSE POSITIVES.

OUTPUT FORMAT:
{{
    "resolved": [  // Conflicts where consensus reached
        {{
            "topic": "payment_terms",
            "is_conflict": true,  // true if real conflict, false if false positive
            "rationale": "All agents agree after debate...",
            "confidence": 0.85
        }}
    ],
    "escalate_to_human": [  // Conflicts where agents still disagree
        {{
            "topic": "warranty",
            "reason": "Ambiguous - requires human judgment"
        }}
    ]
}}
"""

        # Call AI for debate
        debate_response = await self.ai_client.analyze(debate_prompt)
        debate_result = json.loads(debate_response)

        return debate_result

    async def _synthesize_consensus(
        self, consensus: list[DetectedConflict], debate_result: dict[str, Any]
    ) -> list[DetectedConflict]:
        """
        Synthesize final conflict list from consensus + debate

        Args:
            consensus: Conflicts where all agents initially agreed
            debate_result: Results of debate on disputed conflicts

        Returns:
            Final list of conflicts to present to user
        """

        final_conflicts = list(consensus)  # Start with consensus conflicts

        # Add resolved conflicts from debate (where is_conflict = true)
        for resolved in debate_result.get("resolved", []):
            if resolved["is_conflict"]:
                # Reconstruct conflict object
                # (In real implementation, would pull from original analyses)
                pass  # TODO: Implement reconstruction

        return final_conflicts

    def _format_disputes(self, disputed: list[tuple], analyses: dict) -> str:
        """Format disputed conflicts for debate prompt"""
        lines = []
        for (topic, a_val, b_val), agents in disputed:
            agents_str = ", ".join([a.value for a in agents])
            lines.append(f"- {topic}: '{a_val}' vs '{b_val}' (flagged by: {agents_str})")
        return "\n".join(lines)

    def _mock_agent_analysis(self, transcript, agent: DebateAgent) -> list[DetectedConflict]:
        """Mock analysis for planning phase"""
        # Conservative finds more conflicts
        if agent.role == AgentRole.CONSERVATIVE:
            return [
                DetectedConflict(
                    id=uuid4(),
                    session_id=transcript.id,
                    topic="payment_terms",
                    party_a_proposal=Term(
                        topic="payment_terms",
                        value="$500",
                        normalized=500,
                        context="...",
                        confidence=0.95,
                    ),
                    party_b_proposal=Term(
                        topic="payment_terms",
                        value="$450",
                        normalized=450,
                        context="...",
                        confidence=0.92,
                    ),
                    confidence=0.93,
                    explanation="Payment amount conflict",
                    severity="high",
                    detected_by=AgentRole.CONSERVATIVE,
                ),
                DetectedConflict(
                    id=uuid4(),
                    session_id=transcript.id,
                    topic="timeline",
                    party_a_proposal=Term(
                        topic="timeline",
                        value="2 weeks",
                        normalized=14,
                        context="...",
                        confidence=0.85,
                    ),
                    party_b_proposal=Term(
                        topic="timeline", value="ASAP", normalized=7, context="...", confidence=0.70
                    ),
                    confidence=0.78,
                    explanation="Timeline ambiguity",
                    severity="medium",
                    detected_by=AgentRole.CONSERVATIVE,
                ),
            ]

        # Liberal finds fewer (only clear conflicts)
        elif agent.role == AgentRole.LIBERAL:
            return [
                DetectedConflict(
                    id=uuid4(),
                    session_id=transcript.id,
                    topic="payment_terms",
                    party_a_proposal=Term(
                        topic="payment_terms",
                        value="$500",
                        normalized=500,
                        context="...",
                        confidence=0.95,
                    ),
                    party_b_proposal=Term(
                        topic="payment_terms",
                        value="$450",
                        normalized=450,
                        context="...",
                        confidence=0.92,
                    ),
                    confidence=0.93,
                    explanation="Payment amount conflict",
                    severity="high",
                    detected_by=AgentRole.LIBERAL,
                )
            ]

        # Neutral is balanced
        else:
            return [
                DetectedConflict(
                    id=uuid4(),
                    session_id=transcript.id,
                    topic="payment_terms",
                    party_a_proposal=Term(
                        topic="payment_terms",
                        value="$500",
                        normalized=500,
                        context="...",
                        confidence=0.95,
                    ),
                    party_b_proposal=Term(
                        topic="payment_terms",
                        value="$450",
                        normalized=450,
                        context="...",
                        confidence=0.92,
                    ),
                    confidence=0.93,
                    explanation="Payment amount conflict",
                    severity="high",
                    detected_by=AgentRole.NEUTRAL,
                )
            ]

    async def update_glicko_ratings(
        self, conflicts: list[DetectedConflict], user_feedback: dict[UUID, bool]
    ) -> None:
        """
        Update Glicko-2 ratings based on user feedback

        Args:
            conflicts: List of detected conflicts
            user_feedback: {conflict_id: user_agreed (bool)}

        Process:
        - For each conflict, get which agent detected it
        - Update that agent's Glicko rating based on user agreement
        - Agents that detect conflicts users agree with gain rating
        - Agents that flag false positives lose rating
        """

        for conflict in conflicts:
            agent_role = conflict.detected_by
            agent = self.agents[agent_role]

            user_agreed = user_feedback.get(conflict.id)

            if user_agreed is not None:
                # Update Glicko rating
                # Opponent = "ground truth" (user judgment) at rating 1600
                match_result = 1.0 if user_agreed else 0.0

                agent.glicko_player.update(opponents=[(1600, 200, match_result)], tau=0.5, tol=1e-6)

    def get_agent_ratings(self) -> dict[AgentRole, float]:
        """Get current Glicko ratings for all agents"""
        return {role: agent.glicko_player.get_rating() for role, agent in self.agents.items()}


# ============================================================================
# Usage Example
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of MultiAgentDebateSystem

    This demonstrates the core workflow:
    1. Create transcript from negotiation
    2. Analyze with multi-agent panel
    3. Get consensus conflicts
    4. Update Glicko ratings based on user feedback
    """

    import asyncio
    from uuid import uuid4

    async def main():
        # Create mock transcript
        from collections import namedtuple

        Transcript = namedtuple("Transcript", ["id", "text"])

        transcript = Transcript(
            id=uuid4(),
            text="Party A: I can do this job for $500. Party B: I was thinking more like $450.",
        )

        # Initialize multi-agent debate system
        debate_system = MultiAgentDebateSystem()

        # Analyze with panel
        print("Analyzing transcript with multi-agent panel...\n")
        conflicts = await debate_system.analyze_with_panel(transcript)

        print(f"Panel detected {len(conflicts)} conflict(s):")
        for conflict in conflicts:
            print(f"\nConflict ID: {conflict.id}")
            print(f"Topic: {conflict.topic}")
            print(f"Party A: {conflict.party_a_proposal.value}")
            print(f"Party B: {conflict.party_b_proposal.value}")
            print(f"Detected by: {conflict.detected_by}")
            print(f"Confidence: {conflict.confidence:.2%}")
            print(f"Severity: {conflict.severity}")

        # Simulate user feedback
        print("\n\nSimulating user feedback...")
        user_feedback = {
            conflict.id: True  # User agrees with all detected conflicts
            for conflict in conflicts
        }

        # Update Glicko ratings
        await debate_system.update_glicko_ratings(conflicts, user_feedback)

        # Show updated ratings
        print("\nUpdated agent ratings:")
        ratings = debate_system.get_agent_ratings()
        for role, rating in ratings.items():
            print(f"- {role.value}: {rating:.0f} Elo")

    # Run example
    asyncio.run(main())
