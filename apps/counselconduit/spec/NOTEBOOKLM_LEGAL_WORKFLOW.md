# NotebookLM → KovelAI: 6-Step Cognitive Workflow for Lawyers

> **Source**: Google NotebookLM Help Center, adapted for legal privilege workflow
> **Purpose**: Maps the NotebookLM 6-step user journey into the Oracle Studio pipeline

---

## Background

Google NotebookLM works in 6 steps: Upload Sources → Ask Questions →
Generate Summaries → Create Audio Overviews → Share → Iterate.

KovelAI translates this cognitive model into a privilege-preserving legal workflow
where each "notebook" is a privileged case file, each "question" is a privileged
legal research query, and each "summary" is Attorney Work-Product.

---

## The 6-Step Translation

### Step 1: Upload Sources → Privileged Intake

**NotebookLM**: User uploads PDFs, docs, websites as source material.
**KovelAI**: Client's Vent Mode transcript + uploaded documents are ingested
into a privilege-sealed Aegaeon context cache. Documents are encrypted at rest
and bound to the S.E.U. token.

**Key Difference**: In KovelAI, the "sources" include:
- Client transcript (RAM-only, never persisted)
- Uploaded documents (encrypted, tenant-isolated)
- OSINT web search results (ZDR, enterprise-grade)
- Prior case files from Precedent Vault

---

### Step 2: Ask Questions → Oracle Query Layer

**NotebookLM**: User asks natural language questions grounded in sources.
**KovelAI**: The Oracle model generates legal research queries automatically
from the intake extraction (Stage 1 output). The lawyer can also ask
custom queries through the Attorney Dashboard.

**Key Difference**: KovelAI queries are:
- Automatically generated (no manual input needed for base analysis)
- Grounded in Vertex AI Enterprise Search (not generic web)
- Privilege-sealed (all queries are Attorney Work-Product)
- Enhanced with arXiv:2512.14982 prompt repetition

---

### Step 3: Generate Summaries → Oracle Synthesis

**NotebookLM**: AI generates summaries grounded in uploaded sources.
**KovelAI**: Oracle Studio Stage 4 generates a comprehensive strategy memo
with structured sections: FACTS | LEGAL ANALYSIS | STRATEGY | RISKS | DEADLINES.

**Key Difference**: The summary is:
- Multi-model (Gemini Pro + Claude Sonnet for cross-validation)
- Citation-grounded (every claim links to specific authority)
- Risk-assessed (Judge 6 flags potential issues)
- Verb-enriched (Action Verb Auditor's kinematic analysis embedded)

---

### Step 4: Create Audio Overviews → CLE Demo Mode

**NotebookLM**: AI generates podcast-style audio discussions of sources.
**KovelAI**: CLE Seminar Mode generates audio briefings for:
- Attorney case review (listen while commuting)
- CLE presentation content (continuing legal education)
- Client-safe factual summaries (stripped of legal analysis)

**Key Difference**: Audio output follows the same privilege rules:
- Attorney audio = work-product (full analysis)
- Client audio = factual summary only (no legal advice)
- CLE audio = anonymized, educational use

---

### Step 5: Share → Vault Push

**NotebookLM**: Users share notebooks with collaborators.
**KovelAI**: War Room Stage 7 pushes completed intelligence package to:
- Clio (case management notes + time entries)
- OneDrive (document storage)
- Attorney Dashboard (real-time access)
- Shadow Invoice (auto-drafted billing)

**Key Difference**: Sharing is:
- Role-gated (attorney vs client vs admin)
- Privilege-sealed (Heppner receipt attached to every share)
- Audit-logged (immutable trail in Firestore)
- TTL-enforced (GDPR 30-day auto-deletion for client-facing content)

---

### Step 6: Iterate → Precedent Vault

**NotebookLM**: Users refine questions and add more sources over time.
**KovelAI**: Completed War Room sessions feed into the firm's Precedent Vault,
creating a growing knowledge base that improves future analysis.

**Key Difference**: Iteration is:
- Cross-matter (patterns identified across all firm cases)
- Cached (Aegaeon context slabs for 84% cost reduction on repeat)
- Privacy-isolated (per-firm, never cross-tenant)
- Continuously learning (verb ledger improves cause-of-action mapping)

---

## Mapping Table

| NotebookLM Step | KovelAI Equivalent | Pipeline Stage |
|-----------------|-------------------|----------------|
| Upload Sources | Privileged Intake | Stage 1 |
| Ask Questions | Oracle Query Layer | Stage 2-3 |
| Generate Summaries | Oracle Synthesis | Stage 4 |
| Create Audio | CLE Demo Mode | (future feature) |
| Share | Vault Push | Stage 7 |
| Iterate | Precedent Vault | Post-pipeline |

---

## Why This Matters

NotebookLM has proven that the **upload → query → synthesize → share** workflow
resonates with knowledge workers. KovelAI wraps this proven UX pattern in a
**privilege-preserving, revenue-generating, compliance-enforced** envelope
specifically for lawyers.

The lawyer doesn't need to learn a new workflow. They already understand
"gather sources → ask questions → get answers → share with team."
We just make it legally bulletproof.
