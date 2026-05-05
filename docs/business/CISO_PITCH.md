# CounselConduit CISO Pitch

## Executive Summary
CounselConduit is designed from the ground up to meet the rigorous security, privacy, and compliance requirements of modern law firms. Our architecture employs a Zero Trust model, ensuring that privileged legal data remains secure, isolated, and verifiably deleted upon request. This document outlines our security posture, compliance strategy, data lifecycle management, and enterprise pricing model.

## Zero Trust Architecture
Our Zero Trust design operates on the principle of "never trust, always verify." 
- **Identity & Access Management:** We enforce strict identity verification for every request, whether internal or external.
- **Tenant Isolation:** Data is strictly segregated by firm (`firm_id`). Cross-tenant access is cryptographically and logically prohibited.
- **Epistemic Airgap:** We utilize NotebookLM for zero-trust data ingestion, ensuring that external or untrusted data is strictly quarantined and cannot poison the context window or execute malicious payloads.
- **Secret Management:** All secrets, keys, and credentials are managed via GCP Secret Manager. No hardcoded secrets exist in our source code or environment files.
- **Least Privilege:** Service accounts and API integrations operate with the minimum permissions necessary to function.

## SOC 2 & HIPAA Compliance Strategy
CounselConduit is building towards full SOC 2 Type II and HIPAA compliance:
- **Encryption:** All data is encrypted at rest (using AES-256) and in transit (via TLS 1.3).
- **Audit Logging:** Every critical action (e.g., account deletion, data access) generates an immutable, append-only audit log entry.
- **Business Associate Agreements (BAAs):** For our Enterprise tier customers, we support executing BAAs to ensure HIPAA compliance for protected health information (PHI) that may be present in legal transcripts.
- **Continuous Monitoring:** We employ automated security scanning (Betterleaks, detect-private-key) and rigorous CI/CD pipeline checks to prevent vulnerabilities from reaching production.

## GDPR "Nuke My Data" Logic
We provide automated, verifiable compliance with GDPR Article 17 (Right to Erasure) and Article 20 (Right to Portability).

### Account Deletion (Right to Erasure)
- **Initiation:** Authorized users can request account deletion, which requires explicit confirmation ("DELETE MY ACCOUNT").
- **Soft Delete & Grace Period:** The account is marked for deletion and enters a 30-day grace period, allowing for recovery if the request was made in error.
- **Hard Wipe:** After 30 days, a scheduled Cloud Task automatically triggers the `_execute-delete` endpoint. This performs a cascading hard delete across all subcollections: `sessions`, `transcripts`, `matters`, `billing_records`, and `clients`.
- **Audit Trail:** An immutable audit log entry is created confirming the deletion, ensuring compliance with regulatory reporting requirements.
- **Confirmation:** Users receive automated email receipts confirming the scheduling and completion of the deletion.

### Data Export (Right to Portability)
- **Async Processing:** Users can request a complete export of their data in JSON or CSV format. 
- **Secure Delivery:** The export is processed asynchronously via Cloud Tasks, uploaded to a secure GCS bucket, and a signed URL (valid for 24 hours) is emailed to the requesting attorney.

## Enterprise Pricing & The "SSO Tax"
CounselConduit operates a transparent, tiered pricing model:
- **Professional Tier:** $149/mo (or $1,428/yr) - Designed for small practices needing core AI capabilities.
- **Enterprise Tier:** $20,000/mo - Designed for mid-to-large firms requiring enterprise-grade security and governance.

### Justification for the Enterprise Tier
The significant step-up to the Enterprise tier reflects the substantial operational and liability costs associated with enterprise features, commonly referred to as the "SSO Tax":
1. **Single Sign-On (SSO) & SAML Integration:** Native integration with enterprise identity providers (Okta, Entra ID) requires dedicated support, custom mapping, and ongoing maintenance.
2. **Dedicated Compliance Support:** Executing BAAs, providing custom SOC 2 reports, and responding to extensive vendor security questionnaires requires dedicated legal and security resources.
3. **Advanced Audit & Governance:** Enterprise customers receive expanded, exportable audit logs and advanced role-based access control (RBAC).
4. **VPC Peering & Custom Networking:** Support for custom network topologies and dedicated egress IPs.
5. **Increased Token Limits:** A 10x increase in monthly token limits (1,000,000 tokens) to support large-scale document processing and firm-wide adoption.

## HeadFade Platform — Synthetic Media Compliance

### Deepfake Detection & EU AI Act Compliance
HeadFade operates as a gamified Turing Test for synthetic media detection. Our compliance posture addresses the rapidly evolving regulatory landscape:
- **EU AI Act Article 52 (Transparency):** All AI-generated content displayed on the platform is labeled with provenance metadata. Users are informed post-vote whether content was synthetic, satisfying the transparency obligation for AI-generated media.
- **Visual Provenance Chain:** Every video in the Human Deception Index (HDI) carries a cryptographic hash linking to its source provenance record in Firestore, enabling full audit trail reconstruction.

### Consent & Data Collection Framework
- **Informed Consent:** Users are presented with clear Terms of Use before participating in the Turing Test. Vote data (user selection, latency, accuracy) is collected under a legitimate interest basis (GDPR Art. 6(1)(f)) for improving deepfake detection accuracy.
- **COPPA Compliance:** The platform requires age verification (13+) before participation. No personally identifiable information is collected from votes — only anonymous behavioral telemetry (vote direction, hesitation latency).
- **Data Minimization:** HDI telemetry records contain only: video_id, user_vote, actual_truth, hesitation_latency_ms, and timestamp. No IP addresses, device fingerprints, or user identifiers are stored.

### Liability & Safe Harbor
- **Section 230 Positioning:** HeadFade functions as an interactive computer service hosting third-party content for educational and research purposes. The forensic analysis is AI-generated commentary, not editorial endorsement.
- **Deepfake Liability Shield:** HeadFade does not create or distribute deepfakes. The platform ingests content solely for detection benchmarking. All synthetic content is sourced from authorized generative AI services (Veo 3.1, Sora) with proper licensing.
- **Research Use Exception:** HDI data may be used for academic research into human susceptibility to synthetic media, subject to IRB approval and de-identification requirements.

