# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Cheat Sheet Fusion - Provider-Optimized Prompt Engineering.

Implements the 21→10 essentials framework for prompt optimization:
1. Tone
2. Format
3. Act (role)
4. Objective
5. Context
6. Keywords
7. Examples
8. Audience
9. Citations
10. Call to action

Each LLM provider excels with different prompt styles:
- Gemini: Professional, structured, minimal examples
- Claude: Conversational, narrative, contextual
- GPT-5: Technical, bullet-points, abundant examples

This module provides:
- Provider-specific cheat sheet profiles
- Prompt optimization for each provider
- Evolution of cheat sheets based on performance data (DTE)
- Marketplace-ready cheat sheet packages
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProviderType(Enum):
  """LLM provider types."""

  GEMINI = "gemini"
  CLAUDE = "claude"
  GPT5 = "gpt5"
  LOCAL = "local"


@dataclass
class CheatSheet:
  """
  Cheat sheet profile for prompt optimization.

  The 10 essentials (condensed from original 21):
  """

  tone: str = "professional"  # professional, conversational, technical, friendly
  format: str = "structured"  # structured, narrative, bullet-points, table
  act: str = "assistant"  # role/persona to adopt
  objective: str = "help_user"  # primary goal
  context: str = "minimal"  # minimal, moderate, detailed, comprehensive
  keywords: list[str] = field(default_factory=list)  # Important terms to include
  examples: int = 2  # Number of examples to provide
  audience: str = "general"  # general, technical, business, academic
  citations: str = "minimal"  # minimal, moderate, extensive
  call_to_action: str = "respond"  # What you want at the end

  def to_dict(self) -> dict[str, Any]:
    """Convert to dictionary for serialization."""
    return {
      "tone": self.tone,
      "format": self.format,
      "act": self.act,
      "objective": self.objective,
      "context": self.context,
      "keywords": self.keywords,
      "examples": self.examples,
      "audience": self.audience,
      "citations": self.citations,
      "call_to_action": self.call_to_action,
    }

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> "CheatSheet":
    """Create CheatSheet from dictionary."""
    return cls(**data)


# Provider-specific cheat sheet profiles (optimized for each LLM)

GEMINI_PROFILE = CheatSheet(
  tone="professional",
  format="structured",
  act="decision_engine",
  objective="analyze_and_decide",
  context="concise",
  keywords=["criteria", "policy", "compliance", "validate"],
  examples=2,  # Gemini works well with few, clear examples
  audience="automated_system",
  citations="minimal",
  call_to_action="structured_decision",
)

CLAUDE_PROFILE = CheatSheet(
  tone="conversational",
  format="narrative",
  act="thoughtful_advisor",
  objective="analyze_deeply_and_recommend",
  context="detailed",
  keywords=["consider", "analyze", "nuance", "context", "implications"],
  examples=3,  # Claude benefits from contextual examples
  audience="human_decision_maker",
  citations="moderate",
  call_to_action="recommendation_with_rationale",
)

GPT5_PROFILE = CheatSheet(
  tone="technical",
  format="bullet_points",
  act="expert_system",
  objective="evaluate_and_classify",
  context="comprehensive",
  keywords=["criteria", "threshold", "specification", "validation", "edge_cases"],
  examples=5,  # GPT-5 excels with abundant examples
  audience="technical_system",
  citations="extensive",
  call_to_action="formatted_output",
)

LOCAL_PROFILE = CheatSheet(
  tone="direct",
  format="structured",
  act="rule_engine",
  objective="classify",
  context="minimal",  # Local model has limited context window
  keywords=["rule", "condition", "match", "threshold"],
  examples=1,  # Minimal examples (inference speed priority)
  audience="automated_system",
  citations="none",
  call_to_action="binary_decision",
)


