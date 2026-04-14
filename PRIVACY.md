# ShadowTag AI — Privacy Policy

**Effective Date:** April 14, 2026
**Last Updated:** April 14, 2026
**Version:** 1.0

---

## 1. Introduction

ShadowTag AI ("we," "us," or "our") operates the **shadowtagai.com** and **kovelai.com** web properties, along with associated APIs, services, and open-source tooling (collectively, the "Services"). This Privacy Policy describes how we collect, use, disclose, and safeguard your information when you interact with our Services.

We are committed to a **Sovereign-First Data Governance** posture. This means your data stays under your control, on your infrastructure, processed by models you select.

## 2. Information We Collect

### 2.1 Information You Provide Directly
- **Contact Forms:** Name, email address, and message content submitted through our website contact forms.
- **Account Information:** If you create an account, we collect your email, display name, and authentication credentials (managed via Firebase Authentication).
- **Legal Intake (KovelAI):** If you use KovelAI's intake system, we collect the information you voluntarily provide regarding your legal matter. This data is treated with the highest sensitivity.

### 2.2 Information Collected Automatically
- **Server Logs:** Standard HTTP request logs including IP address, User-Agent, request path, and response status code. These are retained for **30 days** for operational debugging and then purged.
- **Firebase Analytics (Limited):** We use Firebase Analytics with **IP anonymization enabled** and **advertising features disabled**. We collect only aggregate page view counts and performance metrics. No individual user tracking profiles are created.

### 2.3 Information We Do NOT Collect
- **Biometric Data:** Never.
- **Location Data:** We do not track GPS or fine-grained location.
- **Third-Party Tracking:** We do not use Facebook Pixel, Google Ads conversion tracking, or any third-party advertising tracker.
- **Keystroke or Interaction Recording:** We do not use session replay tools (e.g., Hotjar, FullStory).

## 3. Telemetry Disclosure

### 3.1 Open-Source Telemetry Posture
All ShadowTag AI open-source repositories enforce a strict **telemetry-disabled** posture:

```
DISABLE_TELEMETRY=1
DISABLE_ERROR_REPORTING=1
```

These environment variables are set globally across all build pipelines, CI/CD workflows, and development environments. No telemetry data is transmitted to any external service from our open-source tooling.

### 3.2 Runtime Model Telemetry
When using our AI-powered features, queries are processed by **Google Gemini models** (specifically `gemini-3.1-flash-lite-preview-thinking`) via the Vertex AI API. Google's data processing terms apply to model inference. We do not store prompts or completions beyond the duration of the active session unless you explicitly opt in to session persistence.

## 4. How We Use Your Information

We use collected information exclusively for:
- **Service Delivery:** Processing your requests, rendering pages, and executing AI inference.
- **Security:** Detecting and preventing abuse, unauthorized access, and DDoS attacks.
- **Operational Monitoring:** Google Cloud Monitoring alerting policies for uptime and error rate tracking.
- **Legal Compliance:** Responding to lawful requests from governmental authorities.

We **never** sell, rent, or trade your personal information to third parties.

## 5. Data Storage & Security

### 5.1 Infrastructure
- **Primary Cloud:** Google Cloud Platform (GCP), project `shadowtag-omega-v4`.
- **Database:** Google Firestore with **zero-trust security rules** (default deny-all, admin-only access).
- **Hosting:** Firebase Hosting with automatic SSL/TLS encryption.
- **Authentication:** Firebase Authentication with bcrypt-hashed credentials.

### 5.2 Encryption
- **In Transit:** All data is encrypted via TLS 1.3.
- **At Rest:** All Firestore data is encrypted at rest using Google-managed encryption keys (AES-256).

### 5.3 Access Controls
- **Workload Identity Federation (WIF):** No persistent service account keys exist in our CI/CD pipeline. All deployments authenticate via ephemeral, scoped tokens.
- **Principle of Least Privilege:** Service accounts are granted only the minimum IAM roles required for their function.

## 6. Data Retention

| Data Type | Retention Period | Deletion Method |
|-----------|-----------------|-----------------|
| Server Logs | 30 days | Automatic rotation |
| Contact Form Submissions | 1 year | Manual purge on request |
| Firebase Analytics | 14 months (Google default) | Automatic expiration |
| Legal Intake Data (KovelAI) | Duration of engagement + 7 years | Secure deletion per legal retention requirements |
| Session Data | Duration of session | Automatic on session end |

## 7. Your Rights

Regardless of your jurisdiction, we honor the following rights:

