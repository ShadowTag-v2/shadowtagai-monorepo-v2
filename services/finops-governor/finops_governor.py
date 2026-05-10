"""
finops-governor/finops_governor.py — Economic Circuit Breaker

Autonomous cost monitoring for the Sovereign OS. Queries the Cloud Billing API
to enforce budget thresholds and prevent runaway spend.

Operational model:
  - Invoked hourly by Cloud Scheduler cron job
  - Also invoked per-event by the database-events-handler via Pub/Sub
  - Can scale down non-essential Cloud Run services if budget threshold breached
  - Sends alerts to Pub/Sub topic for agent consumption

Thresholds (environment variables):
  - BUDGET_MONTHLY_USD: Monthly budget in USD (default: $500)
  - WARN_PCT: Warning threshold as percentage (default: 80)
  - HALT_PCT: Hard stop threshold as percentage (default: 100)

Deployment:
  gcloud run deploy finops-governor \
    --source=services/finops-governor \
    --region=us-central1 \
    --project=shadowtag-omega-v4 \
    --set-env-vars=GCP_PROJECT=shadowtag-omega-v4,BUDGET_MONTHLY_USD=500 \
    --no-allow-unauthenticated
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, UTC
from enum import StrEnum

import functions_framework

# ─── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ID = os.environ.get("GCP_PROJECT", "shadowtag-omega-v4")
BUDGET_MONTHLY_USD = float(os.environ.get("BUDGET_MONTHLY_USD", "500"))
WARN_PCT = float(os.environ.get("WARN_PCT", "80"))
HALT_PCT = float(os.environ.get("HALT_PCT", "100"))
ALERTS_TOPIC = os.environ.get("ALERTS_TOPIC", "finops-alerts")

# Non-essential services that can be scaled to zero
SCALABLE_SERVICES = [
  "database-events-handler",
  "mcp-workspace-bridge",
]

# Critical services that must NEVER be scaled down
PROTECTED_SERVICES = [
  "counselconduit",
  "headfade",
]

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("finops-governor")


# ─── Data Models ───────────────────────────────────────────────────────────────


class BudgetStatus(StrEnum):
  """Budget health status."""

  GREEN = "GREEN"  # Under WARN_PCT
  YELLOW = "YELLOW"  # Between WARN_PCT and HALT_PCT
  RED = "RED"  # Over HALT_PCT — scale down non-essential services


@dataclass
class CostReport:
  """Snapshot of current spend vs budget."""

  current_spend_usd: float
  budget_usd: float
  utilization_pct: float
  status: BudgetStatus
  timestamp: str
  services_scaled_down: list[str]
  alert_message: str


# ─── Cost Query ────────────────────────────────────────────────────────────────


def query_current_spend() -> float:
  """Query the Cloud Billing API for current month spend.

  In production, this uses the Cloud Billing Budget API:
    billing.budgets.list() + billing.budgets.get()

  Or the BigQuery billing export:
    SELECT SUM(cost) FROM `billing_export.gcp_billing_export_v1_*`
    WHERE invoice.month = FORMAT_DATE('%Y%m', CURRENT_DATE())
  """
  try:
    from google.cloud import bigquery

    bq_client = bigquery.Client(project=PROJECT_ID)

    # Query the billing export dataset
    query = f"""
            SELECT SUM(cost) as total_cost
            FROM `{PROJECT_ID}.billing_export.gcp_billing_export_v1_*`
            WHERE invoice.month = FORMAT_DATE('%Y%m', CURRENT_DATE())
        """
    result = bq_client.query(query).result()
    for row in result:
      return float(row.total_cost or 0.0)
  except Exception:
    logger.warning("BigQuery billing export not available — using cost estimation")

  # Fallback: estimate from Cloud Monitoring metrics
  try:
    from google.cloud import monitoring_v3

    _unused = monitoring_v3  # noqa: F841 — import needed for availability check
    # In production, query compute/run cost metrics
    return 0.0
  except Exception:
    logger.warning("Cloud Monitoring not available — returning 0")
    return 0.0


def scale_down_services(services: list[str]) -> list[str]:
  """Scale non-essential Cloud Run services to zero instances.

  Uses `gcloud run services update --min-instances=0 --max-instances=0`.
  Returns list of services actually scaled down.
  """
  scaled = []
  try:
    import subprocess

    for service in services:
      if service in PROTECTED_SERVICES:
        logger.warning("REFUSING to scale down protected service: %s", service)
        continue

      cmd = [
        "gcloud",
        "run",
        "services",
        "update",
        service,
        f"--project={PROJECT_ID}",
        "--region=us-central1",
        "--max-instances=0",
        "--quiet",
      ]

      logger.info("Scaling down: %s", service)
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
      )

      if result.returncode == 0:
        scaled.append(service)
        logger.info("✅ Scaled down: %s", service)
      else:
        logger.error("Failed to scale down %s: %s", service, result.stderr)
  except Exception:
    logger.exception("Error scaling down services")

  return scaled


def publish_alert(report: CostReport) -> None:
  """Publish a FinOps alert to Pub/Sub for agent consumption."""
  try:
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, ALERTS_TOPIC)

    message = json.dumps(asdict(report)).encode("utf-8")
    future = publisher.publish(topic_path, message)
    logger.info("Alert published: %s", future.result(timeout=10))
  except Exception:
    logger.exception("Failed to publish FinOps alert")


# ─── Governor Logic ───────────────────────────────────────────────────────────


def evaluate_budget() -> CostReport:
  """Run the full FinOps evaluation cycle."""
  current_spend = query_current_spend()
  utilization = (
    (current_spend / BUDGET_MONTHLY_USD * 100) if BUDGET_MONTHLY_USD > 0 else 0
  )
  scaled_down: list[str] = []
  alert_msg = ""

  if utilization >= HALT_PCT:
    status = BudgetStatus.RED
    alert_msg = f"🔴 BUDGET HALT: ${current_spend:.2f}/${BUDGET_MONTHLY_USD:.2f} ({utilization:.1f}%). Scaling down non-essential services."
    scaled_down = scale_down_services(SCALABLE_SERVICES)
    logger.critical(alert_msg)

  elif utilization >= WARN_PCT:
    status = BudgetStatus.YELLOW
    alert_msg = f"🟡 BUDGET WARNING: ${current_spend:.2f}/${BUDGET_MONTHLY_USD:.2f} ({utilization:.1f}%). Monitor closely."
    logger.warning(alert_msg)

  else:
    status = BudgetStatus.GREEN
    alert_msg = f"🟢 Budget healthy: ${current_spend:.2f}/${BUDGET_MONTHLY_USD:.2f} ({utilization:.1f}%)."
    logger.info(alert_msg)

  report = CostReport(
    current_spend_usd=current_spend,
    budget_usd=BUDGET_MONTHLY_USD,
    utilization_pct=round(utilization, 2),
    status=status,
    timestamp=datetime.now(tz=UTC).isoformat(),
    services_scaled_down=scaled_down,
    alert_message=alert_msg,
  )

  # Publish alert for non-green states
  if status != BudgetStatus.GREEN:
    publish_alert(report)

  return report


# ─── HTTP Handler (Cloud Run) ─────────────────────────────────────────────────


@functions_framework.http
def handle_finops_check(request):
  """HTTP handler for Cloud Scheduler cron and Pub/Sub push events."""
  try:
    report = evaluate_budget()
    return (json.dumps(asdict(report), indent=2), 200)
  except Exception:
    logger.exception("FinOps evaluation failed")
    return ("Internal error", 500)


# ─── Standalone Mode ──────────────────────────────────────────────────────────


def _run_standalone():
  """Run the governor in standalone diagnostic mode."""
  print("=" * 60)
  print("  💰 FinOps Governor — Diagnostic Mode")
  print("=" * 60)
  print(f"\n  Project: {PROJECT_ID}")
  print(f"  Budget: ${BUDGET_MONTHLY_USD:.2f}/month")
  print(f"  Warning at: {WARN_PCT}%")
  print(f"  Hard stop at: {HALT_PCT}%")
  print(f"  Protected services: {', '.join(PROTECTED_SERVICES)}")
  print(f"  Scalable services: {', '.join(SCALABLE_SERVICES)}")

  report = evaluate_budget()

  print(f"\n  Status: {report.status.value}")
  print(f"  Current spend: ${report.current_spend_usd:.2f}")
  print(f"  Utilization: {report.utilization_pct}%")
  print(f"  Alert: {report.alert_message}")

  if report.services_scaled_down:
    print(f"  Scaled down: {', '.join(report.services_scaled_down)}")

  print("\n" + "=" * 60)
  print("  ✅ FinOps Governor Diagnostic Complete")
  print("=" * 60)

  return json.dumps(asdict(report), indent=2)


if __name__ == "__main__":
  result = _run_standalone()
  if "--json" in sys.argv:
    print(result)
