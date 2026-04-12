# Analysis Input Documents

This directory contains supporting documents for PNKLN component analyses.

## Directory Structure

```
analysis-inputs/
├── README.md (this file)
├── ingestion-layer/      # Gemini Ingestion Layer specifications
│   ├── gke-cronjob-spec.md
│   ├── source-matrix.md
│   └── cost-model.md
├── judge-6/              # Judge #6 specifications (future)
├── autogen/              # AutoGen specifications (future)
└── ...                   # Other components
```

## How to Add Documents

### For Gemini Ingestion Layer Analysis

Add the following types of documents to `ingestion-layer/`:

1. **Architecture Specifications**
   - GKE CronJob YAML files
   - Container configurations (Dockerfile, docker-compose.yml)
   - Kubernetes manifests (deployments, services, configmaps)
   - Terraform configurations for GKE node pools

2. **Source Configuration**
   - Source matrix (which sources, rate limits, credentials)
   - API documentation links
   - robots.txt compliance strategy
   - Ethical crawling policies

3. **Cost Models**
   - GKE compute cost breakdowns
   - API cost estimates (Gemini, YouTube, Twitter, etc.)
   - Storage costs (Cloud Storage, Cloud SQL)
   - Scaling scenarios (2×, 5×, 10× volume)

4. **Integration Contracts**
   - API specifications (OpenAPI/Swagger)
   - Data schemas (JSON/Protobuf)
   - Event formats (PubSub messages)
   - Error handling protocols

5. **Performance Benchmarks** (if available)
   - Runtime measurements
   - Item throughput rates
   - Tier classification accuracy
   - Briefing delivery timelines

6. **Monitoring & Alerts**
   - Cloud Monitoring dashboard configs
   - Alert policies
   - SLO definitions
   - Runbook snippets

## Supported File Formats

- **Markdown** (`.md`) - Preferred for documentation
- **YAML** (`.yaml`, `.yml`) - Kubernetes manifests, configs
- **JSON** (`.json`) - API specs, data schemas
- **Text** (`.txt`) - Plain text notes, logs
- **Code** (`.py`, `.js`, `.sh`) - Implementation files (for context)

## File Naming Conventions

Use descriptive, kebab-case names:

✅ Good:

- `gke-cronjob-spec.yaml`
- `source-api-contracts.md`
- `cost-breakdown-monthly.md`
- `performance-benchmarks-2024-11.md`

❌ Avoid:

- `spec.yaml` (too generic)
- `MyDocument.md` (PascalCase)
- `notes_final_v2.txt` (unclear versioning)

## Example: Minimal Document Set

To run a basic analysis, provide at minimum:

```
ingestion-layer/
├── architecture-overview.md      # High-level system design
├── component-specifications.md   # Detailed component specs
└── cost-estimates.md             # Budget breakdown
```

The analysis will work better with more detailed documents, but can provide valuable insights even with minimal input.

## Example: Comprehensive Document Set

For production-ready analysis:

```
ingestion-layer/
├── architecture/
│   ├── gke-cluster-config.yaml
│   ├── cronjob-definition.yaml
│   ├── service-accounts.yaml
│   └── network-policies.yaml
├── sources/
│   ├── source-matrix.md
│   ├── youtube-api-config.yaml
│   ├── twitter-api-config.yaml
│   └── rate-limit-strategies.md
├── costs/
│   ├── monthly-budget.md
│   ├── gke-cost-breakdown.xlsx (or .csv)
│   └── scaling-scenarios.md
├── integration/
│   ├── api-contracts.yaml (OpenAPI spec)
│   ├── data-schemas.json
│   └── downstream-dependencies.md
├── monitoring/
│   ├── dashboard-config.yaml
│   ├── alert-policies.yaml
│   └── slo-definitions.md
└── performance/
    ├── runtime-benchmarks.md
    ├── tier-classification-accuracy.csv
    └── load-test-results.md
```

## Document Quality Guidelines

### Good Document Characteristics

- **Specific**: Include exact numbers (45 min runtime, not "fast")
- **Current**: Date documents and keep them updated
- **Complete**: Cover all aspects of the component
- **Honest**: Flag assumptions and unknowns clearly

### What to Include

- ✅ Numeric targets and thresholds
- ✅ Resource specifications (CPU, memory, storage)
- ✅ Cost breakdowns with assumptions
- ✅ Failure scenarios and recovery strategies
- ✅ Open questions and uncertainties

