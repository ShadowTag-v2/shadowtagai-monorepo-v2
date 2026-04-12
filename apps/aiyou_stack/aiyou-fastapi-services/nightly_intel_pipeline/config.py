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
        "user_agent": "NightlyIntelBot/1.0 (Research; +https://github.com/shadowtag_v4-intel)",
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

# arXiv Crawler Configuration - PNKLN 19-Vertical Aligned
# Optimized for $77.5B-$124.5B business model intel capture
# Expanded to 50 categories for full tech alignment
ARXIV_CONFIG = {
    "categories": [
        # === CORE AI/ML (15 categories) ===
        "cs.AI",  # Artificial Intelligence
        "cs.LG",  # Machine Learning
        "stat.ML",  # Machine Learning (Statistics)
        "cs.NE",  # Neural and Evolutionary Computing
        "cs.CL",  # Computation and Language (NLP)
        "cs.CV",  # Computer Vision
        "cs.IR",  # Information Retrieval
        "cs.MA",  # Multiagent Systems
        "cs.RO",  # Robotics
        "cs.SD",  # Sound (speech, audio ML)
        "cs.SI",  # Social and Information Networks
        "stat.CO",  # Computation (Statistics)
        "stat.ME",  # Methodology (Statistics)
        "stat.TH",  # Theory (Statistics)
        "stat.AP",  # Applications (Statistics)
        # === SYSTEMS & INFRASTRUCTURE (12 categories) ===
        "cs.DC",  # Distributed Computing
        "cs.NI",  # Networking
        "cs.AR",  # Hardware Architecture
        "cs.OS",  # Operating Systems
        "cs.PF",  # Performance
        "cs.SE",  # Software Engineering
        "cs.DB",  # Databases
        "cs.DS",  # Data Structures
        "cs.ET",  # Emerging Technologies
        "cs.HC",  # Human-Computer Interaction
        "cs.MM",  # Multimedia
        "cs.SY",  # Systems and Control
        # === SECURITY & CRYPTO (5 categories) ===
        "cs.CR",  # Cryptography and Security
        "cs.IT",  # Information Theory
        "cs.LO",  # Logic in Computer Science
        "cs.CY",  # Computers and Society (governance, ethics)
        "quant-ph",  # Quantum Physics (QML, quantum computing)
        # === ENERGY & CONTROL (8 categories) ===
        "eess.SY",  # Systems and Control
        "eess.SP",  # Signal Processing
        "eess.AS",  # Audio and Speech Processing
        "eess.IV",  # Image and Video Processing
        "physics.app-ph",  # Applied Physics
        "cond-mat.mtrl-sci",  # Materials Science
        "math.OC",  # Optimization and Control
        "physics.comp-ph",  # Computational Physics
        # === MEDICAL/BIO AI (6 categories) ===
        "q-bio.QM",  # Quantitative Methods (Biology)
        "q-bio.NC",  # Neurons and Cognition
        "q-bio.GN",  # Genomics
        "cs.CE",  # Computational Engineering
        "physics.bio-ph",  # Biological Physics
        "physics.med-ph",  # Medical Physics
        # === FINANCE/ECON (4 categories) ===
        "q-fin.ST",  # Statistical Finance
        "q-fin.CP",  # Computational Finance
        "q-fin.RM",  # Risk Management
        "econ.EM",  # Econometrics
    ],
    "max_results_per_category": 30,  # Reduced per-category to manage volume
    "days_back": 7,
    # Search terms organized by PNKLN vertical - 100 terms for full coverage
    "search_terms": [
        # === LAYER 2: Core Stack ($6.4B) - 30 terms ===
        "MLOps",
        "LLM",
        "large language model",
        "model serving",
        "ML infrastructure",
        "AI governance",
        "model monitoring",
        "GRPO",  # Group Relative Policy Optimization
        "DPO",  # Direct Preference Optimization
        "vLLM",  # High-performance serving
        "Mixture of Experts",  # MoE scaling
        "RLHF",  # Alignment
        "transformer efficiency",
        "neural architecture search",
        "digital watermarking",  # ShadowTag v2
        "content provenance",  # ShadowTag attestation
        "speculative decoding",  # Inference speedup
        "KV cache optimization",  # Memory efficiency
        "attention mechanism",  # Core architecture
        "flash attention",  # Memory-efficient attention
        "parameter efficient",  # LoRA, QLoRA
        "model quantization",  # INT8, INT4
        "knowledge distillation",  # Model compression
        "inference optimization",  # Deployment efficiency
        "tensor parallelism",  # Distributed training
        "pipeline parallelism",  # Model sharding
        "continuous batching",  # Serving efficiency
        "prefix caching",  # Prompt optimization
        "RAG retrieval",  # Retrieval augmented generation
        "agent framework",  # AI agents
        # === LAYER 3: Digital Mall ($7.7B) - 12 terms ===
        "AI marketplace",
        "model marketplace",
        "API pricing",
        "AI compliance",
        "binary authorization",
        "model registry",  # MLflow, Weights & Biases
        "feature store",  # Feast, Tecton
        "experiment tracking",  # ML lifecycle
        "AI monetization",  # Business models
        "usage metering",  # API billing
        "model licensing",  # Commercial terms
        "AI audit trail",  # Compliance logging
        # === LAYER 4: RoadMesh ($9.6B) - 15 terms ===
        "V2X",  # Vehicle-to-Everything
        "C-V2X",  # Cellular V2X
        "edge computing",
        "LiDAR perception",
        "autonomous driving",
        "connected vehicles",
        "intelligent transportation",
        "traffic optimization",
        "sensor fusion",  # Multi-sensor integration
        "path planning",  # Navigation algorithms
        "object detection",  # Computer vision
        "SLAM",  # Simultaneous localization
        "vehicle localization",  # Positioning
        "V2I communication",  # Vehicle-to-infrastructure
        "platooning",  # Convoy automation
        # === LAYER 5: AiU Orbital ($17.3B) - 12 terms ===
        "LEO satellite",
        "satellite communication",
        "ground station network",
        "space-ground integration",
        "orbital edge computing",
        "satellite AI",
        "CubeSat",  # Small satellites
        "inter-satellite link",  # Mesh networks
        "Earth observation",  # Remote sensing
        "satellite constellation",  # Network topology
        "space debris tracking",  # Orbital safety
        "launch vehicle AI",  # Rocket automation
        # === LAYER 6: Gov & Defense ($31.4B) - 18 terms ===
        "tactical AI",
        "defense AI",
        "medical AI",
        "FDA AI regulation",
        "HIPAA compliance",
        "legal AI",
        "judicial AI",
        "aerospace AI",
        "FAA automation",
        "clinical decision support",  # Medical AI
        "radiology AI",  # Medical imaging
        "drug discovery AI",  # Pharma
        "contract analysis",  # Legal AI
        "compliance automation",  # RegTech
        "ISR intelligence",  # Surveillance
        "predictive maintenance",  # Defense logistics
        "cyber threat detection",  # Security AI
        "simulation AI",  # Training systems
        # === LAYER 1: Gulfstream ($5.1B) - 10 terms ===
        "offshore wind",
        "renewable energy optimization",
        "grid integration",
        "power system AI",
        "CAISO",
        "battery storage",  # Energy storage
        "demand response",  # Grid balancing
        "load forecasting",  # Energy prediction
        "smart grid",  # Grid automation
        "carbon optimization",  # Emissions reduction
        # === Quantum Horizon - 5 terms ===
        "quantum machine learning",
        "quantum computing",  # General QC
        "quantum error correction",  # QC reliability
        "variational quantum",  # VQE, QAOA
        "quantum advantage",  # Supremacy applications
    ],
    # Exclusion filters to avoid immaterial papers
    "exclude_terms": [
        "survey only",  # Pure surveys without implementation
        "theoretical only",  # No practical application
        "toy dataset",  # Not production-relevant
        "mnist",  # Basic benchmarks only
        "cifar-10 only",  # Basic benchmarks only
    ],
    # Vertical relevance scoring weights
    "vertical_weights": {
        "core_stack": 1.0,  # Layer 2: Always relevant
        "digital_mall": 0.9,  # Layer 3: High priority
        "roadmesh": 0.85,  # Layer 4: Infrastructure
        "orbital": 0.8,  # Layer 5: Strategic
        "gov_defense": 0.95,  # Layer 6: Revenue driver
        "energy": 0.7,  # Layer 1: Foundational
        "quantum": 0.6,  # Future: Horizon planning
    },
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
    "RA-4": {"severity": "Low", "controls": ["Basic validation"], "review": "Auto-approve"},
}

