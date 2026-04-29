# Core Governance Control Plane

Cor.Claude_Code_6 engine, RKILL protocol, and governance tools for the ShadowTag monorepo.

## Components
- `Cor.Claude_Code_6_core.py` — Policy evaluation engine
- `Cor.Claude_Code_6_factory.py` — Rule factory and composition
- `judge_architecture.py` — Architectural constraint enforcement
- `rkill.py` — Circuit breaker against hallucination

## Integration
All governance checks run as pre-commit and CI gates.
