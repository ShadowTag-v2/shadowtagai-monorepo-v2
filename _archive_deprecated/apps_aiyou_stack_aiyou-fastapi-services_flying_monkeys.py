"""
n-autoresearch/Kosmos/BioAgents Service.QA~~~~~~~~~~~~~~

Simulates load generation (Chaos Engineering) for testing purposes.
"""

import asyncio
import json
import logging
import os
import random
from datetime import datetime

import httpx
from fastapi import FastAPI

try:
  from google.cloud import storage
except ImportError:
  storage = None
try:
  from playwright.async_api import async_playwright
except ImportError:
  async_playwright = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("n-autoresearch/Kosmos/BioAgents")


async def release_monkeys(
  target_url: str,
  instances: int = 10,
  chaos_mode: bool = False,
  burst_mode: bool = False,
  reporting: bool = False,
) -> None:
  """
  Simulate latency load on a target URL.

  Args:
      target_url: The URL to target.
      instances: Number of simulated instances.
      chaos_mode: Enable chaos injection (malformed headers/payloads).
      burst_mode: Enable burst mode (simultaneous requests).
      reporting: Enable saving run results to a JSON file.
  """
  if instances <= 0:
    logger.info(
      f"🐵 [n-autoresearch/Kosmos/BioAgents] No instances requested for {target_url}."
    )
    return

  logger.info(
    f"🐵 [n-autoresearch/Kosmos/BioAgents] Spawning {instances} Antigravity instances targeting {target_url}..."
  )
  results = []
  async with httpx.AsyncClient() as client:

    async def _attack(i: int) -> dict:
      try:
        method = "GET"
        headers = {}
        content = None
        request_url = target_url
        status_code = 0

        if chaos_mode and random.random() < 0.3:
          roll = random.choice(["header", "post", "method", "fuzz"])
          if roll == "header":
            # Inject massive header to test buffer limits
            headers = {
              "X-Chaos-Monkey": "🙈" * 500,
              "Content-Type": "application/x-chaos",
            }
          elif roll == "post":
            method = "POST"
            content = b"\x00\xff" * 100  # Garbage binary payload
          elif roll == "method":
            method = "PUT"
          elif roll == "fuzz":
            # Fuzzing: Mutate query parameters with chaos payload
            sep = "&" if "?" in request_url else "?"
            request_url = f"{request_url}{sep}chaos_fuzz=🐵&<script>alert(1)</script>"

        response = await client.request(
          method, request_url, headers=headers, content=content
        )
        latency = response.elapsed.total_seconds()
        status_code = response.status_code
        status = (
          f"Hit ({int(latency * 1000)}ms)"
          if response.status_code == 200
          else f"Miss ({response.status_code})"
        )
      except Exception as e:
        latency = 0.0
        status_code = -1
        status = f"Error ({e})"
      logger.info(f"   - Monkey-{i + 1}: {status} | Load applied.")
      return {
        "monkey_id": i + 1,
        "status": status,
        "status_code": status_code,
        "latency_sec": latency,
      }

    if burst_mode:
      logger.info(
        "🔥 [n-autoresearch/Kosmos/BioAgents] Burst mode engaged! Releasing all n-autoresearch/Kosmos/BioAgents simultaneously."
      )
      results = await asyncio.gather(*[_attack(i) for i in range(instances)])
    else:
      for i in range(instances):
        results.append(await _attack(i))

  latencies = [r["latency_sec"] for r in results]
  avg = sum(latencies) / len(latencies)
  logger.info(
    f"🐵 [n-autoresearch/Kosmos/BioAgents] Swarm complete. Avg Latency: {avg * 1000:.2f}ms"
  )

  if reporting:
    report_filename = f"chaos_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    report_data = {
      "target_url": target_url,
      "run_summary": {"instances": instances, "avg_latency_ms": avg * 1000},
      "results": results,
    }

    # Check for GCS bucket config for cloud-native reporting
    gcs_bucket_name = os.environ.get("GCS_BUCKET_NAME")
    if gcs_bucket_name and storage:
      try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket_name)
        blob = bucket.blob(report_filename)
        blob.upload_from_string(
          json.dumps(report_data, indent=2),
          content_type="application/json",
        )
        gcs_path = f"gs://{gcs_bucket_name}/{report_filename}"
        logger.info(
          f"📊 [n-autoresearch/Kosmos/BioAgents] Report uploaded to {gcs_path}"
        )
      except Exception as e:
        logger.error(f"🔥 [n-autoresearch/Kosmos/BioAgents] GCS upload failed: {e}")
        # Fallback to local file
        with open(report_filename, "w") as f:
          json.dump(report_data, f, indent=2)
        logger.info(
          f"📊 [n-autoresearch/Kosmos/BioAgents] Report saved locally as fallback: {report_filename}"
        )
    elif gcs_bucket_name and not storage:
      logger.warning(
        "⚠️ [n-autoresearch/Kosmos/BioAgents] GCS_BUCKET_NAME set but google-cloud-storage not installed."
      )
      with open(report_filename, "w") as f:
        json.dump(report_data, f, indent=2)
      logger.info(
        f"📊 [n-autoresearch/Kosmos/BioAgents] Report saved locally: {report_filename}"
      )
    else:
      with open(report_filename, "w") as f:
        json.dump(report_data, f, indent=2)
      logger.info(
        f"📊 [n-autoresearch/Kosmos/BioAgents] Report saved to {report_filename} (GCS_BUCKET_NAME not set)"
      )


