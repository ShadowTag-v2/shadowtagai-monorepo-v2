# True Obsidian — Target Architecture Roadmap

> This document captures the FULL aspirational architecture for the True Obsidian
> system. Many components described here do NOT yet exist as implemented code.
> They are preserved as design specifications for future implementation phases.

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Implemented and operational |
| 🔧 | Partially implemented |
| 📋 | Documented, not implemented |
| ❌ | Blocked on external dependency |

## Layer 1: Silicon Chassis (IDE Integration)

**Status: 📋 Aspirational — requires VS Code fork or Electron patches**

The Silicon Chassis layer describes IDE-level modifications for deep integration:

- **VS Code Extension API patches** — Custom sidebar, vault browser, knowledge graph viewer
- **Tauri Rust backend** — Native desktop shell replacing Electron for lower memory footprint
- **AdminLTE React dashboard** — Real-time monitoring UI for vault health, pipeline metrics
- **Electron IPC bridge** — Direct communication between IDE and vault daemon

> [!NOTE]
> These require forking VS Code or building a custom IDE extension. Current
> implementation uses COR.KAIROS daemon + MCP servers as the integration layer instead.

## Layer 2: Intelligence Pipeline (Implemented ✅)

The middleware layer that processes data through the vault:

| Component | File | Status |
|-----------|------|--------|
| Zero Trust Pipeline | `scripts/vault/zero_trust_pipeline.py` | ✅ |
| Pathway Ingest | `scripts/vault/pathway_ingest.py` | ✅ |
| Intelligence Router | `scripts/vault/intelligence_router.py` | ✅ |
| Secret Manager Utility | `scripts/vault/secret_manager_util.py` | ✅ |
| Existing Pipeline | `scripts/intelligence_pipeline/` | ✅ |

## Layer 3: Compute Plane (Partial)

| Component | Status | Notes |
|-----------|--------|-------|
| Go Ingress Firewall | 📋 | Would replace Python-level request validation with Go-native perf |
| C++ Monte Carlo Hot Path | 📋 | Financial modeling acceleration via native code |
| Nginx Relay Config | 📋 | Reverse proxy for multi-service routing |
| Cloud Run Services | ✅ | CounselConduit v3.2.0 LIVE |

## Layer 4: Infrastructure (Partial)

| Component | Status | Notes |
|-----------|--------|-------|
| Terraform FedRAMP | 📋 | Phase 4 enterprise requirement |
| Cloud Armor WAF | ✅ | Deployed on Cloud Run |
| Secret Manager | ✅ | All secrets migrated from .env |
| Firestore | ✅ | Canonical database |
| Cloud Tasks | ✅ | Exclusive queue broker |

## Layer 5: Observability

| Component | Status | Notes |
|-----------|--------|-------|
| COR.KAIROS Daemon | ✅ | Background autonomous agent |
| Dream Consolidation | ✅ | Nightly KI maintenance |
| Loop Steward | ✅ | Autonomous task continuation |
| Vault Monitor | ✅ | Pipeline metrics in `vault/monitor/` |

## Future Phase: Go Ingress Firewall

```go
// ASPIRATIONAL — not implemented
// Would provide native-speed request validation at the edge
// Target: Phase 4 Enterprise
package main

// See full spec in original True Obsidian design document
```

## Future Phase: C++ Monte Carlo Engine

```cpp
// ASPIRATIONAL — not implemented
// Would accelerate financial modeling for pricing optimization
// Target: Phase 4 Enterprise, requires CMake integration
```

## Future Phase: Tauri Desktop Shell

```rust
// ASPIRATIONAL — not implemented
// Would replace Electron with native Rust backend
// Target: Post-v1.0 when IDE extension matures
```
