---
description: Strict 4-file reporting schema for the /governed-merge-56 pipeline.
---

# /merge-56-four-file-proof

After running `/governed-merge-56`, produce exactly these 4 files at the monorepo root and nothing else as the primary report set:

1. `01_repo_census.json`
2. `02_merge_plan.md`
3. `03_execution_log.md`
4. `04_canonical_state.md`

## STRICT FILE CONTRACT

### `01_repo_census.json`
- One object per repo.
- Required keys:
  - repo_name
  - github_present
  - monorepo_present
  - destination_path
  - disposition
  - latest_sha
  - duplicate_family
  - blocker
  - evidence
- Allowed `disposition` values only:
  - canonical_in_monorepo
  - queued_for_fold_in
  - archived_after_fold_in
  - reference_only
  - deprecated
  - blocked

### `02_merge_plan.md`
For every non-canonical repo include:
- repo
- destination
- rationale
- duplicate/legacy paths to demote
- exact next action
- risk note
- rollback note

Order entries by:
1. safest and highest-confidence first
2. blocked items last

### `03_execution_log.md`
Append-only run log.
For each repo processed, write:
- timestamp
- repo
- phase
- action taken
- files/paths touched
- result
- evidence
- rollback path if needed

No vague language. No “done” unless actually done.

### `04_canonical_state.md`
This is the executive truth file.
It must contain:
- total repos counted
- total canonical
- total queued
- total archived
- total reference_only
- total deprecated
- total blocked
- list of all canonical live roots
- list of all blocked repos with one-line blocker
- manifest/doc alignment result
- duplicate-live-root result
- nested-git result
- final verdict:
  - NOT_COMPLETE
  - COMPLETE_WITH_BLOCKERS
  - COMPLETE

## RULES

1. Do not claim COMPLETE if any repo is still `blocked` or `queued_for_fold_in`.
2. Do not claim manifest alignment unless filesystem truth matches.
3. Do not omit blocked repos.
4. Do not emit secondary summary docs before these 4 files exist.
5. Keep this report set latest-only: overwrite previous versions of these exact 4 files.

## REQUIRED TERMINAL OUTPUT

When finished, print only:

FOUR_FILE_REPORT_READY
- 01_repo_census.json
- 02_merge_plan.md
- 03_execution_log.md
- 04_canonical_state.md