class CheatSheetLibrary:
  """
  Library of cheat sheet profiles for different providers and use cases.
  """

  def __init__(self):
    """Initialize library with default provider profiles."""
    self.profiles = {
      ProviderType.GEMINI: GEMINI_PROFILE,
      ProviderType.CLAUDE: CLAUDE_PROFILE,
      ProviderType.GPT5: GPT5_PROFILE,
      ProviderType.LOCAL: LOCAL_PROFILE,
    }

    # Custom profiles for specific use cases
    self.use_case_profiles: dict[str, CheatSheet] = {}

  def get_profile(self, provider: ProviderType) -> CheatSheet:
    """Get cheat sheet profile for a provider."""
    return self.profiles[provider]

  def add_use_case_profile(self, name: str, profile: CheatSheet):
    """Add a custom profile for a specific use case."""
    self.use_case_profiles[name] = profile

  def get_use_case_profile(self, name: str) -> CheatSheet | None:
    """Get a use case-specific profile."""
    return self.use_case_profiles.get(name)

  def evolve_profile(
    self, provider: ProviderType, performance_data: dict[str, Any]
  ) -> CheatSheet:
    """
    Evolve a profile based on performance data (DTE integration).

    Args:
        provider: Provider to evolve profile for
        performance_data: Dict with metrics like accuracy, latency, confidence

    Returns:
        Evolved CheatSheet
    """
    current_profile = self.get_profile(provider)

    # Analyze performance data to adjust profile
    avg_accuracy = performance_data.get("avg_accuracy", 0.8)
    avg_latency = performance_data.get("avg_latency_ms", 100)
    avg_confidence = performance_data.get("avg_confidence", 0.75)

    # Create evolved profile (copy current)
    evolved = CheatSheet(
      tone=current_profile.tone,
      format=current_profile.format,
      act=current_profile.act,
      objective=current_profile.objective,
      context=current_profile.context,
      keywords=current_profile.keywords.copy(),
      examples=current_profile.examples,
      audience=current_profile.audience,
      citations=current_profile.citations,
      call_to_action=current_profile.call_to_action,
    )

    # Evolution rules based on performance

    # If accuracy is low (<70%), increase context and examples
    if avg_accuracy < 0.70:
      if evolved.context == "minimal":
        evolved.context = "moderate"
      elif evolved.context == "moderate":
        evolved.context = "detailed"

      evolved.examples += 1

    # If latency is high (>100ms), reduce context and examples
    if avg_latency > 100:
      if evolved.context == "comprehensive":
        evolved.context = "detailed"
      elif evolved.context == "detailed":
        evolved.context = "moderate"

      evolved.examples = max(1, evolved.examples - 1)

    # If confidence is low (<75%), make tone more directive
    if avg_confidence < 0.75:
      if evolved.tone == "conversational":
        evolved.tone = "professional"

    return evolved


