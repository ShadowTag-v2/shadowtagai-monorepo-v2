# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cinematic Verification Pipeline — Browser-based Lighthouse + screenshot audit."""

import json
import subprocess
import sys
from pathlib import Path


SITES = [
  {"name": "kovelai", "url": "https://kovelai.web.app"},
  {"name": "shadowtagai", "url": "https://shadowtagai.web.app"},
  {"name": "shadowtag-omega-v4", "url": "https://shadowtag-omega-v4.web.app"},
]

THRESHOLDS = {
  "performance": 90,
  "accessibility": 95,
  "best-practices": 95,
  "seo": 95,
}


def run_lighthouse(url: str, output_dir: Path) -> dict:
  """Run Lighthouse CI and return scores."""
  output_path = (
    output_dir / f"lighthouse-{url.replace('https://', '').replace('/', '_')}.json"
  )
  cmd = [
    "npx",
    "-y",
    "lighthouse",
    url,
    "--output=json",
    f"--output-path={output_path}",
    "--chrome-flags=--headless --no-sandbox",
    "--quiet",
  ]
  try:
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    with open(output_path) as f:
      report = json.load(f)
    return {
      cat: int(report["categories"][cat]["score"] * 100)
      for cat in THRESHOLDS
      if cat in report.get("categories", {})
    }
  except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
    return {"error": str(e)}


def verify_all(output_dir: str = "/tmp/lighthouse-reports") -> bool:
  """Verify all sites meet thresholds."""
  out = Path(output_dir)
  out.mkdir(parents=True, exist_ok=True)
  all_pass = True
  for site in SITES:
    scores = run_lighthouse(site["url"], out)
    if "error" in scores:
      print(f"❌ {site['name']}: {scores['error']}")
      all_pass = False
      continue
    for category, threshold in THRESHOLDS.items():
      score = scores.get(category, 0)
      status = "✅" if score >= threshold else "❌"
      print(f"{status} {site['name']} {category}: {score}/{threshold}")
      if score < threshold:
        all_pass = False
  return all_pass


if __name__ == "__main__":
  success = verify_all()
  sys.exit(0 if success else 1)
