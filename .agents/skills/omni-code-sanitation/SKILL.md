---
name: omni-code-sanitation
description: Top 0.001% Standard Operating Procedure for resolving massive tech debt across Python and TS/JS. Utilizes AST-aware refactoring, dead-code necromancy, Biome, and Type-Guarded LLM chunks.
---
# Omni-Sanitation Pipeline

## Strict Order of Operations

**1. The Necromancy Pass (Kill Zombie Code):**
Before formatting or linting, we must delete what isn't used. Never waste LLM tokens reading dead code.
- **Python (Vulture):** Run `vulture . --make-whitelist > .vulture_whitelist.py` to protect dynamic endpoints (FastAPI/Pydantic). Then run `vulture . .vulture_whitelist.py --min-confidence 90`. Delete strictly dead code.
- **TS/JS (Knip):** Run `knip`. Delete unused exports and remove bloated NPM dependencies.

**2. The Polyglot Rust Auto-Fix Pass:**
Use compiler engines to mathematically fix styling and modernizations without LLM context limits.
- **Python:** Run `ruff check . --fix --unsafe-fixes`.
- **TS/JS (Biome):** Run `biome check --write --unsafe ./apps`. (This replaces Prettier/ESLint entirely).

**3. Strategic Triage & Baselining (Ruff):**
- Add noisy/intentional rules (`E402`, `E741`) to `ignore` arrays in `ruff.toml`.
- Baseline mechanical debt to unblock CI using `ruff check . --add-noqa`.

**4. The AST-Grep Scalpel (No Regex):**
Never use `sed` or Regex to refactor code blocks. Use AST-Grep (`sg`) for deterministic structural replacements (e.g., `sg --lang python -p 'except:' -r 'except Exception:' --update-all`).

**5. Chunked AI Refactoring & Type Guarding:**
For architectural refactors (e.g., `SIM102` collapsible ifs):
- Refactor a maximum of 3-5 files at a time.
- **The Guardrail:** Run `pyright <file>` (Python) or `tsc --noEmit` (JS/TS) AND `pytest` on the chunk. The LLM must not break static typing during an AST rewrite.

## Tool Versions (Minimum)
- ruff >= 0.15.0
- vulture >= 2.14
- biome >= 2.4.0
- ast-grep (sg) >= 0.42.0
- knip >= 6.0.0

## Anti-Patterns (PROHIBITED)
- Using `sed` or `re.sub()` for code refactoring (use `sg` instead)
- Auto-fixing 800+ errors on `main` branch (use `debt-burn` branch)
- Running Prettier or ESLint alongside Biome (Biome replaces both)
- Applying `--unsafe-fixes` without immediate `pytest` verification
- Deleting Vulture-flagged code without checking for dynamic usage (FastAPI routes, Pydantic validators)
