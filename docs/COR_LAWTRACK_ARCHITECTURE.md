# Cor.LawTrack Engineering Blueprint

**Status:** ACTIVE
**Doctrine:** Business Judgment Rule Compliance (Latest/Greatest/Best-Value, Rolling ROI, Zero-Trust Absolute).
**Engine:** Event → Rules → Nagging → Help-on-Demand → Verification.

## 1. The Core Infrastructure (Zero-Trust Standard)

All data paths strictly abide by the "no plaintext" rule.

- **Relational Data:** PostgreSQL (encrypted at rest via Cloud KMS, TLS in transit).
- **Object Storage:** S3/GCS (SSE-KMS + Object Lock for immutable backups).
- **Vector DB:** Isolated AI context layer for rules and RAG.
- **Identity:** OIDC/SSO enforced with MFA/Hardware Key requirements for Partner/Admin access.

## 2. The Core Engine Loop

Cor.LawTrack is structurally vertical-agnostic but launches configured for Academic (B2C) and Legal (B2B).

1. **Event Ingestion:** Primed for Email Webhooks -> Parser -> RAG -> Timeline.
2. **Rules DB:** Configurable logic packs (e.g., FRCP, Tax, Academic Syllabi).
3. **Nagging Core:** Multi-channel alerting (SMS, Push, Email) tied to an Escalation Slider (Gentle -> Strict).
4. **Help-On-Demand:** Integrated ping router for AI Tutors, Teachers, or Paralegals.
5. **Audit Ledger:** Immutable compliance trails.

## 3. Immediate Technical Execution (Phase 1 MVP)

We are executing the **BEST (secure + investor-ready)** option:

1. **Schema Generation:** `core/lawtrack/schema.sql` (Matters, Events, Rules, Timelines, Audit).
2. **Email Ingestion API:** Cloud Run service receiving SendGrid/Mailgun parsed webhooks.
3. **Timeline Engine:** Python backend applying the Rules DB to the Ingestion Output.
4. **Enforcement Dashboard (UI):** React/Vite implementation of the Critical Tiles.

## 4. Business Judgment Rule Parameters Check

- **Opportunity Cost Tracker:** Focus engineering _only_ on the core parsing and timeline generation. Defer custom integrations (Canvas, Clio) in favor of standard Email Webhooks to maximize speed to market.
- **Tech Stack Future-Proofing:** Using FastAPI/Python for backend to natively support the Gemini 3.1 Pro ML extraction models seamlessly. Postgres with `pgcrypto` handles the Zero-Trust data at rest requirement cleanly.
