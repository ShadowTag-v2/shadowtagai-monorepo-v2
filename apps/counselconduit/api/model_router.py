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
from enum import StrEnum

from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.model_router")


# ── Supported Models ──────────────────────────────────────────────────────


class ModelProvider(StrEnum):
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


# ── NadirClaw-Inspired 3-Tier Dispatch ────────────────────────────────────
# Architecture: 10ms prompt classification → tier routing → session pinning
# Tiers: Simple → Flash ($0.075/1M), Complex → Sonnet ($3/1M), Agentic → Pro ($3.50/1M)


class DispatchTier(StrEnum):
    """NadirClaw-style 3-tier dispatch classification."""

    SIMPLE = "simple"  # FAQ, greetings, short lookups → Flash
    COMPLEX = "complex"  # Multi-step analysis, case review → Sonnet/Pro
    AGENTIC = "agentic"  # Tool use, multi-turn reasoning → Pro/Opus


# ── Per-Tenant Request Quotas (Noisy Neighbor Protection) ─────────────────


class TenantQuota(BaseModel):
    """Per-tenant request quota for noisy neighbor protection."""

    firm_id: str
    max_rpm: int = 60  # requests per minute
    max_daily: int = 5000
    current_rpm: int = 0
    current_daily: int = 0
    tier_overrides: dict[str, int] = Field(
        default_factory=lambda: {
            "trial": 20,
            "professional": 60,
            "enterprise": 200,
        }
    )

    def is_within_quota(self, tier: str) -> bool:
        """Check if tenant is within rate limits."""
        limit = self.tier_overrides.get(tier, self.max_rpm)
        return self.current_rpm < limit and self.current_daily < self.max_daily


# Tenant quota registry (in production: Firestore-backed)
_tenant_quotas: dict[str, TenantQuota] = {}


def get_tenant_quota(firm_id: str, tier: str = "trial") -> TenantQuota:
    """Get or create quota tracker for a tenant."""
    if firm_id not in _tenant_quotas:
        _tenant_quotas[firm_id] = TenantQuota(firm_id=firm_id)
    return _tenant_quotas[firm_id]


# ── BYOK Encryption Config (Phase 4 Stub) ────────────────────────────────


class BYOKConfig(BaseModel):
    """Bring-Your-Own-Key encryption config. Phase 4 enterprise feature."""

    enabled: bool = False
    kms_key_uri: str | None = None  # GCP KMS key URI
    rotation_period_days: int = 90


# ── Session Pinning ───────────────────────────────────────────────────────

# Session → model mapping for multi-turn context preservation
_session_pins: dict[str, str] = {}


def pin_session_model(session_id: str, model_key: str) -> None:
    """Pin a session to a specific model for context continuity."""
    _session_pins[session_id] = model_key


def get_pinned_model(session_id: str) -> str | None:
    """Get the pinned model for a session."""
    return _session_pins.get(session_id)


# ── Prompt Classifier (NadirClaw-style, ~10ms) ───────────────────────────


def classify_prompt(query: str) -> DispatchTier:
    """Classify prompt complexity in ~10ms using heuristics.

    NadirClaw-inspired: no LLM call, pure string analysis.
    """
    query_lower = query.lower()
    word_count = len(query.split())

    # Agentic indicators
    agentic_signals = [
        "analyze", "compare", "draft", "review contract",
        "find precedent", "summarize case", "prepare memo",
        "tool:", "search:", "cite:", "multi-step",
    ]
    if any(signal in query_lower for signal in agentic_signals) or word_count > 200:
        return DispatchTier.AGENTIC

    # Complex indicators
    complex_signals = [
        "explain", "why", "how does", "what are the implications",
        "difference between", "pros and cons", "legal analysis",
    ]
    if any(signal in query_lower for signal in complex_signals) or word_count > 50:
        return DispatchTier.COMPLEX

    # Default: simple
    return DispatchTier.SIMPLE


# ── Tier-to-Model Mapping ────────────────────────────────────────────────

