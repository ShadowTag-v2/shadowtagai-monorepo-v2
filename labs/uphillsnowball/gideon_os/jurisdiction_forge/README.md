# Jurisdiction Forge

> Gideon OS Block 8 — Legal Jurisdiction Routing Engine

## Purpose

Jurisdiction Forge determines the applicable legal jurisdiction for all data processing, storage, and AI inference operations within CounselConduit. It enforces data residency requirements and routes operations to jurisdiction-appropriate infrastructure.

## Architecture

```
┌─────────────────────────────────────────┐
│          Jurisdiction Forge             │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │     Jurisdiction Classifier       │  │
│  │  • Client IP geolocation          │  │
│  │  • Bar admission state mapping    │  │
│  │  • Matter jurisdiction override   │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│  ┌──────────────▼────────────────────┐  │
│  │      Routing Policy Engine        │  │
│  │  • Data residency rules           │  │
│  │  • Cross-border transfer gates    │  │
│  │  • Privilege preservation rules   │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│  ┌──────────────▼────────────────────┐  │
│  │    Compliance Audit Logger        │  │
│  │  → .beads/jurisdiction_log.jsonl  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| State Bar Mapping | Maps attorney bar admissions to applicable jurisdictions |
| Data Residency | Enforces storage location constraints per jurisdiction |
| Cross-Border Gates | Controls international data transfers (GDPR Article 46+) |
| Privilege Routing | Routes AI queries through privilege-preserving pathways |
| Audit Logging | Complete jurisdiction decision audit trail |

## Jurisdiction Rules

| Jurisdiction | Data Residency | AI Model Routing | Privilege Standard |
|-------------|---------------|-------------------|-------------------|
| US Federal | US-only | Any US region | Attorney-Client (FRE 502) |
| US State | State-specific | Same region preferred | State bar rules |
| EU/EEA | EU-only | EU endpoints only | GDPR + Legal Professional Privilege |
| UK | UK-only | UK endpoints | UK LPP |

## Integration Points

- **Shield1 Ingress**: Receives jurisdiction hints from IP geolocation
- **Zero Trust Pipeline**: Enforces jurisdiction constraints on data flow
- **Vault Constitution**: Jurisdiction-aware access policies
- **CounselConduit API**: Matter-level jurisdiction overrides

## Status

🔶 Scaffolded — Classifier logic defined, routing policy engine pending Firestore rules integration.