### What to Avoid

- ❌ Marketing fluff ("best-in-class", "revolutionary")
- ❌ Vague statements ("should be fast enough")
- ❌ Outdated information (mark as "DRAFT" or "DEPRECATED")
- ❌ Secrets or credentials (use placeholders like `<API_KEY>`)

## Security Notes

**DO NOT** commit sensitive information:

- ❌ API keys, passwords, tokens
- ❌ Production credentials
- ❌ Customer data or PII
- ❌ Internal IP addresses or hostnames

Use placeholders instead:

- ✅ `YOUTUBE_API_KEY: <redacted>`
- ✅ `Database: postgresql://user:***@host:5432/db`
- ✅ `Cluster: projects/<PROJECT_ID>/locations/<REGION>/clusters/ingestion`

## Analysis Workflow

1. **Prepare Documents**

   ```bash
   # Add your specifications
   cp ~/my-specs/* analysis-inputs/ingestion-layer/
   ```

2. **Validate Documents**

   ```bash
   # Check that files are present
   ls -lh analysis-inputs/ingestion-layer/
   ```

3. **Run Analysis**

   ```bash
   # Dry run to review combined prompt
   npm run analyze:ingestion -- --dry-run

   # Actual analysis with Gemini
   GEMINI_API_KEY=xxx npm run analyze:ingestion -- --provider gemini

   # Or with Claude
   npm run analyze:ingestion -- --provider claude
   ```

4. **Review Results**

   ```bash
   # Check output
   cat analysis-outputs/ingestion-layer-analysis-*.md
   ```

5. **Iterate**
   - Address missing information flagged in analysis
   - Add clarifying documents
   - Re-run analysis

## Tips for Better Analysis Quality

### Increase Confidence (Pre-Production: 60% → 70%+)

- Add **actual cost data** (even from dev/staging)
- Include **performance benchmarks** (synthetic load tests)
- Provide **integration test results** (API contract validation)
- Document **failure scenario testing** (chaos engineering results)

### Get More Actionable Recommendations

- Be explicit about **constraints** (budget, timeline, team size)
- List **current pain points** ("briefing delivery fails 10% of nights")
- State **optimization priorities** (cost > performance, or vice versa)
- Include **stakeholder concerns** (legal worried about robots.txt)

### Improve Analysis Depth

- Attach **diagrams** (architecture, data flow, sequence)
- Include **code snippets** (critical sections, not entire repos)
- Reference **external docs** (link to GKE docs, API docs)
- Provide **historical context** (why decisions were made)

## Troubleshooting

### Analysis is too vague

**Problem**: LLM gives generic recommendations

**Solution**: Add more specific documents

- Replace "GKE cluster" with actual YAML manifests
- Replace "costs around $77/month" with itemized breakdown
- Include numeric targets (not "fast", but "≤45 min")

### Analysis flags many "low confidence" items

**Problem**: LLM uncertain about key aspects

**Solution**: Address missing information

- Check "Questions/Clarifications Needed" section of previous analysis
- Add documents that answer those specific questions
- Re-run analysis

### Analysis doesn't match reality

**Problem**: LLM assumptions are wrong

**Solution**: Provide more production-like data

- Use actual telemetry (logs, metrics) if available
- Include load test results, not just theoretical specs
- Document known issues and edge cases

## Examples from Sample Documents

See `analysis-inputs/ingestion-layer/` for three example documents:

1. **`gke-cronjob-spec.md`** - Complete CronJob specification with container definitions, resource quotas, and failure scenarios

2. **`source-matrix.md`** - Comprehensive source configuration matrix covering 8 sources (YouTube, Twitter, News RSS, Reddit, etc.) with rate limits, expected yields, and ethical compliance

3. **`cost-model.md`** - Detailed cost breakdown ($108/month unoptimized → $21/month optimized) with scaling scenarios and cost/item analysis

These serve as templates for creating your own component specifications.

## Questions or Feedback?

- Check: `prompts/README.md` for analysis prompt usage guide
- Review: `docs/prompts/` for design rationale documents
- Run: `node scripts/analyze-ingestion-layer.js --help` for CLI options

---

**Last Updated**: 2025-11-15
**Maintained by**: PNKLN Core Stack Team
