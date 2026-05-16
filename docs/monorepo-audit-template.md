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
| aiyou-fastapi-services | | | | | |
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
