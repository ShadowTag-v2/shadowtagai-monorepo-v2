# CLE Provider Applications — KovelAI

## Overview

KovelAI qualifies as a Continuing Legal Education (CLE) provider for AI-assisted legal
research competency courses under the following state bar requirements.

---

## California State Bar — MCLE Provider Application

**Applying To:** State Bar of California, Office of MCLE
**Provider Category:** Group 1 (Live/Webinar)

### Course 1: "Privilege-Preserving AI Research for Litigators"
- **Credits:** 1.5 hours General MCLE
- **Format:** Live webinar + recorded replay
- **Faculty:** Erik Hanson, JD (Founder, KovelAI); Guest: Prof. TBD (Legal Ethics)
- **Topics:**
  1. *United States v. Heppner* (S.D.N.Y., 2026) — privilege implications
  2. Kovel doctrine applied to AI-generated work product
  3. Multi-model orchestration (Gemini, Claude, GPT-4) — comparative analysis
  4. ABA Rules 1.1 (Competence), 1.6 (Confidentiality), 5.3 (Supervision)
  5. Hands-on: Using KovelAI's ephemeral research portal
- **Evaluation:** 10-question assessment + attendance verification
- **Fee:** $0 (promotional launch)

### Course 2: "AI Ethics — Zero-Data Architecture for Law Firms"
- **Credits:** 1.0 hour Ethics MCLE
- **Format:** On-demand (recorded)
- **Topics:**
  1. Data residency and the duty of competence in AI adoption
  2. Zero-data routing: why your AI provider should never see client data
  3. Kovel attestation receipts as evidence of privileged communication
  4. Practical compliance checklist for firms adopting AI research tools

### Application Timeline
- **Submission:** 2026-05-01
- **Expected Approval:** 2026-05-30 (30-day review)
- **First Course:** 2026-06-15

---

## New York CLE Board — Accredited Provider Application

**Applying To:** NYS CLE Board
**Provider Category:** Accredited Provider (AO) or Newly Approved (NA)

### Course: "Confidentiality in the Age of AI Legal Research"
- **Credits:** 2.0 hours (1.0 Ethics + 1.0 Skills)
- **Reference:** NY Rules 1.1, 1.6, 5.3
- **Format:** Live interactive webinar with Q&A
- **Attendance:** Verified via platform session tokens (signed, timestamped)

### NY-Specific Requirements
- Course materials distributed ≥3 days before
- Evaluation form collected post-session
- Certificate of attendance with attorney registration number
- Maintain attendance records for 4 years

### Application Timeline
- **Submission:** 2026-05-01
- **Expected Approval:** 2026-06-15 (45-day review)

---

## Texas MCLE — Provider Application

**Applying To:** State Bar of Texas, MCLE Department
**Provider Category:** Accredited Sponsor

### Course: "AI-Powered Research Under Texas Disciplinary Rules"
- **Credits:** 1.5 hours (including 0.5 Ethics)
- **Reference:** TX Disciplinary Rules 1.01, 1.05, 5.03
- **Format:** Live CLE or interactive webinar
- **Unique Feature:** Texas requires "participatory" activity
  - KovelAI live demo segment counts as participatory

### TX-Specific Requirements
- Accredited Sponsor status application + $100 fee
- 60-minute minimum per credit hour
- Written course materials provided
- Attendee evaluation within 30 days

### Application Timeline
- **Submission:** 2026-05-15
- **Expected Approval:** 2026-06-30 (45-day review)

---

## KovelAI CLE Platform Integration

### Automated Certificate Generation
Each completed course generates:
1. **PDF Certificate** with attorney name, bar number, course title, date, credit hours
2. **Kovel Attestation Hash** proving session integrity (HMAC-SHA256)
3. **Reporting API** — direct submission to state bar CLE tracking (where APIs exist)

### Revenue Model
- **Phase 1:** Free courses (marketing + lead gen)
- **Phase 2:** $49/credit hour (market rate: $30-75)
- **Phase 3:** Bundled with Pro subscription (unlimited CLE included)

### Compliance Tracking
Firestore collection: `cle_certificates/{barNumber}/{courseId}`
TTL: 4 years (NY requirement, longest)
