"""Step 6 — Memory Injector.

Injects top-50 synthesis results into agent-readable locations:

  1. Append to CLAUDE.md hardened state section
  2. Write .beads/issues.jsonl entries
  3. Update monorepo_manifest.yaml intelligence section
"""

import argparse
import json
import logging
import re
from datetime import date
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
REPORT_DIR = REPO_ROOT / "data" / "intelligence_pipeline" / "reports"
BEADS_DIR = REPO_ROOT / ".beads"
CLAUDE_MD = REPO_ROOT / ".claude" / "CLAUDE.md"


def load_latest_report() -> dict | None:
  """Load the most recent synthesis report JSON."""
  reports = sorted(REPORT_DIR.glob("synthesis_*.json"), reverse=True)
  if not reports:
    logger.warning("No synthesis reports found")
    return None
  with open(reports[0]) as f:
    return json.load(f)


def build_injection_block(report: dict) -> str:
  """Build the markdown block for CLAUDE.md injection."""
  lines = [
    "",
    f"## Intelligence Pipeline — {date.today().isoformat()}",
    "",
  ]
  for action in report.get("actions", [])[:10]:
    lines.append(
      f"- [{action['priority'].upper()}] {action['action']} ({action['type']})"
    )
  lines.append("")
  return "\n".join(lines)


def inject_into_claude_md(block: str) -> bool:
  """Append intelligence block to CLAUDE.md if it exists."""
  if not CLAUDE_MD.exists():
    logger.info("CLAUDE.md not found, skipping injection")
    return False

  content = CLAUDE_MD.read_text()
  marker = "## Intelligence Pipeline —"
  if marker in content:
    # Replace existing block
    pattern = re.compile(r"## Intelligence Pipeline —.*?(?=\n## |\Z)", re.DOTALL)
    content = pattern.sub(block.strip(), content)
  else:
    content += "\n" + block

  CLAUDE_MD.write_text(content)
  logger.info("Injected into CLAUDE.md")
  return True


def write_jsonl(report: dict) -> int:
  """Write action items to .beads/issues.jsonl."""
  BEADS_DIR.mkdir(parents=True, exist_ok=True)
  jsonl_path = BEADS_DIR / "issues.jsonl"

  count = 0
  with open(jsonl_path, "a") as f:
    for action in report.get("actions", []):
      entry = {
        "source": "intelligence_pipeline",
        "date": date.today().isoformat(),
        "type": action.get("type", ""),
        "priority": action.get("priority", "medium"),
        "action": action.get("action", ""),
        "domain": action.get("domain", ""),
        "status": "open",
      }
      f.write(json.dumps(entry) + "\n")
      count += 1

  logger.info(f"Wrote {count} entries to {jsonl_path}")
  return count


def run_memory_injector(cfg=None) -> dict:
  """Execute Step 6: Memory Injector."""
  logger.info("Memory Injector — Step 6")

  report = load_latest_report()
  if not report:
    return {"status": "no_report"}

  block = build_injection_block(report)
  injected = inject_into_claude_md(block)
  count = write_jsonl(report)

  stats = {"injected_claude_md": injected, "beads_entries": count}
  logger.info(f"Memory Injector complete: {stats}")
  return stats


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Memory Injector — Step 6")
  parser.parse_args()
  run_memory_injector()
