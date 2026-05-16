---
description: Code-only import of ehanc69 repositories without preserving git history
---

# /merge-56-code-only-no-history

MISSION
Complete the merge of all ehanc69 repos into the ShadowTag monorepo using CODE-ONLY import.
Do not preserve git history. Do not merge commit graphs. Do not import tags, branches, reflogs, hooks, or nested .git directories.
Goal: only the current file trees survive, mapped into canonical monorepo destinations, to minimize repository size.

CANONICAL ROOT
/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

CANONICAL PROJECT
shadowtag-omega-v4

CANONICAL MODEL FAMILY
gemini-3.1-family

HARD RULES
1. monorepo_manifest.yaml is workspace truth
2. antigravity-mcp-config.json is MCP truth
3. .env holds secrets; never inline secrets
4. counselconduit = product
5. uphillsnowball = lab
6. import FILES ONLY
7. never preserve source git history
8. never nest repos
9. never claim complete until manifest + destination + validation all match reality

REQUIRED IMPORT MODE
For every source repo:
- export only working tree contents
- exclude:
  - .git
  - .github if destination policy says centralize separately
  - large caches
  - node_modules
  - dist/build artifacts unless explicitly canonical
  - venvs
  - compiled binaries
  - duplicate archives
  - legacy mirrors
- import only the surviving code/docs/config assets needed for the canonical destination

ALLOWED METHODS
Choose one of these, preferring the simplest truthful path:
A. filesystem copy from checked-out repo root into canonical destination
B. rsync/cp-based tree import with explicit excludes
C. git archive of source HEAD piped into destination
Do NOT use:
- git merge
- git pull with history
- subtree with full history
- submodule preservation
- filter-repo history transplant unless needed only to strip before a code-only export

PER-REPO END STATE
Each repo must end as exactly one of:
- canonical_in_monorepo
- queued_for_fold_in
- archived_after_code_import
- reference_only
- deprecated

PHASE 0 — PRECHECK
- confirm canonical root
- confirm MCP truth
- confirm destination map exists or generate repo_fold_in_delta.json
- confirm import mode = code_only_no_history

PHASE 1 — REPO CENSUS
- enumerate all target repos
- classify current state
- identify destination path for each repo
- write repo_census.current.json

PHASE 2 — CODE-ONLY EXPORT
For each repo:
- snapshot only current code tree
- strip nested .git and git metadata
- strip caches, build outputs, and noncanonical heavy assets
- preserve only code, docs, configs, schemas, tests, and required static assets

PHASE 3 — DESTINATION IMPORT
- place imported code into exactly one canonical destination
- if destination already has content, do a file-level reconcile
- prefer canonical destination content when clearly newer or already declared live
- move superseded duplicates into archive lanes, not live paths

PHASE 4 — MANIFEST TRUTH
- update monorepo_manifest.yaml
- update docs/MERGE_STATUS.md
- update fold_in_checklist.yaml
- no repo remains floating or ambiguous

PHASE 5 — TOOLING REALIGNMENT
- ensure workspace, pyright, search excludes, watcher excludes, AGENTS, and indexing target only canonical live roots
- ensure archived, legacy, backup, and recovered trees are excluded from active analysis/build loops

PHASE 6 — VALIDATION
For each imported repo:
- verify files landed in destination
- verify no nested .git remains
- verify no history-preserving merge was used
- verify destination is referenced correctly by tooling if it is live
- run light sanity checks where available

PHASE 7 — STAMP
Only after prior checks pass:
- mark repo final
- mark status in fold_in_checklist.yaml
- include evidence in final_canonical_state_report.md

REQUIRED OUTPUT FILES
1. repo_census.current.json
2. repo_fold_in_delta.json
3. repo_merge_execution_log.md
4. repo_merge_blockers.json
5. final_canonical_state_report.md
6. updated monorepo_manifest.yaml
7. updated docs/MERGE_STATUS.md
8. updated fold_in_checklist.yaml

SUCCESS FORMAT
CODE_ONLY_BATCH_COMPLETE
repos_completed=<n>
repos_remaining=<n>
history_imported=no
nested_git_remaining=no
manifest_updated=yes|no
merge_status_updated=yes|no
tooling_updated=yes|no
next_batch=<text>

FAIL-CLOSED FORMAT
BLOCKED
phase=<phase>
repo=<repo>
blocker=<text>
evidence=<text>
safe_to_continue_with_unrelated_repos=yes|no

OPERATOR NOTE:
Space-saving directive:
- Treat every source repo as a code payload, not a history asset.
- Never merge histories into the monorepo.
- If a repo must be retained for provenance, record its URL and source HEAD SHA in the execution log only.
- Provenance belongs in metadata files, not in imported git history.
