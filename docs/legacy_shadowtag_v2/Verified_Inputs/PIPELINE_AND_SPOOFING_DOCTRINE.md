# Pipeline & Spoofing Doctrine (Verified Input)

> **SOURCE**: iPhone Notes (User Provided)
> **CLASSIFICATION**: TECHNICAL DOCTRINE
> **STATUS**: COMPLIANT IMPLEMENTATION

## Principle: No Spoofing / No MITM

We do **not** fake entitlements or hook private extension internals.

- **Excluded**: Paywalled features without paying, private APIs, hosted vendor indexes.
- **Included**: Use official SDKs or local proxies. Your data, your index (GPTRAM/SQLite).

## The "Universal Copilot" Architecture

- **UX**: Browser/editor widget ("Send selection -> Get patch").
- **Routing**: Multi-LLM support (OpenAI, Anthropic, Mock).
- **Safety**: Clear logs, cost tracking, zero gray-area traffic.

## Mock Setup (mock-universal-copilot)

A minimal, dependency-free testbed to simulate the "Select -> Think -> Patch" flow.

- **Router**: Logic to choose provider and enforce limits.
- **Mock Provider**: Deterministic responses for CI/Testing.
- **Patching**: Simulates applying the diff to the file.
