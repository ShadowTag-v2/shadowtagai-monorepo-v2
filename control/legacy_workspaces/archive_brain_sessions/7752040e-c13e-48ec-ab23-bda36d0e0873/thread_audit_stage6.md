# Omni-Sweep Stage 6: The Final Google-Native Excellence Audit

## 1. Executive Directive

“It is not enough for the system to function. It must become the obvious and durable architecture.”

We have already consolidated major infrastructure, stabilized the MCP layer, improved data tooling, and removed large classes of integration drift. Stage 6 exists to close the gap between a rushed prototype and a disciplined production system.

This stage is not about adding novelty. It is about:
* removing ambiguity,
* aligning each product to its real mission,
* hardening the runtime,
* and making the commercial path inevitable.

### Product split, clarified

**UphillSnowball**
* Personal-use performance lab
* Runs locally on Apple Silicon
* May use ANE / Metal / MPS optimizations
* Used for experimentation, local indexing, benchmarking, and developer acceleration
* Not the production architecture for CounselConduit

**CounselConduit**
* Customer-facing legal workflow product
* MVP must be production-ready now
* Google-native by default
* Uses Gemini tool calls and Google Cloud services
* Optimized for security, reliability, auditability, and rapid commercialization

## 2. Stage 6 Audit Targets

### A. Legal Workflow Classification Hardening
**Original state:** scattered references to legal/privileged handling without a real system boundary.
**Stage 6 target:** formal legal workflow metadata classification across requests, traces, documents, and storage writes.
* **Fields Required:** `workflow_scope`, `document_sensitivity`, `privilege_candidate`, `retention_policy`.

### B. Pricing Intelligence Rewrite
**Original state:** hardcoded or arbitrary savings logic (Fear & Greed).
**Stage 6 target:** transparent, value-based pricing intelligence that supports CounselConduit commercialization.
* **Logic:** Generate ROI narrative based on regional market rates, time-saved assumptions, and review intensity. No deceptive "pain threshold" language.

### C. UphillSnowball Apple Silicon Performance Hardening
**Original state:** local vector/embedding work exists blindly.
**Stage 6 target:** make UphillSnowball a true Apple Silicon local acceleration sandbox targeting `torch.device("mps")` securely behind `UPHILLSNOWBALL_LOCAL_ACCEL=1` flags.

### D. Confidential Review Surface Hardening
**Original state:** vaguely defined.
**Stage 6 target:** production-grade confidential review mode (`ephemeral_review_hardening`) enforcing `Cache-Control: no-store`, `X-Frame-Options: DENY`, and short-lived review tokens.

## 3. The Final Architecture
**UphillSnowball = local performance lab**
**CounselConduit = Google-native product**
