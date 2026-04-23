---
name: epistemic-airgap
description: >
  Strict cognitive routing protocol for differentiating between Public Domain
  discovery (web search, public git) and Proprietary Private discovery
  (Corporate Monorepo). Enforces DLP circuit breaker to prevent IP leakage
  via public search tools.
---
# The Epistemic Airgap & DLP Doctrine

> **V10 Directive** — Zero-Trust Cognitive Routing for Split-Brain Agent Operations

## 0. Activation Triggers

This skill activates when:
- The agent encounters an import it cannot resolve locally
- The agent is about to search the web for an error containing proprietary identifiers
- The agent is asked about internal microservices, corporate APIs, or shared UI libraries
- Any `pip install` or `npm install` command targets a package not in the public registry

## 1. The Cognitive Boundary (Where to Search)

You possess **distinct search capabilities**. You **MUST** pause and classify your intent before executing a tool:

### Route A: Internal IP (Proprietary)
**Trigger:** Internal microservice, proprietary UI token, shared corporate type, internal billing module, corporate database schema, internal API endpoint.

**Action:** Route to `search_corporate_ip` — execute `rg` or `ast-grep` **strictly** within `./external_repos/corp-monorepo/`. Never touch the public web.

```bash
# Ripgrep for text search
rg --type py --type ts "$SEARCH_TERM" ./external_repos/corp-monorepo/

# AST-Grep for structural patterns
sg scan --pattern "$AST_PATTERN" ./external_repos/corp-monorepo/
```

### Route B: Public IP (Open Source)
**Trigger:** Public library (React, FastAPI, Firebase), open-source documentation, competitor analysis, public API docs.

**Action:** Route to `google-developer-knowledge` MCP, `search_web`, or browser tools. Standard search hygiene applies.

### Route C: Hybrid (Internal + Public Intersection)
**Trigger:** Internal code that wraps or extends a public library.

**Action:**
1. First, search `./external_repos/corp-monorepo/` for the internal wrapper
2. Then, search public docs for the underlying library
3. Perform intersection **locally in agent RAM** — never paste internal identifiers into public queries

## 2. 🔴 Data Leak Prevention (DLP Circuit Breaker)

### ABSOLUTE PROHIBITIONS

You are **strictly PROHIBITED** from passing the following into public search tools (`search_web`, `google-developer-knowledge`, browser navigation):

| Category | Examples | Why |
|----------|----------|-----|
| **Proprietary variable names** | `internal_billing_core`, `kovel_attestation_hash` | Reveals internal architecture |
| **Corporate database schemas** | Table names, column names, Firestore collection paths | Reveals data model |
| **Internal IP addresses** | `10.x.x.x`, private Cloud Run URLs | Reveals infrastructure |
| **Corporate API keys/secrets** | Any string from `.env` or Secret Manager | Direct credential leak |
| **Internal error traces** | Stack traces containing proprietary module paths | Reveals code structure |
| **Internal package names** | Any `import` that resolves only in corp-monorepo | Supply chain attack vector |

### Sanitization Protocol

If you MUST search publicly for an error that contains proprietary identifiers:

1. **Extract** the generic error type (e.g., `TypeError`, `ConnectionRefused`)
2. **Extract** the public library name (e.g., `sqlalchemy`, `firebase-admin`)
3. **Strip** all proprietary paths, variable names, and internal identifiers
4. **Construct** a generic public query using ONLY public library + error type
5. **Search** with the sanitized query

**Example:**
```
# PROHIBITED (leaks internal architecture):
search_web("kovel_attestation_service.py line 42 KovelHashMismatchError in _validate_hmac_chain")

# CORRECT (sanitized):
search_web("HMAC SHA256 validation error Python mismatch hash comparison")
```

### PROPRIETARY ISOLATION (Mandatory Enforcement)

> **PROPRIETARY ISOLATION:** Internal IP searches MUST route to local `rg`/`ast-grep` against `./external_repos/corp-monorepo/`. Never leak corporate schemas, internal API keys, proprietary variable names, or internal module paths to the open web or public MCPs. This is a non-negotiable DLP enforcement — violation constitutes an IP leak incident.

## 3. Supply Chain Protection (Dependency Confusion Prevention)

### The Samsung Problem — Prevention Protocol

When the agent encounters an unresolved import:

1. **NEVER** run `pip install <unknown_package>` without verification
2. **FIRST** check if the package exists in `./external_repos/corp-monorepo/`
3. **SECOND** check if it's in `requirements.txt`, `pyproject.toml`, or `package.json`
4. **THIRD** verify the package exists on the **official** PyPI/NPM registry
5. **IF** the package name matches an internal module name → **HALT** and warn the user

```python
# PROHIBITED: Blind install of unknown package
# pip install internal_billing_core  ← SUPPLY CHAIN ATTACK VECTOR

# CORRECT: Check local resolution first
# 1. rg "internal_billing_core" ./external_repos/corp-monorepo/
# 2. Check if it's a local module with __init__.py
# 3. If not found locally, ASK THE USER before any install
```

### Pyright Integration

`pyrightconfig.json` includes `external_repos/corp-monorepo` in `extraPaths`. This means:
- Internal imports resolve locally without hitting public registries
- Pyright will not flag internal imports as "missing"
- No phantom `pip install` suggestions for internal packages

## 4. Cognitive Cross-Referencing (The Override Rule)

When asked to build a feature that intersects internal and public code:

1. **ALWAYS** check `./external_repos/corp-monorepo/` first via ripgrep/ast-grep
2. If a proprietary internal API and a public open-source pattern conflict:
   - **The proprietary corporate code ALWAYS overrides public internet patterns**
   - Inherit corporate interfaces over hallucinated public ones
3. If corp-monorepo is empty, prompt the user to clone securely:
   ```
   "The corporate monorepo at ./external_repos/corp-monorepo/ is empty.
   Please clone your corporate repo securely using your authorized GitHub CLI:
   git clone git@github.com:YourOrg/corp-monorepo.git ./external_repos/corp-monorepo/"
   ```

## 5. Audit Trail

Every search routed through this doctrine MUST be logged mentally:
- **Route taken:** A (Internal) / B (Public) / C (Hybrid)
- **Sanitization applied:** Yes/No
- **DLP check passed:** Yes/No

## 6. Integration with Existing Doctrine

| Existing Rule | Airgap Extension |
|---------------|------------------|
| Cor.30 R3 (Secrets) | Extended to cover proprietary identifiers in search queries |
| OWASP LLM01 (Prompt Injection) | Internal code never injected into public prompts |
| OWASP LLM02 (Sensitive Info) | DLP circuit breaker enforces stripping |
| GitHub Doctrine (SSH Primary) | Corp monorepo cloned via SSH only |
| Security Ghost Mode | Proprietary paths excluded from all telemetry |