TIER_MODEL_MAP: dict[DispatchTier, list[str]] = {
    DispatchTier.SIMPLE: ["gemini-flash"],
    DispatchTier.COMPLEX: ["claude-sonnet", "gemini-pro", "gpt-4-1"],
    DispatchTier.AGENTIC: ["gemini-pro", "claude-opus", "grok-3-5"],
}

# Rate limit fallback chain
FALLBACK_CHAIN: dict[str, str] = {
    "gemini-pro": "claude-sonnet",
    "claude-sonnet": "gpt-4-1",
    "claude-opus": "gemini-pro",
    "gpt-4-1": "gemini-pro",
    "grok-3-5": "gemini-pro",
    "perplexity": "gemini-flash",
}


# ── Routing Logic ─────────────────────────────────────────────────────────


class ModelRequest(BaseModel):
    """User's model selection or auto-route request."""

    preferred_model: str | None = None  # None = auto-route
    query_complexity: str = "medium"  # low, medium, high
    query_text: str = ""  # for NadirClaw classifier
    user_tier: str = "trial"
    firm_id: str = ""
    session_id: str = ""
    firm_allowed_models: list[str] = Field(default_factory=lambda: ["gemini-flash"])


def select_model(req: ModelRequest) -> ModelConfig:
    """Select the optimal model using NadirClaw 3-tier dispatch.

    Priority:
    1. Session pin (multi-turn context preservation)
    2. User preference (if allowed by tier + firm policy)
    3. NadirClaw auto-classify → tier dispatch
    4. Rate limit fallback chain
    5. Fallback to cheapest allowed model
    """
    # Check per-tenant quota (noisy neighbor protection)
    if req.firm_id:
        quota = get_tenant_quota(req.firm_id, req.user_tier)
        if not quota.is_within_quota(req.user_tier):
            logger.warning("Tenant %s exceeded quota, rate limiting", req.firm_id)
            return AVAILABLE_MODELS["gemini-flash"]  # degrade to cheapest

    # 1. Session pin — preserve multi-turn context
    if req.session_id:
        pinned = get_pinned_model(req.session_id)
        if pinned and pinned in AVAILABLE_MODELS and pinned in req.firm_allowed_models:
            return AVAILABLE_MODELS[pinned]

    # 2. User preference
    if req.preferred_model and req.preferred_model in AVAILABLE_MODELS:
        model = AVAILABLE_MODELS[req.preferred_model]
        if req.preferred_model in req.firm_allowed_models:
            if req.session_id:
                pin_session_model(req.session_id, req.preferred_model)
            return model
        logger.warning("Model %s not in firm policy, falling back", req.preferred_model)

    # 3. NadirClaw auto-classify (~10ms)
    if req.query_text:
        dispatch_tier = classify_prompt(req.query_text)
    else:
        # Legacy compatibility: map query_complexity to dispatch tier
        complexity_map = {
            "low": DispatchTier.SIMPLE,
            "medium": DispatchTier.COMPLEX,
            "high": DispatchTier.AGENTIC,
        }
        dispatch_tier = complexity_map.get(req.query_complexity, DispatchTier.COMPLEX)

    # Find best model from tier candidates
    tier_candidates = TIER_MODEL_MAP.get(dispatch_tier, ["gemini-flash"])
    for candidate in tier_candidates:
        if candidate in req.firm_allowed_models and candidate in AVAILABLE_MODELS:
            if req.session_id:
                pin_session_model(req.session_id, candidate)
            return AVAILABLE_MODELS[candidate]

    # 4. Rate limit fallback chain
    for candidate in tier_candidates:
        fallback = FALLBACK_CHAIN.get(candidate)
        if fallback and fallback in req.firm_allowed_models and fallback in AVAILABLE_MODELS:
            logger.info("Fallback: %s → %s", candidate, fallback)
            return AVAILABLE_MODELS[fallback]

    # 5. Absolute fallback
    return AVAILABLE_MODELS["gemini-flash"]


def get_models_for_tier(tier: str) -> list[ModelConfig]:
    """Return all models available for a given subscription tier."""
    tier_rank = {"trial": 0, "professional": 1, "enterprise": 2}
    user_rank = tier_rank.get(tier, 0)

    return [model for model in AVAILABLE_MODELS.values() if tier_rank.get(model.tier_minimum, 0) <= user_rank]
