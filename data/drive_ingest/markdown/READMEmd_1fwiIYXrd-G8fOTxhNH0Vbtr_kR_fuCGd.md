# Nightly Intel Pipeline

**ATP 5-19 Compliant Intelligence Gathering System for Local Execution**

An ethical, automated intelligence pipeline that discovers, scores, and delivers briefings on AI/MLOps technologies from GitHub and arXiv.

## Features

### Ethical Web Scraping (ATP 5-19 RA-1 Compliant)
- RFC 9309 compliant robots.txt parsing (24-hour cache)
- Domain-specific rate limiting with adaptive jitter
- Circuit breaker pattern for sustained failures
- Proper User-Agent identification
- Crawl-delay respect

### Multi-Source Intelligence Gathering
- **GitHub Repositories**: Topic-based discovery, star filtering, code flattening
- **arXiv Papers**: Category and keyword search, metadata extraction

### JR Engine Scoring (Purpose → Reasons → Brakes)
- Purpose Alignment: MLOps/AI strategic fit
- Technical Merit: Implementation quality
- Adoption Potential: Community traction
- Risk Assessment: ATP 5-19 risk levels (RA-1 through RA-4)

### Tier Classification
- **Tier 1**: Executive review required (score ≥ 85)
- **Tier 2**: Auto-action approved (score ≥ 70)
- **Tier 3**: Archive for later (score ≥ 50)
- **Tier 4**: Low priority (score < 50)

### Local Storage & Briefings
- SQLite database for scored content
- Markdown briefings with executive summaries
- Tiered recommendations

## Installation

### Prerequisites
- Python 3.9+
- GitHub Personal Access Token
- Anthropic API Key (for Claude)

### Setup

```bash
# 1. Navigate to the pipeline directory
cd nightly_intel_pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export GITHUB_TOKEN = "REDACTED_API_KEY"
export ANTHROPIC_API_KEY = "REDACTED_API_KEY"

# 4. Run the pipeline
python main.py
```

### Environment Variables

