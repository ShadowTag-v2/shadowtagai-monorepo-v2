# Gemini Analysis Framework - Integration Guide

## Overview

The Intelligence Pipeline includes a **Gemini 2.0 Pro self-analysis framework** that provides automated architecture review, compliance validation, and performance assessment. This capability is adapted from the Judge #6 analysis prompt, customized for the pipeline's upstream intelligence collection role.

## Why Self-Analysis?

Self-analysis provides:

1. **Pre-Production Validation** - Identify issues before deployment
2. **Architecture Review** - Automated evaluation of design decisions
3. **Compliance Verification** - ATP 5-19 RA-1 compliance checking
4. **Performance Benchmarking** - Compare against targets
5. **Documentation Quality** - Ensure specs are complete
6. **Knowledge Transfer** - Help new team members understand the system
7. **Continuous Improvement** - Track metrics over time

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GEMINI 2.0 PRO ANALYSIS FRAMEWORK                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  DOCUMENT LOADER                                            │
│  • README.md (623 lines)                                    │
│  • DEPLOYMENT.md (456 lines)                                │
│  • pipeline.yaml (168 lines)                                │
│  • Python modules (7 files, ~1,600 lines)                   │
│  • K8s manifests (4 files, ~340 lines)                      │
│  • Terraform (283 lines)                                    │
│  • SQL queries (362 lines)                                  │
│  ────────────────────────────────────────────────────────   │
│  TOTAL: ~4,500 lines of specifications                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  ANALYSIS PROMPT (10 Sections)                              │
│  1. Architecture Evaluation                                 │
│  2. Ethical Compliance Model                                │
│  3. Multi-Source Coverage Analysis                          │
│  4. Tier Classification Metrics                             │
│  5. Performance Metrics                                     │
│  6. Cost Model                                              │
│  7. Quality Focus                                           │
│  8. AM Briefing Delivery Effectiveness                      │
│  9. Integration with PNKLN Core Stack™                      │
│  10. Edge Case Analysis                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  GEMINI 2.0 PRO EXECUTION                                   │
│  • Model: gemini-2.0-flash-exp                              │
│  • Temperature: 0.3 (consistent scoring)                    │
│  • Max output: 8,192 tokens (~3,000-5,000 words)            │
│  • Runtime: 2-5 minutes                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STRUCTURED REPORT                                          │
│  • Executive Summary                                        │
│  • 6 Scored Sections (0-100)                                │
│  • Prioritized Recommendations (Critical → Low)             │
│  • Confidence Level (≥60% required)                         │
│  • Visualization (score bars, health indicators)            │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Google API Key**
   - Get one at: https://makersuite.google.com/app/apikey
   - Set environment variable: `export GOOGLE_API_KEY="your-key"`

2. **Python Dependencies**
   ```bash
   pip install google-generativeai
   ```

### Running Analysis

**Option 1: Automated Test Script** (Recommended)

```bash
cd intelligence-pipeline
export GOOGLE_API_KEY="your-key"
./scripts/test_analysis.sh
```

**Option 2: Manual Execution**

```bash
cd intelligence-pipeline
export GOOGLE_API_KEY="your-key"

python scripts/run_gemini_analysis.py \
  --output reports/analysis_$(date +%Y%m%d).md
```

**Option 3: Custom Configuration**

```bash
python scripts/run_gemini_analysis.py \
  --base-path /path/to/intelligence-pipeline \
  --output /custom/output/path.md \
  --api-key "your-key"
```

### Viewing Results

```bash
# View latest report
cat reports/analysis_*.md | less

# Or open in editor
code reports/analysis_$(date +%Y%m%d)_*.md
```

## Analysis Sections

### 1. Architecture Evaluation (0-100)

**Evaluates**:
- Container orchestration strategy (GKE CronJob)
- Resource allocation (2-4 CPU, 8-16GB RAM)
- Failure recovery (backoffLimit: 2)
- IAM scoping (Workload Identity)
- Integration reliability (Anthropic, BigQuery, etc.)
- Data persistence (BigQuery partitioning)

**Sample Output**:
```
Architecture Score: 85%

✅ Strengths:
  - Workload Identity properly configured
  - Resource limits prevent runaway costs
  - BigQuery partitioning by published_date efficient

⚠️  Warnings:
  - No auto-scaling for volume surges
  - Circuit breaker timeout (5 min) may be too short
  - Missing pod disruption budget

💡 Recommendations:
  [HIGH] Add HorizontalPodAutoscaler for volume surges
  [MEDIUM] Increase circuit breaker timeout to 15 minutes
  [LOW] Document resource allocation decisions
```

