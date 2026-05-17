# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Configuration for Nightly Intel Pipeline
ATP 5-19 Risk Management Framework Implementation
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
STORAGE_DIR = BASE_DIR / "storage"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, STORAGE_DIR]:
  directory.mkdir(parents=True, exist_ok=True)

# Ethical Scraping Configuration (ATP 5-19 RA-1 Compliant)
SCRAPING_ETHICS = {
  "robots_txt": {
    "enabled": True,
    "cache_ttl": 86400,  # 24 hours per RFC 9309
    "respect_crawl_delay": True,
    "honor_disallow": True,
    "user_agent": "NightlyIntelBot/1.0 (Research; +https://github.com/aiyou-intel)",
  },
  "rate_limiting": {
    "default_delay": 3.0,  # seconds between requests
    "youtube": 5.0,
    "twitter": 4.0,
    "github": 2.0,
    "arxiv": 3.0,
    "news_api": 2.0,
    "regulatory": 10.0,  # .gov domains
    "adaptive_throttling": True,
    "max_concurrent": 3,
    "jitter_factor": 0.3,  # ±30% randomization
  },
  "circuit_breaker": {
    "failure_threshold": 5,  # Consecutive failures to open circuit
    "timeout_seconds": 300,  # 5 minutes before retry
    "half_open_max_calls": 1,
  },
  "retry_policy": {"max_attempts": 3, "backoff_multiplier": 2, "initial_wait": 1.0},
}

# GitHub Repository Configuration
GITHUB_CONFIG = {
  "token": os.getenv("GITHUB_TOKEN", ""),  # Set in .env file
  "target_topics": [
    "mlops",
    "machine-learning",
    "kubernetes",
    "ai-orchestration",
    "llm",
    "vector-database",
    "feature-store",
    "model-serving",
    "ml-pipeline",
    "data-engineering",
  ],
  "min_stars": 100,
  "max_repos_per_topic": 10,
  "flatten_config": {
    "include_extensions": [".py", ".yaml", ".yml", ".json", ".md", ".tf"],
    "exclude_dirs": ["node_modules", "venv", ".git", "__pycache__", "dist", "build"],
    "max_file_size_mb": 5,
  },
}

# arXiv Crawler Configuration
ARXIV_CONFIG = {
  "categories": [
    "cs.AI",  # Artificial Intelligence
    "cs.LG",  # Machine Learning
    "cs.CL",  # Computation and Language
    "cs.CV",  # Computer Vision
    "cs.DC",  # Distributed Computing
    "stat.ML",  # Machine Learning (Statistics)
  ],
  "max_results_per_category": 50,
  "days_back": 7,  # Look back 7 days for new papers
  "search_terms": [
    "MLOps",
    "LLM",
    "large language model",
    "model serving",
    "ML infrastructure",
    "AI governance",
    "model monitoring",
  ],
}

# JR Engine Scoring Configuration
JR_ENGINE_CONFIG = {
  "enabled": True,
  "model": "claude-3-5-sonnet-20241022",  # Primary LLM for scoring
  "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
  "scoring_criteria": {
    "purpose_alignment": 0.35,  # How well does it align with MLOps/AI goals
    "technical_merit": 0.25,  # Quality of implementation
    "adoption_potential": 0.20,  # Community traction
    "risk_assessment": 0.20,  # ATP 5-19 risk level
  },
  "tier_thresholds": {
    "tier_1": 85,  # Executive review required
    "tier_2": 70,  # Auto-action approved
    "tier_3": 50,  # Archive for later
  },
}

# ATP 5-19 Risk Assessment Levels
ATP_RISK_LEVELS = {
  "RA-1": {
    "severity": "Catastrophic",
    "controls": ["Multi-layer validation", "Circuit breakers", "Rate limiting"],
    "review": "Executive approval required",
  },
  "RA-2": {
    "severity": "Critical",
    "controls": ["Automated monitoring", "Rollback capability"],
    "review": "Senior engineer approval",
  },
  "RA-3": {
    "severity": "Moderate",
    "controls": ["Standard testing", "Code review"],
    "review": "Peer review",
  },
  "RA-4": {
    "severity": "Low",
    "controls": ["Basic validation"],
    "review": "Auto-approve",
  },
}

# Storage Configuration (Local execution)
STORAGE_CONFIG = {
  "database": {"type": "sqlite", "path": str(STORAGE_DIR / "intel_pipeline.db")},
  "briefing_output": {"format": "markdown", "path": str(DATA_DIR / "briefings")},
  "flattened_repos": {"path": str(DATA_DIR / "repos")},
  "arxiv_papers": {"path": str(DATA_DIR / "papers")},
}