- **Access:** You may request a copy of all personal data we hold about you.
- **Rectification:** You may request correction of inaccurate data.
- **Deletion:** You may request deletion of your data ("Right to be Forgotten").
- **Portability:** You may request your data in a machine-readable format.
- **Objection:** You may object to processing of your data for specific purposes.

### 7.1 GDPR (European Economic Area)
If you are located in the EEA, you have additional rights under the General Data Protection Regulation. Our lawful basis for processing is **legitimate interest** (service delivery and security) and **consent** (for optional features).

### 7.2 CCPA (California)
If you are a California resident, you have the right to know what personal information is collected, request deletion, and opt out of the sale of personal information. **We do not sell personal information.**

## 8. Children's Privacy

Our Services are not directed to individuals under the age of 18. We do not knowingly collect personal information from children. If we become aware that a child under 18 has provided us with personal information, we will take steps to delete such information promptly.

## 9. Third-Party Services

Our Services integrate with the following third-party providers:
- **Google Cloud Platform / Firebase:** Infrastructure and authentication.
- **Stripe:** Payment processing (PCI DSS Level 1 compliant). We never store credit card numbers.
- **GitHub:** Source code hosting and CI/CD (no user data is shared with GitHub).

Each third-party provider has its own privacy policy. We encourage you to review them.

## 10. Changes to This Policy

We may update this Privacy Policy from time to time. Material changes will be posted on this page with an updated "Last Updated" date. Continued use of our Services after changes constitutes acceptance of the revised policy.

## 11. Contact Us

For privacy inquiries, data requests, or concerns:

- **Email:** privacy@shadowtagai.com
- **Website:** [https://shadowtagai.com/contact](https://shadowtagai.com/contact)
- **Mailing Address:** Available upon written request.

## 12. Open-Source Privacy Policy

ShadowTag AI maintains open-source repositories under the `ShadowTag-v2` GitHub organization. This section governs data handling within those repositories and any forks or derivatives.

### 12.1 Contributor Data

- **Git Metadata:** Contributor names and email addresses are captured in Git commit history as part of the standard open-source contribution workflow. This data is publicly visible and governed by GitHub's Privacy Statement.
- **Issue & PR Content:** Information submitted in GitHub Issues and Pull Requests is public. Do not submit personal data, client data, or privileged information in public issues.
- **CLA:** We do not currently require a Contributor License Agreement. All contributions are accepted under the repository's stated license.

### 12.2 Telemetry Kill-Switch Doctrine

All ShadowTag AI open-source software ships with telemetry **disabled by default**. The following invariants are enforced:

```
DISABLE_TELEMETRY=1
DISABLE_ERROR_REPORTING=1
```

- These variables are set in all CI/CD pipelines, development environments, and production runtimes.
- **Forks and derivatives** are strongly encouraged to maintain this posture but are not legally required to do so.
- No open-source package published by ShadowTag AI will ever phone home, transmit usage statistics, or collect crash reports without explicit, opt-in user consent.

### 12.3 License Obligations

| Repository | License | Privacy Implication |
|-----------|---------|-------------------|
| Core infrastructure (`apps/shadowtagai`, `apps/kovelai`) | Proprietary | Covered by Sections 1–11 of this Policy |
| Open-source tooling (`tools/*`, `labs/*`) | Apache 2.0 / MIT | Covered by this Section 12 |
| Third-party vendored code (`external_repos/*`, `external_sdks/*`) | Original upstream license | Governed by upstream project's privacy policy |

### 12.4 Sovereign Execution Guarantee

When you deploy ShadowTag AI open-source tooling on your own infrastructure:

- **Zero data egress:** No data leaves your execution environment to ShadowTag AI servers.
- **Zero phone-home:** No license validation, update checks, or analytics callbacks are embedded in the codebase.
- **Full auditability:** All source code is available for inspection. We encourage security audits and responsible disclosure.

### 12.5 Vulnerability Disclosure

If you discover a privacy or security vulnerability in any ShadowTag AI open-source repository:

- **Email:** security@shadowtagai.com
- **Response SLA:** Acknowledgment within 48 hours, patch within 7 days for critical issues.
- **No retaliation:** We will never pursue legal action against good-faith security researchers.

---

*This Privacy Policy is provided as part of ShadowTag AI's commitment to transparency and data sovereignty. It complements our [Terms of Service](/terms.html), our [Open-Source Telemetry Doctrine](#121-telemetry-kill-switch-doctrine), and is governed by the laws of the State of Washington, USA.*
