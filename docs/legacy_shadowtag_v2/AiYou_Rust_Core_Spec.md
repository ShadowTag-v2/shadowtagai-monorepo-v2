# pnkln-stack Core Proxy Spec (Rust/Oxy Model)

> **BASED ON**: Cloudflare FL2 / Oxy Architecture
> **GOAL**: High-performance, modular inference & RAG routing.

## 1. ARCHITECTURE

- **Language**: Rust (Memory safety, concurrency).
- **Pattern**: Modular Proxy (Oxy-like).
- **Components**:
  - **Ingestion Module**: Validation, sanitization.
  - **Routing Module**: Traffic direction (RAG vs Inference).
  - **Safety Module**: pnkln-stackJR policies (Compliance Framework).

## 2. KEY PATTERNS

- **Graceful Restarts**: Systemd socket activation. Zero-downtime upgrades.
- **Fallback**: Automatic downgrade to legacy path (FL1/CUDA) on failure.
- **Strict Contracts**: Compile-time enforcement of module boundaries.

## 3. ROLLOUT STRATEGY ("Flamingo-Lite")

1.  **Dual Run**: Run new Core Proxy alongside legacy.
2.  **Compare**: Validate outputs & latency.
3.  **Switch**: Gradual traffic shift.
4.  **Rollback**: Auto-trigger on metric slip.

## 4. MVP TIMELINE IMPACT

- **Current State**: ~60% Complete (Infra + Back-end).
- **With Rust Core**: Accelerates remaining 40% (Product/Scale).
- **Target**: MVP in <4 months.