class CheatSheetFusion:
  """
  Fuses cheat sheet profiles into optimized prompts for each provider.
  """

  def __init__(self, library: CheatSheetLibrary | None = None):
    """
    Initialize fusion engine.

    Args:
        library: CheatSheetLibrary to use (creates default if None)
    """
    self.library = library or CheatSheetLibrary()

  def apply(
    self,
    base_prompt: str,
    provider: ProviderType,
    use_case: str | None = None,
    custom_overrides: dict[str, Any] | None = None,
  ) -> str:
    """
    Apply cheat sheet fusion to optimize prompt for provider.

    Args:
        base_prompt: Base prompt content
        provider: Target provider
        use_case: Optional use case for custom profile
        custom_overrides: Optional dict to override profile fields

    Returns:
        Optimized prompt string
    """
    # Get base profile
    if use_case and self.library.get_use_case_profile(use_case):
      sheet = self.library.get_use_case_profile(use_case)
    else:
      sheet = self.library.get_profile(provider)

    # Apply custom overrides if provided
    if custom_overrides:
      sheet = CheatSheet(
        tone=custom_overrides.get("tone", sheet.tone),
        format=custom_overrides.get("format", sheet.format),
        act=custom_overrides.get("act", sheet.act),
        objective=custom_overrides.get("objective", sheet.objective),
        context=custom_overrides.get("context", sheet.context),
        keywords=custom_overrides.get("keywords", sheet.keywords),
        examples=custom_overrides.get("examples", sheet.examples),
        audience=custom_overrides.get("audience", sheet.audience),
        citations=custom_overrides.get("citations", sheet.citations),
        call_to_action=custom_overrides.get("call_to_action", sheet.call_to_action),
      )

    # Build optimized prompt
    return self._build_prompt(base_prompt, sheet)

  def _build_prompt(self, base_content: str, sheet: CheatSheet) -> str:
    """
    Build prompt using cheat sheet template.

    Args:
        base_content: Core prompt content
        sheet: CheatSheet profile to apply

    Returns:
        Formatted prompt
    """
    # Format based on provider preferences
    if sheet.format == "structured":
      prompt = self._format_structured(base_content, sheet)
    elif sheet.format == "narrative":
      prompt = self._format_narrative(base_content, sheet)
    elif sheet.format == "bullet_points":
      prompt = self._format_bullet_points(base_content, sheet)
    else:
      # Default: simple format
      prompt = base_content

    return prompt

  def _format_structured(self, content: str, sheet: CheatSheet) -> str:
    """Format as structured sections."""
    sections = []

    # Role/Act
    sections.append(f"# ROLE: {sheet.act.replace('_', ' ').title()}")
    sections.append("")

    # Objective
    sections.append("# OBJECTIVE")
    sections.append(sheet.objective.replace("_", " ").capitalize())
    sections.append("")

    # Context level indicator
    sections.append(f"# CONTEXT ({sheet.context.upper()})")
    sections.append(content)
    sections.append("")

    # Keywords
    if sheet.keywords:
      sections.append("# KEY TERMS")
      sections.append(", ".join(sheet.keywords))
      sections.append("")

    # Examples section
    if sheet.examples > 0:
      sections.append(f"# EXAMPLES (showing {sheet.examples} reference cases)")
      sections.append("[Examples would be inserted here based on use case]")
      sections.append("")

    # Audience note
    sections.append(f"# AUDIENCE: {sheet.audience.replace('_', ' ').title()}")
    sections.append("")

    # Call to action
    sections.append(f"# {sheet.call_to_action.replace('_', ' ').upper()}")
    sections.append(f"Provide your {sheet.call_to_action.replace('_', ' ')} now.")

    return "\n".join(sections)

  def _format_narrative(self, content: str, sheet: CheatSheet) -> str:
    """Format as conversational narrative."""
    parts = []

    # Opening with role
    parts.append(
      f"You are acting as a {sheet.act.replace('_', ' ')}. Your goal is to {sheet.objective.replace('_', ' ')}."
    )
    parts.append("")

    # Context introduction
    if sheet.context in ["detailed", "comprehensive"]:
      parts.append("Let me provide you with detailed context:")
    else:
      parts.append("Here's the situation:")

    parts.append(content)
    parts.append("")

    # Keywords as considerations
    if sheet.keywords:
      parts.append("Please consider the following aspects:")
      for kw in sheet.keywords:
        parts.append(f"  - {kw.replace('_', ' ').capitalize()}")
      parts.append("")

    # Examples as references
    if sheet.examples > 0:
      parts.append(
        f"For reference, here are {sheet.examples} similar cases to guide your thinking:"
      )
      parts.append("[Examples would be inserted here]")
      parts.append("")

    # Audience-aware tone
    if sheet.audience == "human_decision_maker":
      parts.append(
        "Please provide a thoughtful recommendation that I can understand and use to make an informed decision."
      )
    else:
      parts.append(f"Please provide your {sheet.call_to_action.replace('_', ' ')}.")

    return "\n".join(parts)

  def _format_bullet_points(self, content: str, sheet: CheatSheet) -> str:
    """Format as technical bullet points."""
    lines = []

    # Header with role and objective
    lines.append(f"**Role**: {sheet.act.replace('_', ' ').title()}")
    lines.append(f"**Objective**: {sheet.objective.replace('_', ' ').capitalize()}")
    lines.append("")

    # Content as structured data
    lines.append("**Input:**")
    lines.append(f"```\n{content}\n```")
    lines.append("")

    # Requirements
    lines.append("**Requirements:**")
    if sheet.keywords:
      for kw in sheet.keywords:
        lines.append(f"  - Evaluate {kw.replace('_', ' ')}")

    lines.append(f"  - Context level: {sheet.context}")
    lines.append(f"  - Provide {sheet.examples} supporting examples")
    lines.append("")

    # Output format
    lines.append("**Output Format:**")
    lines.append(f"  - Type: {sheet.call_to_action.replace('_', ' ')}")
    lines.append(f"  - Audience: {sheet.audience.replace('_', ' ')}")
    lines.append(f"  - Citations: {sheet.citations}")

    return "\n".join(lines)


# Example usage
if __name__ == "__main__":
  # Initialize library and fusion engine
  library = CheatSheetLibrary()
  fusion = CheatSheetFusion(library)

  # Base prompt (same for all providers)
  base_prompt = """
Analyze this user request for production deployment:
- Feature: New payment gateway integration
- Tests: All passed (unit, integration, E2E)
- Security scan: Pending (scheduled for tomorrow)
- Risk level: High (handles customer payments)

Decision required: Approve deployment now, or wait for security scan?
"""

  # Apply fusion for each provider
  for provider in [ProviderType.GEMINI, ProviderType.CLAUDE, ProviderType.GPT5]:
    optimized = fusion.apply(base_prompt, provider)

  # Demo: Evolve profile based on performance

  # Simulate poor performance for Gemini
  performance_data = {
    "avg_accuracy": 0.65,  # Low accuracy
    "avg_latency_ms": 120,  # High latency
    "avg_confidence": 0.70,  # Low confidence
  }

  evolved = library.evolve_profile(ProviderType.GEMINI, performance_data)
