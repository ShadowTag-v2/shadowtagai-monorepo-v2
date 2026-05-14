# Pnkln Platform — System Architecture

**Agent:** 2 — Architecture Reconstructor
**Target:** `shadowtag-omega-v4`

## Core Directory Structure

```text
pnkln-platform/
├── core/                       # Foundational interfaces and execution shells
│   ├── auth/                   # Identity handling (Supabase/Auth0 bindings per COR.30)
│   ├── database/               # PostgreSQL/AlloyDB connectors with strict RLS
│   └── state/                  # High-speed transient state (Redis/Memory MCP integration)
├── agent_engine/               # Swarm & Orchestration
│   ├── sequential_thinking/    # The formal reasoning engine (Process)
│   ├── flying_monkeys/         # The execution swarm routers
│   └── validators/             # Loop handlers enforcing Judge #6 compliance
├── prompt_registry/            # Versioned agent personas and instructions
├── rag_engine/                 # Vector Retrieval System
│   ├── ingestion/              # Ingest pipelines for docs/code
│   └── embedding/              # LLMLingua / Module 11 compression layer
├── policy_engine/              # Automated Governance
│   ├── pre_commit_hooks/       # Design Police (Gate 0)
│   ├── git_intercepts/         # Credential Scanners
│   └── compliance/             # RMF/cATO ongoing operations
├── valuation_engine/           # Automated ARR / Runway Metrics reporting
├── training_pipeline/          # Future fine-tuning dataset aggregators
├── ocr_pipeline/               # Tegu Vision extraction matrices
├── api_gateway/                # Express/FastAPI rate-limited routers
├── observability/              # Telemetry & Tracing
│   ├── structured_logs/        # Winston/Sentry outputs (No secrets/PII)
│   └── audit_ledgers/          # Immutable GDPR compliance logs
├── ui_device_layer/            # Client Presentation
│   ├── a2ui_renderer/          # React Native/Flutter streaming ingestion
│   └── interceptors/           # Local state handlers
└── security/                   # Centralized crypto
    ├── jwt_rotation/           # Token issuers (15min max)
    └── secret_manager/         # GCP/Vault key rotations
```

## System Tenets

1. **Gate 0 Enforcement**: Custom linters act as the unbreakable structural barrier before LLM logic evaluation.
2. **State vs Process Isolation**: Memory servers strictly hold context; computation servers strictly perform analysis.
3. **Hermetic Edge**: Code relies natively on Google Cloud Run & GCP Secret constraints.