### 2. Ethical Compliance Model (0-100)

**Evaluates**:
- RFC 9309 robots.txt compliance
- Rate limiting sufficiency
- Circuit breaker effectiveness
- User-Agent transparency
- Error handling robustness
- ATP 5-19 risk classification

**Sample Output**:
```
Ethical Compliance Score: 92%

✅ Strengths:
  - RFC 9309 fully implemented (24h cache, crawl-delay)
  - Conservative rate limits (.gov = 10s)
  - Transparent User-Agent with contact info

⚠️  Warnings:
  - Circuit breaker threshold (5 failures) untested
  - No explicit GDPR/CCPA data retention policy

💡 Recommendations:
  [CRITICAL] Test circuit breaker with simulated failures
  [HIGH] Add data retention policy to robots.txt
  [MEDIUM] Document consent model for public data
```

### 3. Multi-Source Coverage (0-100)

**Evaluates**:
- Source diversity (8 channels configured)
- Geographic balance (5 states for legislation)
- Keyword effectiveness
- RSS vs API tradeoffs
- Missing sources (EU regulations, etc.)

**Sample Output**:
```
Coverage Score: 78%

✅ Strengths:
  - Broad source mix (regulatory, news, research, competitive)
  - State coverage includes major tech hubs (CA, NY, WA)

⚠️  Warnings:
  - Twitter/X disabled (requires API key) - missing real-time alerts
  - No EU regulation coverage (GDPR, AI Act)
  - Keywords may miss non-English sources

💡 Recommendations:
  [HIGH] Enable Twitter/X with API key for FTC/SEC alerts
  [HIGH] Add EU Official Journal (EUR-Lex) as source
  [MEDIUM] Expand keywords to include "algorithmic accountability"
  [LOW] Consider non-English sources (EU, Asia)
```

### 4. Tier Classification (0-100)

**Evaluates**:
- Scoring weights alignment with business priorities
- Threshold calibration (0.7/0.4)
- Distribution health (target: 10-20% Tier 1)
- False positive/negative rates
- Feedback loop for refinement

**Sample Output**:
```
Tier Classification Score: 83%

✅ Strengths:
  - Regulatory Impact highest weight (30%) - correct priority
  - Tier 1 threshold (0.7) conservative, reduces false positives

⚠️  Warnings:
  - No production data to validate distribution
  - Scoring weights hard-coded, not tunable via config
  - No feedback mechanism for CEO to flag false positives

💡 Recommendations:
  [HIGH] Add tier override API for manual reclassification
  [MEDIUM] Make scoring weights configurable in pipeline.yaml
  [MEDIUM] Track CEO feedback (e.g., "mark as not urgent")
  [LOW] A/B test threshold values (0.65 vs 0.7)
```

### 5. Performance Metrics (0-100)

**Evaluates**:
- Runtime efficiency (target: ~45 min)
- Cost per item (target: ≤$2.00)
- Quality gates (50-200 items/day)
- Parallelization opportunities
- Failure modes

**Sample Output**:
```
Performance Score: 80%

✅ Strengths:
  - Cost per item ($0.10) well below $2.00 target
  - Clear quality gates defined (50-200 items/day)
  - BigQuery write success >99% achievable

⚠️  Warnings:
  - JR Scoring sequential (bottleneck at 200 items)
  - No backpressure handling if ingestion returns 500+ items
  - Missing runtime SLA monitoring

💡 Recommendations:
  [HIGH] Parallelize JR Scoring with asyncio batch processing
  [HIGH] Add item sampling if volume exceeds 300/day
  [MEDIUM] Implement runtime alerts if >60 minutes
  [LOW] Cache JR scores for duplicate items (deduplication)
```

### 6. Cost Model (0-100)

**Evaluates**:
- Cost allocation accuracy
- Sensitivity to volume changes
- API pricing risks
- Storage growth projections
- ROI assumptions

**Sample Output**:
```
Cost Model Score: 77%

✅ Strengths:
  - Monthly cost ($370) well-documented
  - ROI projection (3.3×) conservative and realistic

⚠️  Warnings:
  - Anthropic API pricing subject to change (no contract)
  - BigQuery costs assume <1GB/month (may grow faster)
  - ROI assumptions ($750K revenue) unvalidated

💡 Recommendations:
  [CRITICAL] Set up budget alerts at $400/month (10% buffer)
  [HIGH] Model cost at 2× and 10× volume (sensitivity analysis)
  [MEDIUM] Negotiate Anthropic enterprise pricing
  [LOW] Track ROI metrics in BigQuery dashboard
```

