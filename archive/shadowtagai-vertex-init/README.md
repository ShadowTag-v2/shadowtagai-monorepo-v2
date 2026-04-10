# ShadowTagAi Vertex AI Initialization

**Comprehensive setup for ShadowTagAi Intelligence Pipeline infrastructure on Google Cloud Vertex AI**

## Overview

This initialization package sets up the complete ShadowTagAi stack with 8 specialized AI agents, OCR/vision tools, Monte Carlo valuation engine, and workflow utilities.

---

## Components

### 1. **ShadowTagAi Agents** (8 specialized AI systems)

| Agent | Purpose | Model | Use Case |
|-------|---------|-------|----------|
| **swiper** | Geo-beacon commerce films | Gemini Flash | Product placement, local commerce |
| **verdict** | Task flow enforcement | Python logic | Deadlines, escrows, urgency |
| **vcm** | VC Mirror (investor thesis) | Gemini Pro | Pitch generation, investor matching |
| **geos** | Geo-economic analysis | Gemini Flash | News summarization, capital flow |
| **odor** | Airflow/CBRN modeling | NumPy | Environmental simulations |
| **tokable** | Emotion-first creator scripts | Gemini Flash | Short-form content generation |
| **mcarlo** | Monte Carlo valuations | Python + stats | Financial modeling, risk analysis |
| **core** | Orchestration engine | Gemini Pro | Multi-agent coordination |

### 2. **Infrastructure**

- **Gemini Models**: Pro (reasoning), Flash (bulk), ImageGen (visual)
- **OCR Tools**: Google Cloud Vision API (document text detection)
- **GCS Integration**: Upload/download helpers
- **Statistics**: Percentile calculation, JSON utilities

### 3. **Workflows**

- OCR + Summarization pipeline
- Monte Carlo revenue/valuation modeling
- Task priority/urgency tracking
- Investor thesis extraction
- Geo-economic event analysis
- Airflow/odor diffusion simulation
- Emotion-first script generation

---

## Quick Start

### Option 1: Jupyter Notebook (Recommended)

```bash
# Upload to Vertex AI Workbench
gsutil cp shadowtagai_vertex_init.ipynb gs://your-bucket/

# Or use locally in Vertex AI Workbench
# 1. Open Vertex AI Workbench
# 2. Upload shadowtagai_vertex_init.ipynb
# 3. Run cells sequentially
```

### Option 2: Python Script

```bash
# Run initialization script
python scripts/shadowtagai_vertex_init.py --project YOUR_PROJECT_ID --region us-central1 --bucket shadowtagai-bucket
```

### Option 3: Manual Setup

```python
# 1. Install dependencies
pip install google-cloud-aiplatform google-cloud-storage google-cloud-vision numpy pandas

# 2. Initialize Vertex AI
import google.cloud.aiplatform as a
a.init(project="YOUR_PROJECT", location="us-central1")

# 3. Load Gemini models
from vertexai.generative_models import GenerativeModel
g = GenerativeModel("gemini-1.5-pro")
g1 = GenerativeModel("gemini-1.5-flash")

# 4. Import ShadowTagAi agents (see notebook for full code)
```

---

## Usage Examples

### Swiper (Geo-Beacon Commerce)

```python
# Generate campaign plan
plan = swiper_plan("Patagonia jacket campaign for hikers in Colorado")
# Returns: {wedge, geo, content, cpms, revshare, visualize}

# Visualize product placement
result = swiper_visualize(img_b64, "Patagonia Down Sweater")
# Returns: {placements, style}
```

### Verdict (Task Flow Enforcement)

```python
import time

# Add tasks with deadlines
V.add("Close Series A", time.time() + 86400 * 30, prio=10)  # 30 days
V.add("File patent", time.time() + 86400 * 7, prio=8)  # 7 days
V.add("Launch product", time.time() + 86400 * 60, prio=9)  # 60 days

# Update urgency
V.tick(time.time())

# Get next task (highest urgency/priority)
next_task = V.next()
# Returns: {"t": "File patent", "dl": ..., "p": 8, "k": 1, "d": False}

# Mark done
V.done("File patent")
```

### VC Mirror (Investor Thesis Extraction)

