#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

mkdir -p "${ROOT}/third_party" "${ROOT}/contracts" "${ROOT}/docs"
cd "${ROOT}"

cat > third_party/README.md <<'EOF'
# third_party

## Purpose
This directory is the canonical home for intentionally vendored third-party dependencies in the monorepo.

## Policy
Use `third_party/` only when one of the following is true:
1. the dependency cannot be consumed cleanly through the normal package manager flow
2. the dependency must be patched locally
3. the dependency must be pinned and audited as source
4. the dependency is part of reproducible build infrastructure

## Rules
- Do not vendor dependencies ad hoc inside app directories.
- Do not maintain duplicate copies of the same dependency in multiple app trees.
- Prefer one version of each dependency across the monorepo where feasible.
- Every vendored dependency must include:
  - source origin
  - version or commit
  - reason for vendoring
  - patch policy
  - owner

## Required metadata
Each dependency directory should contain a small metadata file, for example:

```yaml
name: example-lib
source: https://github.com/example/example-lib
version: v1.2.3
owner: @ehanc69
reason: local patch required for Bazel build
patches:
  - fix-build.patch
status: active
```

## Not allowed
* vendored copies under apps/.../vendor unless explicitly approved and scheduled for migration
* duplicate mirrors under external_memory, external_repos, backups, or recovered trees
* using vendored code as an excuse to bypass monorepo dependency policy

## Migration rule
If a vendored dependency currently exists outside third_party/, it must be:
1. moved into third_party/
2. referenced from canonical build metadata
3. removed from the old location after validation
EOF

cat > contracts/README.md <<'EOF'
# contracts

## Purpose
This directory is the canonical home for shared contracts used across services, libraries, and applications.

## What belongs here
Use contracts/ for:
* shared API schemas
* protobuf definitions
* shared DTO / interface declarations
* event schemas
* generated code configuration
* cross-language service contracts

## What does not belong here
Do not put:
* service-private models that are not shared
* duplicated local copies of shared schemas
* temporary migration copies
* archival or legacy definitions

## Rules
* Shared contracts must be declared once here and consumed from here.
* Services may not maintain independent duplicate versions of shared contracts.
* Breaking changes must be versioned or coordinated explicitly.
* Generated artifacts should be reproducible from source contracts.

## Suggested layout
contracts/
├── proto/
├── events/
├── http/
├── generated/
└── README.md

## Required metadata for each contract area
Document:
* owner
* consumers
* versioning policy
* generation method
* compatibility expectations

## Migration rule
If a shared contract exists in multiple service-local locations:
1. select the canonical definition
2. move it under contracts/
3. update consumers
4. delete or archive duplicate local copies after validation
EOF

cat > docs/monorepo-audit-template.md <<'EOF'
# Monorepo Audit Template

## Audit date
YYYY-MM-DD

## Auditor
name

## Scope
Describe which parts of the monorepo were audited.

### 1. Canonical repo audit
| Repo | Status | Canonical path | Duplicate paths found | Archived paths | Notes |
|------|--------|----------------|-----------------------|----------------|-------|
| pnkln-stack-fastapi-services | | | | | |
| cosmic-crab-payload | | | | | |
| Pipeline | | | | | |
| nascent-apollo | | | | | |

Questions
* Are any repos still unresolved?
* Does each canonical repo have exactly one live root?
* Are any duplicate live roots still present?

Findings
* Good:
* Bad:
* Action required:

### 2. Live tree cleanliness audit
Questions
* Are there any live backup trees?
* Are there any live recovered trees?
* Are there any nested legacy repos in live code?
* Is raw ingest still inside live paths?

Findings
| Path | Category | Should stay | Should archive | Should delete later | Notes |
|------|----------|-------------|----------------|---------------------|-------|

Action required
*

### 3. GitHub governance audit
Questions
* Is main protected?
* Are PRs required?
* Are code owner reviews required?
* Are bazel-build and bazel-test required?

Findings
* Ruleset:
* CODEOWNERS present:
* Required checks present:
* Direct push blocked:

Action required
*

### 4. Build / CI audit
Questions
* Does bazel build //... pass?
* Does bazel test //... pass?
* Is archive material excluded from active CI scope?

Findings
* Last green build:
* Last green test:
* Known flaky path:
* Notes:

Action required
*

### 5. third_party audit
Questions
* Are vendored dependencies centralized under third_party/?
* Are app-local vendor mirrors still present?
* Does each vendored dependency have metadata and owner?

Findings
| Dependency | Canonical location | Duplicate location(s) | Owner | Status | Notes |
|------------|-------------------|-----------------------|-------|--------|-------|

Action required
*

### 6. Contracts audit
Questions
* Is there one shared contract root?
* Are duplicated service-local contracts still present?
* Are shared schemas being consumed from the canonical root?

Findings
| Contract area | Canonical location | Duplicate location(s) | Consumers | Status | Notes |
|---------------|-------------------|-----------------------|-----------|--------|-------|

Action required
*

### 7. Workspace / tooling audit
Questions
* Is workspace root stable?
* Is Python interpreter stable?
* Is basedpyright narrowed to canonical roots?
* Are denied zones excluded by default?

Findings
* Active interpreter:
* Basedpyright source file count:
* Workspace root:
* Drift observed:
* Notes:

Action required
*

### 8. MCP stack audit
Questions
* Which MCP servers are enabled by default?
* Which are timing out?
* Are secrets kept out of repo config?
* Is Chrome DevTools MCP healthy?

Findings
| MCP server | Enabled | Healthy | Auth method | Last validated | Notes |
|------------|---------|---------|-------------|----------------|-------|
| chrome-devtools | | | | | |
| google-developer-knowledge | | | | | |
| firebase-mcp-server | | | | | |
| mcp-toolbox-for-databases | | | | | |
| sequential-thinking | | | | | |

Action required
*

### Overall audit score
| Category | Weight | Score | Weighted score |
|----------|-------:|------:|---------------:|
| Canonical repo resolution | 20 | | |
| Live tree cleanliness | 20 | | |
| GitHub governance | 15 | | |
| Bazel / CI reliability | 15 | | |
| third_party discipline | 10 | | |
| Shared contracts | 10 | | |
| Workspace / tooling stability | 5 | | |
| MCP stack stability | 5 | | |
| **Total** | | | **__/100** |

## Executive summary
Write 3–7 sentences covering:
* current state
* most important improvement
* biggest blocker
* what must happen next
EOF

echo
echo "Wrote:"
echo " ${ROOT}/third_party/README.md"
echo " ${ROOT}/contracts/README.md"
echo " ${ROOT}/docs/monorepo-audit-template.md"
echo
echo "Suggested next step:"
echo " git add third_party/README.md contracts/README.md docs/monorepo-audit-template.md"
echo " git commit -m 'docs(monorepo): add third_party policy, contracts guide, and audit template'"
