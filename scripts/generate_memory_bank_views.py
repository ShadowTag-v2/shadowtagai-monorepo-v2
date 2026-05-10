from pathlib import Path

from service.app.adapters.authority_state import AuthorityState
from service.app.config import load_settings

s = load_settings()
authority = AuthorityState(s.authority_state_path).read()

base = Path(".agent/memory")
(base / "patterns").mkdir(parents=True, exist_ok=True)

(base / "project-brief.md").write_text(
  "# Project Brief\n\nAuthority memory is canonical. Codebase is secondary context.\n",
  encoding="utf-8",
)

(base / "product-vision.md").write_text(
  "# Product Vision\n\nWake up current, stay current, and upgrade code from memory-first truth.\n",
  encoding="utf-8",
)

(base / "context.md").write_text(
  f"# Context\n\nStartup contract: {authority.get('startup_contract', {})}\n\nSettings: {authority.get('settings', {})}\n",
  encoding="utf-8",
)

(base / "architecture.md").write_text(
  "# Architecture\n\n"
  "Truth hierarchy:\n"
  "1. authority-current.json\n"
  "2. authority snapshots + atoms\n"
  "3. tasks + drift\n"
  "4. memory bank generated views\n"
  "5. summaries + journal\n"
  "6. code graph + retrieval\n"
  "7. raw codebase\n",
  encoding="utf-8",
)

(base / "tech-stack.md").write_text(
  "# Tech Stack\n\n- Postgres\n- JSONL\n- LanceDB\n- SQLite\n- FastAPI\n- ANE-first runtime\n",
  encoding="utf-8",
)

(base / "patterns" / "common-tasks.md").write_text(
  "# Common Tasks\n\n## Session bootstrap\nGET /api/hydrate-pack before any substantial reasoning.\n",
  encoding="utf-8",
)
