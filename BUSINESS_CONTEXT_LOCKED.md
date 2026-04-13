# BUSINESS_CONTEXT_LOCKED — v8.4

## Consumer Syndicate
- Price: `$149/mo`
- Margin: `95%`
- Architecture: `Centralized Hive Mind Oracle + Stateless Micro-Edge`

## Enterprise Base SLA
- Price: `$20,000/mo`
- Margin: `69–71%`
- Core value: `Zero-latency AST risk mitigation`
- Isolation: `Dedicated GCP sidecar`

## Enterprise EU26 Premium
- Price: `$28,333/mo`
- Margin: `76–78%`
- Core value: `higher-assurance compliance and enterprise isolation posture`

## Sovereign Scale
- Customer pays `100% compute pass-through`
- Software margin retained on the base license

## Latency doctrine
- Target: `p99 <= 90ms total application path` where the architecture permits

## Architectural split
- Consumer path: centralized intelligence + stateless micro-edge
- Enterprise path: tenant-isolated sidecars + stronger controls + mTLS

## Rule
Do not mix these lanes casually. Consumer and enterprise economics are different products.

## Hardened State
- v8.4 canonicalized: 2026-04-13
- Commit: `c279f820037`
- Lighthouse: A97 / BP100 / SEO100
- Structural tests: 30/30
- Dead code: clean (vulture + ruff)
