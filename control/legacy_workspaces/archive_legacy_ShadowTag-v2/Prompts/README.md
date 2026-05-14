# Prompt Templates

This directory contains system prompt templates for various AI components in the aiyou-fastapi-services project.

## Structure

```
prompts/
├── README.md                    # This file
├── judge/                       # Judge #6 risk enforcement prompts
│   ├── README.md                # Judge-specific documentation
│   ├── metadata/                # Version registry and metadata
│   ├── examples/                # Benchmark test cases
│   ├── v1/                      # Baseline prompts
│   └── v2/                      # Current version (A/B testing)
│       ├── variants/            # A/B test variants
│       ├── AB-TEST-CONFIG.json  # Testing configuration
│       └── CHANGELOG.md         # Version history
│
└── ingestion-layer/             # Gemini Ingestion Layer analysis prompts
    ├── README.md                # Ingestion-specific documentation
    ├── metadata/                # Version registry and metadata
    ├── examples/                # Sample GKE specs, pipeline configs
    └── v1/                      # Current version (active)
        └── gemini-ingestion-layer-analysis.md
```

## Current Components

### Judge #6 (Midstream Validation)
**Purpose**: High-accuracy, low-latency risk enforcement engine
**Framework**: ATP 5-19 Risk Frameworks
**Status**: v2 A/B testing in progress
**Stack Position**: Midstream (validates intelligence)

**Key Features**:
- Pattern-integrated prompts (Role, Few-Shot, Scratchpad, SxS)
- Strict SLA constraints (p99 ≤ 90ms)
- Binary decision making (ALLOW/BLOCK/FLAG_FOR_REVIEW)
- Standardized JSON output

**Learn More**: See `judge/README.md`

### Gemini Ingestion Layer (Upstream Collection)
**Purpose**: Intelligence collection pipeline analysis for PNKLN Core Stack™
**Framework**: GKE CronJob multi-container orchestration
**Status**: v1 active (pre-production analysis)
**Stack Position**: Upstream (collects raw intelligence)

**Key Features**:
- 10-section comprehensive analysis framework
- Multi-source coverage (YouTube, Twitter, News, Web)
- Ethical crawling compliance evaluation
- Tier classification metrics (Tier 1/2/3)
- Runtime efficiency analysis (~45 min/night target)
- Cost optimization ($77/month budget)

**Learn More**: See `ingestion-layer/README.md`

## Design Philosophy

All prompts in this repository follow these principles:

1. **Contract-First Design**: Output format leads, not trails
2. **Zero Meta-Commentary**: Models execute, they don't need motivation
3. **Latency-Aware**: Token count is a first-class constraint
4. **Validated Through Testing**: A/B test before production
5. **Version Controlled**: All changes tracked and documented

## Versioning Strategy

- **v1.x**: Baseline implementations
- **v2.x**: Pattern-integrated improvements
- **vX.Y**: Major.Minor versioning
  - Major: Breaking changes to output format or behavior
  - Minor: Non-breaking enhancements

## A/B Testing

All significant prompt changes must undergo A/B testing:

1. Create variant in appropriate version directory
2. Configure A/B test parameters
3. Execute benchmark suite
4. Measure accuracy and latency
5. Declare winner based on success criteria
6. Promote to staging → canary → production
7. Monitor for 7 days
8. Document findings

## Usage

### Loading Prompts

```python
from prompt_loader import load_prompt

# Load specific version and variant
prompt = load_prompt(
    component="judge",
    version="v2",
    variant="b"
)
```

### Version Registry

All versions are tracked in `{component}/metadata/{component}-versions.json`

```python
from version_manager import get_active_version

# Get currently active version
active = get_active_version("judge")
# Returns: {"version": "v2", "variant": "b", ...}
```

## Adding New Prompts

1. Create directory structure: `prompts/{component}/`
2. Add version subdirectories: `v1/`, `v2/`, etc.
3. Create metadata: `metadata/{component}-versions.json`
4. Add README: `{component}/README.md`
5. Document in this file

## SLA Constraints

Each component has specific performance requirements:

### Judge #6 (Real-Time Validation)
- **Latency**: p99 ≤ 90ms
- **Accuracy**: ≥90% correct classifications
- **False Negative Rate**: ≤2%
- **False Positive Rate**: ≤5%
- **Availability**: 99.9%

### Ingestion Layer (Batch Processing)
- **Runtime**: ~45 minutes/night
- **Delivery**: AM Briefing ready by 6 AM
- **Cost**: $77/month operational budget
- **Relevance**: ≥80% aligned with objectives
- **Completeness**: ≥95% metadata coverage
- **Source Diversity**: ≥4 active sources

## Contributing

When modifying prompts:

1. ✅ Create new variant, don't modify existing
2. ✅ Update version registry
3. ✅ Configure A/B test
4. ✅ Run benchmark validation
5. ✅ Document changes in CHANGELOG
6. ✅ Validate against SLA constraints
7. ✅ Get review approval
8. ✅ Monitor post-deployment

## PNKLN Stack Integration

For comprehensive pipeline analysis, both prompts work together:

1. **Ingestion Layer** → Analyzes upstream collection (sources, ethics, tiers)
2. **Judge #6** → Analyzes midstream validation (enforcement, accuracy)
3. **Combined Analysis** → Evaluates end-to-end flow and handoffs

**See**: `/docs/PNKLN-STACK-INTEGRATION.md` for detailed integration guide

## References

### Judge #6
- **Documentation**: `judge/README.md`
- **Design Critique**: `/docs/JUDGE-6-V2-DESIGN-CRITIQUE.md`
- **Version Registry**: `judge/metadata/judge-versions.json`
- **A/B Test Config**: `judge/v2/AB-TEST-CONFIG.json`

### Gemini Ingestion Layer
- **Documentation**: `ingestion-layer/README.md`
- **Main Prompt**: `ingestion-layer/v1/gemini-ingestion-layer-analysis.md`
- **Version Registry**: `ingestion-layer/metadata/ingestion-versions.json`

### Cross-Component
- **Comparison Analysis**: `/docs/JUDGE-6-TO-INGESTION-LAYER-COMPARISON.md`
- **PNKLN Stack Integration**: `/docs/PNKLN-STACK-INTEGRATION.md`
- **ATP 5-19 Framework**: `/docs/ATP-5-19-FRAMEWORK.md`

---

**Maintained by**: PNKLN Engineering / AI Engineering Team
**Last Updated**: 2025-11-14
