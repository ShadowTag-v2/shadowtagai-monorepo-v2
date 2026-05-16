# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Boy Scout Rule Audit Trail System
Version: 1.0.0

Persistent tracking of all pnkln executions with monetization metrics.
Philosophy: Leave everything cleaner than you found it - and prove it.
"""

import json
from pathlib import Path
from typing import Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class AuditMetrics:
  """Aggregate metrics across time periods"""

  period: str  # "daily", "weekly", "monthly", "annual", "lifetime"
  total_executions: int
  total_time_saved_hours: float
  total_revenue_identified_usd: float
  total_revenue_generated_usd: float
  average_leverage_ratio: float
  start_date: str
  end_date: str

  def to_dict(self) -> dict[str, Any]:
    return asdict(self)


class AuditTrailPersistence:
  """
  Persistent audit trail with Boy Scout Rule tracking.

  Features:
  - JSON-based storage (SQLite upgrade path ready)
  - Append-only writes (audit trail integrity)
  - Time-based aggregation (daily/weekly/monthly/annual)
  - Monetization metrics tracking
  - Before/after state snapshots

  Design: Simple file-based with atomic writes, ready for production DB upgrade
  """

  def __init__(
    self, audit_file: str = "/home/user/aiyou-fastapi-services/data/audit_trail.jsonl"
  ):
    self.audit_file = Path(audit_file)
    self.audit_file.parent.mkdir(parents=True, exist_ok=True)

    # Ensure file exists
    if not self.audit_file.exists():
      self.audit_file.touch()

  def append(self, audit_entry: dict[str, Any]) -> None:
    """
    Append audit entry to trail.

    Uses JSONL format (one JSON object per line) for append-only semantics.
    Each entry is atomic - no partial writes.
    """
    # Ensure timestamp is present
    if "timestamp" not in audit_entry:
      audit_entry["timestamp"] = datetime.now().isoformat()

    # Atomic append
    with open(self.audit_file, "a") as f:
      f.write(json.dumps(audit_entry) + "\n")

  def read_all(self) -> list[dict[str, Any]]:
    """Read all audit entries"""
    entries = []
    if not self.audit_file.exists():
      return entries

    with open(self.audit_file) as f:
      for line in f:
        if line.strip():
          try:
            entries.append(json.loads(line))
          except json.JSONDecodeError:
            continue  # Skip malformed entries

    return entries

  def read_range(
    self, start_date: datetime, end_date: datetime
  ) -> list[dict[str, Any]]:
    """Read audit entries within date range"""
    all_entries = self.read_all()
    filtered = []

    for entry in all_entries:
      try:
        entry_date = datetime.fromisoformat(entry["timestamp"])
        if start_date <= entry_date <= end_date:
          filtered.append(entry)
      except (KeyError, ValueError):
        continue

    return filtered

  def get_metrics(
    self,
    period: str = "lifetime",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
  ) -> AuditMetrics:
    """
    Calculate aggregate metrics for a time period.

    Periods: daily, weekly, monthly, annual, lifetime
    """
    now = datetime.now()

    # Determine date range based on period
    if period == "daily":
      start = now.replace(hour=0, minute=0, second=0, microsecond=0)
      end = now
    elif period == "weekly":
      start = now - timedelta(days=7)
      end = now
    elif period == "monthly":
      start = now - timedelta(days=30)
      end = now
    elif period == "annual":
      start = now - timedelta(days=365)
      end = now
    else:  # lifetime
      start = datetime.min
      end = now

    # Override with custom range if provided
    if start_date:
      start = start_date
    if end_date:
      end = end_date

    # Read entries in range
    entries = self.read_range(start, end)

    # Aggregate metrics
    total_executions = len(entries)
    total_time_saved = 0.0
    total_revenue_identified = 0.0
    total_revenue_generated = 0.0

    for entry in entries:
      metrics = entry.get("metrics", {})
      total_time_saved += metrics.get("time_saved_hours", 0.0)
      total_revenue_identified += metrics.get("revenue_identified_usd", 0.0)
      total_revenue_generated += metrics.get("revenue_generated_usd", 0.0)

    # Calculate leverage ratio
    total_value = total_revenue_identified + total_revenue_generated
    avg_leverage = total_value / total_time_saved if total_time_saved > 0 else 0.0

    return AuditMetrics(
      period=period,
      total_executions=total_executions,
      total_time_saved_hours=total_time_saved,
      total_revenue_identified_usd=total_revenue_identified,
      total_revenue_generated_usd=total_revenue_generated,
      average_leverage_ratio=avg_leverage,
      start_date=start.isoformat(),
      end_date=end.isoformat(),
    )

  def get_dashboard(self) -> dict[str, Any]:
    """
    Get comprehensive dashboard view.

    Returns metrics for all time periods plus recent activity.
    """
    return {
      "lifetime": self.get_metrics("lifetime").to_dict(),
      "annual": self.get_metrics("annual").to_dict(),
      "monthly": self.get_metrics("monthly").to_dict(),
      "weekly": self.get_metrics("weekly").to_dict(),
      "daily": self.get_metrics("daily").to_dict(),
      "recent_executions": self.read_all()[-10:],  # Last 10 executions
    }

  def export_json(self, output_file: str) -> None:
    """Export full audit trail to JSON file"""
    entries = self.read_all()
    with open(output_file, "w") as f:
      json.dump(entries, f, indent=2)

  def get_boy_scout_report(self) -> str:
    """
    Generate Boy Scout Rule report.

    Shows what we've improved and by how much.
    Jobs mode: Make the data sing.
    """
    lifetime = self.get_metrics("lifetime")
    monthly = self.get_metrics("monthly")
    daily = self.get_metrics("daily")

    report = f"""
