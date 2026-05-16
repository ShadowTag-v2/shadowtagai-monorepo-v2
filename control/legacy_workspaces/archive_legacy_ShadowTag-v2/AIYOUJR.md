# AIYOUJR Doctrine and Operating Posture

This document adopts the user's AIYOUJR posture and Bourne-Enhanced SOPs for the AiYou project. It codifies strict, security-first, and evidence-driven engineering.

## Standing Defaults

- Baseline: peg cognition at 160 (productivity posture via tools and rigor)
- Cursor-only prompts; apply instructions via Chat/Inline Edit/Code Actions
- Strict posture: staged-first fixes; minimal diffs; deterministic retries
- Coverage threshold ≥ 98%; require two consecutive green CI runs to merge
- Rate-limit pacing/backoff; model cooperation (Claude + GPT-5)
- Auto-approve improvements when all gates pass; objections logged when AIYOUJR flags
- Decision guardrails: AiYouJR (purpose), doctrine (reasons), Army Risk Management (brakes)

## SOPs (Bourne-Enhanced)

- Upload Triage: classify {KEEP | REFERENCE | DISCARD}, score utility 0–5, extract actions, post delta summaries
- Change & Release: pre-mortem, staged behind flags, stress drills, rollback readiness, postmortems within 24h
- Decision Protocol: Mochary-style form; include 5-Whys, risks, owner, success metrics
- Code Review: minimal diff, tests, security/privacy, observability hooks, rollback plan
- Structured Frameworks: Pre-Mortem, 5-Whys, Postmortem
- Army Risk Management: hazard detection, controls, rollback readiness

## Cursor Usage (How to Apply)

- Chat across files; Inline Edit (Ctrl+K) for targeted refactors; Code Actions for selections
- Never run prompts in terminal; keep provenance and auditability

## Non-biological “Enhancements”

We interpret productivity “enhancements” as legal, tooling-based methods: SOPs, automation, testing, static analysis, pair-programming, and structured reviews. No medical or biological claims are made.

## Governance and Compliance

- PR template requires: pre-mortem, 5-Whys, pair/recipe review, static analysis, tests, objections captured, postmortem readiness
- Lightweight PR gate enforces presence of sections and denies merge on missing doctrine fields
- Logs and metrics are retained for auditability


