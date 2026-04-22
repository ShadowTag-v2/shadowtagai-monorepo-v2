# KovelAI + CounselConduit — Business Plan v2.2

> **Codename**: War Room
> **Status**: LOCKED — Board-approved
> **Last Updated**: 2026-04-22
> **Predecessor**: BUSINESS_CONTEXT_LOCKED.md

---

## Executive Summary

CounselConduit is the **"Shopify for Legal AI"** — a privilege-preserving B2B router between law firms and foundational LLMs, protected under *United States v. Heppner* (S.D.N.Y. Feb. 10, 2026). KovelAI is the client-facing AI portal that converts panicked midnight callers into paid, privilege-sealed matters.

### The War Room Add-On

The **War Room** (internally: Oracle Studio + Murder Board) adds a 7-step cognitive pipeline that transforms raw client transcripts into board-ready litigation intelligence. It is the premium differentiation layer that separates KovelAI from commodity LLM wrappers.

---

## Product Architecture

### Three Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Solo Practitioner** | $299/mo | Triage + Vent Mode + S.E.U. + 1 model |
| **Practice** (3-10 attorneys) | $599/mo | + Oracle Studio + Multi-model + Clio Vault |
| **Enterprise** | $999+/mo | + War Room + BYOK + Sandbox + Precedent Vaults |

### Dual-Billing Engine (Stripe Connect)

1. **Client → Lawyer**: Destination charge. Client's credit card pays lawyer directly for the triage session.
2. **Lawyer → Us**: Auto-scaling subscription. Covers ALL LLM API costs + 85%+ margin.

---

## The War Room: 7-Step Murder Board Pipeline

The War Room is the premium Oracle Studio orchestration that runs UNDERNEATH the
client-facing Vent Mode session. The lawyer never manually triggers it — it fires
automatically when certain signals are detected.

### Pipeline Stages

```
  Step 1: 📥 INTAKE — Raw transcript extraction
  Step 2: 🔬 WEB OSINT — Vertex AI privileged search
  Step 3: 🎯 VERB AUDIT — Action verb kinematic analysis
  Step 4: 📊 ORACLE SYNTHESIS — Multi-model strategy memo
  Step 5: ⚖️ CITATION CHAIN — Authority validation + scoring
  Step 6: 📋 BRIEF BUILDER — Attorney Work-Product assembly
  Step 7: 🏦 VAULT PUSH — Clio/OneDrive + Shadow Invoice
```

### Step 3: Action Verb Auditor

The Action Verb Auditor is a core differentiator. It analyzes the client's
language for kinematic action verbs that unlock or destroy causes of action:

| Verb (COD) | Why It Matters |
|------------|----------------|
| "hit me" | Battery: intentional harmful contact |
| "ran the light" | Negligence per se: statutory violation |
| "knew about" | Impedes summary judgment: material fact dispute |
| "promised" | Triggers promissory estoppel analysis |
| "fired me" | Opens wrongful termination window |
| "said to me" | Potential defamation + hostile work environment |
| "recorded" | Evidence preservation + wiretapping analysis |
| "signed" | Contract formation + capacity analysis |

The UI renders these as a **Kinematic Verb Matrix** — a real-time dashboard of
legally significant language that the client has used.

---

## Monetization Model

### Revenue Streams

1. **SaaS subscription** — Auto-scaling tiers ($299-$999/mo per firm)
2. **Client triage fee** — Destination charge via Stripe Connect ($25-$50/session)
3. **Document generation** — Briefs, memos, Kovel attestation receipts
4. **Precedent Vaults** — Firm-specific case library storage (per-GB pricing)
5. **CLE seminar platform** — Continuing Legal Education demo tools

### Unit Economics

| Metric | Value |
|--------|-------|
| API cost per session (blended) | ~$0.35 |
| Client triage fee | $25.00 |
| Gross margin on AI | 85%+ |
| Target ACV (Solo) | $3,588/yr |
| Target ACV (Practice) | $7,188/yr |
| Target ACV (Enterprise) | $12,000+/yr |

---

## Competitive Moat

### What Others Can't Copy

1. **Heppner Privilege UX** — Dead-man's switch, evaporating chat, Kovel attestation
2. **S.E.U. Token Security** — IP-bound, ephemeral, user-billed (defeats .npmrc exfiltration)
3. **Zero Data Retention** — Provably no stored conversations (RAM-only + ZDR audit trail)
4. **Emotional Arbitrage** — Vent Mode captures clients at peak willingness-to-pay
5. **Shadow Invoice** — Revenue automation that makes the lawyer money while they sleep
6. **Action Verb Auditor** — NLP pipeline mapping client language to causes of action
7. **War Room Pipeline** — 7-step automated litigation intelligence (no competitor has this)

---

## Valuation & Fundraising

### Current Position

| Metric | Value |
|--------|-------|
| Stage | Pre-revenue / Live backend |
| Cloud Run API | v3.2.0, 30 endpoints LIVE |
| Stripe Connect | Fully wired, destination charges active |
| Target Seed Round | $2.5M at $12-15M pre-money |
| Use of Funds | GTM (legal conferences) + 2 engineers + compliance |

### 5-Year Revenue Projection

| Year | Law Firms | ARR |
|------|-----------|-----|
| 1 | 50 | $300K |
| 2 | 200 | $1.2M |
| 3 | 800 | $5.6M |
| 4 | 2,000 | $16M |
| 5 | 5,000 | $45M |

### Comparable Exits

- **Clio**: $900M+ valuation (practice management)
- **Relativity**: $3.6B acquisition (eDiscovery)
- **Ironclad**: $3.2B valuation (contract lifecycle)
- **Harvey AI**: $1.5B valuation (legal AI, BUT no privilege protection)

---

## Risk Register (v2.2 Additions)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Unauthorized practice of law (UPL) | CRITICAL | NY SB 7263 compliance gate in every prompt |
| Privilege waiver by AI output | HIGH | Heppner receipt + ZDR + evaporating chat |
| Citation hallucination | MEDIUM | Judge 6 + Westlaw/LexisNexis validation stubs |
| Verb audit false positives | LOW | Human lawyer review mandatory before action |
| Sandbox escape (BYOK) | MEDIUM | Read-only FS + egress restriction + token TTL |

---

## Implementation Status

### ✅ Complete (Phase 1-2)

- Cloud Run v3.2.0 LIVE (30 endpoints)
- S.E.U. token system (IP-bound, ephemeral, user-billed)
- Stripe Connect destination charges
- Heppner privilege attestation receipts
- Oracle Studio 7-stage pipeline
- LiteLLM multi-model routing
- SSE streaming (Vent Mode)
- Firestore persistence
- Prompt repetition (arXiv 2512.14982)
- Google Workspace alerts

### 🔧 In Progress (This Sprint)

- War Room Murder Board orchestrator
- Action Verb Auditor + Kinematic Verb Matrix UI
- Citation Panel (Perplexity-style)
- Brief Builder (PDF export)
- Advanced fee engine (state-by-state rules)
- BYOK key management UI
- Sandbox isolation (per-tenant)

### 📋 Planned (Phase 3-4)

- Westlaw/LexisNexis live citation validation
- CLE seminar platform
- FedRAMP compliance
- Enterprise BYOC/BYOK
- Evidence-grade audit exports
