#!/usr/bin/env bash
set -euo pipefail

CANONICAL_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p "${CANONICAL_ROOT}"
cd "${CANONICAL_ROOT}"

mkdir -p .github/workflows .vscode scripts

cat > .github/CODEOWNERS <<'EOF'
# Default owner
* @ehanc69

# Monorepo governance
/.github/ @ehanc69
/MODULE.bazel @ehanc69
/.editorconfig @ehanc69
/monorepo_manifest.yaml @ehanc69

# Core apps
/apps/pnkln-stack_stack/pnkln-stack-fastapi-services/ @ehanc69
/apps/pnkln-stack_stack/cosmic-crab-payload/ @ehanc69

# Ecosystem / import lanes
/apps/pnkln-stack_ecosystem/ @ehanc69

# Libraries
/libs/ @ehanc69

# Tooling and docs
/tools/ @ehanc69
/docs/ @ehanc69

# Archive / legacy zones
/archive/ @ehanc69
/tools/legacy/ @ehanc69
/docs/legacy_shadowtag_v2/ @ehanc69
EOF

cat > .github/workflows/main.yml <<'EOF'
name: Google3 Matrix CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: monorepo-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  bazel-build:
    name: bazel-build
    runs-on: ubuntu-latest
    timeout-minutes: 45

    steps:
      - name: Git Checkout
        uses: actions/checkout@v4

      - name: Mount Bazel Cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/bazel
          key: bazel-cache-${{ runner.os }}-${{ hashFiles('MODULE.bazel', '**/*.bzl', '**/BUILD.bazel') }}
          restore-keys: |
            bazel-cache-${{ runner.os }}-

      - name: Setup Bazel
        uses: bazelbuild/setup-bazelisk@v2

      - name: Build All Targets
        run: bazel build //...

  bazel-test:
    name: bazel-test
    runs-on: ubuntu-latest
    timeout-minutes: 60
    needs: bazel-build

    steps:
      - name: Git Checkout
        uses: actions/checkout@v4

      - name: Mount Bazel Cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/bazel
          key: bazel-cache-${{ runner.os }}-${{ hashFiles('MODULE.bazel', '**/*.bzl', '**/BUILD.bazel') }}
          restore-keys: |
            bazel-cache-${{ runner.os }}-

      - name: Setup Bazel
        uses: bazelbuild/setup-bazelisk@v2

      - name: Test All Targets
        run: bazel test //...
EOF

cat > .vscode/settings.json <<'EOF'
{
  "window.title": "Monorepo-Uphillsnowball",

  "git.openRepositoryInParentFolders": "never",
  "git.autoRepositoryDetection": false,
  "git.detectSubmodules": false,

  "geminicodeassist.project": "shadowtag-omega-v4",
  "cloudcode.project": "shadowtag-omega-v4",
  "geminicodeassist.updateChannel": "Insiders",
  "cloudcode.updateChannel": "Insiders",

  "python.defaultInterpreterPath": "${workspaceFolder}/.venv",
  "python.useEnvironmentsExtension": false,
  "python.terminal.activateEnvInCurrentTerminal": true,
  "python.terminal.useEnvFile": true,

  "java.import.maven.enabled": false,
  "java.import.gradle.enabled": false,

  "basedpyright.analysis.diagnosticMode": "openFilesOnly",
  "basedpyright.analysis.typeCheckingMode": "basic",

  "files.exclude": {
    "**/.DS_Store": true,
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true,
    "**/.ipynb_checkpoints": true,
    "**/_PRE_OMEGA_BACKUP_*": true,
    "archive/**": true,
    "tools/legacy/**": true,
    "docs/legacy_shadowtag_v2/**": true,
    "apps/pnkln-stack_ecosystem/raw_ingest/**": true,
    "**/ShadowTag-Omega/**": true,
    "**/arsenal_recovered/**": true,
    "**/repos/*-legacy/**": true
  },

  "search.exclude": {
    "**/.git/**": true,
    "**/.DS_Store": true,
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true,
    "**/.mypy_cache/**": true,
    "**/.ruff_cache/**": true,
    "**/.ipynb_checkpoints/**": true,
    "**/_PRE_OMEGA_BACKUP_*/**": true,
    "archive/**": true,
    "tools/legacy/**": true,
    "docs/legacy_shadowtag_v2/**": true,
    "apps/pnkln-stack_ecosystem/raw_ingest/**": true,
    "**/ShadowTag-Omega/**": true,
    "**/arsenal_recovered/**": true,
    "**/repos/*-legacy/**": true
  },

  "files.watcherExclude": {
    "**/.git/**": true,
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true,
    "**/.mypy_cache/**": true,
    "**/.ruff_cache/**": true,
    "**/.ipynb_checkpoints/**": true,
    "**/_PRE_OMEGA_BACKUP_*/**": true,
    "archive/**": true,
    "tools/legacy/**": true,
    "docs/legacy_shadowtag_v2/**": true,
    "apps/pnkln-stack_ecosystem/raw_ingest/**": true,
    "**/ShadowTag-Omega/**": true,
    "**/arsenal_recovered/**": true,
    "**/repos/*-legacy/**": true
  }
}
EOF

