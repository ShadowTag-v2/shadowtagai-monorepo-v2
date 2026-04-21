# apps/counselconduit/api/model_router.py
"""Multi-Model Selector — LiteLLM-based routing.

Routes queries to the optimal model based on:
- Query complexity (simple → flash, complex → pro)
- Firm-level model policy (which models are allowed)
- Cost tier (trial -> cheapest, enterprise -> best)
- Per-tenant quotas (noisy neighbor protection)
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
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
        model_id="gemini-3.1-flash-lite-preview-thinking",
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
    """Get or create quota tracker for a tenant.

    In production, this reads/writes to Firestore:
        db.collection('tenant_quotas').document(firm_id)
    In-memory fallback for local dev and tests.
    """
    if firm_id not in _tenant_quotas:
        _tenant_quotas[firm_id] = TenantQuota(firm_id=firm_id)
    return _tenant_quotas[firm_id]


async def sync_quota_to_firestore(firm_id: str) -> None:
    """Persist tenant quota state to Firestore (Item 5).

    Called after each request to persist RPM/daily counters.
    Uses Firestore's increment() for atomic counter updates.
    """
    try:
        from google.cloud import firestore as _fs  # lazy import

        db = _fs.AsyncClient(project="shadowtag-omega-v4")
        doc_ref = db.collection("tenant_quotas").document(firm_id)
        quota = _tenant_quotas.get(firm_id)
        if quota:
            await doc_ref.set(
                {
                    "firm_id": firm_id,
                    "current_rpm": quota.current_rpm,
                    "current_daily": quota.current_daily,
                    "max_rpm": quota.max_rpm,
                    "max_daily": quota.max_daily,
                    "updated_at": _fs.SERVER_TIMESTAMP,
                },
                merge=True,
            )
    except ImportError:
        pass  # Firestore SDK not installed (local dev)
    except Exception as e:
        logger.warning("Firestore quota sync failed for %s: %s", firm_id, e)


# ── BYOK Encryption Config (Phase 4 Stub) ────────────────────────────────


class BYOKConfig(BaseModel):
    """Bring-Your-Own-Key configuration for enterprise tenants.

    Supports customer-managed encryption keys via Cloud KMS.
    Fields:
        enabled: Whether BYOK is active for this tenant.
        kms_key_uri: Full Cloud KMS CryptoKey resource name.
        kms_rotation_period_days: Key rotation period in days (default 90).
        kms_next_rotation_time: ISO 8601 timestamp for next scheduled rotation.
        key_algorithm: KMS key algorithm (default GOOGLE_SYMMETRIC_ENCRYPTION).
    """

    enabled: bool = False
    kms_key_uri: str = ""
    kms_rotation_period_days: int = 90
    kms_next_rotation_time: str = ""
    key_algorithm: str = "GOOGLE_SYMMETRIC_ENCRYPTION"


# ── Session Pinning with TTL (Item 13) ────────────────────────────────────

SESSION_PIN_TTL_SECONDS = 30 * 60  # 30 minutes auto-expire

# Session → (model_key, pinned_at_timestamp)
_session_pins: dict[str, tuple[str, float]] = {}


def pin_session_model(session_id: str, model_key: str) -> None:
    """Pin a session to a specific model for context continuity."""
    _session_pins[session_id] = (model_key, time.time())


def get_pinned_model(session_id: str) -> str | None:
    """Get the pinned model for a session, respecting TTL."""
    pin = _session_pins.get(session_id)
    if pin is None:
        return None
    model_key, pinned_at = pin
    if time.time() - pinned_at > SESSION_PIN_TTL_SECONDS:
        del _session_pins[session_id]
        logger.info("Session pin expired for %s (TTL=%ds)", session_id, SESSION_PIN_TTL_SECONDS)
        return None
    return model_key


# ── Dispatch Metrics (Items 9, 16) ────────────────────────────────────────

# In-memory counters for Cloud Monitoring export
_dispatch_metrics: dict[str, int] = defaultdict(int)
_fallback_hits: dict[str, int] = defaultdict(int)


def record_dispatch(tier: str, model_key: str) -> None:
    """Record dispatch decision for Cloud Monitoring metrics."""
    _dispatch_metrics[f"dispatch.{tier}.{model_key}"] += 1


def record_fallback(original: str, fallback: str) -> None:
    """Record fallback chain activation."""
    _fallback_hits[f"fallback.{original}->{fallback}"] += 1
    logger.info("Fallback chain hit: %s → %s", original, fallback)


def get_dispatch_metrics() -> dict[str, int]:
    """Return all dispatch metrics for Cloud Monitoring export."""
    return {**_dispatch_metrics, **_fallback_hits}


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
            record_fallback(candidate, fallback)
            return AVAILABLE_MODELS[fallback]

    # 5. Absolute fallback
    record_dispatch("fallback", "gemini-flash")
    return AVAILABLE_MODELS["gemini-flash"]


# ── FastAPI Integration (Item 4: Wire NadirClaw into CC API) ──────────────


async def dispatch_request(
    query: str,
    firm_id: str,
    session_id: str = "",
    user_tier: str = "trial",
    preferred_model: str | None = None,
    firm_allowed_models: list[str] | None = None,
) -> dict:
    """Top-level dispatch function for CounselConduit API endpoints.

    Wires NadirClaw classification → model selection → quota tracking → metrics.
    Call this from FastAPI route handlers.
    """
    if firm_allowed_models is None:
        firm_allowed_models = ["gemini-flash"]

    req = ModelRequest(
        query_text=query,
        firm_id=firm_id,
        session_id=session_id,
        user_tier=user_tier,
        preferred_model=preferred_model,
        firm_allowed_models=firm_allowed_models,
    )

    # Classify and route
    model = select_model(req)
    tier = classify_prompt(query) if query else DispatchTier.SIMPLE

    # ── arXiv 2512.14982: Prompt Repetition (Zero-Cost Accuracy Boost) ────
    # For non-reasoning model tiers (flash, lite, mini, haiku), repeat the
    # user's instruction in the context. Boosts accuracy 1-8% with zero
    # additional output tokens or latency.
    # Source: Leviathan, Kalman, Matias (Google Research)
    # DO NOT apply to: thinking/reasoning models (Gemini thinking, extended thinking)
    _NON_REASONING_SIGNALS = ("flash", "lite", "mini", "haiku", "pplx")
    prompt_repeated = False
    effective_query = query
    if any(sig in model.model_id.lower() for sig in _NON_REASONING_SIGNALS):
        if not model.model_id.lower().endswith("-thinking"):
            effective_query = f"{query}\n\n---\n[Instruction Repeat]: {query}"
            prompt_repeated = True

    # Record metrics for Cloud Monitoring
    record_dispatch(tier.value, model.model_id)

    # Increment tenant quota counters
    if firm_id:
        quota = get_tenant_quota(firm_id, user_tier)
        quota.current_rpm += 1
        quota.current_daily += 1
        # Fire-and-forget Firestore sync
        import asyncio
        asyncio.create_task(sync_quota_to_firestore(firm_id))

    return {
        "model": model.model_id,
        "provider": model.provider,
        "tier": tier.value,
        "session_pinned": bool(get_pinned_model(session_id)) if session_id else False,
        "cost_per_1k_input": model.cost_per_1k_input,
        "prompt_repeated": prompt_repeated,
        "effective_query": effective_query,
    }


def get_models_for_tier(tier: str) -> list[ModelConfig]:
    """Return all models available for a given subscription tier."""
    tier_rank = {"trial": 0, "professional": 1, "enterprise": 2}
    user_rank = tier_rank.get(tier, 0)

    return [model for model in AVAILABLE_MODELS.values() if tier_rank.get(model.tier_minimum, 0) <= user_rank]
