"""Gemini Ingestion Layer Configuration
====================================
Configuration for Gemini-powered semantic extraction.
"""

import os

# Gemini API Configuration
GEMINI_INGESTION_CONFIG = {
    # API Settings
    "api_key": os.getenv("GEMINI_API_KEY", ""),
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    # Model Selection - Flash 2.0 for cost efficiency
    # Flash: $0.075/1M input, $0.30/1M output (200x cheaper than Claude)
    "model": os.getenv("GEMINI_INGESTION_MODEL", "gemini-2.0-flash"),
    "fallback_model": "gemini-2.0-flash-lite",
    # Generation Settings
    "max_tokens": 4096,
    "temperature": 0.3,  # Lower temp for consistent extraction
    "timeout": 60.0,  # Seconds
    # Batch Processing
    "batch_size": 10,
    "concurrent_requests": 3,
    "delay_between_batches": 1.0,  # Seconds
    # Retry Policy
    "max_retries": 3,
    "retry_backoff": 2.0,  # Exponential backoff multiplier
    # Quality Gates
    "min_confidence": 0.5,  # Minimum confidence to accept
    "fallback_on_low_conf": True,  # Use fallback model if confidence too low
    # Cost Controls
    "max_tokens_per_doc": 50000,  # Truncate docs > 50K tokens
    "max_daily_spend_usd": 10.0,  # Daily spending cap
    "track_costs": True,
    # Feature Flags
    "enabled": os.getenv("GEMINI_INGESTION_ENABLED", "true").lower() == "true",
    "enable_delta_detection": True,
    "enable_jr_hints": True,  # Pre-fill JR Engine hints
    # Source Type Detection Rules
    "source_type_rules": {
        "federal_register": {
            "url_patterns": ["federalregister.gov"],
            "keywords": ["CFR", "docket", "effective date"],
        },
        "arxiv": {
            "url_patterns": ["arxiv.org"],
            "keywords": ["abstract", "authors", "categories"],
        },
        "github": {
            "url_patterns": ["github.com"],
            "keywords": ["repository", "stars", "forks"],
        },
    },
    # Topic Classification
    "topic_categories": [
        "AI_GOVERNANCE",
        "ML_OPS",
        "SECURITY",
        "COMPLIANCE",
        "INFRASTRUCTURE",
        "DATA_PRIVACY",
        "AUTONOMOUS_SYSTEMS",
        "ENERGY",
        "DEFENSE",
        "HEALTHCARE",
        "FINANCE",
        "SPACE",
    ],
    # Risk Tag Vocabulary
    "risk_tags": [
        "compliance_deadline",
        "fine_per_violation",
        "enforcement_action",
        "data_breach_risk",
        "export_control",
        "itar_restricted",
        "hipaa_relevant",
        "fda_regulated",
        "critical_infrastructure",
        "executive_order",
        "agency_guidance",
        "comment_period",
        "effective_immediately",
        "phase_in_period",
    ],
    # Pricing (for cost tracking)
    "pricing": {
        "gemini-2.0-flash": {
            "input_per_million": 0.075,
            "output_per_million": 0.30,
        },
        "gemini-2.0-flash-lite": {
            "input_per_million": 0.0375,
            "output_per_million": 0.15,
        },
        "gemini-2.5-pro-preview-06-05": {
            "input_per_million": 1.25,
            "output_per_million": 10.0,
        },
    },
}


def get_model_pricing(model: str) -> dict:
    """Get pricing for a specific model"""
    return GEMINI_INGESTION_CONFIG["pricing"].get(
        model,
        {"input_per_million": 0.1, "output_per_million": 0.4},  # Default estimate
    )


def estimate_cost(input_tokens: int, output_tokens: int, model: str = None) -> float:
    """Estimate cost for a Gemini API call.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (uses config default if not specified)

    Returns:
        Estimated cost in USD

    """
    model = model or GEMINI_INGESTION_CONFIG["model"]
    pricing = get_model_pricing(model)

    input_cost = (input_tokens / 1_000_000) * pricing["input_per_million"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_million"]

    return input_cost + output_cost
