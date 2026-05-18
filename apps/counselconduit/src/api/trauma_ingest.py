# Copyright 2026 ShadowTag AI — All Rights Reserved.
# trauma_ingest.py — AST-grep & Prompt Repetition Layer
"""
Trauma Ingest — AST-Grep Pattern Matching + Prompt Repetition Boost

Uses ast-grep structural patterns to detect dangerous code constructs
before they enter the CounselConduit pipeline. Implements the arXiv:2512.14982
prompt repetition accuracy boost for non-reasoning model calls.
"""

import logging
import re
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ─── Dangerous Patterns (AST-grep YAML rules) ─────────────────────

DANGEROUS_PATTERNS = [
  {
    "id": "eval_injection",
    "language": "python",
    "pattern": "eval($$$)",
    "severity": "critical",
    "message": "eval() detected — potential code injection vector",
  },
  {
    "id": "exec_injection",
    "language": "python",
    "pattern": "exec($$$)",
    "severity": "critical",
    "message": "exec() detected — potential code injection vector",
  },
  {
    "id": "sql_format_string",
    "language": "python",
    "pattern": 'f"$$$SELECT$$$"',
    "severity": "high",
    "message": "f-string SQL detected — use parameterized queries",
  },
  {
    "id": "subprocess_shell",
    "language": "python",
    "pattern": "subprocess.run($$$, shell=True, $$$)",
    "severity": "high",
    "message": "shell=True in subprocess — command injection risk",
  },
  {
    "id": "hardcoded_secret",
    "language": "python",
    "pattern": '$KEY = "$$$"',
    "severity": "critical",
    "message": "Potential hardcoded secret — use Secret Manager",
  },
]

# ─── Regex-based fallback for environments without ast-grep ────────

REGEX_PATTERNS = [
  (re.compile(r"\beval\s*\("), "eval() call detected"),
  (re.compile(r"\bexec\s*\("), "exec() call detected"),
  (re.compile(r"subprocess\..*shell\s*=\s*True"), "shell=True subprocess"),
  (
    re.compile(r'(?i)(api[_-]?key|secret|password|token)\s*=\s*["\'][^"\']+["\']'),
    "Hardcoded secret",
  ),
  (re.compile(r"rm\s+-rf\s+/"), "Destructive rm -rf command"),
]


@dataclass
class IngestResult:
  """Result of trauma ingestion scan."""

  clean: bool
  findings: list[dict]
  scan_method: str  # "ast-grep" or "regex-fallback"


def scan_with_ast_grep(file_path: str) -> list[dict]:
  """Run ast-grep scan on a file. Returns findings list."""
  findings = []
  try:
    result = subprocess.run(
      ["sg", "scan", "--json", file_path],
      capture_output=True,
      text=True,
      timeout=30,
    )
    if result.returncode == 0 and result.stdout.strip():
      import json

      matches = json.loads(result.stdout)
      for match in matches:
        findings.append(
          {
            "rule": match.get("ruleId", "unknown"),
            "file": file_path,
            "line": match.get("range", {}).get("start", {}).get("line", 0),
            "message": match.get("message", "AST pattern match"),
            "severity": match.get("severity", "warning"),
          }
        )
  except FileNotFoundError:
    logger.debug("ast-grep (sg) not found — falling back to regex")
    return []
  except subprocess.TimeoutExpired:
    logger.warning("ast-grep timed out on %s", file_path)
    return []
  return findings


def scan_with_regex(content: str, file_path: str = "<stdin>") -> list[dict]:
  """Regex fallback scanner for environments without ast-grep."""
  findings = []
  for line_num, line in enumerate(content.splitlines(), 1):
    for pattern, message in REGEX_PATTERNS:
      if pattern.search(line):
        findings.append(
          {
            "rule": "regex-fallback",
            "file": file_path,
            "line": line_num,
            "message": message,
            "severity": "warning",
            "matched_text": line.strip()[:80],
          }
        )
  return findings


def ingest(file_path: str, content: str | None = None) -> IngestResult:
  """
  Scan a file for dangerous patterns.
  Tries ast-grep first, falls back to regex.
  """
  # Try ast-grep first
  findings = scan_with_ast_grep(file_path)
  if findings:
    return IngestResult(
      clean=len(findings) == 0, findings=findings, scan_method="ast-grep"
    )

  # Regex fallback
  if content is None:
    try:
      with open(file_path) as f:
        content = f.read()
    except OSError as e:
      logger.error("Cannot read %s: %s", file_path, e)
      return IngestResult(clean=True, findings=[], scan_method="error")

  findings = scan_with_regex(content, file_path)
  return IngestResult(
    clean=len(findings) == 0, findings=findings, scan_method="regex-fallback"
  )


# ─── Prompt Repetition Boost (arXiv:2512.14982) ───────────────────


def apply_prompt_repetition(prompt: str, *, repetitions: int = 2) -> str:
  """
  Apply prompt repetition for non-reasoning models.
  arXiv:2512.14982 shows 2x repetition boosts accuracy
  without invoking slow reasoning loops.

  IMPORTANT: Do NOT apply to thinking/reasoning models
  (gemini-*-thinking, o1, claude-*-thinking).
  """
  if repetitions < 1:
    return prompt
  return "\n\n".join([prompt] * repetitions)
