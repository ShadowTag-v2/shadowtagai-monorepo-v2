# Quick Start Guide - Nightly Intel Pipeline

Get your intelligence pipeline running in 5 minutes!

## Prerequisites

- Python 3.9+
- GitHub Personal Access Token
- Anthropic API Key

## Installation (30 seconds)

```bash
cd nightly_intel_pipeline

# Run automated setup
./setup.sh

# If you created a virtual environment:
source venv/bin/activate
```

## Configuration (2 minutes)

### 1. Set API Keys

Edit `.env` file:
```bash
nano .env
```

Add your keys:
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

### 2. (Optional) Customize Topics

Edit `config.py` to change GitHub topics:
```python
GITHUB_CONFIG = {
    "target_topics": [
        "mlops",           # Your topics here
        "kubernetes",
        "ai-orchestration"
    ]
}
```

## Run It! (2 minutes)

### Basic Run
```bash
python main.py
```

### Custom Run
```bash
# Specific topics
python main.py --topics mlops llm kubernetes

# Look back 30 days
python main.py --days-back 30

# Download PDFs (slower)
python main.py --download-pdfs
```

## What Happens?

The pipeline will:

1. **Discover** (30-60 seconds)
   - Search GitHub for repos matching your topics
   - Search arXiv for recent AI/ML papers

2. **Flatten** (1-2 minutes)
   - Download and flatten repository code
   - Extract paper metadata and abstracts

3. **Score** (2-5 minutes, depends on volume)
   - Evaluate each item using Claude API
   - Apply JR Engine (Purpose → Reasons → Brakes)
   - Calculate composite scores

4. **Classify** (instant)
   - Tier 1: Executive review (score ≥ 85)
   - Tier 2: Auto-action approved (score ≥ 70)
   - Tier 3: Archive (score ≥ 50)
   - Tier 4: Low priority (< 50)

5. **Brief** (instant)
   - Generate markdown briefing
   - Store in database

## View Results

### Read Briefing
```bash
# Find latest briefing
ls -lt data/briefings/

# View it
cat data/briefings/briefing_YYYYMMDD_HHMMSS.md
```

### Check Database
```bash
sqlite3 storage/intel_pipeline.db

# Example queries:
sqlite> SELECT repo_name, total_score, tier FROM repositories ORDER BY total_score DESC LIMIT 10;
sqlite> SELECT title, total_score, tier FROM papers ORDER BY total_score DESC LIMIT 10;
sqlite> .quit
```

### Explore Raw Data
```bash
# Flattened repositories
ls data/repos/

# Paper metadata
ls data/papers/
```

## Example Output

```markdown
# Nightly Intelligence Briefing

**Generated:** 2025-11-15 02:30:15
**Total Intelligence Items:** 47
- GitHub Repositories: 32
- arXiv Papers: 15

### Tier Breakdown

**Tier 1 (Executive Review):** 5 items
  - Repositories: 3
  - Papers: 2

**Tier 2 (Auto-Action):** 18 items
  - Repositories: 12
  - Papers: 6

## Tier 1: Executive Review Required

### GitHub Repositories

#### feast-dev/feast
**URL:** https://github.com/feast-dev/feast
**Score:** 87.5 | **ATP Risk:** RA-2 | **Stars:** 5234

**Evaluation:**
- Purpose Alignment (92): Feature store directly supports MLOps best practices...
- Technical Merit (88): Well-architected, production-grade implementation...
- Adoption Potential (85): Strong community, used by major tech companies...
- Risk Assessment (85): Moderate complexity, well-documented...

**Concerns (Brakes):**
- Requires infrastructure investment (Redis, databases)
- Learning curve for distributed systems
```

## Scheduling

### Run Nightly (Linux/Mac)
```bash
# Add to crontab
crontab -e

# Run at 2 AM daily
0 2 * * * cd /path/to/nightly_intel_pipeline && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

### Run Nightly (Windows)
```powershell
schtasks /create /tn "NightlyIntel" /tr "python C:\path\to\main.py" /sc daily /st 02:00
```

## Costs

**Per Run (typical):**
- GitHub API: Free (within rate limits)
- arXiv API: Free
- Claude API: ~$0.50-2.00 (depends on content volume)

**Monthly (nightly runs):**
- ~$15-60 for Claude API

## Troubleshooting

### "GITHUB_TOKEN not set"
```bash
export GITHUB_TOKEN='your_token_here'
# Or add to .env file
```

### "Rate limit exceeded"
Wait 1 hour or reduce `max_repos_per_topic` in config.py

### "Database locked"
```bash
# Close any open connections
rm storage/intel_pipeline.db  # Resets database
```

### Missing dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Next Steps

1. **Customize** `config.py` for your specific needs
2. **Review** first briefing to validate relevance
3. **Tune** tier thresholds and scoring weights
4. **Schedule** for nightly execution
5. **Integrate** with your workflow (Slack, email, etc.)

## Support

- Check logs: `cat logs/pipeline.log`
- Review config: `cat config.py`
- Read docs: `cat README.md`

---

**You're ready!** Run `python main.py` and get your first intelligence briefing.
