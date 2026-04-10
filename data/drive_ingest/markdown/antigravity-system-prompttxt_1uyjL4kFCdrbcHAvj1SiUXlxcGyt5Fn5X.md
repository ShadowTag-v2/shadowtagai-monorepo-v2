ANTIGRAVITY WORKSPACE CONTAINMENT + MONOREPO DISCIPLINE

Canonical workspace root:
/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

Mission
Operate only within the canonical monorepo root, treat only canonical live paths as authoritative, and fail closed on ambiguity, workspace drift, nested repo drift, or path escape.

Core rules

1. Single-root mode only
- Treat the canonical workspace root as the only valid project root.
- Do not infer project context from parent folders, sibling folders, prior sessions, or historical thread paths.
- Do not open or treat any parent directory as the workspace.

2. Workspace verification before action
Before any file read, write, search, rename, move, delete, refactor, index, or code-generation action:
- resolve the active workspace root
- resolve the target path to an absolute realpath
- verify the realpath is inside the canonical workspace root
- if verification fails, stop immediately and report workspace drift

3. Fail closed
If any of the following are true, stop and report the problem instead of guessing:
- active workspace root is not exactly the canonical workspace root
- target path resolves outside the canonical workspace root
- multiple candidate files appear to satisfy the request
- nested repo structure creates competing sources of truth
- requested operation touches a denied zone without explicit authorization

4. Deny non-workspace access
- Never read, write, create, rename, or delete files outside the canonical workspace root.
- Never use sibling repos, parent repos, previous ShadowTag-v2 paths, playground paths, or old thread paths as implicit context.
- Never follow symlinks or path traversal outside the canonical root.

5. Realpath enforcement
- All path validation must use resolved realpaths, not string prefix checks.
- Reject symlink escapes, ../ traversal, mounted indirections, and absolute paths outside the canonical root.

6. Canonical source-of-truth policy
Treat only canonical live paths as authoritative.
Do not treat backups, recovered fragments, nested repos, raw ingests, vendor mirrors, or legacy archives as writable source of truth.
If duplicate candidates exist, prefer the path declared canonical in monorepo_manifest.yaml.
If canonical status is unclear, stop and report ambiguity.

7. Denied zones
The following zones are excluded from normal source operations unless explicitly authorized:
- archive/
- tools/legacy/
- docs/legacy_shadowtag_v2/
- apps/ShadowTag-v2_ecosystem/raw_ingest/
- **/_PRE_OMEGA_BACKUP_*/
- **/repos/*-legacy/
- **/ShadowTag-Omega/
- **/arsenal_recovered/

Behavior in denied zones:
- do not modify
- do not refactor
- do not generate code into them
- do not treat them as primary evidence for code changes
- only inspect when the task explicitly targets archival, forensic, or migration work

8. Canonical namespace policy
Preferred canonical live namespace:
- apps/ShadowTag-v2_stack/

Until explicitly changed in monorepo_manifest.yaml:
- apps/ShadowTag-v2_stack/* = canonical candidate
- apps/ShadowTag-v2_ecosystem/* = transitional or staging unless explicitly marked canonical
- archive/* = non-canonical
- legacy/recovered/backup areas = non-canonical

9. Nested repo discipline
- Do not treat nested repos, copied repos, vendored mirrors, backup trees, or recovered trees as independent workspaces.
- Do not create new nested repos inside live app trees.
- If a nested repo is encountered, treat it as non-canonical unless monorepo_manifest.yaml explicitly marks it canonical.

10. Monorepo manifest precedence
If monorepo_manifest.yaml exists, it overrides heuristics.
Use it to determine:
- canonical paths
- archived paths
- unresolved repos
- excluded zones

11. Safe write policy
Writes are allowed only when:
- target path is inside canonical workspace root
- target path is not in a denied zone
- target path is canonical or explicitly authorized
- the operation does not create a second competing source of truth

12. Safe search policy
When searching for code or files:
- prefer canonical live paths first
- exclude denied zones by default
- include denied zones only for forensic, archival, or migration tasks explicitly asking for them

13. Startup guard
At session start, verify and mentally enforce:
- workspace root = /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
- mode = single-root
- non-workspace access = denied
- canonical namespace = apps/ShadowTag-v2_stack
- denied zones = excluded by default

14. Output behavior
When drift or ambiguity is detected:
- explicitly name the conflicting paths
- state why the workspace is unsafe or ambiguous
- propose the canonical target path
- do not continue silently

15. Repo hygiene goals
Optimize for:
- one canonical live path per repo
- zero backup trees in live code
- zero nested legacy repos in live code
- zero recovered fragments acting as source of truth
- build, test, and indexing pointed only at canonical live roots

Non-negotiable summary
One root.
One canonical namespace.
No parent access.
No sibling access.
No non-workspace access.
No archive access by default.
No nested repo access by default.
Realpath validation on every operation.
Fail closed on ambiguity.