```python
profile = "Partner at a16z, focused on B2B SaaS, 15 years enterprise sales"
company = "ShadowTag-v2: AI-powered content moderation platform, $60M seed, 500M TAM"

pitch = vcmirror(profile, company)
# Returns: {thesis, fit, angles, email_open, deck_outline}
```

### Monte Carlo Valuations

```python
# Define components
cfg = {
    "platform_rev": {"n": 10000, "base": 50e6, "sd": 20e6, "gr": 0.6, "mult": 15},
    "ai_services": {"n": 10000, "base": 30e6, "sd": 15e6, "gr": 0.7, "mult": 20}
}

# Run simulation
result = mcarlo_bundle(cfg)
# Returns: {
#   "components": {
#     "platform_rev": {"mean": 750M, "p10": 450M, "p50": 720M, "p90": 1.1B},
#     "ai_services": {"mean": 600M, "p10": 350M, "p50": 580M, "p90": 920M}
#   },
#   "sum_mean": 1.35B
# }
```

### OCR + Summarization

```python
# From local file
summary = ocr_and_sum_file("/path/to/document.pdf")

# From GCS
summary = ocr_and_sum_gcs("gs://bucket/path/to/document.pdf")

# Returns: JSON with {facts, metrics, actions}
```

### Geos (Geo-Economic Analysis)

```python
news = """
UAE announces $50B infrastructure fund for Africa.
Focus on ports, renewable energy, telecom.
Initial deployments: Kenya, Nigeria, Egypt.
"""

analysis = geos_skim(news)
# Returns: {triggers, actors, capital_flow, compliance}
```

### Odor (Airflow Modeling)

```python
import numpy as np

# Simulate odor diffusion from sources
field = odor_sim(
    n=128,  # 128×128 grid
    src=[(64, 64, 1.0), (32, 96, 0.5)],  # 2 sources
    k=0.92,  # Decay constant
    fx=0.02  # Diffusion factor
)

# Calculate average concentration
score = odor_score(field)
# Returns: 0.023 (example)

# With mask (only measure specific zones)
mask = np.zeros((128, 128))
mask[40:88, 40:88] = 1  # Central zone
zone_score = odor_score(field, mask)
```

### Tokable (Emotion-First Creator Scripts)

```python
script = tokable_script(
    theme="overcoming imposter syndrome",
    persona="relatable tech YouTuber, 25-35 demo"
)

# Returns: JSON with {
#   "duration": "60s",
#   "beats": [
#     {"time": "0-20s", "emotion": "vulnerable", "text": "..."},
#     {"time": "21-40s", "emotion": "hopeful", "text": "..."},
#     {"time": "41-60s", "emotion": "empowered", "text": "..."}
#   ],
#   "interactive_cues": ["Poll at 20s: Have you felt this?", ...]
# }
```

---

## Configuration

### Environment Variables

```bash
# Required
export GCP_PROJECT="your-project-id"
export GCP_REGION="us-central1"
export GCS_BUCKET="shadowtagai-bucket"

# Optional
export GEMINI_PRO_MODEL="gemini-1.5-pro"
export GEMINI_FLASH_MODEL="gemini-1.5-flash"
export IMAGEGEN_MODEL="imagegeneration@006"
```

### Customization

Edit prompt templates in the notebook:

```python
pt = {
    "sys_shadowtagai_core": "You are shadowtagai—an orchestration and analysis engine. Output JSON or code. Be concise.",
    "sys_swiper": "You are shadowtagai-swiper. Optimize geo-beacon commerce films. Output plans and JSON recipes.",
    # ... customize as needed
}
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Vertex AI (us-central1)                            │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Gemini Pro   │  │ Gemini Flash │  │ ImageGen │ │
│  │ (reasoning)  │  │ (bulk)       │  │ (visual) │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬────┘ │
│         │                 │                 │      │
│         └─────────┬───────┴─────────────────┘      │
│                   │                                │
│         ┌─────────▼─────────┐                      │
│         │  ShadowTagAi Agents      │                      │
│         │  ├─ swiper         │                      │
│         │  ├─ verdict        │                      │
│         │  ├─ vcm            │                      │
│         │  ├─ geos           │                      │
│         │  ├─ odor           │                      │
│         │  ├─ tokable        │                      │
│         │  ├─ mcarlo         │                      │
│         │  └─ core           │                      │
│         └────────────────────┘                      │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  GCS (shadowtagai-bucket)    │
         │  ├─ prompts/           │
         │  ├─ valuations/        │
         │  └─ templates/         │
         └────────────────────────┘
```

