> [!WARNING]
> **DEPRECATED (2026-04-27)** — Superseded by `/gated-maintenance`.
> Documentation generation is governed by the canonical truth hierarchy in AGENTS.md.
> Use `/gated-maintenance` for bounded documentation updates.
> Retained for reference only. Do not execute.

# Workflow: Auto-Documentation — DEPRECATED

**Trigger:** "document this repo", "write the readme", or "setup contributing guidelines".

**Goal:** Create or update the primary documentation files (`README.md` and `CONTRIBUTING.md`).

## Step 1: Deep Audit
1.  **Analyze Dependencies:** Read `package.json`, `go.mod`, `pom.xml`, or `requirements.txt`.
2.  **Map Structure:** Run a tree scan of the `src/` directory.
3.  **Identify Scripts:** Look for `scripts` in package files or `Makefile` entries.

## Step 2: Generate README.md & CONTRIBUTING.md
- Document title, badge, one-liner, tech stack, and prerequisites.
- Generate valid run commands.
- Reference `.agent/rules/CONSTITUTION.md` in CONTRIBUTING.md.
- Run link checks.
