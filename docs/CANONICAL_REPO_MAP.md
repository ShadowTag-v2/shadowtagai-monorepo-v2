# CANONICAL_REPO_MAP.md — v1.0

> Canonical directory structure for `ShadowTag-v2/Monorepo-Uphillsnowball`.
> This map supersedes all ad-hoc directory trees. Drift guard enforces compliance.

## Canonical Layout

```
Monorepo-Uphillsnowball/
├── apps/                       # Deployable applications
│   ├── counselconduit/         # CounselConduit Cloud Run API (v3.2.0 LIVE)
│   ├── kovelai/                # KovelAI Firebase Hosting (marketing + app)
│   ├── shadowtagai/            # ShadowTag Firebase Hosting
│   ├── lead-capture-router/    # Lead capture Cloud Function
│   ├── counselconduit-dashboard/ # Admin dashboard
│   └── [30+ reference/archived apps] # Most are fold-in from 56-repo merge
│
├── libs/                       # Shared libraries
│   ├── autoresearch_sources/   # Research agent sources
│   ├── steel/                  # Browser automation (Navigator/Jetski)
│   └── [shared utilities]
│
├── labs/                       # R&D only — never deployed
│   └── uphillsnowball/         # Core R&D lab
│       ├── gideon-os/          # 14-block sovereign OS (7 languages)
│       └── [experimental work]
│
├── packages/                   # Internal packages
│   ├── core/                   # ShadowTag core (locked)
│   └── ag-ui/                  # AG-UI components (active)
│
├── scripts/                    # Operational scripts (352 files)
│   ├── preflight_gate.sh       # ⭐ MANDATORY pre-commit gate
│   ├── pnkln_root_guard.sh     # Root context guard
│   ├── audit_monorepo_state.sh # Structural audit
│   ├── verify_mcp.sh           # MCP stack verification
│   ├── finish_changes.py       # Standardized commit flow
│   ├── repo_doctor.py          # ⭐ Automated repo health check
│   ├── auth_github_app.py      # GitHub App JWT auth (5-tier PEM)
│   └── load_mcp_secrets.sh     # Secret Manager loader
│
├── tools/                      # External tooling
│   ├── external_sdks/          # .gitignored cloned reference repos
│   ├── security/               # Security tooling
│   └── [SDK references]
│
├── docs/                       # Documentation
│   ├── SECURITY_DOD.md         # Cor.30 security checklist
│   ├── SECRET_ROTATION.md      # Secret rotation procedures
│   ├── CANONICAL_REPO_MAP.md   # ⭐ THIS FILE
│   └── REPO_MAINTENANCE_RUNBOOK.md # ⭐ Maintenance procedures
│
├── infra/                      # Infrastructure as Code
│   └── terraform/              # OpenTofu/Terraform configs
│
├── vault/                      # True Obsidian intelligence pipeline
│   ├── ingest/                 # .gitignored — raw data
│   ├── quarantine/             # .gitignored — IPI isolation
│   ├── embed/                  # .gitignored — vector embeddings
│   ├── serve/                  # Retrieval layer
│   └── monitor/                # Pipeline monitoring
│
├── archive/                    # Dead code — read-only reference
│   ├── Code_Legacy/
│   ├── agent_debris/
│   ├── broken/
│   └── [historical artifacts]
│
├── third_party/                # .gitignored third-party repos
│
├── .agent/                     # Agent runtime config
│   ├── workflows/              # Workflow definitions
│   ├── rules/                  # Agent rules
│   └── skills/                 # Agent skills (secondary)
│
├── .agents/                    # Agent skills & characters
│   ├── skills/                 # Primary agent skills
│   └── characters/             # Agent personas
│
└── [Root Truth Files]
    ├── AGENTS.md               # ⭐ Canonical agent contract
    ├── GEMINI.md               # Operator invariants
    ├── CLAUDE.md               # Thin shim
    ├── monorepo_manifest.yaml  # ⭐ Workspace truth
    ├── RISK_REGISTER.md        # Operational risks
    ├── BUSINESS_CONTEXT_LOCKED.md # Pricing/architecture
    ├── .betterleaks.toml       # Secret scanner config
    ├── .betterleaksignore      # Allowlisted fingerprints
    ├── .gitleaksignore         # Legacy allowlist (compat)
    ├── .pre-commit-config.yaml # Pre-commit hooks
    └── pyrightconfig.json      # Python type checking
```

## Canonical Apps (Active)

| App | Path | Runtime | Status | Brand Role |
|-----|------|---------|--------|------------|
| CounselConduit | `apps/counselconduit/` | Cloud Run | v3.2.0 LIVE | Product API |
| KovelAI | `apps/kovelai/` | Firebase Hosting | LIVE | Marketing Website |
| ShadowTagAI | `apps/shadowtagai/` | Firebase Hosting | LIVE | Parent Brand |
| Lead Capture | `apps/lead-capture-router/` | Cloud Function | LIVE | Lead Gen |
| CC Dashboard | `apps/counselconduit-dashboard/` | Firebase Hosting | Dev | Admin UI |

## Gitignored Paths (On Disk, Never Committed)

| Path | Purpose | Size |
|------|---------|------|
| `external_repos/` | Cloned reference repos | ~2GB |
| `tools/external_sdks/` | SDK clones (betterleaks, swarm, etc.) | ~500MB |
| `third_party/security/` | Security tool sources | ~200MB |
| `browser_artifacts/` | Agent browser screenshots | Variable |
| `.lancedb/` | Local vector embeddings | ~1GB |
| `vault/ingest/`, `vault/quarantine/`, `vault/embed/` | Intelligence pipeline | Variable |
| `archive/recovered_assets/` | Historical debris | ~500MB |

## Anti-Drift Rules

1. **No new top-level directories** without updating this map and `monorepo_manifest.yaml`.
2. **All new apps** go under `apps/`. All new libraries go under `libs/`.
3. **All R&D** goes under `labs/uphillsnowball/`.
4. **All external code** goes under `tools/external_sdks/` (gitignored).
5. **All archived code** goes under `archive/` with a `MIGRATED_FROM.md`.
6. **Scripts** stay in `scripts/` unless they're app-specific.
7. **Infrastructure** stays in `infra/terraform/`.