### 7. Quality Focus (0-100)

**Evaluates**:
- Relevance (Tier 1 items strategic?)
- Timeliness (detection delay <24h)
- Completeness (all fields populated)
- Accuracy (scoring consistency)
- Deduplication

**Sample Output**:
```
Quality Score: 81%

✅ Strengths:
  - Clear quality metrics (relevance, timeliness, completeness)
  - Detection delay trackable via BigQuery view

⚠️  Warnings:
  - No deduplication (same article from multiple sources)
  - Sentiment analysis could enhance relevance scoring
  - Missing data validation schema enforcement

💡 Recommendations:
  [HIGH] Add deduplication by URL or content hash
  [MEDIUM] Implement BigQuery schema validation
  [MEDIUM] Pilot sentiment analysis for Tier 1 items
  [LOW] Track Cor synthesis quality (CEO feedback)
```

### 8. AM Briefing Delivery (0-100)

**Evaluates**:
- Readability (HTML formatting)
- Actionability (can CEO act from email?)
- Mobile rendering
- Fallback reliability
- Archive access

**Sample Output**:
```
Briefing Delivery Score: 84%

✅ Strengths:
  - HTML + plain text multipart (email client compatible)
  - Fallback to file if SMTP fails
  - Clear structure (Tier 1 → Tier 2 → Tier 3)

⚠️  Warnings:
  - Mobile rendering untested
  - No archive access (emails deleted after 30 days)
  - Missing "reply to reclassify" feature

💡 Recommendations:
  [HIGH] Test HTML on mobile email clients (iOS Mail, Gmail)
  [MEDIUM] Add BigQuery view for briefing history
  [MEDIUM] Implement email reply-to for feedback
  [LOW] Add PDF export option for archiving
```

### 9. Stack Integration (0-100)

**Evaluates**:
- BigQuery schema compatibility
- Query performance
- Real-time vs batch consumption
- Data freshness SLAs
- Cross-component auth
- Failure isolation

**Sample Output**:
```
Stack Integration Score: 79%

✅ Strengths:
  - BigQuery partitioning enables efficient queries
  - Workload Identity consistent across components
  - Clear data flow (intelligence → consumers)

⚠️  Warnings:
  - No downstream consumer specs provided (can't validate schema)
  - Query performance untested at scale (10K+ items)
  - Missing integration tests with Judge #6

💡 Recommendations:
  [HIGH] Create integration tests with Judge #6 handoff
  [MEDIUM] Document BigQuery schema contract for consumers
  [MEDIUM] Add query performance benchmarks
  [LOW] Implement data freshness SLA (<24h)
```

### 10. Edge Case Readiness (0-100)

**Evaluates**:
- Source outage handling
- Cost spike mitigation
- Volume surge handling
- API rate limit protection
- Data quality degradation detection
- Disaster recovery

**Sample Output**:
```
Edge Case Readiness: 75%

✅ Strengths:
  - Circuit breaker handles source outages
  - Budget alerts configured
  - Clear failure modes documented

⚠️  Warnings:
  - Volume surge (1,000 items) untested
  - No chaos engineering tests
  - Disaster recovery plan missing

💡 Recommendations:
  [CRITICAL] Test volume surge scenario (simulate 1,000 items)
  [HIGH] Document disaster recovery (restore from BigQuery)
  [MEDIUM] Implement data quality anomaly detection
  [LOW] Run monthly chaos tests (disable random source)
```

## Understanding Confidence Levels

The analyzer provides a confidence level (0-100%) for each conclusion:

- **≥80%**: Strong evidence in specs, clear architecture
- **60-79%**: Reasonable inference from docs, some assumptions
- **40-59%**: Significant gaps, multiple assumptions
- **<40%**: Insufficient information, flag for manual review

**Minimum acceptable confidence**: 60% overall

**Example**:
```
Overall Confidence: 73%

High Confidence (≥80%):
  - Architecture design (85%) - well-documented in manifests
  - Ethical compliance (92%) - explicit implementation in code
  - Cost model (81%) - detailed breakdown provided

Medium Confidence (60-79%):
  - Coverage (68%) - keywords listed but effectiveness unknown
  - Performance (72%) - runtime estimates, no production data

Low Confidence (<60%):
  - Stack integration (58%) - missing downstream consumer specs
```

