#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Suggestion Acceptance Rate Dashboard — KAIROS Telemetry Analyzer.

Reads .beads/speculation_telemetry.jsonl and computes:
  - Acceptance rate (accepted / total outcomes)
  - Filter hit distribution (which filters block most suggestions)
  - Generation latency percentiles (p50, p90, p99)
  - TTL decay analysis (how suggestion freshness correlates with acceptance)
  - Hourly activity heatmap

Usage:
    python scripts/suggestion_dashboard.py [--json] [--beads-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


def load_events(beads_dir: Path) -> list[dict]:
  """Load all speculation telemetry events."""
  log_file = beads_dir / "speculation_telemetry.jsonl"
  if not log_file.exists():
    return []
  events = []
  with open(log_file) as f:
    for line in f:
      line = line.strip()
      if not line:
        continue
      try:
        events.append(json.loads(line))
      except json.JSONDecodeError:
        continue
  return events


def compute_acceptance_rate(events: list[dict]) -> dict:
  """Compute suggestion acceptance metrics."""
  outcomes = [e for e in events if e.get("event_type") == "suggestion_outcome"]
  if not outcomes:
    return {"total_outcomes": 0, "acceptance_rate": 0.0}

  accepted = sum(1 for o in outcomes if o.get("accepted"))
  total = len(outcomes)
  return {
    "total_outcomes": total,
    "accepted": accepted,
    "dismissed": total - accepted,
    "acceptance_rate": round(accepted / total * 100, 1) if total else 0.0,
  }


def compute_filter_distribution(events: list[dict]) -> dict:
  """Compute which filters block most suggestions."""
  filtered = [e for e in events if e.get("event_type") == "suggestion_filtered"]
  if not filtered:
    return {"total_filtered": 0, "reasons": {}}

  reasons = Counter(e.get("reason", "unknown") for e in filtered)
  return {
    "total_filtered": len(filtered),
    "reasons": dict(reasons.most_common()),
  }


def compute_latency_percentiles(events: list[dict]) -> dict:
  """Compute generation latency percentiles."""
  prefetch = [
    e
    for e in events
    if e.get("event_type") == "suggestion_proactive_prefetch"
    and e.get("generation_time_ms")
  ]
  latencies = [e["generation_time_ms"] for e in prefetch if e["generation_time_ms"] > 0]
  if not latencies:
    return {"sample_count": 0}

  return {
    "sample_count": len(latencies),
    "p50_ms": round(statistics.median(latencies), 1),
    "p90_ms": round(sorted(latencies)[int(len(latencies) * 0.9)], 1),
    "p99_ms": round(sorted(latencies)[int(len(latencies) * 0.99)], 1),
    "mean_ms": round(statistics.mean(latencies), 1),
    "min_ms": round(min(latencies), 1),
    "max_ms": round(max(latencies), 1),
  }


def compute_ttl_decay(events: list[dict]) -> dict:
  """Analyze how suggestion age correlates with acceptance.

  Groups outcomes by age bucket (0-1m, 1-5m, 5-10m) and computes
  acceptance rate per bucket to determine optimal TTL.
  """
  outcomes = [e for e in events if e.get("event_type") == "suggestion_outcome"]
  if not outcomes:
    return {"buckets": {}}

  buckets: dict[str, dict] = {
    "0-60s": {"accepted": 0, "total": 0},
    "60-300s": {"accepted": 0, "total": 0},
    "300-600s": {"accepted": 0, "total": 0},
  }

  for o in outcomes:
    accept_ms = o.get("time_to_accept_ms") or o.get("time_to_ignore_ms") or 0
    age_s = accept_ms / 1000 if accept_ms else 0

    if age_s < 60:
      bucket = "0-60s"
    elif age_s < 300:
      bucket = "60-300s"
    else:
      bucket = "300-600s"

    buckets[bucket]["total"] += 1
    if o.get("accepted"):
      buckets[bucket]["accepted"] += 1

  # Compute per-bucket rates
  result = {}
  for name, data in buckets.items():
    rate = round(data["accepted"] / data["total"] * 100, 1) if data["total"] else 0.0
    result[name] = {**data, "acceptance_rate": rate}

  return {"buckets": result}


def compute_hourly_activity(events: list[dict]) -> dict:
  """Compute hourly distribution of suggestion activity."""
  prefetch = [
    e for e in events if e.get("event_type") == "suggestion_proactive_prefetch"
  ]
  if not prefetch:
    return {"hours": {}}

  hourly: dict[int, dict] = defaultdict(lambda: {"generated": 0, "empty": 0})
  for e in prefetch:
    ts = e.get("timestamp", 0)
    if ts:
      import datetime

      hour = datetime.datetime.fromtimestamp(ts).hour
      if e.get("status") == "generated":
        hourly[hour]["generated"] += 1
      else:
        hourly[hour]["empty"] += 1

  return {"hours": dict(sorted(hourly.items()))}


def compute_prefetch_summary(events: list[dict]) -> dict:
  """Summary of proactive prefetch attempts."""
  prefetch = [
    e for e in events if e.get("event_type") == "suggestion_proactive_prefetch"
  ]
  if not prefetch:
    return {"total_prefetches": 0}

  generated = sum(1 for e in prefetch if e.get("status") == "generated")
  empty = sum(1 for e in prefetch if e.get("status") == "empty")
  no_messages = sum(1 for e in prefetch if e.get("status") == "no_messages")
  suppressed = sum(1 for e in prefetch if e.get("suppressed"))
  filtered_count = sum(1 for e in prefetch if e.get("filtered"))

  return {
    "total_prefetches": len(prefetch),
    "generated": generated,
    "empty": empty,
    "no_messages": no_messages,
    "suppressed": suppressed,
    "filtered": filtered_count,
    "success_rate": round(generated / len(prefetch) * 100, 1) if prefetch else 0.0,
  }


def build_dashboard(beads_dir: Path) -> dict:
  """Build the full dashboard report."""
  events = load_events(beads_dir)
  return {
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "total_events": len(events),
    "prefetch_summary": compute_prefetch_summary(events),
    "acceptance_rate": compute_acceptance_rate(events),
    "filter_distribution": compute_filter_distribution(events),
    "latency_percentiles": compute_latency_percentiles(events),
    "ttl_decay_analysis": compute_ttl_decay(events),
    "hourly_activity": compute_hourly_activity(events),
  }


def print_human_dashboard(dashboard: dict) -> None:
  """Pretty-print the dashboard for human consumption."""
  print("=" * 60)
  print("  KAIROS Suggestion Dashboard")
  print(f"  Generated: {dashboard['generated_at']}")
  print(f"  Total events: {dashboard['total_events']}")
  print("=" * 60)

  # Prefetch summary
  pf = dashboard["prefetch_summary"]
  print("\n📡 Prefetch Summary")
  print(f"  Total attempts: {pf.get('total_prefetches', 0)}")
  print(f"  Generated:      {pf.get('generated', 0)}")
  print(f"  Empty:          {pf.get('empty', 0)}")
  print(f"  No messages:    {pf.get('no_messages', 0)}")
  print(f"  Success rate:   {pf.get('success_rate', 0)}%")

  # Acceptance
  ar = dashboard["acceptance_rate"]
  print("\n✅ Acceptance Rate")
  print(f"  Total outcomes: {ar.get('total_outcomes', 0)}")
  print(f"  Accepted:       {ar.get('accepted', 0)}")
  print(f"  Dismissed:      {ar.get('dismissed', 0)}")
  print(f"  Rate:           {ar.get('acceptance_rate', 0)}%")

  # Filters
  fd = dashboard["filter_distribution"]
  print(f"\n🚫 Filter Distribution (total: {fd.get('total_filtered', 0)})")
  for reason, count in fd.get("reasons", {}).items():
    print(f"  {reason}: {count}")

  # Latency
  lp = dashboard["latency_percentiles"]
  if lp.get("sample_count", 0) > 0:
    print(f"\n⏱️  Latency Percentiles (n={lp['sample_count']})")
    print(f"  p50: {lp.get('p50_ms', 0)}ms")
    print(f"  p90: {lp.get('p90_ms', 0)}ms")
    print(f"  p99: {lp.get('p99_ms', 0)}ms")
    print(f"  mean: {lp.get('mean_ms', 0)}ms")
  else:
    print("\n⏱️  Latency: No data")

  # TTL decay
  ttl = dashboard["ttl_decay_analysis"]
  buckets = ttl.get("buckets", {})
  if buckets:
    print("\n📉 TTL Decay Analysis")
    for name, data in buckets.items():
      print(
        f"  {name}: {data['acceptance_rate']}% ({data['accepted']}/{data['total']})"
      )

    # TTL recommendation
    best_bucket = max(buckets.items(), key=lambda x: x[1]["acceptance_rate"])
    print(f"\n  💡 Optimal TTL window: {best_bucket[0]} (highest acceptance)")

  print()


def main() -> None:
  parser = argparse.ArgumentParser(description="KAIROS Suggestion Dashboard")
  parser.add_argument(
    "--beads-dir",
    type=Path,
    default=Path(".beads"),
    help="Path to .beads/ directory (default: .beads/)",
  )
  parser.add_argument(
    "--json",
    action="store_true",
    help="Output as JSON instead of human-readable",
  )
  args = parser.parse_args()

  dashboard = build_dashboard(args.beads_dir)

  if args.json:
    json.dump(dashboard, sys.stdout, indent=2)
    print()
  else:
    print_human_dashboard(dashboard)


if __name__ == "__main__":
  main()