---

## Cost Estimates

### Gemini API Pricing (November 2025)

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| Gemini 1.5 Pro | $3.50/1M tokens | $10.50/1M tokens | Complex reasoning |
| Gemini 1.5 Flash | $0.075/1M tokens | $0.30/1M tokens | Bulk operations |
| ImageGen 006 | $0.02/image | N/A | Visual generation |

### Typical Costs (Monthly)

| Workflow | Volume | Cost |
|----------|--------|------|
| Swiper campaigns | 1K plans | $15 |
| VC Mirror pitches | 500 pitches | $20 |
| Geos analysis | 10K articles | $50 |
| Tokable scripts | 2K scripts | $10 |
| Monte Carlo sims | 100 runs | $5 |
| OCR + summarization | 5K docs | $100 (Vision API) |
| **Total** | - | **~$200/month** |

**Note**: Costs scale linearly with volume. Use Gemini Flash for bulk operations to reduce costs by 95%.

---

## Integration with ShadowTag-v2

### Scenario 1: Monte Carlo Valuations for ShadowTag-v2

```python
# Define ShadowTag-v2 components
cfg = {
    "base_platform": {"n": 10000, "base": 68.4e9, "sd": 20e9, "gr": 0.5, "mult": 1.0},
    "gemini_ai": {"n": 10000, "base": 38.9e9, "sd": 15e9, "gr": 0.6, "mult": 1.0},
    "satellite_mesh": {"n": 10000, "base": 18.3e9, "sd": 8e9, "gr": 0.55, "mult": 1.0}
}

ShadowTag-v2_valuation = mcarlo_bundle(cfg)
# Cross-validate with existing $207B 2030 valuation
```

### Scenario 2: VC Mirror for ShadowTag-v2 Fundraising

```python
# Extract investor thesis and generate pitch
investor_profile = "a16z partner, focused on creator economy platforms"
ShadowTag-v2_desc = "AI-powered content moderation, $207B 2030 valuation, 94/100 10 Fingers score"

pitch = vcmirror(investor_profile, ShadowTag-v2_desc)
# Use for Series A outreach
```

### Scenario 3: Geos Analysis for Market Intelligence

```python
# Track regulatory changes in EU/UK markets
eu_news = "EU AI Act enforcement begins Q1 2026, DSA VLOP compliance mandatory"

impact = geos_skim(eu_news)
# Use to prioritize Judge Architecture compliance roadmap
```

---

## Files

| File | Description | Lines |
|------|-------------|-------|
| `shadowtagai_vertex_init.ipynb` | Jupyter notebook (recommended) | 500+ |
| `scripts/shadowtagai_vertex_init.py` | Python script version | 400+ |
| `README.md` | This file | 400+ |
| `ARCHITECTURE.md` | Technical architecture details | (coming soon) |

---

## Requirements

- **GCP Project** with Vertex AI API enabled
- **Python 3.10+**
- **Dependencies**:
  - `google-cloud-aiplatform`
  - `google-cloud-storage`
  - `google-cloud-vision`
  - `numpy`
  - `pandas`
  - `matplotlib` (optional, for visualizations)

---

## Support

For issues or questions:
- File issue on GitHub: `ehanc69/ShadowTag-v2-fastapi-services`
- Email: [support email if available]
- Documentation: See `docs/architecture/SHADOWTAGAI_VERTEX_INTEGRATION.md`

---

## License

MIT License (same as ShadowTag-v2 parent project)

---

## Changelog

### v1.0.0 (November 2025)
- Initial release
- 8 ShadowTagAi agents
- Gemini Pro/Flash/ImageGen integration
- Monte Carlo valuation engine
- OCR + summarization pipeline
- GCS helpers
- Comprehensive documentation

---

**Status**: Production-ready
**Last Updated**: November 2025
**Maintainer**: Claude (AI Assistant)