# Industry Crawler Configuration
INDUSTRY_SOURCES_CONFIG = {
    "enabled": True,
    "rate_limits": {
        "rss": 1.0,  # 1 second between RSS feeds
        "html": 3.0,  # 3 seconds between HTML scrapes
        "gov": 10.0,  # 10 seconds for .gov/.mil domains
        "default": 3.0,  # Default rate limit
    },
    "days_back": 30,  # How far back to fetch articles
    "min_relevance": 0.5,  # Minimum relevance score to keep
    "max_articles_per_source": 20,  # Limit per source per crawl
    "vertical_weights": {
        "core_stack": 1.0,
        "digital_mall": 0.9,
        "roadmesh": 0.85,
        "orbital": 0.8,
        "gov_defense": 0.95,
        "energy": 0.7,
        "analysts": 0.75,
    },
}

# Storage Configuration (Local execution)
STORAGE_CONFIG = {
    "database": {"type": "sqlite", "path": str(STORAGE_DIR / "intel_pipeline.db")},
    "briefing_output": {"format": "markdown", "path": str(DATA_DIR / "briefings")},
    "flattened_repos": {"path": str(DATA_DIR / "repos")},
    "arxiv_papers": {"path": str(DATA_DIR / "papers")},
    "industry_articles": {"path": str(DATA_DIR / "industry")},
    "federal_register": {"path": str(DATA_DIR / "federal_register")},
}

