# Gemini Ingestion Layer - Integration Guide

**Added to COR.53 Stack:** Phase 0 (Pre-Validation Intelligence Collection)
**Version:** 2.0.0 (with Ingestion Layer)
**Architecture:** GKE CronJob Multi-Container

---

## What Changed?

The COR.53 pipeline now includes **PHASE 0: Intelligence Ingestion** as the first stage:

```
OLD PIPELINE (v1.0.0):
1. Task intake (manual only)
2. Judge 6 validation
3. Skill routing
4. AutoGen execution
5. Audit trail

NEW PIPELINE (v2.0.0):
0. Intelligence ingestion (multi-source collection) ← NEW
1. Task intake (intelligence-driven OR manual)
2. Judge 6 validation
3. Skill routing
4. AutoGen execution
5. Audit trail
```

---

## New Capabilities

### 1. Automated Intelligence Collection

**Nightly Batch Ingestion:**

- Runs as GKE CronJob (~45 min target runtime)
- Multi-source crawling (YouTube, Twitter, News, RSS, etc.)
- Ethical compliance (robots.txt, rate limiting)
- Tier classification (Tier 1/2/3 using Gemini 2.0 Flash)

### 2. Intelligence-Driven Task Generation

**Automatic Task Creation:**

- Convert Tier 1/2 intelligence items to validated tasks
- AM briefing → automated action
- 30-vertical monitoring without manual intervention

### 3. AM Briefing Delivery

**Morning Intelligence Summary:**

- Tier-sorted intelligence (Tier 1 first)
- Relevance-scored items
- Actionable insights with source links

---

## Integration Options

### Option 1: Manual Task Mode (Default Behavior)

**What it does:** Uses existing COR.53 workflow without ingestion
**When to use:** You have manual tasks or don't need automated intelligence
**How to enable:** `enable_ingestion=False` (or omit the parameter)

```python
from cor53_integration_guide import initialize_cor53, TaskRequest

# Initialize WITHOUT ingestion layer
cor = initialize_cor53(
    strict_mode=True,
    enable_ingestion=False  # Disable Phase 0
)

# Use manual tasks as before
task = TaskRequest(
    task_id="MANUAL_001",
    description="Your manual task",
    justification="Your justification",
    ...
)

result = cor['process_task'](task)
```

**Advantage:** Simpler setup, lower cost (no ingestion API costs)
**Disadvantage:** No automated intelligence collection

---

### Option 2: Intelligence-Driven Mode (NEW)

**What it does:** Runs nightly ingestion + automated task generation
**When to use:** You want hands-off 30-vertical monitoring
**How to enable:** `enable_ingestion=True`

```python
from cor53_integration_guide import initialize_cor53
from gemini_ingestion_layer import SourceType, DataTier

# Initialize WITH ingestion layer
cor = initialize_cor53(
    strict_mode=True,
    enable_ingestion=True  # Enable Phase 0
)

# Configure intelligence sources
source_configs = {
    SourceType.YOUTUBE: {
        'channels': ['@healthcare_ai', '@fintech_news'],
        'keywords': ['AI', 'healthcare', 'fintech']
    },
    SourceType.TWITTER: {
        'accounts': ['@tech_insider', '@health_tech'],
        'hashtags': ['#HealthTech', '#AIinHealthcare']
    },
    SourceType.NEWS: {
        'feeds': ['https://news.example.com/rss'],
        'keywords': ['FDA', 'AI', 'healthcare']
    }
}

# STEP 1: Run nightly ingestion
metrics = cor['run_intelligence_ingestion'](source_configs)
print(f"Ingested {metrics.items_ingested} items (Tier 1: {metrics.tier_1_count})")

# STEP 2: Generate AM briefing
briefing = cor['generate_intelligence_briefing']()
print(briefing)

# STEP 3: Convert Tier 1 intelligence to tasks
tasks = cor['intelligence_to_tasks'](
    min_tier=DataTier.TIER_1_CRITICAL,  # Only Tier 1
    auto_execute=False  # Review before execution
)
print(f"Generated {len(tasks)} tasks from intelligence")

# STEP 4: Review and execute tasks
for task in tasks:
    print(f"Task: {task.description}")
    # Execute if approved
    result = cor['process_task'](task)
```

