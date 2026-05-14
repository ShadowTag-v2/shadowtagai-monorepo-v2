# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Cheat Sheet Fusion for prompt engineering.

Evolved from 21 elements to 10 essentials via DTE testing (+3.7% accuracy).

Original 21 elements → Fused 10 essentials:
1. Tone (professional, casual, technical)
2. Format (JSON, markdown, code, bullet points)
3. Act (role/persona to adopt)
4. Objective (clear goal statement)
5. Context (background information)
6. Keywords (domain-specific terms)
7. Examples (few-shot demonstrations)
8. Audience (who will use this)
9. Citations (sources if needed)
10. Call (call-to-action or next step)
"""

from pydantic import BaseModel, Field
from enum import Enum


class ToneType(str, Enum):
    """Tone options for prompts."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EMPATHETIC = "empathetic"
    URGENT = "urgent"
    CREATIVE = "creative"


class FormatType(str, Enum):
    """Output format options."""

    JSON = "json"
    MARKDOWN = "markdown"
    CODE = "code"
    BULLETS = "bullets"
    PROSE = "prose"
    TABLE = "table"


class CheatSheet(BaseModel):
    """
    Evolved cheat sheet for prompt engineering.

    Based on DTE testing: 10 essentials reduced from original 21.
    Achieved +3.7% accuracy improvement over baseline.
    """

    # 1. Tone
    tone: ToneType = Field(
        ToneType.PROFESSIONAL,
        description="Communication style to adopt",
    )

    # 2. Format
    format: FormatType = Field(
        FormatType.MARKDOWN,
        description="Expected output format",
    )

    # 3. Act (Role/Persona)
    act: str = Field(
        ...,
        description="Role or persona to adopt (e.g., 'expert Python developer')",
        min_length=1,
    )

    # 4. Objective
    objective: str = Field(
        ...,
        description="Clear, measurable goal for the prompt",
        min_length=1,
    )

    # 5. Context
    context: str | None = Field(
        None,
        description="Background information or constraints",
    )

    # 6. Keywords
    keywords: list[str] = Field(
        default_factory=list,
        description="Domain-specific terms to include",
    )

    # 7. Examples (Few-shot)
    examples: list[str] = Field(
        default_factory=list,
        description="Example inputs/outputs for few-shot learning",
    )

    # 8. Audience
    audience: str | None = Field(
        None,
        description="Target audience (e.g., 'technical stakeholders', 'executives')",
    )

    # 9. Citations
    citations_required: bool = Field(
        False,
        description="Whether to include source citations",
    )

    # 10. Call (Call-to-action)
    call: str | None = Field(
        None,
        description="Specific action or next step to emphasize",
    )

    def to_system_prompt(self) -> str:
        """
        Convert cheat sheet to system prompt.

        Fuses all 10 elements into optimized prompt structure.
        """
        parts = []

        # Act (Role)
        parts.append(f"You are {self.act}.")

        # Tone
        tone_descriptions = {
            ToneType.PROFESSIONAL: "Communicate in a professional, clear manner.",
            ToneType.CASUAL: "Use a friendly, conversational tone.",
            ToneType.TECHNICAL: "Use precise technical language and terminology.",
            ToneType.EMPATHETIC: "Show understanding and empathy in responses.",
            ToneType.URGENT: "Communicate with urgency and directness.",
            ToneType.CREATIVE: "Think creatively and explore novel solutions.",
        }
        parts.append(tone_descriptions.get(self.tone, ""))

        # Objective
        parts.append(f"\nObjective: {self.objective}")

        # Context (if provided)
        if self.context:
            parts.append(f"\nContext: {self.context}")

        # Keywords (if provided)
        if self.keywords:
            keywords_str = ", ".join(self.keywords)
            parts.append(f"\nKey terms to use: {keywords_str}")

        # Format
        format_instructions = {
            FormatType.JSON: "Return your response in valid JSON format only.",
            FormatType.MARKDOWN: "Format your response in markdown.",
            FormatType.CODE: "Provide code examples with syntax highlighting.",
            FormatType.BULLETS: "Use bullet points for clarity.",
            FormatType.PROSE: "Write in clear prose paragraphs.",
            FormatType.TABLE: "Present information in table format.",
        }
        parts.append(f"\n{format_instructions.get(self.format, '')}")

        # Examples (if provided)
        if self.examples:
            parts.append("\n\nExamples:")
            for i, ex in enumerate(self.examples, 1):
                parts.append(f"{i}. {ex}")

        # Audience (if provided)
        if self.audience:
            parts.append(f"\n\nAudience: {self.audience}")

        # Citations (if required)
        if self.citations_required:
            parts.append("\n\nInclude citations for all claims.")

        # Call (if provided)
        if self.call:
            parts.append(f"\n\n{self.call}")

        return "\n".join(parts)

    def to_user_prompt(self, content: str) -> str:
        """
        Wrap user content with cheat sheet formatting.

        Args:
            content: Raw user input

        Returns:
            Enhanced user prompt
        """
        return f"{content}\n\n[Remember: {self.objective}]"


class CheatSheetEvolution(BaseModel):
    """Track evolution of cheat sheet via DTE testing."""

    version: str
    elements_count: int
    accuracy_improvement: float = Field(description="Improvement over baseline (%)")
    notes: str


# Evolution history (per architecture spec)
CHEAT_SHEET_VERSIONS = [
    CheatSheetEvolution(
        version="v1.0",
        elements_count=21,
        accuracy_improvement=0.0,
        notes="Original 21-element cheat sheet (baseline)",
    ),
    CheatSheetEvolution(
        version="v2.0",
        elements_count=10,
        accuracy_improvement=3.7,
        notes="Fused to 10 essentials via DTE testing (+3.7% accuracy)",
    ),
]


def create_kernel_cheat_sheet() -> CheatSheet:
    """Create cheat sheet optimized for kernel operations."""
    return CheatSheet(
        tone=ToneType.TECHNICAL,
        format=FormatType.JSON,
        act="an expert kernel optimizer focused on performance and reliability",
        objective="Extract maximum value with minimum latency and cost",
        context="Kernel chaining architecture with 3-kernel pipeline",
        keywords=["violations", "risk tier", "confidence", "latency", "tokens"],
        examples=[
            "Input: Decision context → Output: Structured violations JSON",
            "Input: Violations → Output: Binary decision + risk tier",
        ],
        audience="Technical stakeholders monitoring kernel performance",
        citations_required=False,
        call="Optimize for p99 latency ≤90ms and cost ≤$0.001 per decision",
    )


def create_wealth_planning_cheat_sheet() -> CheatSheet:
    """Create cheat sheet for wealth-planning model."""
    return CheatSheet(
        tone=ToneType.PROFESSIONAL,
        format=FormatType.MARKDOWN,
        act="a wealth strategist who spots revenue leaks and redesigns funnels",
        objective="Identify leaks, redesign funnels (upsells/recurring), leverage viral/conversion",
        context="Structured response: hard truth → plan → challenge",
        keywords=["revenue leaks", "upsells", "recurring revenue", "viral coefficient", "conversion"],
        examples=[
            "Leak: 30% churn on trial → Plan: Add onboarding sequence → Challenge: Implement in 2 weeks",
        ],
        audience="Business owners and product teams",
        citations_required=False,
        call="Deliver actionable plan with ROI projections",
    )