# Agent Properties (Autonomous execution framework)
AGENT_PROPERTIES = {
  "autonomy": {
    "enabled": True,
    "description": "Agent operates independently with sequential decision-making",
  },
  "proactiveness": {
    "enabled": True,
    "description": "Anticipates needs and opportunities",
  },
  "reactivity": {
    "enabled": True,
    "description": "Monitors state and adapts to changes",
  },
  "social_ability": {
    "enabled": True,
    "description": "Multi-agent collaboration when needed",
  },
}

# Execution Framework Principles
EXECUTION_FRAMEWORK = {
  "monte_carlo_decisions": True,  # Probabilistic decision making
  "jr_engine_primary": True,  # Purpose → Reasons → Brakes
  "boy_scout_rule": True,  # Leave code cleaner
  "reality_distortion_field": True,  # Iterate until "insanely great"
  "revenue_focus": True,  # Prioritize monetization opportunities
}

# Logging Configuration
LOGGING_CONFIG = {
  "level": "INFO",
  "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  "file": str(LOGS_DIR / "pipeline.log"),
  "console": True,
}

# Pipeline Schedule (for local execution)
PIPELINE_SCHEDULE = {
  "run_hour": 2,  # 2 AM local time
  "enabled": True,
  "steps": [
    "ingestion",
    "jr_scoring",
    "tier_classification",
    "synthesis",
    "tier2_actions",
    "storage",
    "briefing_delivery",
  ],
}

# GKE Deployment Configuration
GKE_CONFIG = {
  "enabled": os.getenv("EXECUTION_MODE") == "gke",
  "cluster": {
    "name": "nightly-intel-cluster",
    "zone": "us-central1-a",
    "project_id": os.getenv("GCP_PROJECT_ID", ""),
    "namespace": "default",
  },
  "cronjob": {
    "schedule": "0 2 * * *",  # 2 AM UTC daily
    "timezone": "UTC",
    "concurrency_policy": "Forbid",
    "runtime_target_minutes": 45,
    "timeout_minutes": 60,
  },
  "resources": {
    "requests": {"cpu": "1000m", "memory": "2Gi", "ephemeral_storage": "5Gi"},
    "limits": {"cpu": "2000m", "memory": "4Gi", "ephemeral_storage": "10Gi"},
  },
  "storage": {
    "data_pvc": "intel-pipeline-data-pvc",
    "storage_pvc": "intel-pipeline-storage-pvc",
    "logs_pvc": "intel-pipeline-logs-pvc",
    "data_size_gb": 50,
    "storage_size_gb": 10,
    "logs_size_gb": 5,
  },
  "monitoring": {
    "enabled": True,
    "metrics": [
      "runtime_duration_minutes",
      "items_ingested_total",
      "items_per_source",
      "tier_distribution",
      "cost_per_item_usd",
      "failure_rate_percent",
    ],
    "alerts": {
      "runtime_exceeded_minutes": 60,
      "failure_rate_threshold_percent": 5,
      "cost_spike_multiplier": 2.0,
    },
  },
  "cost_model": {
    "target_monthly_usd": 77,
    "breakdown": {
      "claude_api_per_run": 1.50,  # Average
      "gke_compute_monthly": 12.50,
      "storage_monthly": 3.00,
    },
    "sensitivity": {"2x_volume": 120, "3x_volume": 180},
  },
}

# Multi-Source Coverage Targets (for Gemini Analysis)
MULTI_SOURCE_COVERAGE = {
  "targets": {
    "github": 0.40,  # 40% of daily items
    "arxiv": 0.25,  # 25%
    "youtube": 0.15,  # 15%
    "twitter": 0.10,  # 10%
    "news": 0.10,  # 10%
  },
  "quality_metrics": {
    "relevance": {
      "metric": "jr_engine_score_distribution",
      "target_tier1_tier2_percent": 40,
    },
    "timeliness": {"metric": "data_freshness_days", "target_max_days": 7},
    "completeness": {"metric": "sources_active", "target_min_sources": 5},
  },
}

# Tier Distribution Targets (for Gemini Analysis)
TIER_DISTRIBUTION_TARGETS = {
  "tier_1": {"min": 0.10, "max": 0.15},  # 10-15% executive review
  "tier_2": {"min": 0.35, "max": 0.40},  # 35-40% auto-action
  "tier_3": {"min": 0.30, "max": 0.35},  # 30-35% archive
  "tier_4": {"min": 0.15, "max": 0.20},  # 15-20% low priority
}

# Gemini Analysis Prompt Configuration
GEMINI_ANALYSIS_CONFIG = {
  "enabled": os.getenv("GEMINI_ANALYSIS_ENABLED", "false").lower() == "true",
  "model": "gemini-2.0-pro",
  "confidence_target": 0.60,  # 60% pre-production, 70% post-deployment
  "analysis_areas": [
    "ethical_compliance",
    "architecture_optimization",
    "cost_sustainability",
    "multi_source_coverage",
    "tier_classification",
    "runtime_efficiency",
    "integration_patterns",
    "edge_case_resilience",
  ],
  "output_formats": ["markdown_report", "json_metrics", "visualization_data"],
}