**Advantage:** Fully automated 30-vertical monitoring
**Disadvantage:** Higher cost (~$77/month for ingestion API)

---

### Option 3: Hybrid Mode (RECOMMENDED)

**What it does:** Ingest intelligence + review before task generation
**When to use:** You want automation but with human oversight
**How to enable:** `enable_ingestion=True` + `auto_execute=False`

```python
from cor53_integration_guide import initialize_cor53
from gemini_ingestion_layer import SourceType, DataTier

cor = initialize_cor53(strict_mode=True, enable_ingestion=True)

# Run ingestion (automated)
metrics = cor['run_intelligence_ingestion'](source_configs)

# Generate briefing (automated)
briefing = cor['generate_intelligence_briefing']()
with open('daily_briefing.md', 'w') as f:
    f.write(briefing)

# Convert to tasks but DON'T auto-execute
tasks = cor['intelligence_to_tasks'](
    min_tier=DataTier.TIER_1_CRITICAL,
    auto_execute=False  # Human review required
)

# HUMAN REVIEW STEP
print(f"\n{len(tasks)} intelligence tasks awaiting review:")
for i, task in enumerate(tasks):
    print(f"{i+1}. {task.description}")
    print(f"   Tier: {task.context['tier']}")
    print(f"   Relevance: {task.context['relevance_score']:.2f}")
    print(f"   Source: {task.context['source_url']}")

# Execute approved tasks
approved_task_ids = [0, 2, 4]  # Example: approve tasks 1, 3, 5
for i in approved_task_ids:
    result = cor['process_task'](tasks[i])
    print(f"✓ Executed: {result.overall_status}")
```

**Advantage:** Balance of automation + control
**Disadvantage:** Requires daily review (5-10 minutes)

---

## Cost Comparison

| Mode | Monthly Cost | Pros | Cons |
|------|-------------|------|------|
| **Manual** | $90-450 (tasks only) | Simple, predictable | No automated intelligence |
| **Intelligence-Driven** | $167-527 ($77 ingestion + $90-450 tasks) | Fully automated | Higher cost, requires tuning |
| **Hybrid** | $107-527 ($77 ingestion + $30-450 tasks) | Automation + control | Daily review required |

---

## GKE CronJob Deployment

### Setup CronJob for Nightly Ingestion

**Kubernetes manifest** (`ingestion-cronjob.yaml`):

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gemini-ingestion
  namespace: pnkln-intelligence
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: ingestion
            image: gcr.io/your-project/gemini-ingestion:latest
            env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-keys
                  key: anthropic
            - name: GOOGLE_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-keys
                  key: google
            command:
            - python
            - -c
            - |
              from cor53_integration_guide import initialize_cor53
              from gemini_ingestion_layer import SourceType

              cor = initialize_cor53(enable_ingestion=True)

              source_configs = {...}  # Your config

              metrics = cor['run_intelligence_ingestion'](source_configs)

              briefing = cor['generate_intelligence_briefing']()
              with open('/output/briefing.md', 'w') as f:
                  f.write(briefing)

              print(f"Ingestion complete: {metrics.items_ingested} items")
          restartPolicy: OnFailure
```

**Deploy:**

```bash
kubectl apply -f ingestion-cronjob.yaml
```

**Monitor:**

```bash
kubectl logs -n pnkln-intelligence -l job-name=gemini-ingestion
```

---

## Performance Tuning

### Ingestion Runtime Optimization

**Target:** 45 minutes for 1000-5000 items

**Bottlenecks:**

1. **Rate limiting** (1 req/sec default) → 3600 requests/hour max
2. **Sequential source processing** → Can parallelize
3. **Tier classification** (Gemini API calls) → Can batch

**Optimizations:**

```python
from gemini_ingestion_layer import EthicalCrawlConfig

# Faster rate limiting (if sources allow)
ethical_config = EthicalCrawlConfig(
    rate_limit_requests_per_second=2.0,  # 2x faster
    max_concurrent_requests=10  # More parallelism
)

