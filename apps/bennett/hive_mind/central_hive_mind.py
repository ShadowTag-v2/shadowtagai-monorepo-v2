"""Bennett Central Hive Mind — Asymmetric Compute Engine.

The Vanguard move for consumer commerce:
  1. Pool subscription revenue from N users.
  2. Run ONE monstrously powerful trend discovery engine (O(1) cost).
  3. Distribute the output to N households (O(N) revenue).
  4. Collect keep/return outcomes as proprietary taste intelligence.

This reverses the fatal AI startup compute death spiral:
  Naive: N users × expensive-LLM-per-user = margin destruction
  Bennett: 1 Gemini run × $X = $1.49M/mo distributed to 10,000 users

Runs as a Cloud Run Job (4× daily via Cloud Scheduler).
Never runs LLMs on the consumer's phone.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import requests
import stripe
from google import genai
from google.cloud import bigquery

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [HIVE] %(levelname)s %(message)s",
)
log = logging.getLogger("bennett.hive_mind")

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
bq = bigquery.Client()
ai = genai.Client()

SHIELD_URL = os.environ.get(
  "SHIELD_URL", "http://internal-go-shield/api/v1/evaluate/human"
)
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")

TREND_VELOCITY_THRESHOLD = 85  # TVI score above which we act


@dataclass
class TrendThesis:
  name: str
  category: str
  estimated_cost_usd: float
  demographic_target: str
  supplier_sku: str
  tvi_score: int
  compliance_cleared: bool = False


def analyze_global_zeitgeist() -> TrendThesis:
  """Step 1 — The O(1) Heavy Lift.

  One massive context window ingests the global OSINT exhaust
  (scraped by the Jetski fleet and dropped to GCS by the prior pipeline).
  Cost: ~$0.50 per run. Revenue distributed: $1.49M/mo.

  Returns exactly one trend thesis above the TVI threshold.
  """
  log.info("Waking Hive Mind. Ingesting OSINT payload…")

  # In production: load from GCS bucket written by the Jetski fleet
  # osint_payload = load_osint_from_gcs()
  osint_payload = "PLACEHOLDER: loaded from gs://pnkln-jetski-drops/latest.json"

  prompt = f"""
You are the Bennett Trend Oracle. Analyze the aggregated global OSINT data below
(TikTok velocity, Shenzhen factory manifests, underground fashion nodes, creator graphs).

Identify exactly ONE hyper-emerging consumer trend with a Trend Velocity Index (TVI) > {TREND_VELOCITY_THRESHOLD}.
The trend must be real, sourceable, and pre-peak — not already mainstream.

OSINT DATA:
{osint_payload}

Output MUST be valid JSON matching this schema exactly:
{{
    "name": "string — trend name",
    "category": "string — fashion|tech|travel|entertainment|beauty|home",
    "estimated_cost_usd": float,
    "demographic_target": "string",
    "supplier_sku": "string — Alibaba/1688 SKU or travel identifier",
    "tvi_score": integer
}}
"""
  response = ai.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=prompt,
    config={"response_mime_type": "application/json"},
  )

  raw = json.loads(response.text)
  thesis = TrendThesis(**raw)
  log.info(
    "Trend thesis: %s (TVI=%d, cost=$%.2f)",
    thesis.name,
    thesis.tvi_score,
    thesis.estimated_cost_usd,
  )
  return thesis


def filter_through_sentinel(thesis: TrendThesis) -> bool:
  """Step 2 — The Brakes.

  Before purchasing for 10,000 households, the trend must clear
  the Go sentinel (ATP 5-19 matrix). Checks include:
  - CA AADC (no minor-targeted items)
  - Supply chain / UFLPA (no sanctioned factory)
  - CA SB 343 / forced labor
  - Consumer safety

  The Go binary evaluates in <2ms. If it returns anything other than
  HTTP 200 CLEARED, the cycle terminates and nothing is purchased.
  """
  log.info("Passing thesis through Sentinel Shield…")
  try:
    resp = requests.post(
      SHIELD_URL,
      json={
        "event_id": f"hive-{int(time.time())}",
        "actor_id": "SYSTEM_BENNETT_MACRO",
        "content": json.dumps(
          {
            "trend": thesis.name,
            "category": thesis.category,
            "sku": thesis.supplier_sku,
            "cost": thesis.estimated_cost_usd,
          },
        ),
      },
      timeout=3.0,
    )
    if resp.status_code == 200:
      thesis.compliance_cleared = True
      log.info("Shield: CLEARED")
      return True
    log.warning("Shield rejected trend: %s (HTTP %d)", thesis.name, resp.status_code)
    return False
  except Exception as exc:
    log.error("Shield unreachable: %s — aborting cycle", exc)
    return False


def execute_syndicate_allocation(thesis: TrendThesis) -> dict[str, Any]:
  """Step 3 — The O(N) Revenue Distribution.

  ONE BigQuery query replaces running expensive LLMs for every user.
  A sub-penny SQL op matches the trend against 10,000 preference vectors.
  Stripe charges are fire-and-forget per eligible household.
  """
  log.info("Allocating trend to Syndicate…")

  query = f"""
        SELECT user_id, stripe_customer_id, remaining_budget, notify_email
        FROM `{PROJECT_ID}.syndicate.active_users`
        WHERE @category IN UNNEST(opt_in_categories)
        AND remaining_budget >= @cost
        AND account_status = 'ACTIVE'
        LIMIT 10000
    """

  job_config = bigquery.QueryJobConfig(
    query_parameters=[
      bigquery.ScalarQueryParameter("category", "STRING", thesis.category),
      bigquery.ScalarQueryParameter("cost", "FLOAT64", thesis.estimated_cost_usd),
    ],
  )

  rows = list(bq.query(query, job_config=job_config).result())
  log.info("Eligible households: %d", len(rows))

  charged = 0
  skipped = 0
  for row in rows:
    try:
      stripe.Charge.create(
        amount=int(thesis.estimated_cost_usd * 100),
        currency="usd",
        customer=row.stripe_customer_id,
        description=f"Bennett Vanguard Box: {thesis.name}",
        metadata={
          "trend": thesis.name,
          "category": thesis.category,
          "sku": thesis.supplier_sku,
          "tvi": str(thesis.tvi_score),
        },
      )
      charged += 1
    except stripe.error.CardError:
      skipped += 1
    except stripe.error.StripeError as exc:
      log.error("Stripe error for %s: %s", row.user_id, exc)
      skipped += 1

  gross = charged * thesis.estimated_cost_usd
  log.info(
    "Allocation complete — charged=%d skipped=%d gross=$%.2f", charged, skipped, gross
  )
  return {
    "charged": charged,
    "skipped": skipped,
    "gross_usd": gross,
    "trend": thesis.name,
  }


def run() -> None:
  """Entry point for Cloud Run Job execution."""
  thesis = analyze_global_zeitgeist()

  if thesis.tvi_score < TREND_VELOCITY_THRESHOLD:
    log.info(
      "TVI=%d below threshold=%d — no action",
      thesis.tvi_score,
      TREND_VELOCITY_THRESHOLD,
    )
    return

  if not filter_through_sentinel(thesis):
    log.warning("Trend failed compliance — cycle terminated cleanly")
    return

  result = execute_syndicate_allocation(thesis)
  log.info("Hive cycle complete: %s", json.dumps(result))


if __name__ == "__main__":
  run()