## Comparison with Judge #6

The Gemini analysis framework is adapted from the Judge #6 analysis prompt. Here's how they differ:

| Aspect | Judge #6 (Enforcement) | Intelligence Pipeline (Collection) |
|--------|------------------------|-----------------------------------|
| **Role** | Downstream validation | Upstream intelligence gathering |
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container |
| **Execution** | Real-time (p99 ≤90ms) | Batch nightly (~45 min) |
| **Key Metrics** | Latency, Throughput, Block Rate | Items/Day, Sources, Cost/Item |
| **Integration** | Calls 4 namespaces (services) | Called by 4 namespaces (consumers) |
| **Unique Features** | ATP 5-19, JR Validation, FP/FN rates | Ethical Crawling, Tier Classification |
| **Cost Model** | Per-validation API calls | Monthly operational ($370) |
| **Quality Focus** | False positive/negative rates | Relevance, Timeliness, Completeness |
| **Data Source** | Production telemetry + specs | Specifications only (pre-prod) |
| **Confidence Floor** | ≥70% (with prod data) | ≥60% (specs-only) |

**Shared Patterns**:
- 10-section analysis framework
- 0-100 scoring system
- Prioritized recommendations (Critical → Low)
- Confidence calibration
- ATP 5-19 compliance focus

## Best Practices

### 1. Run Before Deployment

```bash
# Pre-deployment checklist
./scripts/test_analysis.sh
# Review report for CRITICAL issues
# Address before kubectl apply
```

### 2. Track Over Time

```bash
# Monthly analysis
python scripts/run_gemini_analysis.py \
  --output reports/monthly_$(date +%Y%m).md

# Compare with previous month
diff reports/monthly_202501.md reports/monthly_202502.md
```

### 3. Integrate with CI/CD

```yaml
# GitHub Actions example
- name: Run Gemini Analysis
  env:
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: |
    ./scripts/test_analysis.sh
    # Parse report and fail if critical issues found
```

### 4. Share with Stakeholders

```bash
# Generate PDF for non-technical stakeholders
pandoc reports/analysis_20250115.md -o reports/analysis_20250115.pdf
```

### 5. Use Recommendations for Roadmap

```bash
# Extract recommendations
grep -A 3 "💡 Recommendations:" reports/analysis_*.md > roadmap.md
```

## Troubleshooting

### Issue: "GOOGLE_API_KEY not set"

**Solution**:
```bash
export GOOGLE_API_KEY="your-key-here"
# Or add to .bashrc/.zshrc for persistence
```

### Issue: "google-generativeai not found"

**Solution**:
```bash
pip install google-generativeai
# Or add to requirements.txt
```

### Issue: "Rate limit exceeded"

**Solution**:
- Wait 60 seconds and retry
- Use lower temperature (0.1) for faster processing
- Reduce max_output_tokens (4096 instead of 8192)

### Issue: "Low confidence (<60%)"

**Solution**:
- Add more documentation to specs
- Include production telemetry (logs, metrics)
- Run manual review for low-confidence sections

### Issue: "Analysis takes >10 minutes"

**Solution**:
- Check internet connection (large document upload)
- Reduce context (fewer documents)
- Use gemini-1.5-flash instead of gemini-2.0-flash-exp

## Future Enhancements

1. **Automated Issue Creation** - Auto-create GitHub issues for CRITICAL recommendations
2. **Trend Analysis** - Compare scores over time, detect regressions
3. **Integration Tests** - Validate recommendations with actual tests
4. **Multi-Model Comparison** - Run analysis with Claude 3.5 Sonnet vs Gemini 2.0 Pro
5. **Visual Dashboards** - Generate HTML dashboards with charts
6. **Slack Integration** - Post summary to #intelligence-pipeline channel
7. **Recommendation Tracking** - Mark recommendations as "addressed" with commit links

## Support

For issues or questions:

- **Documentation**: This file
- **Analysis Prompt**: `docs/GEMINI_ANALYSIS_PROMPT.md`
- **Execution Script**: `scripts/run_gemini_analysis.py`
- **Email**: intelligence@pnkln.ai
- **Slack**: #intelligence-pipeline

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
**Adapted From**: Judge #6 Gemini Analysis Prompt