# Initialize with custom config
from gemini_ingestion_layer import GeminiIngestionPipeline
ingestion = GeminiIngestionPipeline(
    gemini_api_key=os.environ['GOOGLE_API_KEY'],
    ethical_config=ethical_config
)

# Use in COR.53
cor = initialize_cor53(enable_ingestion=True)
cor['pipeline'].ingestion_pipeline = ingestion
```

**Expected Impact:**

- 2 req/sec → 7200 requests/hour → ~22.5 min for 5000 items
- 10 concurrent requests → potential 10x speedup if sources parallelized

---

## Cost Optimization

### Target: $77/month

**Breakdown:**

- Gemini API (tier classification): ~$50/month (5000 items/day × $0.0003/item)
- Compute (GKE CronJob): ~$20/month (1 vCPU, 45 min/day)
- Storage (briefings): ~$5/month (1 GB)
- Network: ~$2/month

**Optimization Strategies:**

1. **Selective Tier Classification:**

   ```python
   # Only classify high-relevance items
   if item.preliminary_score > 0.5:
       tier = classifier.classify_item(...)
   else:
       tier = DataTier.TIER_3_BACKGROUND  # Default low-tier
   ```

2. **Batch Gemini Calls:**

   ```python
   # Classify multiple items in one API call
   # (requires custom prompt engineering)
   ```

3. **Use Fallback Classification:**

   ```python
   # Disable Gemini for cost savings (uses keyword-based fallback)
   # Note: Lower accuracy
   TierClassifier(gemini_api_key=None)  # Forces fallback
   ```

4. **Filter Sources:**

   ```python
   # Only ingest from high-value sources
   source_configs = {
       SourceType.NEWS: {...},  # Keep (high value)
       # SourceType.TWITTER: {...},  # Remove (noisy)
   }
   ```

---

## Troubleshooting

### Issue: "Ingestion layer not available"

**Cause:** `gemini_ingestion_layer.py` not imported
**Fix:**

```bash
# Verify file exists
ls gemini_ingestion_layer.py

# Reinstall if missing
git checkout claude/cor-integration-deployment-01H68gzv26893rqrchCFHTww
```

### Issue: "Ingestion layer disabled"

**Cause:** `enable_ingestion=False` or Google API key missing
**Fix:**

```python
# Enable ingestion
cor = initialize_cor53(enable_ingestion=True)

# Set Google API key
export GOOGLE_API_KEY="AIza..."
```

### Issue: Ingestion taking > 45 minutes

**Cause:** Rate limiting too conservative, sequential processing
**Fix:** See "Performance Tuning" section above

### Issue: High API costs (> $77/month)

**Cause:** Too many items ingested, all items classified
**Fix:** See "Cost Optimization" section above

---

## Migration from v1.0.0 to v2.0.0

**Breaking Changes:** None (ingestion is opt-in)

**Backward Compatibility:** All v1.0.0 code works unchanged

**To adopt ingestion:**

1. **Add ingestion layer:**

   ```bash
   git pull origin claude/cor-integration-deployment-01H68gzv26893rqrchCFHTww
   ```

2. **Install dependencies:**

   ```bash
   pip install google-generativeai --break-system-packages
   ```

3. **Set Google API key:**

   ```bash
   export GOOGLE_API_KEY="AIza..."
   ```

4. **Enable ingestion:**

   ```python
   # Change this:
   cor = initialize_cor53(strict_mode=True)

   # To this:
   cor = initialize_cor53(strict_mode=True, enable_ingestion=True)
   ```

5. **Configure sources and run ingestion:**

   ```python
   source_configs = {...}
   metrics = cor['run_intelligence_ingestion'](source_configs)
   ```

---

## Example: Full Intelligence-Driven Workflow

```python
from cor53_integration_guide import initialize_cor53, TaskRequest
from gemini_ingestion_layer import SourceType, DataTier

# PHASE 0: Initialize with ingestion
cor = initialize_cor53(
    strict_mode=True,
    enable_ingestion=True
)

