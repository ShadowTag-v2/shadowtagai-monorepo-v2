# Perplexity Paradigm — Feature Mapping for CounselConduit

> **Version**: v1.0 | **Last Updated**: 2026-04-22
> **Thesis**: Perplexity proved the "answer engine" model works at scale. CounselConduit is the answer engine for legal — with privilege, empathy, and 85%+ margins.

---

## Core Insight

Perplexity's breakthrough wasn't better search — it was **trust through citations**. Users trust Perplexity because every claim is sourced. CounselConduit applies the same pattern to legal AI, but with three critical additions:

1. **Privilege**: Every citation chain is wrapped in Kovel attestation
2. **Empathy**: Every answer opens with S.E.U. emotional acknowledgment
3. **Authority**: Citations are statutes, case law, and bar opinions — not web pages

---

## Feature Mapping: Perplexity → CounselConduit

### 1. Pro Search → Deep Intake

| Perplexity | CounselConduit |
|------------|----------------|
| Multi-turn clarifying questions | S.E.U. layered intake flow |
| "Let me understand your question better" | "Tell us what's happening — we're here to help" |
| Structured follow-ups | Progressive depth (Safety → Empathy → Utility) |
| Result: precise answer | Result: complete client picture + emotional rapport |

**Implementation**: `intake_summarizer.py` + `empathy_templates.py` + `vent_mode.py`

**Key Difference**: Perplexity optimizes for answer precision. We optimize for client trust. The intake isn't done until the client feels safe AND we have the full picture.

---

### 2. Citations → Legal Authority Chain

| Perplexity | CounselConduit |
|------------|----------------|
| Web URL citations [1][2][3] | Statute/case law citations [§ 1983][*Heppner*][ABA Rule 1.6] |
| "According to this source..." | "Under [statute], the relevant standard is..." |
| Hyperlinked sources | Privileged citation chain with Kovel wrapping |
| Verifiable by clicking | Verifiable by Westlaw/LexisNexis cross-reference |

**Implementation**: Oracle Studio Stage 4 (Citation Injection) + Stage 6 (Authority Validation)

**Citation UI Spec**:
```
┌─────────────────────────────────────────────────────┐
│ Response text with inline citations [1] and [2]     │
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ [1] 42 U.S.C. § 1983 — Civil Rights Act        │ │
│ │     "Every person who, under color of any       │ │
│ │      statute... shall be liable..."             │ │
│ │     Authority: Federal Statute                  │ │
│ │     Relevance: ████████░░ 85%                   │ │
│ ├─────────────────────────────────────────────────┤ │
│ │ [2] United States v. Heppner, S.D.N.Y. (2026)  │ │
│ │     "AI-assisted communications... may fall     │ │
│ │      under attorney-client privilege..."        │ │
│ │     Authority: Federal District Court           │ │
│ │     Relevance: ██████████ 97%                   │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

### 3. Sonar RAG → Oracle Studio Pipeline

| Perplexity | CounselConduit |
|------------|----------------|
| Sonar (custom RAG model) | Oracle Studio (7-stage pipeline) |
| Web-wide retrieval | Jurisdiction-scoped retrieval |
| Real-time index | Precedent vault (per-firm) + live statute feed |
| Single-pass generation | 7-stage: extract → classify → research → cite → validate → gate → format |

**Implementation**: `oracle_studio.py` (14KB, 7 stages live)

**Oracle Studio Stages**:
1. **Extract**: Parse client query into legal concepts, entities, jurisdiction
2. **Classify**: Determine practice area, urgency, complexity score
3. **Research**: Multi-model retrieval (Gemini for breadth, Claude for depth)
4. **Cite**: Inject statute/case law citations with authority scoring
5. **Validate**: Cross-check citations against known law databases
6. **Gate**: Judge 6 policy check (privilege, ethics, scope, risk)
7. **Format**: S.E.U. wrapping + layman translation + warm close

---

### 4. Pages / Dossier → Attorney Brief Builder

| Perplexity | CounselConduit |
|------------|----------------|
| Pages (curated document) | Attorney Brief (privileged export) |
| User-created collections | Auto-generated from session transcript |
| Public sharing | Privilege-locked (Kovel attestation) |
| Formatted for web | Formatted for legal submission |

**Implementation**: Phase 2 — `brief_builder.py` (planned)

**Brief Format**:
```markdown
# PRIVILEGED & CONFIDENTIAL — ATTORNEY WORK PRODUCT
## Kovel Attestation: [HMAC-SHA256 receipt hash]
## Session: [session_id] | Date: [timestamp] | Duration: [minutes]

### Client Summary
[Extracted from Vent Mode + Deep Intake]

### Legal Issues Identified
1. [Issue] — [Statute/Case Law] — [Risk Level]
2. [Issue] — [Statute/Case Law] — [Risk Level]

### Recommended Actions
1. [Action] — [Timeline] — [Cost Estimate]

### Full Transcript
[Linked, not inline — preserves privilege]

### Citation Chain
[All authorities cited, with relevance scores]
```

---

### 5. Spaces → Precedent Vaults

| Perplexity | CounselConduit |
|------------|----------------|
| Spaces (shared research) | Precedent Vaults (per-firm collections) |
| Team collaboration | Attorney team + client view |
| File uploads for context | Case law uploads + matter files |
| Persistent knowledge base | Tenant-isolated RAG namespace |

**Implementation**: Phase 3 — Firestore `precedent_vaults/{tenant_id}/` + LanceDB vector index

**Precedent Vault Architecture**:
```
┌─ Firm: Smith & Associates ─────────────────────┐
│                                                 │
│  ┌─ Vault: Employment Law ─────────────────┐   │
│  │  • 847 case law excerpts                │   │
│  │  • 23 state statutes                    │   │
│  │  • 156 firm-specific memos              │   │
│  │  • RAG index: 15K vectors               │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─ Vault: Personal Injury ────────────────┐   │
│  │  • 1,204 case law excerpts              │   │
│  │  • 45 state + federal statutes          │   │
│  │  • 89 settlement precedents             │   │
│  │  • RAG index: 22K vectors               │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Implementation Phases

| Phase | Features | Timeline | Sprint |
|-------|----------|----------|--------|
| Phase 1 (LIVE) | Deep Intake, S.E.U. empathy, Oracle Studio 7-stage | ✅ v10.0 | Done |
| Phase 2 (v11.0) | Citation UI, Attorney Brief Builder, Layman Translation | Next | v11.0 |
| Phase 3 (v12.0) | Precedent Vaults, Per-Firm RAG, Case Law Upload | Q3 2026 | v12.0 |
| Phase 4 (v13.0) | Collaborative Spaces, Multi-Attorney View, Real-Time Statute Feed | Q4 2026 | v13.0 |

---

## Why This Beats Perplexity for Legal

1. **Privilege**: Perplexity has no concept of privileged communication. We do.
2. **Empathy**: Perplexity optimizes for speed. We optimize for trust.
3. **Authority**: Perplexity cites web pages. We cite statutes and case law.
4. **Monetization**: Perplexity fights Google. We monopolize the legal privilege layer.
5. **Margins**: Perplexity burns cash on compute. We have 85%+ margins from emotional arbitrage.
