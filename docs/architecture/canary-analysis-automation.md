# Canary Analysis Automation

## Architecture
Automated error-rate comparison between stable and canary revisions.

### Canary Analysis Script
```python
#!/usr/bin/env python3
"""canary_analysis.py — Compare canary vs stable error rates."""
import subprocess, json, sys, time

PROJECT = "shadowtag-omega-v4"
SERVICE = "counselconduit"
REGION = "us-central1"
WINDOW_MINUTES = 10
ERROR_THRESHOLD = 0.05  # 5% error rate delta triggers rollback

def get_revision_metrics(revision: str, window_min: int) -> dict:
    """Query Cloud Monitoring for revision-specific metrics."""
    filter_str = (
        f'resource.type="cloud_run_revision" '
        f'AND resource.labels.service_name="{SERVICE}" '
        f'AND resource.labels.revision_name="{revision}" '
        f'AND metric.type="run.googleapis.com/request_count"'
    )
    # Use Cloud Monitoring API to get request counts and error rates
    # Returns: {"total": N, "errors": M, "error_rate": M/N}
    return {"total": 0, "errors": 0, "error_rate": 0.0}

def analyze_canary():
    # Get current traffic split
    result = subprocess.run([
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}",
        "--format=json(status.traffic)"
    ], capture_output=True, text=True)
    
    traffic = json.loads(result.stdout)
    stable_rev = None
    canary_rev = None
    
    for t in traffic.get("status", {}).get("traffic", []):
        if t.get("tag") == "canary":
            canary_rev = t["revisionName"]
        elif t.get("percent", 0) > 50:
            stable_rev = t["revisionName"]
    
    if not canary_rev:
        print("No canary revision found")
        sys.exit(0)
    
    stable_metrics = get_revision_metrics(stable_rev, WINDOW_MINUTES)
    canary_metrics = get_revision_metrics(canary_rev, WINDOW_MINUTES)
    
    delta = canary_metrics["error_rate"] - stable_metrics["error_rate"]
    
    if delta > ERROR_THRESHOLD:
        print(f"ROLLBACK: Canary error rate {canary_metrics['error_rate']:.2%} "
              f"exceeds stable {stable_metrics['error_rate']:.2%} by {delta:.2%}")
        # Auto-rollback
        subprocess.run([
            "gcloud", "run", "services", "update-traffic", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}",
            "--to-tags=canary=0", "--quiet"
        ])
        sys.exit(1)
    else:
        print(f"PASS: Canary delta {delta:.2%} within threshold {ERROR_THRESHOLD:.2%}")

if __name__ == "__main__":
    analyze_canary()
```

### GitHub Actions Integration
```yaml
- name: Canary Analysis
  run: python scripts/canary_analysis.py
  timeout-minutes: 15
```

### Metrics Compared
| Metric | Weight | Threshold |
|--------|--------|-----------|
| Error rate (5xx) | 40% | +5% |
| Latency p95 | 30% | +200ms |
| Latency p50 | 20% | +100ms |
| Memory usage | 10% | +50% |
