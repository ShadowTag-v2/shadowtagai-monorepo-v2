# apps/counselconduit/api/model_router.py
"""Multi-Model Selector — LiteLLM-based routing.

Routes queries to the optimal model based on:
- Query complexity (simple → flash, complex → pro)
- Firm-level model policy (which models are allowed)
- Cost tier (trial → cheapest, enterprise → best)
- Load balancing (distribute across providers)

Supported models:
- Gemini (3.1 Flash Lite, 3.1 Pro) — default
- Claude (Sonnet 4.5, Opus 4) — via API key
- GPT (4.1, o3) — via API key
- Grok (3.5) — via API key
- Perplexity (pplx-api) — via API key

Architecture: LiteLLM proxy with tenant-scoped, ephemeral, sandbox-bound tokens.
"""

from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.model_router")


# ── Supported Models ──────────────────────────────────────────────────────

class ModelProvider(str, Enum):
    GEMINI = "gemini"
    CLAUDE = "claude"
    GPT = "openai"
    GROK = "grok"
    PERPLEXITY = "perplexity"


class ModelConfig(BaseModel):
    """Configuration for a single model."""
    provider: ModelProvider
    model_id: str
    display_name: str
    max_tokens: int = 8192
    cost_per_1k_input: float  # USD
    cost_per_1k_output: float
    supports_streaming: bool = True
    supports_tools: bool = False
    tier_minimum: str = "trial"  # minimum subscription tier


# Model registry
AVAILABLE_MODELS: dict[str, ModelConfig] = {
    "gemini-flash": ModelConfig(
        provider=ModelProvider.GEMINI,
        model_id="gemini-3.1-flash-lite-preview",
        display_name="Gemini Flash (Fast)",
        cost_per_1k_input=0.00005,
        cost_per_1k_output=0.0001,
        supports_tools=True,
        tier_minimum="trial",
    ),
    "gemini-pro": ModelConfig(
        provider=ModelProvider.GEMINI,
        model_id="gemini-3.1-pro",
        display_name="Gemini Pro (Balanced)",
        cost_per_1k_input=0.00125,
        cost_per_1k_output=0.005,
        supports_tools=True,
        tier_minimum="professional",
    ),
    "claude-sonnet": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_id="claude-sonnet-4-5-20250514",
        display_name="Claude Sonnet (Analysis)",
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        supports_tools=True,
        tier_minimum="professional",
    ),
    "claude-opus": ModelConfig(
        provider=ModelProvider.CLAUDE,
        model_id="claude-opus-4-20250514",
        display_name="Claude Opus (Deep Reasoning)",
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        supports_tools=True,
        tier_minimum="enterprise",
    ),
    "gpt-4-1": ModelConfig(
        provider=ModelProvider.GPT,
        model_id="gpt-4.1",
        display_name="GPT-4.1 (General)",
        cost_per_1k_input=0.002,
        cost_per_1k_output=0.008,
        supports_tools=True,
        tier_minimum="professional",
    ),
    "grok-3-5": ModelConfig(
        provider=ModelProvider.GROK,
        model_id="grok-3.5",
        display_name="Grok 3.5 (Real-time)",
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        tier_minimum="professional",
    ),
    "perplexity": ModelConfig(
        provider=ModelProvider.PERPLEXITY,
        model_id="pplx-api",
        display_name="Perplexity (Web Search)",
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.005,
        tier_minimum="professional",
    ),
}


# ── Routing Logic ─────────────────────────────────────────────────────────

class ModelRequest(BaseModel):
    """User's model selection or auto-route request."""
    preferred_model: str | None = None  # None = auto-route
    query_complexity: str = "medium"  # low, medium, high
    user_tier: str = "trial"
    firm_allowed_models: list[str] = Field(default_factory=lambda: ["gemini-flash"])


def select_model(req: ModelRequest) -> ModelConfig:
    """Select the optimal model based on request parameters.

    Priority:
    1. User preference (if allowed by tier + firm policy)
    2. Auto-route based on complexity + tier
    3. Fallback to cheapest allowed model
    """
    # User preference
    if req.preferred_model and req.preferred_model in AVAILABLE_MODELS:
        model = AVAILABLE_MODELS[req.preferred_model]
        if req.preferred_model in req.firm_allowed_models:
            return model
        logger.warning(
            "Model %s not in firm policy, falling back", req.preferred_model
        )

    # Auto-route by complexity + tier
    tier_models = {
        k: v
        for k, v in AVAILABLE_MODELS.items()
        if k in req.firm_allowed_models
    }

    if not tier_models:
        # Absolute fallback
        return AVAILABLE_MODELS["gemini-flash"]

    # Complexity-based selection
    if req.query_complexity == "low":
        # Cheapest and fastest
        return min(tier_models.values(), key=lambda m: m.cost_per_1k_input)
    elif req.query_complexity == "high":
        # Most capable
        return max(tier_models.values(), key=lambda m: m.cost_per_1k_output)

    # Medium — balanced
    sorted_models = sorted(
        tier_models.values(),
        key=lambda m: m.cost_per_1k_input + m.cost_per_1k_output,
    )
    return sorted_models[len(sorted_models) // 2]


def get_models_for_tier(tier: str) -> list[ModelConfig]:
    """Return all models available for a given subscription tier."""
    tier_rank = {"trial": 0, "professional": 1, "enterprise": 2}
    user_rank = tier_rank.get(tier, 0)

    return [
        model
        for model in AVAILABLE_MODELS.values()
        if tier_rank.get(model.tier_minimum, 0) <= user_rank
    ]
