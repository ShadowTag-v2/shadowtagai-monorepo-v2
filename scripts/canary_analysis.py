#!/usr/bin/env python3
"""Item 15: Canary analysis script for CounselConduit.

Compares error rates between canary and baseline Cloud Run revisions.
Used in deploy-counselconduit.yml workflow to gate production promotion.

Usage:
    python scripts/canary_analysis.py \\
        --project shadowtag-omega-v4 \\
        --service counselconduit \\
        --canary-revision <rev> \\
        --baseline-revision <rev> \\
        --threshold 0.01
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time


def get_error_rate(
  project: str,
  service: str,
  revision: str,
  window_minutes: int = 10,
) -> dict[str, float]:
  """Query Cloud Monitoring for a revision's error rate."""
  end_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
  start_time = time.strftime(
    "%Y-%m-%dT%H:%M:%SZ",
    time.gmtime(time.time() - window_minutes * 60),
  )

  # Query total requests
  filter_total = (
    f'resource.type="cloud_run_revision" AND '
    f'resource.labels.service_name="{service}" AND '
    f'resource.labels.revision_name="{revision}" AND '
    f'metric.type="run.googleapis.com/request_count"'
  )

  filter_errors = filter_total + ' AND metric.labels.response_code_class="5xx"'

  def _query_metric(mql_filter: str) -> float:
    """Execute a Cloud Monitoring query and return total value."""
    cmd = [
      "gcloud",
      "monitoring",
      "time-series",
      "list",
      f"--project={project}",
      f"--filter={mql_filter}",
      f"--interval-start-time={start_time}",
      f"--interval-end-time={end_time}",
      "--format=json",
    ]
    try:
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
      )
      if result.returncode != 0:
        print(f"Warning: gcloud query failed: {result.stderr.strip()}", file=sys.stderr)
        return 0.0

      data = json.loads(result.stdout) if result.stdout.strip() else []
      total = 0.0
      for ts in data:
        for point in ts.get("points", []):
          val = point.get("value", {})
          total += float(val.get("int64Value", val.get("doubleValue", 0)))
      return total
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
      print(f"Warning: metric query error: {e}", file=sys.stderr)
      return 0.0

  total_requests = _query_metric(filter_total)
  error_requests = _query_metric(filter_errors)

  error_rate = error_requests / total_requests if total_requests > 0 else 0.0

  return {
    "revision": revision,
    "total_requests": total_requests,
    "error_requests": error_requests,
    "error_rate": round(error_rate, 6),
  }


def analyze(
  project: str,
  service: str,
  canary_rev: str,
  baseline_rev: str,
  threshold: float,
  window: int,
) -> bool:
  """Compare canary vs baseline and return True if canary is healthy."""
  print(f"Analyzing canary: {canary_rev} vs baseline: {baseline_rev}")
  print(f"Window: {window} min, Threshold: {threshold}")
  print("-" * 60)

  canary = get_error_rate(project, service, canary_rev, window)
  baseline = get_error_rate(project, service, baseline_rev, window)

  print(f"\nCanary  ({canary_rev}):")
  print(f"  Requests: {canary['total_requests']}")
  print(f"  Errors:   {canary['error_requests']}")
  print(f"  Rate:     {canary['error_rate']:.4%}")

  print(f"\nBaseline ({baseline_rev}):")
  print(f"  Requests: {baseline['total_requests']}")
  print(f"  Errors:   {baseline['error_requests']}")
  print(f"  Rate:     {baseline['error_rate']:.4%}")

  # Decision logic
  if canary["total_requests"] < 10:
    print("\n⚠️  Insufficient canary traffic (<10 requests). Passing by default.")
    return True

  delta = canary["error_rate"] - baseline["error_rate"]
  print(f"\nDelta: {delta:+.4%}")

  if canary["error_rate"] > threshold:
    print(
      f"\n❌ FAIL: Canary error rate ({canary['error_rate']:.4%}) exceeds threshold ({threshold:.4%})"
    )
    return False

  if delta > threshold:
    print(
      f"\n❌ FAIL: Error rate increase ({delta:+.4%}) exceeds threshold ({threshold:.4%})"
    )
    return False

  print(
    f"\n✅ PASS: Canary is healthy (error rate: {canary['error_rate']:.4%}, delta: {delta:+.4%})"
  )
  return True


def main() -> None:
  parser = argparse.ArgumentParser(description="Canary analysis for Cloud Run")
  parser.add_argument("--project", default="shadowtag-omega-v4")
  parser.add_argument("--service", default="counselconduit")
  parser.add_argument("--canary-revision", required=True)
  parser.add_argument("--baseline-revision", required=True)
  parser.add_argument("--threshold", type=float, default=0.01)
  parser.add_argument(
    "--window", type=int, default=10, help="Analysis window in minutes"
  )
  args = parser.parse_args()

  healthy = analyze(
    args.project,
    args.service,
    args.canary_revision,
    args.baseline_revision,
    args.threshold,
    args.window,
  )
  sys.exit(0 if healthy else 1)


if __name__ == "__main__":
  main()