cat > .vscode/tasks.json <<'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Verify Canonical Workspace Root",
      "type": "shell",
      "command": "${workspaceFolder}/scripts/check_workspace_root.sh",
      "problemMatcher": []
    }
  ]
}
EOF

cat > .gitignore <<'EOF'
# OS / editor noise
.DS_Store
*.swp
*.swo

# Python caches
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.ipynb_checkpoints/

# Virtual environments
.venv/
venv/

# Monorepo denied zones
archive/
tools/legacy/
docs/legacy_shadowtag_v2/
apps/pnkln-stack_ecosystem/raw_ingest/

# Backup / recovered / nested legacy zones
**/_PRE_OMEGA_BACKUP_*/
**/ShadowTag-Omega/
**/arsenal_recovered/
**/repos/*-legacy/

# Large generated / temporary outputs
coverage/
dist/
build/
out/

# Local vector / index artifacts
.chroma_db/
.beads/
EOF

cat > .ignore <<'EOF'
# OS / editor noise
.DS_Store
*.swp
*.swo

# Python caches
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.ipynb_checkpoints/

# Virtual environments
.venv/
venv/

# Monorepo denied zones
archive/
tools/legacy/
docs/legacy_shadowtag_v2/
apps/pnkln-stack_ecosystem/raw_ingest/

# Backup / recovered / nested legacy zones
**/_PRE_OMEGA_BACKUP_*/
**/ShadowTag-Omega/
**/arsenal_recovered/
**/repos/*-legacy/

# Large generated / temporary outputs
coverage/
dist/
build/
out/

# Local vector / index artifacts
.chroma_db/
.beads/
EOF

cat > Monorepo-Uphillsnowball.code-workspace <<'EOF'
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "window.title": "Monorepo-Uphillsnowball",

    "git.openRepositoryInParentFolders": "never",
    "git.autoRepositoryDetection": false,
    "git.detectSubmodules": false,

    "geminicodeassist.project": "shadowtag-omega-v4",
    "cloudcode.project": "shadowtag-omega-v4",
    "geminicodeassist.updateChannel": "Insiders",
    "cloudcode.updateChannel": "Insiders",

    "python.defaultInterpreterPath": "${workspaceFolder}/.venv",
    "python.useEnvironmentsExtension": false,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.terminal.useEnvFile": true,

    "java.import.maven.enabled": false,
    "java.import.gradle.enabled": false,

    "basedpyright.analysis.diagnosticMode": "openFilesOnly",
    "basedpyright.analysis.typeCheckingMode": "basic",

    "files.exclude": {
      "**/.git": false,
      "**/.DS_Store": true,
      "**/__pycache__": true,
      "**/.pytest_cache": true,
      "**/.mypy_cache": true,
      "**/.ruff_cache": true,
      "**/.ipynb_checkpoints": true,
      "**/_PRE_OMEGA_BACKUP_*": true,
      "archive/**": true,
      "tools/legacy/**": true,
      "docs/legacy_shadowtag_v2/**": true,
      "apps/pnkln-stack_ecosystem/raw_ingest/**": true,
      "**/ShadowTag-Omega/**": true,
      "**/arsenal_recovered/**": true,
      "**/repos/*-legacy/**": true
    },

    "search.exclude": {
      "**/.git/**": true,
      "**/.DS_Store": true,
      "**/__pycache__/**": true,
      "**/.pytest_cache/**": true,
      "**/.mypy_cache/**": true,
      "**/.ruff_cache/**": true,
      "**/.ipynb_checkpoints/**": true,
      "**/_PRE_OMEGA_BACKUP_*/**": true,
      "archive/**": true,
      "tools/legacy/**": true,
      "docs/legacy_shadowtag_v2/**": true,
      "apps/pnkln-stack_ecosystem/raw_ingest/**": true,
      "**/ShadowTag-Omega/**": true,
      "**/arsenal_recovered/**": true,
      "**/repos/*-legacy/**": true
    },

    "files.watcherExclude": {
      "**/.git/**": true,
      "**/__pycache__/**": true,
      "**/.pytest_cache/**": true,
      "**/.mypy_cache/**": true,
      "**/.ruff_cache/**": true,
      "**/.ipynb_checkpoints/**": true,
      "**/_PRE_OMEGA_BACKUP_*/**": true,
      "archive/**": true,
      "tools/legacy/**": true,
      "docs/legacy_shadowtag_v2/**": true,
      "apps/pnkln-stack_ecosystem/raw_ingest/**": true,
      "**/ShadowTag-Omega/**": true,
      "**/arsenal_recovered/**": true,
      "**/repos/*-legacy/**": true
    },
    "explorer.excludeGitIgnore": false,
    "extensions.ignoreRecommendations": false
  },
  "extensions": {
    "recommendations": [
      "ms-python.python",
      "detachhead.basedpyright",
      "charliermarsh.ruff",
      "esbenp.prettier-vscode",
      "EditorConfig.EditorConfig",
      "redhat.vscode-yaml",
      "ms-vscode.makefile-tools",
      "bazelbuild.vscode-bazel",
      "eamodio.gitlens"
    ],
    "unwantedRecommendations": [
      "GitHub.vscode-github-actions",
      "GitHub.vscode-pull-request-github",
      "github.copilot",
      "github.copilot-chat"
    ]
  }
}
EOF

