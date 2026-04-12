"""
Core configuration and constants for Gemini API + Custom Tools workaround.

CONTEXT: Google Gemini API blocks simultaneous use of:
  - Custom tools (MCP/function calling)
  - Google Search grounding

This module defines the architecture options and SLA gates.
"""

# ============================================================================
# CORE CONSTRAINT
# ============================================================================
GEMINI_LIMITATION = "tools + grounding = mutually exclusive (unverified)"


# ============================================================================
# ARCHITECTURE OPTIONS
# ============================================================================
class ArchitectureOption:
    SEQUENTIAL_ORCHESTRATION = "sequential_orchestration"  # Best long-term
    PARALLEL_EXECUTION = "parallel_execution"  # Rejected (cost)
    CUSTOM_SEARCH_TOOL = "custom_search_tool"  # Ship now


# ============================================================================
# IMPLEMENTATION TARGETS
# ============================================================================
class SearchProvider:
    BRAVE = "brave_search_api"
    SERPER = "serper_api"
    TAVILY = "tavily_api"


DEFAULT_SEARCH_PROVIDER = SearchProvider.BRAVE

# Model configuration
INTENT_CLASSIFIER_MODEL = "gemini-1.5-flash"
ORCHESTRATOR = "cor_routing_layer"

# ============================================================================
# SLA REQUIREMENTS
# ============================================================================
P99_LATENCY_MS = 90
MAX_SYNTHESIS_OVERHEAD_MS = 300
TARGET_SEARCH_COST_PER_QUERY = 0.01  # $0.01


# ============================================================================
# REVENUE TIERS
# ============================================================================
class RevenueTier:
    FREE = "single_mode_selection"  # User picks internal OR web
    PRO = "automatic_hybrid_routing"  # Auto-detect, seamless blend
    ENTERPRISE = "custom_tool_chains"  # Full customization


TIER_PRICING = {
    RevenueTier.FREE: 0.00,
    RevenueTier.PRO: 19.99,  # Monthly - TBD
    RevenueTier.ENTERPRISE: 500.00,  # Monthly minimum
}

# ============================================================================
# BOOTSTRAP GATES
# ============================================================================
ROI_TARGET = 3.0  # 18 months
LTV_CAC_MIN = 4.0  # 12 months
MIN_FEATURE_QUALITY = 0.90  # 90% search quality parity


# ============================================================================
# QUERY ROUTING CATEGORIES
# ============================================================================
class QueryIntent:
    INTERNAL = "internal"  # Files/docs/repos only
    WEB = "web"  # Current events/URLs/external
    HYBRID = "both"  # Company context + external validation


# Intent classification confidence threshold
INTENT_CONFIDENCE_THRESHOLD = 0.80

# ============================================================================
# SEARCH CONFIGURATION
# ============================================================================
BRAVE_API_CONFIG = {
    "free_tier_limit": 2000,  # Queries per month
    "endpoint": "https://api.search.brave.com/res/v1/web/search",
    "snippet_count": 5,
    "max_snippet_length": 300,
}


# ============================================================================
# MONITORING & METRICS
# ============================================================================
class MetricKey:
    SEARCH_QUALITY = "search_quality_score"
    INTENT_ACCURACY = "intent_classification_accuracy"
    LATENCY_P99 = "latency_p99_ms"
    COST_PER_QUERY = "cost_per_query_usd"
    SYNTHESIS_HALLUCINATION = "synthesis_hallucination_rate"


SUCCESS_THRESHOLDS = {
    MetricKey.SEARCH_QUALITY: 0.90,  # 90% vs Google Grounding
    MetricKey.INTENT_ACCURACY: 0.80,  # 80% classification accuracy
    MetricKey.LATENCY_P99: P99_LATENCY_MS,
    MetricKey.COST_PER_QUERY: 0.02,  # <2¢ including search API
    MetricKey.SYNTHESIS_HALLUCINATION: 0.05,  # <5% hallucination rate
}