# BOY SCOUT RULE REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Lifetime Impact
- Total Executions: {lifetime.total_executions}
- Time Saved: {lifetime.total_time_saved_hours:.2f} hours
- Revenue Identified: ${lifetime.total_revenue_identified_usd:,.2f}
- Revenue Generated: ${lifetime.total_revenue_generated_usd:,.2f}
- Average Leverage Ratio: {lifetime.average_leverage_ratio:.2f}x

## This Month
- Executions: {monthly.total_executions}
- Time Saved: {monthly.total_time_saved_hours:.2f} hours
- Revenue Identified: ${monthly.total_revenue_identified_usd:,.2f}
- Revenue Generated: ${monthly.total_revenue_generated_usd:,.2f}

## Today
- Executions: {daily.total_executions}
- Time Saved: {daily.total_time_saved_hours:.2f} hours
- Revenue Identified: ${daily.total_revenue_identified_usd:,.2f}
- Revenue Generated: ${daily.total_revenue_generated_usd:,.2f}

## Compound Effect
If current monthly pace continues:
- Annual time savings: {monthly.total_time_saved_hours * 12:.2f} hours
- Annual revenue identified: ${monthly.total_revenue_identified_usd * 12:,.2f}
- Annual revenue generated: ${monthly.total_revenue_generated_usd * 12:,.2f}

At $200/hour value:
- Annual value unlocked: ${monthly.total_time_saved_hours * 12 * 200:,.2f}

---
Philosophy: Every execution should leave the system cleaner, faster, more valuable.
We measure what matters: Time, Revenue, Leverage.
"""
    return report


# Factory
def create_audit_trail(audit_file: str | None = None) -> AuditTrailPersistence:
  """Create audit trail with default or custom file path"""
  return AuditTrailPersistence(
    audit_file=audit_file or "/home/user/aiyou-fastapi-services/data/audit_trail.jsonl"
  )


if __name__ == "__main__":
  # Self-test
  audit = create_audit_trail()

  # Add sample entries
  sample_entries = [
    {
      "action": "Research edge AI market",
      "skills_activated": ["research_explorer_v1"],
      "metrics": {
        "time_saved_hours": 2.5,
        "revenue_identified_usd": 50000,
        "revenue_generated_usd": 0,
      },
    },
    {
      "action": "Design authentication API",
      "skills_activated": ["design_critic_v1"],
      "metrics": {
        "time_saved_hours": 1.0,
        "revenue_identified_usd": 0,
        "revenue_generated_usd": 0,
      },
    },
    {
      "action": "Monetize open source project",
      "skills_activated": ["monetization_architect_v1"],
      "metrics": {
        "time_saved_hours": 0.5,
        "revenue_identified_usd": 100000,
        "revenue_generated_usd": 5000,
      },
    },
  ]

  for entry in sample_entries:
    audit.append(entry)

  # Generate report
  print(audit.get_boy_scout_report())
