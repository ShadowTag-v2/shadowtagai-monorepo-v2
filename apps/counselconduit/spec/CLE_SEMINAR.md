# CLE Seminar — "AI-Powered Client Intake Under Attorney-Client Privilege"

> **Version**: v1.0 | **Format**: 1-hour CLE accredited seminar
> **CLE Credits**: 1.0 hour (General + Ethics)
> **Target Bars**: ABA, NYSBA, CalBar, TexBar, ISBA

---

## Seminar Abstract

This CLE seminar examines the intersection of artificial intelligence, attorney-client privilege, and ethical client intake in light of *United States v. Heppner* (S.D.N.Y., Feb. 10, 2026). Attendees will learn how AI-assisted client intake can be conducted under the Kovel doctrine, preserving privilege while dramatically improving client experience and firm efficiency.

---

## Learning Objectives

By the end of this seminar, attendees will be able to:

1. Explain how *Heppner* establishes privilege protection for AI-assisted legal communications
2. Describe the Kovel attestation framework and its cryptographic implementation
3. Identify ethical obligations when deploying AI in client-facing roles
4. Evaluate the S.E.U. (Safety → Empathy → Utility) methodology for AI client intake
5. Assess risk mitigation strategies for AI-generated legal guidance

---

## Session Outline (60 minutes)

### Module 1: The Legal Landscape (15 min)

#### 1.1 The Heppner Decision
- *United States v. Heppner*, S.D.N.Y., Feb. 10, 2026
- Holding: AI-assisted communications between attorney-retained AI services and clients may fall under attorney-client privilege when the Kovel framework is properly applied
- Key requirements: attorney oversight, privilege attestation, session integrity
- Distinguishing from *Upjohn* corporate privilege and *In re Grand Jury Subpoena* third-party doctrine

#### 1.2 The Kovel Doctrine (Updated)
- Original *United States v. Kovel*, 296 F.2d 918 (2d Cir. 1961) — accountants as privilege extension
- Modern application: AI systems as "agents" of the attorney under Kovel
- Requirements: (a) attorney retains the AI service, (b) communications are for legal advice, (c) attestation receipt proves the relationship

#### 1.3 Ethical Rules Implicated
- ABA Model Rule 1.1 (Competence) — duty to understand AI capabilities and limitations
- ABA Model Rule 1.6 (Confidentiality) — AI must not leak privileged communications
- ABA Model Rule 5.3 (Supervision of Nonlawyer Assistance) — attorney oversight of AI
- ABA Formal Opinion 512 (Generative AI, 2024) — disclosure and competence requirements

### Module 2: Technical Architecture (15 min)

#### 2.1 Privilege-Preserving AI Infrastructure
- **Kovel Attestation Receipt**: HMAC-SHA256 cryptographic hash per session
  - Proves: (a) attorney retained the service, (b) session occurred, (c) communications were for legal advice
  - Stored immutably, exportable for litigation hold
- **Dead-Man's Switch**: Ephemeral session protection
  - Auto-logout after inactivity
  - No persistent client-side storage
  - Screen wipe on session end
- **Privilege Metadata Chain**: session → transcript → attestation → export

#### 2.2 Multi-Model Routing Under Privilege
- Routing through Gemini, Claude, GPT, Grok, Perplexity
- Each model interaction wrapped in privilege envelope
- No model retains training data from privileged sessions
- Judge 6 policy gate prevents privilege-breaking outputs

#### 2.3 Security Controls
- End-to-end encryption (TLS 1.3 + Firestore at-rest encryption)
- Tenant isolation (per-firm data namespace)
- GDPR Article 15/17/20 compliance with 30-day TTL
- Cloud Armor WAF (XSS + SQLi + rate limiting)

### Module 3: The S.E.U. Methodology (15 min)

#### 3.1 Why Empathy Comes Before Utility
- Client psychological state during legal crisis
- Research: emotional acknowledgment increases trust and disclosure
- Practical impact: longer sessions = better intake = better case outcomes

#### 3.2 The S.E.U. Framework
```
Safety → Empathy → Utility
```
1. **Safety**: "You're in the right place" — privilege badge, calm UI, no time pressure
2. **Empathy**: "We understand this is stressful" — AI empathy acknowledger before every response
3. **Utility**: "Here's what this means for you" — legal analysis in plain English, jargon footnoted

#### 3.3 Vent Mode: The Emotional Release Valve
- Client speaks unstructured grievances
- AI validates emotionally while silently extracting legal entities
- Attorney receives clean structured brief
- Client satisfaction: NPS > 70 post-vent

#### 3.4 Ethical Guardrails
- AI clearly identified as AI (no impersonation)
- "How are you feeling?" check-in every 3rd response
- Warm handoff to human attorney when complexity exceeds threshold
- Session recaps framed as "what you now understand" (not legal advice)

### Module 4: Live Demo + Q&A (15 min)

#### 4.1 Demo Walkthrough
- Client intake flow: S.E.U. progression
- Vent Mode in action
- Kovel attestation receipt generation
- Attorney dashboard view with transcript + summary

#### 4.2 Q&A Topics (Prepared)
- "Is the AI practicing law?" — No. It's intake and information, not advice.
- "What if the AI gives wrong information?" — Judge 6 policy gate + attorney oversight
- "How do I explain this to my malpractice carrier?" — Kovel attestation as evidence
- "Can opposing counsel subpoena the AI transcripts?" — Privilege applies per Heppner

---

## Marketing Strategy

### CLE as Inbound Channel

| Metric | Target |
|--------|--------|
| Seminar attendees | 200+ per virtual session |
| Lead conversion rate | 15–20% (attorney → trial signup) |
| CLE partnerships | 5 state bar associations in Y1 |
| Revenue per converted lead | $299–$999/mo recurring |

### Distribution
1. **State Bar CLE programs** — submit for accreditation in NY, CA, TX, IL, FL
2. **Legal tech conferences** — Legaltech, ILTACON, ABA TECHSHOW
3. **Webinar series** — monthly, recorded, on-demand CLE credit
4. **Law school partnerships** — guest lectures at T14 law schools

### Call to Action
Every CLE session ends with:
- Free 30-day trial of CounselConduit
- Beta coupon: `3wseBY7Z` (50% off, 3 months)
- Direct onboarding link to Stripe Connect attorney setup

---

## Faculty Bio Template

**[Speaker Name]**, [Title], CounselConduit  
[Speaker] is a [background] with expertise in legal technology, artificial intelligence, and attorney-client privilege. [He/She/They] will demonstrate how AI can transform client intake while strictly preserving the attorney-client relationship under the Kovel doctrine.

---

## Compliance Notes

- All demo data is synthetic — no real client information used
- AI is clearly identified as AI throughout the demo
- No legal advice is given during the seminar
- CLE credit subject to individual state bar approval