cat > monorepo_manifest.yaml <<'EOF'
version: 1
canonical-root: ShadowTag-v2/Monorepo-Uphillsnowball

workspace:
  name: Monorepo-Uphillsnowball
  root: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
  policy: latest-only
  source_of_truth: monorepo_manifest.yaml

policy:
  canonical_path_precedence:
    - apps/aiyou_stack
    - apps
    - libs
  denied_zones:
    - archive/**
    - tools/legacy/**
    - docs/legacy_shadowtag_v2/**
    - apps/pnkln-stack_ecosystem/raw_ingest/**
    - "**/_PRE_OMEGA_BACKUP_*/**"
    - "**/repos/*-legacy/**"
    - "**/ShadowTag-Omega/**"
    - "**/arsenal_recovered/**"
  denied_zone_policy:
    read: allowed_only_when_explicitly_requested
    write: denied
    refactor: denied
    generate: denied
    index: excluded_by_default

# These are folded-in components — NOT canonical roots. The monorepo owns them.
folded_in_components:
  - name: aiyou-fastapi-services
    status: folded-in
    path: apps/aiyou_stack/aiyou-fastapi-services
    notes: Folded-in component. Not a root peer.

  - name: cosmic-crab-payload
    status: folded-in
    path: apps/aiyou_stack/cosmic-crab-payload
    notes: Folded-in component. Not a root peer.

  - name: Pipeline
    status: folded-in
    path: apps/aiyou_stack/Pipeline
    notes: Folded-in component. Not a root peer.

  - name: nascent-apollo
    status: folded-in
    path: apps/aiyou_stack/nascent-apollo
    notes: Folded-in component. Not a root peer.

zones:
  live:
    - apps/**
    - libs/**
    - tools/**
    - docs/**
  archive:
    - archive/**
  legacy:
    - tools/legacy/**
    - docs/legacy_shadowtag_v2/**
  staging:
    - apps/pnkln-stack_ecosystem/**
  excluded_from_default_search:
    - archive/**
    - tools/legacy/**
    - docs/legacy_shadowtag_v2/**
    - apps/pnkln-stack_ecosystem/raw_ingest/**
    - "**/_PRE_OMEGA_BACKUP_*/**"
    - "**/repos/*-legacy/**"
    - "**/ShadowTag-Omega/**"
    - "**/arsenal_recovered/**"

editor_rules:
  prefer_manifest_over_heuristics: true
  stop_on_duplicate_candidates: true
  require_canonical_target_for_writes: true
  require_explicit_authorization_for_denied_zones: true

validation:
  success_definition:
    - one_canonical_live_root_per_repo
    - no_backup_trees_in_live_code
    - no_nested_legacy_repos_in_live_code
    - no_recovered_fragments_as_source_of_truth
    - build_and_index_target_only_canonical_live_paths
EOF

cat > scripts/check_workspace_root.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

CANONICAL_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

if ! command -v realpath >/dev/null 2>&1; then
  echo "ERROR: realpath is required but not installed." >&2
  exit 1
fi

ACTUAL_ROOT="$(realpath "${PWD}")"
EXPECTED_ROOT="$(realpath "${CANONICAL_ROOT}")"

if [ "${ACTUAL_ROOT}" != "${EXPECTED_ROOT}" ]; then
  echo "ERROR: Workspace drift detected." >&2
  echo "Expected root: ${EXPECTED_ROOT}" >&2
  echo "Actual root:   ${ACTUAL_ROOT}" >&2
  echo "Refusing to continue outside canonical monorepo root." >&2
  exit 1
fi

if [ ! -f "${EXPECTED_ROOT}/monorepo_manifest.yaml" ]; then
  echo "ERROR: monorepo_manifest.yaml not found at canonical root." >&2
  exit 1
fi

if [ ! -f "${EXPECTED_ROOT}/MODULE.bazel" ]; then
  echo "ERROR: MODULE.bazel not found at canonical root." >&2
  exit 1
fi

echo "Workspace root verified: ${EXPECTED_ROOT}"
echo "Mode: single-root"
echo "Manifest: present"
echo "Bazel root: present"
EOF

cat > scripts/guard_path.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

CANONICAL_ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path>" >&2
  exit 2
fi

TARGET="$1"

if ! command -v realpath >/dev/null 2>&1; then
  echo "ERROR: realpath is required but not installed." >&2
  exit 1
fi

ROOT_REAL="$(realpath "${CANONICAL_ROOT}")"
TARGET_REAL="$(realpath -m "${TARGET}")"

case "${TARGET_REAL}" in
  "${ROOT_REAL}"|"${ROOT_REAL}"/*)
    ;;
  *)
    echo "ERROR: Target path is outside canonical root." >&2
    echo "Canonical root: ${ROOT_REAL}" >&2
    echo "Target path:    ${TARGET_REAL}" >&2
    exit 1
    ;;
esac

case "${TARGET_REAL}" in
  "${ROOT_REAL}"/archive/*|\
  "${ROOT_REAL}"/tools/legacy/*|\
  "${ROOT_REAL}"/docs/legacy_shadowtag_v2/*|\
  "${ROOT_REAL}"/apps/pnkln-stack_ecosystem/raw_ingest/*|\
  */_PRE_OMEGA_BACKUP_*/*|\
  */ShadowTag-Omega/*|\
  */arsenal_recovered/*|\
  */repos/*-legacy/*)
    echo "ERROR: Target path is inside a denied zone." >&2
    echo "Target path: ${TARGET_REAL}" >&2
    exit 1
    ;;
  *)
    ;;
esac

echo "${TARGET_REAL}"
EOF

chmod +x scripts/check_workspace_root.sh scripts/guard_path.sh

cat > .antigravity-system-prompt.txt <<'EOF'
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
- apps/pnkln-stack_ecosystem/raw_ingest/
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
- apps/pnkln-stack_stack/

Until explicitly changed in monorepo_manifest.yaml:
- apps/pnkln-stack_stack/* = canonical candidate
- apps/pnkln-stack_ecosystem/* = transitional or staging unless explicitly marked canonical
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
- canonical namespace = apps/pnkln-stack_stack
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
EOF
