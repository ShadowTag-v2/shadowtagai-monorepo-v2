# CLE Seminar: KovelAI — Privilege-Preserving AI for Legal Practice

## Sprint Item #8 | CLE Credit Materials

---

## Slide 1: Title

# KovelAI: The First AI-Native Attorney-Client Privilege Shield

**Presented by: [Firm Name] | CLE Credit: 1.5 Hours Ethics**

**Key Premise:** When your client Googles "Can my ex-wife find my hidden crypto wallet?" — that search is NOT privileged. Google logs the IP, ties it to their Gmail, and builds an ad cohort. Opposing counsel can and WILL subpoena it.

KovelAI transforms consumer search into Attorney-Directed Computer-Assisted Legal Research via the Kovel Doctrine.

---

## Slide 2: The Heppner Problem

### *United States v. Heppner* (S.D.N.Y. 2026)

**Ruling:** When a client uses a public AI system (ChatGPT, Claude, Perplexity) for legal questions, the privilege is WAIVED because:

1. **No attorney direction** — the client initiated the query independently
2. **Third-party disclosure** — OpenAI/Anthropic/Perplexity stores the query
3. **No Kovel relationship** — the AI provider is not an accountant/translator under attorney privilege

**Impact:** Every law firm that lets clients interact with public AI is creating discoverable evidence.

---

## Slide 3: The Kovel Doctrine — Legal Foundation

### *United States v. Kovel* (2d Cir. 1961)

**Holding:** Attorney-client privilege extends to agents retained by the attorney to assist in legal representation.

**KovelAI's Architecture:**
- The AI system is an **agent of the attorney**, not the client
- All queries route through **server-side proxies** — Google sees a headless server, NOT the client's IP
- Enterprise APIs use **Zero Data Retention (ZDR)** agreements
- Every session generates a **Kovel Attestation Receipt** (cryptographic hash)

---

## Slide 4: Architecture — The Clean Room

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  CLIENT      │     │  KOVELAI SERVER   │     │  SEARCH APIs     │
│  (Browser)   │────→│  (Clean Room)     │────→│  (ZDR Compliant) │
│              │     │                   │     │                  │
│  IP: Hidden  │     │  IP: Server IP    │     │  Google CSE      │
│  Identity:   │     │  S.E.U. Token     │     │  Perplexity Pro  │
│  Ephemeral   │     │  Kovel Binding    │     │  Westlaw API     │
└──────────────┘     └───────────────────┘     └──────────────────┘
```

**Key Points:**
- Client IP NEVER touches any external API
- S.E.U. (Sandbox-bound, Ephemeral, User-billed) tokens expire in 24 hours
- Anti-forensic HTTP headers: `Cache-Control: no-store, private`
- Dead Man's Switch: automatic session wipe on inactivity

---

## Slide 5: The Anxiety Radar — Intake Intelligence

### What Your Client is REALLY Worried About

KovelAI classifies every search query into anxiety vectors:

| Category | Example Query | Urgency |
|----------|--------------|---------|
| **CRIMINAL_EXPOSURE** | "Will I be arrested for tax fraud?" | 🔴 10/10 |
| **ASSET_PROTECTION** | "Can ex-wife find hidden crypto?" | 🟠 8/10 |
| **FAMILY_LAW** | "How to get full custody?" | 🟡 7/10 |
| **REGULATORY** | "We got an SEC subpoena" | 🟡 7/10 |
| **EMPLOYMENT** | "Fired for whistleblowing" | 🟢 6/10 |
| **GENERAL_ANXIETY** | "Am I liable?" | ⚪ 5/10 |

**Result:** You know the client's exact fears BEFORE the first phone call.

---

## Slide 6: Murder Board Pipeline — 7-Stage Triage

### Automated Intake → Retainer in Under 5 Minutes

1. **🔍 Entity Extraction** — NLP extracts parties, courts, statutes, dates
2. **⚡ Conflict Check** — Cross-references firm's matter database
3. **📊 Viability Scoring** — 6-dimension claim assessment (1-10 each)
4. **💰 Fee Structure** — Jurisdiction-specific billing recommendation
5. **📋 Oracle Memo** — Plain-English client summary with privilege markers
6. **📝 Retainer Draft** — Auto-generated engagement letter
7. **⚖️ Judge 6 Gate** — Final risk approval (GO/NO-GO)

**Ethical guardrail:** Every stage applies arXiv:2512.14982 prompt repetition for accuracy.

---

## Slide 7: S.E.U. Token Architecture — Ethics Compliance

### Sandbox-Bound, Ephemeral, User-Billed

**Why this matters for ethics:**
- **Sandbox-bound:** Each client gets an isolated execution environment
- **Ephemeral:** Tokens expire in 24h, traces auto-delete in 30 days (GDPR)
- **User-billed:** Client pays for their own token usage — no commingling
- **IP-locked:** Token is cryptographically bound to the client's IP address

**Revocation:** One API call immediately invalidates all client tokens firm-wide.

---

## Slide 8: BYOK — Bring Your Own Keys

### Enterprise Feature: Zero-Knowledge Key Management

1. Client encrypts API key via **WebCrypto AES-256-GCM** in browser
2. Encrypted payload transmitted to our BYOK endpoint
3. Stored in **GCP Secret Manager** — we NEVER see the plaintext
4. Key bound to firm_id via S.E.U. token
5. Revocation purges from Secret Manager permanently

**Supported Providers:** Anthropic, Google Vertex AI, OpenAI

---

## Slide 9: Perplexity Pro Search — Legal Research Chain

### Multi-Step Privileged Research (New!)

1. Client types: "Can my employer fire me for whistleblowing in California?"
2. System decomposes into 5 atomic sub-questions:
   - "What are California whistleblower protections?"
   - "Cal. Lab. Code §1102.5 analysis"
   - "Available damages for wrongful termination"
   - "Statute of limitations in CA"
   - "Recent case law 2024-2025"
3. Each sub-question runs through the Clean Room
4. Progressive synthesis builds a structured research brief
5. Auto-generates citation chains with confidence scores

---

## Slide 10: Ethics Checklist — CLE Requirements

### ✅ Model Rules Compliance

| Rule | Status | Implementation |
|------|--------|---------------|
| **1.1 Competence** | ✅ | AI-assisted, attorney-supervised |
| **1.4 Communication** | ✅ | Oracle Memo in plain English |
| **1.5 Fees** | ✅ | Jurisdiction-specific fee compliance |
| **1.6 Confidentiality** | ✅ | ZDR APIs + Kovel architecture |
| **1.7 Conflict of Interest** | ✅ | Automated conflict check (Stage 2) |
| **1.15 Safeguards** | ✅ | S.E.U. token isolation |
| **5.3 Supervisory** | ✅ | Judge 6 final approval gate |

---

## Slide 11: Discussion Questions

1. How does the Heppner ruling change your firm's AI policy?
2. Is the Kovel Doctrine sufficient to protect AI-assisted research?
3. What are the malpractice implications of NOT using privilege-preserving AI?
4. How should bar associations adapt to generative AI in legal practice?
5. Should client-facing AI portals require separate informed consent?

---

## Slide 12: Resources & Contact

- **Website:** [kovelai.web.app](https://kovelai.web.app)
- **API Documentation:** Available under NDA
- **Ethics Opinion Archive:** Updated quarterly
- **CLE Materials:** This deck + supplementary readings

**⚖️ ATTORNEY WORK PRODUCT — PREPARED IN ANTICIPATION OF CLE PRESENTATION**

---

*Generated by CounselConduit CLE Module v1.0*
*All case citations verified as of presentation date*