# PHASE 1: Configure sources
source_configs = {
    SourceType.YOUTUBE: {
        'channels': ['@healthcare_ai', '@fintech_news'],
        'keywords': ['AI', 'healthcare', 'fintech', 'FDA', 'SEC']
    },
    SourceType.TWITTER: {
        'accounts': ['@FDA_Drug_Info', '@SECGov'],
        'hashtags': ['#HealthTech', '#Fintech', '#RegTech']
    },
    SourceType.NEWS: {
        'feeds': [
            'https://www.fiercehealthcare.com/rss',
            'https://www.mobihealthnews.com/rss'
        ],
        'keywords': ['AI', 'healthcare', 'regulation']
    }
}

# PHASE 2: Run nightly ingestion
print("Running intelligence ingestion...")
metrics = cor['run_intelligence_ingestion'](source_configs)

print(f"\nIngestion Metrics:")
print(f"  Items ingested: {metrics.items_ingested}")
print(f"  Tier 1 (Critical): {metrics.tier_1_count}")
print(f"  Tier 2 (Important): {metrics.tier_2_count}")
print(f"  Tier 3 (Background): {metrics.tier_3_count}")
print(f"  Total cost: ${metrics.total_cost:.4f}")
print(f"  Avg relevance: {metrics.avg_relevance_score:.2f}")

# PHASE 3: Generate AM briefing
print("\nGenerating AM briefing...")
briefing = cor['generate_intelligence_briefing']()

with open('daily_intelligence_briefing.md', 'w') as f:
    f.write(briefing)

print("✓ Briefing saved to daily_intelligence_briefing.md")

# PHASE 4: Convert Tier 1 to tasks
print("\nConverting Tier 1 intelligence to tasks...")
tasks = cor['intelligence_to_tasks'](
    min_tier=DataTier.TIER_1_CRITICAL,
    auto_execute=False
)

print(f"Generated {len(tasks)} tasks from Tier 1 intelligence")

# PHASE 5: Human review (optional)
print("\nTasks awaiting review:")
for i, task in enumerate(tasks):
    print(f"\n{i+1}. {task.description}")
    print(f"   Tier: {task.context['tier']}")
    print(f"   Relevance: {task.context['relevance_score']:.2f}")
    print(f"   Source: {task.context['source_url'][:50]}...")

# PHASE 6: Execute approved tasks
approved_ids = [0, 1]  # Approve first 2 tasks
print(f"\nExecuting {len(approved_ids)} approved tasks...")

for task_id in approved_ids:
    result = cor['process_task'](tasks[task_id])
    print(f"\nTask {tasks[task_id].task_id}:")
    print(f"  Status: {result.overall_status}")
    print(f"  Violation Level: {result.validation.violation_level.value}")
    print(f"  Execution Time: {result.execution_time_seconds:.2f}s")

# PHASE 7: Export reports
print("\nExporting execution report...")
report_path = cor['export_report']('intelligence_driven_report.json')
print(f"✓ Report saved to {report_path}")

print("\n✓ Intelligence-driven workflow complete!")
```

---

## Summary

**What you get with Ingestion Layer:**

- ✅ Automated 30-vertical monitoring
- ✅ Tier-classified intelligence (Gemini 2.0 Flash)
- ✅ Daily AM briefings
- ✅ Intelligence-driven task generation
- ✅ Ethical compliance (robots.txt, rate limiting)
- ✅ Cost-optimized (~$77/month)
- ✅ GKE CronJob orchestration

**When to use:**

- Continuous competitive intelligence
- Regulatory monitoring (FDA, SEC, etc.)
- Market opportunity detection
- Hands-off 30-vertical expansion

**When NOT to use:**

- One-off tasks (use manual mode)
- Budget constraints (manual mode is cheaper)
- No intelligence sources configured

**Next steps:**

1. Enable ingestion: `enable_ingestion=True`
2. Configure sources: `source_configs = {...}`
3. Run ingestion: `run_intelligence_ingestion(source_configs)`
4. Review briefing: `generate_intelligence_briefing()`
5. Execute tasks: `intelligence_to_tasks()` → `process_task()`

**Documentation:**

- Full code: `gemini_ingestion_layer.py`
- Analysis prompt: `GEMINI_INGESTION_ANALYSIS_PROMPT.md`
- Integration: `cor53_integration_guide.py` (v2.0.0)
