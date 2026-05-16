# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Gemini 2.0 Pro Multi-Agent System (AutoGen → Gemini Migration)
Replaces custom PanelDebateClassifier with native Gemini agents

Based on migration from:
- Microsoft AutoGen (ConversableAgent, GroupChat)
- To: Google Gemini 2.0 Pro (native multi-turn, function calling)

Performance:
- 87.5% cost reduction vs. GPT-4 ($1.25/M vs. $10/M tokens)
- 1M token context window (entire debate history)
- Native Google Cloud integration (no cross-cloud latency)
"""

import json
from typing import Any

try:
  import google.generativeai as genai
except ImportError:
  genai = None

from app.models.schemas import TierClassification


class GeminiAgent:
  """
  Single Gemini agent with persona and tools
  Replaces AutoGen's ConversableAgent
  """

  def __init__(
    self,
    name: str,
    persona: str,
    tools: list[dict] | None = None,
    model_name: str = "gemini-3.1-flash-exp",
    temperature: float = 0.7,
    api_key: str | None = None,
  ):
    """
    Initialize Gemini agent

    Args:
        name: Agent identifier (e.g., "skeptic", "optimist", "neutral")
        persona: System instruction defining agent role
        tools: Function calling tools (ATP 5-19 rules, Glicko ratings)
        model_name: Gemini model variant
        temperature: Sampling temperature (0.0-1.0)
    """
    self.name = name
    self.persona = persona
    self.tools = tools or []

    if genai and api_key:
      genai.configure(api_key=api_key)
      self.model = genai.GenerativeModel(
        model_name=model_name, system_instruction=persona, tools=self.tools
      )
    else:
      self.model = None

    self.generation_config = {
      "temperature": temperature,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 2048,
    }

  async def propose_tier(
    self,
    title: str,
    content: str,
    tags: list[str],
    debate_history: list[dict] = None,
  ) -> dict[str, Any]:
    """
    Generate tier proposal with reasoning

    Args:
        title: Article title
        content: Full text
        tags: Metadata tags
        debate_history: Previous rounds of debate

    Returns:
        {
          "agent": "skeptic",
          "tier": 2,
          "confidence": 0.75,
          "reasoning": "Source reliability C, credibility 3...",
          "rebuttals": ["Optimist overstated strategic value", ...]
        }
    """
    if not self.model:
      # Fallback to rule-based
      return self._fallback_proposal(title, content, tags)

    # Build prompt with debate history
    prompt = self._build_debate_prompt(title, content, tags, debate_history)

    # Generate response
    response = self.model.generate_content(
      prompt, generation_config=self.generation_config
    )

    # Parse JSON response
    try:
      result = json.loads(response.text)
      result["agent"] = self.name
      return result
    except json.JSONDecodeError:
      # Fallback if JSON parsing fails
      return self._fallback_proposal(title, content, tags)

  def _build_debate_prompt(
    self,
    title: str,
    content: str,
    tags: list[str],
    debate_history: list[dict] | None,
  ) -> str:
    """Build debate prompt with history context"""

    prompt = f"""
You are participating in a multi-agent intelligence classification debate.

ARTICLE TO CLASSIFY:
Title: {title}
Tags: {", ".join(tags)}
Content Preview: {content[:500]}...

TIER CRITERIA:
- Tier 1 (High-Value): Breaking news, FOIA docs, patents, regulations, strategic implications
- Tier 2 (Medium): Industry reports, expert commentary, tutorials, verified sources
- Tier 3 (Low-Value): Social media, evergreen content, duplicates, unverified

"""

    if debate_history:
      prompt += "\nPREVIOUS DEBATE ROUNDS:\n"
      for round_num, round_data in enumerate(debate_history, 1):
        prompt += f"\n--- Round {round_num} ---\n"
        for agent_name, proposal in round_data.items():
          prompt += f"{agent_name.upper()}: Tier {proposal['tier']} "
          prompt += f"({proposal['confidence']:.2f} confidence)\n"
          prompt += f"  Reasoning: {proposal['reasoning']}\n"

    prompt += """
