# DECISION LOG: Cloudflare Rust Migration (Cor.72)

> **DATE**: 2026-02-02
> **STATUS**: ADOPTED
> **OWNER**: ANTIGRAVITY (Founder Proxy)

## 1. CONTEXT

Scaling pnkln-stack's inference and RAG infrastructure requires robust, low-latency performance. We faced a choice: build a custom Python/Lua scaffold (slow, risk of brittleness) or adopt the Cloudflare "FL2" Rust modularization pattern.

## 2. OPTIONS

- **Option A**: Custom Python/Lua Glue. (High risk, slow scaling).
- **Option B**: Cloudflare FL2 / Oxy Framework. (Rust-based, modular, proven).

## 3. RISKS (Option A)

- **Fragility**: Runtime bugs common in loose typing.
- **Latency**: High overhead for RAG routing.
- **Time**: 9-12 months architecture churn.

## 4. RECOMMENDATION (ADOPTED)

**Adopt Option B (Cloudflare FL2 Model).**

- **Why**:
  - **Time Saved**: ~12 months (Architecture refactor avoidance).
  - **Money Saved**: $0.5M-$1M (Headcount efficiency).
  - **Performance**: +25% limit lift, -60% crash rate.
  - **Strategic**: Accelerates MVP timeline to <6 months.

## 5. IMPACT

- **Architecture**: Shift to Rust-based "pnkln-stack Core Proxy".
- **MVP**: "YouTube of AI" pitch powered by industrial-grade infra.
- **Valuation**: Demonstrates "Cloudflare-class" rigor to investors/partners (CoreWeave/NVIDIA).
