# Gemini Ingestion Layer Analysis Scripts

**Automated analysis of the PNKLN Intelligence Pipeline using Gemini 2.0 Pro**

## Overview

These scripts implement the **Gemini Ingestion Layer Analysis Framework** - an adaptation of the Judge #6 validation approach tailored for intelligence collection systems.

### Key Differences from Judge #6

| Aspect | Judge #6 | Gemini Ingestion Layer |
|--------|----------|------------------------|
| **System Type** | Enforcement/Validation | Collection/Intelligence |
| **Execution** | Real-time, per-request | Batch, nightly cron |
| **Primary Metric** | Latency (p99 ≤90ms) | Runtime (≤45 min/night) |
| **Quality Focus** | FP/FN rates, coverage | Relevance, timeliness, completeness |
| **Integration** | Calls 4 namespaces | Called by 4 namespaces |
| **Cost Model** | Per-API-call | Monthly operational (~$77) |
| **Unique Features** | ATP compliance | Ethical crawling, tier classification |
| **Confidence Target** | ≥70% (prod data) | ≥60% (pre-prod specs) |

## Scripts

### 1. `prepare_analysis_input.sh`

Generates a comprehensive input bundle for Gemini analysis.

**Usage**:
```bash
./prepare_analysis_input.sh > analysis_input.txt
```

**Includes**:
- Code structure and key modules
- Infrastructure schemas (BigQuery, GCS)
- Configuration files (repositories, settings)
- Dependencies (requirements.txt)
- Cost estimates and operational metrics
- Ethical compliance standards
- Integration point mappings

**Output**: Formatted markdown document (~10-20KB)

### 2. `aggregate_confidence.py`

Parses Gemini analysis reports and computes confidence scores.

**Usage**:
```bash
python aggregate_confidence.py docs/analysis/gemini_ingestion_2025-11-15.md
```

**Features**:
- Extracts confidence percentages from each dimension
- Computes weighted overall confidence (6 dimensions)
- Identifies low-scoring areas needing attention
- Generates go/no-go deployment recommendation
- Exports structured metrics to JSON

**Dimension Weights**:
- Architecture: 20%
- Cost Efficiency: 15%
- Ethical Compliance: 20%
- Data Quality: 20%
- Operational Reliability: 15%
- Integration Health: 10%

**Thresholds**:
- **Approved**: ≥60% overall confidence
- **Warning**: 50-59% (deployment at risk)
- **Blocked**: <50% (significant issues)

**Output Example**:
```
======================================================================
GEMINI INGESTION LAYER ANALYSIS - CONFIDENCE SUMMARY
======================================================================

DIMENSION SCORES:
  ✅ Architecture                      72% (weight: 20%)
  ⚠️  Cost Efficiency                  58% (weight: 15%)
  ✅ Ethical Compliance                75% (weight: 20%)
  ✅ Data Quality                      62% (weight: 20%)
  ⚠️  Operational Reliability          56% (weight: 15%)
  ✅ Integration Health                68% (weight: 10%)

OVERALL CONFIDENCE: 65.0%
STATUS: ✅ APPROVED

TOP RECOMMENDATIONS:
  1. [SHORT-TERM] Add circuit breaker for failing collectors
  2. [SHORT-TERM] Implement exponential backoff for Vertex AI
  3. [MEDIUM-TERM] Add deduplication layer using content hashes
  4. [MEDIUM-TERM] Build monitoring dashboard for quality gates
  5. [LONG-TERM] Optimize embedding batching for cost reduction

======================================================================
```

### 3. `run_gemini_analysis.py`

Orchestrates the full analysis workflow end-to-end.

**Usage**:
```bash
# With Vertex AI (production)
python run_gemini_analysis.py \
    --project-id your-gcp-project \
    --location us-central1 \
    --output docs/analysis/report_2025-11-15.md

# Without Vertex AI (mock mode for testing)
python run_gemini_analysis.py
```