YOUR TASK:
1. Propose a tier (1, 2, or 3) based on your persona
2. Provide confidence score (0.0-1.0)
3. Explain reasoning using ATP 5-19 criteria (source reliability, credibility, timeliness)
4. Optionally rebut other agents' proposals from previous rounds

OUTPUT (JSON only, no markdown):
{
  "tier": 1-3,
  "confidence": 0.0-1.0,
  "reasoning": "Your detailed analysis...",
  "rebuttals": ["Optional critiques of other proposals"]
}
"""
    return prompt

  def _fallback_proposal(
    self, title: str, content: str, tags: list[str]
  ) -> dict[str, Any]:
    """Rule-based fallback when Gemini unavailable"""
    # Simplified rule-based classification
    tier1_keywords = ["regulation", "filing", "patent", "breaking", "faa", "dod"]
    tier3_keywords = ["opinion", "social media", "evergreen"]

    text_lower = f"{title} {content}".lower()

    if any(kw in text_lower for kw in tier1_keywords):
      tier = 1
      confidence = 0.70
    elif any(kw in text_lower for kw in tier3_keywords):
      tier = 3
      confidence = 0.65
    else:
      tier = 2
      confidence = 0.60

    return {
      "agent": self.name,
      "tier": tier,
      "confidence": confidence,
      "reasoning": f"{self.name} agent fallback (Gemini unavailable)",
      "rebuttals": [],
    }


class GeminiGroupChat:
  """
  Multi-agent debate orchestrator using Gemini 2.0 Pro
  Replaces AutoGen's GroupChat with native Gemini multi-turn
  """

  # Pre-defined agent personas (AutoGen ConversableAgent equivalents)
  AGENT_PERSONAS = {
    "skeptic": {
      "persona": """You are a SKEPTICAL intelligence analyst.
Your role: Question source credibility, demand high standards, default to Tier 2/3.

ATP 5-19 Bias: Prefer source reliability B-C, credibility 3-4 (cautious).
Debate Style: Challenge optimistic assessments, cite historical false positives.
Decision Tendency: Downgrade tier by 1 level vs. consensus (risk-averse).""",
      "temperature": 0.5,  # Lower temperature = more conservative
    },
    "optimist": {
      "persona": """You are an OPTIMISTIC intelligence analyst.
Your role: Identify strategic value, recognize emerging trends, default to Tier 1/2.

ATP 5-19 Bias: Prefer source reliability A-B, credibility 1-2 (aggressive).
Debate Style: Highlight potential impact, cite success stories.
Decision Tendency: Upgrade tier by 1 level vs. consensus (opportunity-seeking).""",
      "temperature": 0.9,  # Higher temperature = more creative
    },
    "neutral": {
      "persona": """You are a NEUTRAL fact-checker and arbiter.
Your role: Stick strictly to ATP 5-19 criteria, no bias, final decision authority.