**Required:**
- `GITHUB_TOKEN`: GitHub personal access token ([Create one here](https://github.com/settings/tokens))
- `ANTHROPIC_API_KEY`: Anthropic API key ([Get one here](https://console.anthropic.com/))

**Optional:**
- Configure topics, categories, and thresholds in `config.py`

## Usage

### Basic Usage

```bash
# Run with default settings
python main.py
```

### Advanced Usage

```bash
# Specify custom topics
python main.py --topics mlops kubernetes llm ai-governance

# Look back further in time
python main.py --days-back 30

# Download arXiv PDFs (slower, more storage)
python main.py --download-pdfs

# Combine options
python main.py --topics llm mlops --days-back 14 --download-pdfs
```

### Programmatic Usage

```python
from pipeline import run_pipeline

# Run the full pipeline
briefing_file = run_pipeline(
    github_topics=["mlops", "kubernetes"],
    arxiv_days_back=7,
    download_pdfs=False
)

print(f"Briefing generated: {briefing_file}")
```

### Module Usage

```python
# GitHub repository flattening
from scrapers.github_flattener import GitHubFlattener

flattener = GitHubFlattener()
repos = flattener.search_repositories(topics=["mlops"])
flattened_files = flattener.flatten_repositories(repos)

# arXiv paper crawling
from scrapers.arxiv_crawler import ArxivCrawler

crawler = ArxivCrawler()
papers = crawler.search_papers(days_back=7)
metadata_files = crawler.download_papers(papers)

# JR Engine scoring
from engines.jr_engine import JREngine

engine = JREngine()
score = engine.score_content(content, "github_repo", "owner/repo")

# Briefing generation
from storage.briefing import BriefingGenerator

generator = BriefingGenerator()
briefing_file = generator.generate_briefing()
```

## Configuration

Edit `config.py` to customize:

### Scraping Ethics
```python
SCRAPING_ETHICS = {
    "robots_txt": {
        "enabled": True,
        "cache_ttl": 86400,  # 24 hours
        "respect_crawl_delay": True,
        "honor_disallow": True
    },
    "rate_limiting": {
        "default_delay": 3.0,  # seconds
        "youtube": 5.0,
        "twitter": 4.0,
        # ... domain-specific delays
    }
}
```

### GitHub Topics
```python
GITHUB_CONFIG = {
    "target_topics": [
        "mlops",
        "machine-learning",
        "kubernetes",
        "ai-orchestration",
        # ... add more topics
    ],
    "min_stars": 100,
    "max_repos_per_topic": 10
}
```

### arXiv Categories
```python
ARXIV_CONFIG = {
    "categories": [
        "cs.AI",  # Artificial Intelligence
        "cs.LG",  # Machine Learning
        # ... add more categories
    ],
    "search_terms": [
        "MLOps",
        "LLM",
        # ... add more keywords
    ]
}
```

### JR Engine Scoring
```python
JR_ENGINE_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "scoring_criteria": {
        "purpose_alignment": 0.35,
        "technical_merit": 0.25,
        "adoption_potential": 0.20,
        "risk_assessment": 0.20
    },
    "tier_thresholds": {
        "tier_1": 85,
        "tier_2": 70,
        "tier_3": 50
    }
}
```

## Architecture

```
nightly_intel_pipeline/
├── config.py                 # Configuration (includes GKE settings)
├── pipeline.py               # Main orchestration
├── main.py                   # CLI entry point
├── Dockerfile                # Container image for GKE
├── requirements.txt          # Dependencies
├── GEMINI_ANALYSIS.md        # Gemini 2.0 Pro analysis framework
├── scrapers/
│   ├── ethical_scraper.py    # ATP 5-19 compliant scraper
│   ├── github_flattener.py   # GitHub repo discovery
│   └── arxiv_crawler.py      # arXiv paper crawler
├── engines/
│   └── jr_engine.py          # JR scoring engine
├── storage/
│   ├── database.py           # SQLite storage
│   └── briefing.py           # Briefing generator
├── utils/
│   └── logging_setup.py      # Logging configuration
├── kubernetes/               # GKE deployment configs
│   ├── README.md             # GKE deployment guide
│   ├── cronjob.yaml          # CronJob specification
│   ├── pvc.yaml              # Persistent volume claims
│   ├── service-account.yaml  # RBAC configuration
│   └── secret.yaml.example   # Secret template
└── data/                     # Generated data
    ├── repos/                # Flattened repositories
    ├── papers/               # arXiv metadata
    └── briefings/            # Generated briefings
```

## Pipeline Execution Flow

1. **Ingestion**
   - Discover GitHub repositories by topic
   - Search arXiv for recent papers
   - Flatten repos and download metadata

2. **JR Scoring**
   - Evaluate content using Claude API
   - Apply Purpose → Reasons → Brakes framework
   - Calculate composite scores

3. **Tier Classification**
   - Classify content into 4 tiers
   - Assign ATP 5-19 risk levels

4. **Storage**
   - Store scores in SQLite database
   - Maintain metadata and reasoning

5. **Briefing**
   - Generate executive briefing
   - Organize by tier
   - Include recommendations

## Output

### Briefing Structure

```markdown
# Nightly Intelligence Briefing

## Executive Summary
- Total items processed
- Tier breakdown
- Key highlights

## Tier 1: Executive Review Required
- High-value items
- Full evaluation details
- Concerns and brakes

## Tier 2: Auto-Action Approved
- Recommended items
- Brief evaluations

## Tier 3-4: Archive/Low Priority
- Summary counts
```

### Database Schema

**Tables:**
- `repositories`: GitHub repo metadata and scores
- `papers`: arXiv paper metadata and scores
- `briefings`: Briefing generation history

## Security & Ethics

### ATP 5-19 Compliance
- RA-1 (Catastrophic): Multi-layer validation
- RA-2 (Critical): Automated monitoring
- RA-3 (Moderate): Standard testing
- RA-4 (Low): Basic validation

### Ethical Scraping Principles
- Respect robots.txt directives
- Rate limiting with jitter
- Circuit breakers for sustained failures
- Proper User-Agent identification
- Crawl-delay compliance

## Troubleshooting

### Common Issues

**GitHub API Rate Limits**
```bash
# Check your rate limit
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

**Missing Dependencies**
```bash
pip install -r requirements.txt --upgrade
```

**Database Locked**
```bash
# Close any open connections to the database
# Or delete and regenerate: rm storage/intel_pipeline.db
```

## Cost Estimates

- **GitHub API**: Free tier (5,000 requests/hour)
- **arXiv API**: Free, unlimited (respect 3-second delay)
- **Claude API**: ~$0.50-2.00 per run (depends on content volume)

## Deployment Options

### Option 1: Local Scheduling

**Cron (Linux/Mac)**
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/nightly_intel_pipeline && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

**Task Scheduler (Windows)**
```powershell
# Create a scheduled task
schtasks /create /tn "NightlyIntel" /tr "python C:\path\to\main.py" /sc daily /st 02:00
```

### Option 2: GKE CronJob (Production)

For production deployments with scalability and monitoring:

**Features:**
- Automated nightly execution on Google Kubernetes Engine
- ~45 minute runtime target
- Persistent storage for data and briefings
- Cost-optimized (~$77/month)
- Multi-container orchestration
- Integration with 4 namespace services

**Quick Start:**
```bash
# See full deployment guide
cat kubernetes/README.md

# Build and deploy
docker build -t gcr.io/PROJECT_ID/nightly-intel-pipeline:latest .
docker push gcr.io/PROJECT_ID/nightly-intel-pipeline:latest
kubectl apply -f kubernetes/
```

**Documentation:**
- [GKE Deployment Guide](kubernetes/README.md) - Full deployment instructions
- [Gemini Analysis Framework](GEMINI_ANALYSIS.md) - Pre-production analysis approach

## License

This project implements ethical intelligence gathering practices and ATP 5-19 risk management frameworks.

## Support

For issues or questions:
1. Check configuration in `config.py`
2. Review logs in `logs/pipeline.log`
3. Verify environment variables are set
4. Ensure API keys have proper permissions

---

**Built with:**
- Python 3.9+
- Claude API (Anthropic)
- GitHub API
- arXiv API
- SQLite