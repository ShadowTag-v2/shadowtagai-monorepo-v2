# Uphill Snowball

**Sovereign Enterprise AI Infrastructure — The Cryptographic Firewall for Agent-Native Deployment**

> *Corporate AI policies are dead. We own the firewall. We charge for the outcome.*

---

## The Problem

Sullivan & Cromwell — Wall Street's most prestigious legal fortress — was forced to apologize to a Federal Judge for AI hallucinations in April 2026. Their defense? *"Our training repeatedly emphasizes the risk of AI 'hallucinations'... It instructs lawyers to 'trust nothing and verify everything.'"*

They brought an Office Manual to an algorithmic gunfight.

**Human policy cannot scale to govern generative AI.** An exhausted associate billing 80 hours a week cannot out-verify a probabilistic token generator. Code is physics. Policy is paper.

## The Architecture

Uphill Snowball is the enterprise AI security firewall that makes deploying autonomous agents **legal and survivable**.

```
┌─────────────────────────────────────────────────────────┐
│                   UPHILL SNOWBALL                        │
│                                                         │
│  Client → Cor-Go PEP → Temporal.io → ScholarEval       │
│              │              │              │             │
│         AST Pre-Crime   Durable Exec   PACER API        │
│              │              │              │             │
│           RKILL?        KICKBACK?      Citation OK?     │
│              ↓              ↓              ↓             │
│         423 Locked    Rewrite + Bill    Release          │
│                             │                            │
│                    Stripe Meter Event                    │
│                  (Kinetic Outcome Tax)                   │
│                             │                            │
│                    Splinter Engine                       │
│               (Distribution Moat Auto-Post)             │
└─────────────────────────────────────────────────────────┘
```

## Kernel Structure

```
labs/uphillsnowball/
├── cmd/cor-go/
│   └── pep_and_billing.go      # Zero Trust PEP + Stripe Metered Billing
├── src/
│   ├── contracts/
│   │   └── constitution.py     # SHA-256 Immutable Call of Question
│   ├── intelligence/
│   │   └── scholar_eval.py     # Epistemological Forensics (S&C Cure)
│   ├── governance/             # Judge 6.1 Policy Engine
│   ├── workflows/
│   │   └── uphill_temporal_mdo.py  # FM 5-0 Temporal Campaign Loop
│   ├── delivery/
│   │   └── splinter_io.py      # J-39 Information Ops / Distribution Moat
│   └── edge/
│       └── MobileTOC.tsx       # Theater Command PWA (C2 Glass)
├── Dockerfile                  # Multi-stage: Rust + Go + Python
├── Makefile                    # Cloud Run source deploy
├── requirements.txt            # Python dependencies
└── EXECUTIVE_BRIEFING.md       # Investor deck (non-technical)
```

## Core Components

| Component | Language | Purpose |
|-----------|----------|---------|
| **Cor-Go PEP** | Go | Zero Trust Policy Enforcement Point |
| **ScholarEval** | Python | Epistemological Forensics (citation verification) |
| **Temporal MDO** | Python | FM 5-0 Durable Execution Campaign Loop |
| **Splinter IO** | Python | J-39 Distribution Moat (Google Cloud Tasks) |
| **Constitution** | Python | SHA-256 Immutable Mission Contracts |
| **MobileTOC** | React/TSX | Theater Command PWA |

## Pricing: Kinetic Outcome Economics

We don't charge per seat. We tax the outcome.

| Outcome | Fee |
|---------|-----|
| Legal Hallucination Averted | $1,000 |
| Compliance Breach Mitigated | $500 |
| SaaS Workflow Automated | $150 |
| Enterprise Platform (monthly) | $20,000 |

## Deploy

```bash
# Local development
make test
make lint
make docker-build

# Production (Cloud Run)
make deploy-kernel
make deploy-workers
```

## License

Proprietary — Uphill Snowball, Inc. 2026.
