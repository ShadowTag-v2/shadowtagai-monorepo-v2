#!/bin/bash
# Generates formatted input bundle for Gemini Ingestion Layer Analysis
# Usage: ./prepare_analysis_input.sh > analysis_input.txt

set -euo pipefail

echo "=== PNKLN Intelligence Pipeline - Analysis Input Bundle ==="
echo "Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

echo "## System Overview"
echo "**Type**: Gemini-powered Nightly Intelligence Ingestion Layer"
echo "**Architecture**: GKE CronJob Multi-Container Orchestration"
echo "**Runtime Target**: ≤45 minutes/night"
echo "**Cost Target**: ~\$77/month"
echo "**Quality Gates**: Items/day, source diversity, cost/item, relevance scores"
echo ""

echo "## Code Structure"
echo "### Main Modules"
find pnkln_intelligence -type d -maxdepth 1 ! -path pnkln_intelligence ! -path "*__pycache__*" -exec echo "- {}" \;
echo ""

echo "### Key Components"
echo ""
echo "#### Aggregators (Data Collection)"
for file in pnkln_intelligence/aggregators/*.py; do
    if [ -f "$file" ] && [ "$(basename "$file")" != "__init__.py" ]; then
        echo "**File**: $file"
        echo "\`\`\`python"
        head -30 "$file"
        echo "..."
        echo "\`\`\`"
        echo ""
    fi
done

echo "#### Embedding Generation"
for file in pnkln_intelligence/embedding/*.py; do
    if [ -f "$file" ] && [ "$(basename "$file")" != "__init__.py" ]; then
        echo "**File**: $file"
        echo "\`\`\`python"
        head -30 "$file"
        echo "..."
        echo "\`\`\`"
        echo ""
    fi
done

echo "#### Search & Vector Storage"
for file in pnkln_intelligence/search/*.py; do
    if [ -f "$file" ] && [ "$(basename "$file")" != "__init__.py" ]; then
        echo "**File**: $file"
        echo "\`\`\`python"
        head -30 "$file"
        echo "..."
        echo "\`\`\`"
        echo ""
    fi
done

echo "## Infrastructure Schemas"
echo ""
echo "### BigQuery Tables"
echo "\`\`\`sql"
cat pnkln_intelligence/infrastructure/bigquery_schemas.sql
echo "\`\`\`"
echo ""

echo "### GCS Lifecycle Policy"
echo "\`\`\`json"
cat pnkln_intelligence/infrastructure/gcs_lifecycle_policy.json
echo "\`\`\`"
echo ""

echo "## Configuration"
echo ""
echo "### Repository Targets"
echo "\`\`\`yaml"
head -200 pnkln_intelligence/config/repositories.yaml
echo "..."
echo "\`\`\`"
echo ""

echo "### Settings & Environment"
echo "\`\`\`python"
cat pnkln_intelligence/config/settings.py
echo "\`\`\`"
echo ""

echo "## Dependencies"
echo "\`\`\`"
cat requirements.txt
echo "\`\`\`"
echo ""

echo "## Documentation References"
if [ -f "README.md" ]; then
    echo "### README.md (Excerpt)"
    echo "\`\`\`markdown"
    head -100 README.md
    echo "..."
    echo "\`\`\`"
    echo ""
fi

if [ -f "SETUP.md" ]; then
    echo "### SETUP.md (Excerpt)"
    echo "\`\`\`markdown"
    head -50 SETUP.md
    echo "..."
    echo "\`\`\`"
    echo ""
fi

echo "## Cost Analysis"
echo "### Estimated Monthly Costs"
echo "| Component | Monthly Cost | Details |"
echo "|-----------|--------------|---------|"
echo "| BigQuery | \$11-13 | 100GB active + 3TB queries |"
echo "| GCS | \$12-15 | 500GB Standard + lifecycle |"
echo "| Vertex AI Vector Search | \$1,100-1,400 | 2× e2-standard-16 nodes |"
echo "| Embeddings (API) | \$2-5 | OpenAI/Voyage calls |"
echo "| **Total** | **~\$1,280** | Optimized: \$600-800 |"
echo ""

echo "## Operational Metrics (Targets)"
echo "| Metric | Target | Current |"
echo "|--------|--------|---------|"
echo "| Items/Day | 500-1,000 | TBD (pre-prod) |"
echo "| Source Coverage | ≥5 active | 5 (arXiv, HN, Reddit, PwC, GitHub) |"
echo "| Cost/Item | <\$0.15 | TBD (pre-prod) |"
echo "| Runtime Efficiency | ≤45 min | TBD (pre-prod) |"
echo "| Error Rate | <2% | TBD (pre-prod) |"
echo "| Relevance Score | ≥70% | TBD (pre-prod) |"
echo ""

echo "## Ethical Compliance"
echo "### Rate Limits"
echo "- **arXiv**: 3-second delay between requests"
echo "- **Hacker News**: 1 request/second max"
echo "- **Reddit**: 60 requests/minute (PRAW)"
echo "- **GitHub**: 10 req/min (unauth) or 5,000/hour (auth)"
echo "- **Papers with Code**: 30 requests/minute"
echo ""
echo "### Compliance Standards"
echo "- robots.txt honor for all HTTP crawlers"
echo "- User-Agent: \`PNKLN-Intelligence-Bot/1.0 (+https://pnkln.ai/bot)\`"
echo "- Public documentation of behavior"
echo "- GDPR-compliant (no PII collection)"
echo ""

echo "## Integration Points"
echo "### Upstream Triggers (Called BY)"
echo "- Cloud Scheduler (nightly cron at 02:00 UTC)"
echo "- Manual triggers via Cloud Run Jobs API"
echo "- CI/CD post-deployment validation"
echo "- On-demand intelligence refresh"
echo ""
echo "### Downstream Consumers (Calls TO)"
echo "- BigQuery (metadata + search indexes)"
echo "- GCS (raw data + embeddings)"
echo "- Vertex AI (embedding generation)"
echo "- Cloud Logging (telemetry)"
echo ""

echo "=== END INPUT BUNDLE ==="
echo ""
echo "**Total Lines**: $(find pnkln_intelligence -name "*.py" | xargs wc -l | tail -1 | awk '{print $1}')"
echo "**Python Files**: $(find pnkln_intelligence -name "*.py" | wc -l)"
echo "**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