**Workflow**:
1. **Generate Input** → Calls `prepare_analysis_input.sh`
2. **Load Prompt** → Reads `GEMINI_INGESTION_ANALYSIS.md`
3. **Submit to Gemini** → Sends to Gemini 2.0 Pro via Vertex AI
4. **Save Report** → Writes analysis to markdown file
5. **Aggregate Scores** → Calls `aggregate_confidence.py`
6. **Return Status** → Exit code 0 (approved) or 1 (blocked)

**Requirements**:
- Vertex AI API enabled
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable set
- `google-cloud-aiplatform` package installed

**Mock Mode**:
If Vertex AI is unavailable, generates a sample analysis for testing the workflow.

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install google-cloud-aiplatform

# Set up GCP authentication
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Ensure scripts are executable
chmod +x pnkln_intelligence/scripts/*.sh
chmod +x pnkln_intelligence/scripts/*.py
```

### Run Analysis

**Option 1: Full Automated Workflow**
```bash
cd /path/to/aiyou-fastapi-services

python pnkln_intelligence/scripts/run_gemini_analysis.py \
    --project-id your-gcp-project-id \
    --output docs/analysis/gemini_ingestion_$(date +%Y-%m-%d).md
```

**Option 2: Manual Step-by-Step**
```bash
# Step 1: Generate input
./pnkln_intelligence/scripts/prepare_analysis_input.sh > analysis_input.txt

# Step 2: Submit to Gemini (manual copy/paste to AI Studio or use API)
# Combine GEMINI_INGESTION_ANALYSIS.md prompt + analysis_input.txt

# Step 3: Save Gemini's response to file
# Save as: docs/analysis/gemini_ingestion_2025-11-15.md

# Step 4: Aggregate confidence
python pnkln_intelligence/scripts/aggregate_confidence.py \
    docs/analysis/gemini_ingestion_2025-11-15.md
```

## Analysis Output Structure

### Generated Files

```
docs/analysis/
├── gemini_ingestion_2025-11-15.md           # Full analysis report
├── gemini_ingestion_2025-11-15.confidence.json  # Structured metrics
└── analysis_input_bundle.txt                # Input sent to Gemini
```

### Report Sections

1. **Executive Summary** - 2-3 paragraph overview
2. **Architecture Assessment** - Strengths, concerns, recommendations
3. **Cost Efficiency Analysis** - Breakdown, optimization opportunities
4. **Ethical Compliance Review** - Rate limits, legal risks, ToS adherence
5. **Data Quality Evaluation** - Relevance scoring, tier distribution
6. **Operational Reliability Check** - Error handling, monitoring, recovery
7. **Integration Health Status** - Upstream/downstream dependencies
8. **Top 5 Risks** - Prioritized by impact × likelihood
9. **Top 5 Optimization Opportunities** - Prioritized by ROI
10. **Recommended Actions** - Short-term vs. long-term roadmap

Each section includes a **confidence score** (0-100%) indicating how certain Gemini is about the assessment given available documentation.

## Use Cases

### Pre-Deployment Validation

Run analysis before production deployment to identify:
- Architectural flaws or single points of failure
- Cost overrun risks
- Ethical/legal compliance gaps
- Missing monitoring/observability

**Target**: ≥60% overall confidence for deployment approval

### Monthly Health Checks

Re-run analysis with production metrics to:
- Validate initial predictions vs. actual performance
- Identify emerging issues (cost drift, quality degradation)
- Track optimization ROI
- Adjust targets based on real data

**Target**: ≥80% confidence once in production

### Architecture Evolution

Use analysis to guide:
- Scaling strategies (10x volume scenarios)
- New feature additions (impact on existing design)
- Technology migrations (e.g., switching embedding providers)
- Cost optimization initiatives

## Customization

### Adjusting Dimension Weights

Edit `aggregate_confidence.py`:

```python
DIMENSION_WEIGHTS = {
    'architecture': 0.25,  # Increase if architecture is critical
    'cost_efficiency': 0.20,  # Increase for cost-sensitive deployments
    'ethical_compliance': 0.15,  # Adjust based on legal risk tolerance
    'data_quality': 0.20,
    'operational_reliability': 0.10,
    'integration_health': 0.10
}
```

### Changing Confidence Thresholds

```python
CONFIDENCE_THRESHOLD_APPROVED = 70  # Stricter approval
CONFIDENCE_THRESHOLD_WARNING = 60
```

### Adding Custom Dimensions

1. Update `GEMINI_INGESTION_ANALYSIS.md` with new `<dimension>` block
2. Add weight to `aggregate_confidence.py`
3. Update prompt to request confidence score in that dimension

## Troubleshooting

### "No confidence scores found"

**Problem**: Gemini output doesn't match expected format
**Solution**: Ensure analysis includes `(Confidence: XX%)` in each section heading

### "Vertex AI not available"

**Problem**: `google-cloud-aiplatform` not installed
**Solution**: `pip install google-cloud-aiplatform`

### "Analysis timeout"

**Problem**: Input bundle too large for Gemini
**Solution**: Edit `prepare_analysis_input.sh` to reduce verbosity (e.g., `head -20` instead of `head -50`)

### "Permission denied" on scripts

**Solution**: `chmod +x pnkln_intelligence/scripts/*.sh`

## Best Practices

1. **Version Control**: Commit analysis reports to git for historical tracking
2. **Regular Cadence**: Run monthly post-deployment for trend analysis
3. **Action Items**: Create GitHub issues from recommendations with priority labels
4. **Metrics Tracking**: Compare confidence scores over time to measure improvement
5. **Feedback Loop**: Feed production metrics back into analysis for refinement

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Gemini Intelligence Analysis

on:
  schedule:
    - cron: '0 2 1 * *'  # Monthly at 2 AM on 1st day
  workflow_dispatch:  # Manual trigger

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Authenticate to GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Run Gemini Analysis
        run: |
          python pnkln_intelligence/scripts/run_gemini_analysis.py \
            --project-id ${{ secrets.GCP_PROJECT_ID }} \
            --output docs/analysis/gemini_$(date +%Y-%m-%d).md

      - name: Upload Analysis Report
        uses: actions/upload-artifact@v3
        with:
          name: analysis-report
          path: docs/analysis/

      - name: Check Deployment Approval
        run: |
          if [ $? -eq 0 ]; then
            echo "✅ Analysis approved - safe to deploy"
          else
            echo "❌ Analysis blocked - address concerns before deployment"
            exit 1
          fi
```

## Advanced Features

### Comparative Analysis

Compare multiple reports to track progress:

```bash
# Run analysis on two different dates
python run_gemini_analysis.py --output analysis_v1.md
# (make changes)
python run_gemini_analysis.py --output analysis_v2.md

# Compare confidence scores
diff <(grep "Confidence:" analysis_v1.md) \
     <(grep "Confidence:" analysis_v2.md)
```

### Cost Projection Scenarios

Modify input bundle to test scaling:

```bash
# Edit prepare_analysis_input.sh to simulate 10x volume
sed -i 's/500-1,000/5,000-10,000/' prepare_analysis_input.sh

# Run analysis to see cost impact
./run_gemini_analysis.py --output analysis_10x_scale.md
```

## References

- [GEMINI_INGESTION_ANALYSIS.md](../GEMINI_INGESTION_ANALYSIS.md) - Full prompt template
- [MASTER_AGENT_PROMPT_FRAMEWORK.md](../../MASTER_AGENT_PROMPT_FRAMEWORK.md) - Master agent framework
- [Judge #6 Analysis](https://internal-docs/judge-6-analysis) - Original validation system (internal)

---

**Maintained by**: PNKLN Intelligence Team
**Last Updated**: 2025-11-15
**Version**: 1.0.0