ATP 5-19 Application: Literal interpretation of source reliability, credibility, timeliness.
Debate Style: Summarize both sides, make data-driven decision.
Decision Tendency: No bias, pure evidence-based classification.""",
      "temperature": 0.3,  # Lowest temperature = most deterministic
    },
  }

  def __init__(self, api_key: str | None = None, agents: list[str] | None = None):
    """
    Initialize multi-agent group chat

    Args:
        api_key: Gemini API key
        agents: List of agent names to include (default: all 3)
    """
    self.api_key = api_key
    agent_names = agents or ["skeptic", "optimist", "neutral"]

    # Initialize agents
    self.agents = {
      name: GeminiAgent(
        name=name,
        persona=self.AGENT_PERSONAS[name]["persona"],
        temperature=self.AGENT_PERSONAS[name]["temperature"],
        api_key=api_key,
      )
      for name in agent_names
    }

    self.debate_history: list[list[dict]] = []

  async def classify_with_debate(
    self,
    title: str,
    content: str,
    tags: list[str],
    rounds: int = 2,
    voting_method: str = "weighted_confidence",
  ) -> TierClassification:
    """
    Run multi-agent debate to classify intelligence item

    Args:
        title: Article title
        content: Full text
        tags: Metadata tags
        rounds: Number of debate rounds (default: 2)
        voting_method: "weighted_confidence" | "majority_vote" | "neutral_arbiter"

    Returns:
        TierClassification with debate metadata

    Example:
        >>> chat = GeminiGroupChat(api_key="...")
        >>> result = await chat.classify_with_debate(
        ...     title="FAA Proposes DO-178D",
        ...     content="The FAA today...",
        ...     tags=["aviation", "regulation"],
        ...     rounds=2
        ... )
        >>> print(result.tier)  # 1 (high-value)
        >>> print(result.confidence)  # 0.87 (high consensus)
    """
    debate_rounds = []

    # Run debate rounds
    for round_num in range(rounds):
      round_proposals = {}

      # Each agent proposes tier with reasoning
      for agent_name, agent in self.agents.items():
        proposal = await agent.propose_tier(
          title=title,
          content=content,
          tags=tags,
          debate_history=debate_rounds,
        )
        round_proposals[agent_name] = proposal

      debate_rounds.append(round_proposals)

    # Aggregate votes
    final_tier, final_confidence, reasoning = self._aggregate_votes(
      debate_rounds, method=voting_method
    )

    # Extract common tags from all proposals
    all_tags = set(tags)
    for round_data in debate_rounds:
      for proposal in round_data.values():
        # Agents might suggest additional tags
        if "suggested_tags" in proposal:
          all_tags.update(proposal["suggested_tags"])

    # Build metadata
    debate_summary = self._build_debate_summary(debate_rounds)

    return TierClassification(
      tier=final_tier,
      confidence=final_confidence,
      reasoning=f"{reasoning}\n\nDebate Summary:\n{debate_summary}",
      tags=list(all_tags),
    )

  def _aggregate_votes(
    self, debate_rounds: list[list[dict]], method: str = "weighted_confidence"
  ) -> tuple[int, float, str]:
    """
    Aggregate agent votes into final tier classification

    Args:
        debate_rounds: All rounds of proposals
        method: Voting aggregation method

    Returns:
        (final_tier, final_confidence, reasoning)
    """
    # Use final round proposals
    final_round = debate_rounds[-1]

    if method == "neutral_arbiter":
      # Neutral agent has final say
      neutral_proposal = final_round.get("neutral")
      if neutral_proposal:
        return (
          neutral_proposal["tier"],
          neutral_proposal["confidence"],
          f"Neutral arbiter decision: {neutral_proposal['reasoning']}",
        )

    elif method == "majority_vote":
      # Simple majority vote
      tiers = [p["tier"] for p in final_round.values()]
      from collections import Counter

      majority_tier = Counter(tiers).most_common(1)[0][0]

      # Average confidence for majority tier
      majority_confidences = [
        p["confidence"] for p in final_round.values() if p["tier"] == majority_tier
      ]
      avg_confidence = sum(majority_confidences) / len(majority_confidences)

      return (
        majority_tier,
        avg_confidence,
        f"Majority vote: {len(majority_confidences)}/{len(tiers)} agents agreed on Tier {majority_tier}",
      )

    elif method == "weighted_confidence":
      # Weight each tier proposal by agent confidence
      weighted_sum = 0.0
      total_weight = 0.0

      for proposal in final_round.values():
        weight = proposal["confidence"]
        weighted_sum += proposal["tier"] * weight
        total_weight += weight

      weighted_avg_tier = weighted_sum / total_weight

      # Round to nearest tier
      final_tier = round(weighted_avg_tier)
      final_tier = max(1, min(3, final_tier))  # Clamp to 1-3

      # Confidence = how close agents were to consensus
      tier_variance = (
        sum(abs(p["tier"] - final_tier) * p["confidence"] for p in final_round.values())
        / total_weight
      )

      final_confidence = max(0.5, 1.0 - (tier_variance / 2))  # Invert variance

      return (
        final_tier,
        final_confidence,
        f"Weighted consensus: {len(final_round)} agents, avg tier {weighted_avg_tier:.2f} → Tier {final_tier}",
      )

    # Default fallback
    return (2, 0.60, "Fallback to Tier 2 (unknown voting method)")

  def _build_debate_summary(self, debate_rounds: list[list[dict]]) -> str:
    """Build human-readable debate summary"""
    summary = []

    for round_num, round_data in enumerate(debate_rounds, 1):
      summary.append(f"Round {round_num}:")
      for agent_name, proposal in round_data.items():
        summary.append(
          f"  {agent_name.capitalize()}: Tier {proposal['tier']} ({proposal['confidence']:.0%} confidence)"
        )
        summary.append(f"    Reasoning: {proposal['reasoning'][:100]}...")
      summary.append("")

    return "\n".join(summary)


# ============================================================================
# Function Calling Tools (AutoGen code_execution_config equivalent)
# ============================================================================


def create_atp_519_tools() -> list[dict]:
  """
  Create Gemini function calling tools for ATP 5-19 validation
  Replaces AutoGen's code_execution_config with native function calling
  """
  return [
    {
      "name": "check_source_reliability",
      "description": "Check source reliability using ATP 5-19 criteria (A-F scale)",
      "parameters": {
        "type": "object",
        "properties": {
          "domain": {
            "type": "string",
            "description": "Source domain (e.g., 'reuters.com', 'twitter.com')",
          }
        },
        "required": ["domain"],
      },
    },
    {
      "name": "check_credibility",
      "description": "Check information credibility using ATP 5-19 (1-6 scale)",
      "parameters": {
        "type": "object",
        "properties": {
          "content": {
            "type": "string",
            "description": "Article content to analyze",
          },
          "cross_references": {
            "type": "integer",
            "description": "Number of cross-referencing sources",
          },
        },
        "required": ["content"],
      },
    },
    {
      "name": "get_glicko_rating",
      "description": "Get Glicko-2 rating for intelligence source",
      "parameters": {
        "type": "object",
        "properties": {
          "source_id": {"type": "string", "description": "Source identifier"}
        },
        "required": ["source_id"],
      },
    },
  ]


# Example usage function
async def example_usage():
  """
  Example: AutoGen → Gemini migration in action
  """
  import os

  # Initialize group chat
  chat = GeminiGroupChat(
    api_key=os.getenv("GEMINI_API_KEY"), agents=["skeptic", "optimist", "neutral"]
  )

  # Classify intelligence item
  result = await chat.classify_with_debate(
    title="FAA Proposes DO-178D Update for AI Systems",
    content="""
        The Federal Aviation Administration (FAA) today released a Notice of
        Proposed Rulemaking (NPRM) requiring AI models in flight-critical systems
        to maintain version-level audit trails and comply with DO-178D software
        certification standards. This represents the first major regulatory update
        for AI in aviation since DO-178C was published in 2011.

        Industry experts estimate compliance costs at $500K-2M per aircraft type,
        but the regulation is expected to accelerate adoption of AI-based autopilot
        systems by providing clear certification pathways.
        """,
    tags=["aviation", "regulation", "AI", "DO-178D"],
    rounds=2,
  )

  print("Classification Result:")
  print(f"  Tier: {result.tier}")
  print(f"  Confidence: {result.confidence:.0%}")
  print(f"  Reasoning: {result.reasoning[:200]}...")
  print(f"  Tags: {', '.join(result.tags)}")

  # Expected output:
  # Tier: 1 (high-value, breaking regulatory news)
  # Confidence: 85-92% (high consensus among agents)
  # Reasoning: "Weighted consensus: 3 agents, avg tier 1.1 → Tier 1
  #             Debate Summary:
  #             Round 1:
  #               Skeptic: Tier 2 (70% confidence) - Source .gov domain reliable but..."
  #               Optimist: Tier 1 (90% confidence) - Primary source, strategic impact..."
  #               Neutral: Tier 1 (85% confidence) - ATP 5-19: source A, credibility 2..."