# Agent Properties (Autonomous execution framework)
AGENT_PROPERTIES = {
    "autonomy": {
        "enabled": True,
        "description": "Agent operates independently with sequential decision-making",
    },
    "proactiveness": {"enabled": True, "description": "Anticipates needs and opportunities"},
    "reactivity": {"enabled": True, "description": "Monitors state and adapts to changes"},
    "social_ability": {"enabled": True, "description": "Multi-agent collaboration when needed"},
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
        "relevance": {"metric": "jr_engine_score_distribution", "target_tier1_tier2_percent": 40},
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

# Federal Register API Configuration
# Free public API - no authentication required
# 530+ federal agencies for regulatory intelligence
FEDERAL_REGISTER_CONFIG = {
    "enabled": True,
    "base_url": "https://www.federalregister.gov/api/v1",
    "rate_limit": 1.0,  # 1 request per second (respectful)
    "days_back": 30,  # Default lookback period
    "max_results_per_page": 100,
    "max_pages": 5,  # Safety limit per query
    # PNKLN-aligned agency slugs (priority agencies)
    "priority_agencies": [
        # Defense & National Security
        "defense-department",
        "army-department",
        "navy-department",
        "air-force-department",
        # Energy & Grid
        "energy-department",
        "federal-energy-regulatory-commission",
        # Space & Aerospace
        "national-aeronautics-and-space-administration",
        "federal-aviation-administration",
        "federal-communications-commission",
        # Technology & Commerce
        "commerce-department",
        "national-institute-of-standards-and-technology",
        "bureau-of-industry-and-security",
        # Homeland Security & Cyber
        "homeland-security-department",
        "cybersecurity-and-infrastructure-security-agency",
        # Health & FDA (SaMD)
        "food-and-drug-administration",
    ],
    "document_types": [
        "RULE",  # Final rules - immediate impact
        "PRORULE",  # Proposed rules - upcoming changes
        "NOTICE",  # General notices
        "PRESDOCU",  # Presidential documents
    ],
    "topic_keywords": [
        "artificial intelligence",
        "machine learning",
        "autonomous systems",
        "cybersecurity",
        "critical infrastructure",
        "encryption",
        "defense procurement",
        "unmanned systems",
        "space force",
        "satellite",
        "spectrum allocation",
        "launch vehicle",
        "grid modernization",
        "energy storage",
        "renewable energy",
        "software as a medical device",
        "digital health",
        "510k",
        "export control",
        "itar",
        "dual use",
    ],
}
