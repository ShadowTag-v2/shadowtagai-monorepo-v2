#!/usr/bin/env python3
"""
ShadowTag-v2 Autonomous Error Repair Engine
=====================================
Watches lint/test output, calls Gemini (primary) for fix, applies it,
re-runs checks, commits when green. Zero user approval required.

Provider matrix (swap via REPAIR_PROVIDER env var):
  gemini   → Gemini generative API  (GEMINI_API_KEY)   [DEFAULT]
  openai   → GPT-4o                 (OPENAI_API_KEY)   [future]
  claude   → claude-sonnet-4-6      (ANTHROPIC_API_KEY) [future]

Usage:
  # Run once against current lint/test failures:
  python scripts/auto_error_repair.py

  # Watch mode (re-runs on file change):
  python scripts/auto_error_repair.py --watch

  # Dry-run (print patches only, no writes):
  python scripts/auto_error_repair.py --dry-run

  # CI mode (non-zero exit on unresolved errors):
  python scripts/auto_error_repair.py --ci
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import NamedTuple

# ── Config ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_GEN_MODEL = os.getenv("GEMINI_GEN_MODEL", "gemini-3.1-pro")
REPAIR_PROVIDER = os.getenv("REPAIR_PROVIDER", "gemini")
MAX_ROUNDS = int(os.getenv("REPAIR_MAX_ROUNDS", "5"))
AUTO_COMMIT = os.getenv("REPAIR_AUTO_COMMIT", "1") == "1"

LINT_CMD = ["uv", "run", "ruff", "check", ".", "--output-format", "json"]
TYPE_CMD = ["uv", "run", "mypy", "--output=json", "."]
TEST_CMD = ["uv", "run", "pytest", "--tb=short", "-q", "--no-header"]
FMT_CMD  = ["uv", "run", "ruff", "format", "."]

# ── Types ─────────────────────────────────────────────────────────────────────

class Error(NamedTuple):
    file: str
    line: int
    col: int
    code: str
    message: str
    source: str  # "ruff" | "mypy" | "pytest"

# ── Linter / test runners ─────────────────────────────────────────────────────

def run_ruff() -> list[Error]:
    r = subprocess.run(LINT_CMD, capture_output=True, text=True, cwd=REPO_ROOT)
    errors: list[Error] = []
    try:
        items = json.loads(r.stdout or "[]")
        for item in items:
            errors.append(Error(
                file=item.get("filename", ""),
                line=item.get("location", {}).get("row", 0),
                col=item.get("location", {}).get("column", 0),
                code=item.get("code", ""),
                message=item.get("message", ""),
                source="ruff",
            ))
    except json.JSONDecodeError:
        pass
    return errors


def run_mypy() -> list[Error]:
    r = subprocess.run(TYPE_CMD, capture_output=True, text=True, cwd=REPO_ROOT)
    errors: list[Error] = []
    # mypy --output=json emits one JSON object per line
    for line in (r.stdout + r.stderr).splitlines():
        try:
            item = json.loads(line)
            if item.get("severity") == "error":
                errors.append(Error(
                    file=item.get("file", ""),
                    line=item.get("line", 0),
                    col=item.get("column", 0),
                    code=item.get("code", ""),
                    message=item.get("message", ""),
                    source="mypy",
                ))
        except json.JSONDecodeError:
            continue
    return errors


def run_tests() -> list[Error]:
    r = subprocess.run(TEST_CMD, capture_output=True, text=True, cwd=REPO_ROOT)
    errors: list[Error] = []
    if r.returncode == 0:
        return errors
    # Parse pytest short tb: "FAILED tests/foo.py::test_bar - AssertionError: ..."
    for line in r.stdout.splitlines():
        m = re.match(r"FAILED (.+?)::(.+?) - (.+)", line)
        if m:
            errors.append(Error(
                file=m.group(1),
                line=0,
                col=0,
                code="TEST_FAIL",
                message=f"{m.group(2)}: {m.group(3)}",
                source="pytest",
            ))
    return errors


def collect_errors() -> list[Error]:
    errs: list[Error] = []
    print("[repair] running ruff...", flush=True)
    errs += run_ruff()
    print("[repair] running mypy...", flush=True)
    errs += run_mypy()
    print("[repair] running pytest...", flush=True)
    errs += run_tests()
    return errs

# ── Provider: Gemini ──────────────────────────────────────────────────────────

def _gemini_generate(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_GEN_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 2048},
    }).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"]


# Future provider stubs:
# def _openai_generate(prompt: str) -> str:
#     import openai
#     client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#     r = client.chat.completions.create(
#         model="gpt-4o", messages=[{"role":"user","content":prompt}],
#         temperature=0, max_tokens=2048,
#     )
#     return r.choices[0].message.content or ""
#
# def _claude_generate(prompt: str) -> str:
#     import anthropic
#     client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#     msg = client.messages.create(
#         model="claude-sonnet-4-6", max_tokens=2048,
#         messages=[{"role":"user","content":prompt}],
#     )
#     return msg.content[0].text

def generate(prompt: str) -> str:
    if REPAIR_PROVIDER == "openai":
        raise NotImplementedError("Set REPAIR_PROVIDER=gemini or stub _openai_generate")
    if REPAIR_PROVIDER == "claude":
        raise NotImplementedError("Set REPAIR_PROVIDER=gemini or stub _claude_generate")
    return _gemini_generate(prompt)

# ── Patch builder ─────────────────────────────────────────────────────────────

def read_file_context(file_path: str, line: int, radius: int = 20) -> str:
    p = REPO_ROOT / file_path
    if not p.exists():
        return ""
    lines = p.read_text(errors="replace").splitlines()
    start = max(0, line - radius - 1)
    end = min(len(lines), line + radius)
    numbered = [f"{i+1}: {l}" for i, l in enumerate(lines[start:end], start=start)]
    return "\n".join(numbered)


def build_repair_prompt(errors: list[Error]) -> str:
    # Group by file
    by_file: dict[str, list[Error]] = {}
    for e in errors:
        by_file.setdefault(e.file, []).append(e)

    sections = []
    for file, file_errors in list(by_file.items())[:5]:  # cap at 5 files per round
        context = read_file_context(file, file_errors[0].line)
        err_lines = "\n".join(
            f"  [{e.source}:{e.code}] line {e.line}: {e.message}"
            for e in file_errors[:10]
        )
        sections.append(textwrap.dedent(f"""
            ### File: {file}
            Errors:
            {err_lines}

            Context (surrounding lines):
            ```
            {context}
            ```
        """))

    return textwrap.dedent(f"""
        You are an expert Python/TypeScript developer performing automated error repair.
        Fix ALL errors listed below. Return ONLY a JSON object — no prose, no markdown fences.

        Schema:
        {{
          "files": [
            {{
              "path": "relative/path/to/file.py",
              "full_content": "<complete corrected file content as a string>"
            }}
          ]
        }}

        Rules:
        - Fix every error. Do not introduce new ones.
        - Preserve all existing functionality.
        - Use os.getenv() for any secrets — never inline them.
        - Follow ruff, mypy strict, and project coding standards.
        - If a test is wrong (not the code), fix the test.

        Errors to fix:
        {"".join(sections)}
    """).strip()


def apply_patches(llm_response: str, dry_run: bool = False) -> list[str]:
    # Strip markdown fences if model adds them despite instructions
    text = re.sub(r"^```[a-z]*\n?", "", llm_response.strip(), flags=re.MULTILINE)
    text = re.sub(r"\n?```$", "", text.strip(), flags=re.MULTILINE)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"[repair] could not parse LLM response as JSON: {exc}", flush=True)
        print(f"[repair] raw: {llm_response[:500]}", flush=True)
        return []

    patched: list[str] = []
    for item in data.get("files", []):
        rel = item.get("path", "")
        content = item.get("full_content", "")
        if not rel or not content:
            continue
        target = REPO_ROOT / rel
        if dry_run:
            print(f"[repair][dry-run] would write {target} ({len(content)} chars)")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            print(f"[repair] patched {rel}")
        patched.append(rel)
    return patched


def auto_format() -> None:
    subprocess.run(FMT_CMD, cwd=REPO_ROOT, capture_output=True)


def auto_commit(patched_files: list[str], round_n: int) -> None:
    if not patched_files or not AUTO_COMMIT:
        return
    subprocess.run(["git", "add"] + patched_files, cwd=REPO_ROOT)
    msg = f"fix(auto-repair): round {round_n} — {len(patched_files)} file(s) [provider={REPAIR_PROVIDER}]"
    subprocess.run(["git", "commit", "-m", msg], cwd=REPO_ROOT)
    print(f"[repair] committed: {msg}")

# ── Main repair loop ──────────────────────────────────────────────────────────

def repair_loop(dry_run: bool = False, ci: bool = False) -> int:
    for round_n in range(1, MAX_ROUNDS + 1):
        errors = collect_errors()
        if not errors:
            print(f"[repair] ✓ all clear after round {round_n - 1}")
            return 0

        print(f"[repair] round {round_n}/{MAX_ROUNDS} — {len(errors)} error(s)")
        prompt = build_repair_prompt(errors)

        try:
            response = generate(prompt)
        except Exception as exc:
            print(f"[repair] LLM call failed: {exc}", flush=True)
            break

        patched = apply_patches(response, dry_run=dry_run)
        if not dry_run:
            auto_format()
            auto_commit(patched, round_n)

        if not patched:
            print("[repair] no patches produced — stopping.")
            break

    remaining = collect_errors()
    if remaining:
        print(f"[repair] ✗ {len(remaining)} unresolved error(s) after {MAX_ROUNDS} rounds")
        for e in remaining[:20]:
            print(f"  [{e.source}] {e.file}:{e.line} {e.code}: {e.message}")
        return 1 if ci else 0
    return 0


def watch_loop() -> None:
    print("[repair] watch mode — polling every 10s (Ctrl-C to stop)")
    try:
        while True:
            repair_loop()
            time.sleep(10)
    except KeyboardInterrupt:
        print("[repair] watch stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowTag-v2 Autonomous Error Repair")
    parser.add_argument("--watch", action="store_true", help="Re-run on interval")
    parser.add_argument("--dry-run", action="store_true", help="Print patches only")
    parser.add_argument("--ci", action="store_true", help="Exit non-zero if unresolved")
    args = parser.parse_args()

    if args.watch:
        watch_loop()
    else:
        sys.exit(repair_loop(dry_run=args.dry_run, ci=args.ci))