async def capture_visual_evidence(target_url: str) -> str:
  """
  Captures visual evidence (screenshot) of the target using a headless browser.
  Bypasses simple curl/wget limitations by rendering full DOM.
  """
  if not async_playwright:
    logger.error(
      "❌ [n-autoresearch/Kosmos/BioAgents] Playwright not installed. Cannot capture evidence."
    )
    return "error_playwright_missing"

  logger.info(
    f"🦅 [n-autoresearch/Kosmos/BioAgents] Launching Headless Scout (Playwright) for {target_url}..."
  )
  async with async_playwright() as p:
    browser = await p.chromium.launch(
      headless=True,
      args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    )
    page = await browser.new_page()
    await page.goto(target_url)
    # Wait for network idle to ensure dynamic content loads
    await page.wait_for_load_state("networkidle")
    filename = f"evidence_{random.randint(10000, 99999)}.png"
    await page.screenshot(path=filename, full_page=True)
    await browser.close()
  logger.info(
    f"🦅 [n-autoresearch/Kosmos/BioAgents] Visual evidence secured: {filename}"
  )
  return filename


app = FastAPI()


@app.post("/auto_mode")
async def auto_mode(
  target_url: str,
  instances: int = 10,
  chaos_mode: bool = False,
  burst_mode: bool = False,
  reporting: bool = False,
) -> dict:
  """
  Trigger the monkey release in auto mode.

  Args:
      target_url: The target URL.
      instances: Number of instances.
      chaos_mode: Enable chaos injection (malformed headers/payloads).
      burst_mode: Enable burst mode (simultaneous requests).
      reporting: Enable saving run results to a JSON file.
  """
  await release_monkeys(
    target_url,
    instances,
    chaos_mode=chaos_mode,
    burst_mode=burst_mode,
    reporting=reporting,
  )
  return {
    "status": "Auto mode engaged",
    "chaos_mode": chaos_mode,
    "burst_mode": burst_mode,
    "reporting": reporting,
  }


@app.post("/deploy_scout")
async def deploy_scout(target_url: str) -> dict:
  """
  Deploy a headless browser scout to capture target content (Screenshot/PDF).
  """
  evidence_path = await capture_visual_evidence(target_url)
  return {"status": "Scout Mission Complete", "evidence": evidence_path}
