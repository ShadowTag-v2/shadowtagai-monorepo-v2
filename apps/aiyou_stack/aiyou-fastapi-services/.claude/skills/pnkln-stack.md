# SKILL: Pnkln Core Stack Technical Assistant

## ARCHITECTURE CONTEXT
- Judge #6: 3-layer hybrid (Gemini+PyTorch+rules), p99≤90ms required
- JR Engine: Decision validation layer, <500μs processing
- Cor.53: Orchestration backbone, <1ms latency target
- NS: Namespace isolation, <100μs routing
- ShadowTag: DCT watermarking with C2PA integration
- Orchestrator: LLM routing (Gemini 40%, Claude 35%, GPT-5 15%, Grok 5%)

## GKE DEPLOYMENT
Using accelerated-platforms reference:
- 4 namespaces: ShadowTag-v2jr-governance, autogen-orchestration, cognitive-stack-v5, shadowtag-v2
- Target: $60-65K monthly burn
- Hypercomputer integration for ML workloads
- TPU v5e for inference acceleration

## TECHNICAL CONSTRAINTS
- All components must be stateless
- Event-driven coordination only
- Deterministic replay requirement
- Fail-fast on constraint violations
- No unencrypted data ever

## CODE OUTPUT
- Always use monospace formatting
- Include latency annotations
- Provide memory/compute estimates
- Note bootstrap compliance
