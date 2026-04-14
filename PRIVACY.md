# PRIVACY.md — ShadowTag AI Open-Source Privacy Policy

**Last Updated:** April 14, 2026  
**Effective Date:** April 14, 2026  
**Version:** 1.0.0

---

## 1. Overview

ShadowTag AI ("we," "us," "our") is committed to protecting the privacy of all users across our suite of products: **ShadowTag AI**, **KovelAI**, and **UphillSnowball**. This policy covers data practices for both our open-source repositories and deployed web services.

## 2. Data We Collect

### 2.1 Web Properties (shadowtagai.com, kovelai.com)

| Data Type | Purpose | Retention |
|-----------|---------|-----------|
| **Contact form submissions** | Sales inquiries, investor relations | 2 years |
| **reCAPTCHA tokens** | Bot protection | Session only |
| **Analytics (Google Analytics)** | Usage patterns, page views | 26 months (GA default) |
| **Cookies** | Session management, preferences | See Cookie Policy |

### 2.2 Open-Source Repository (GitHub)

| Data Type | Purpose | Retention |
|-----------|---------|-----------|
| **Git commit metadata** | Version control, attribution | Permanent (git history) |
| **Issue/PR discussions** | Collaboration | Permanent |
| **CI/CD logs** | Build verification | 90 days |

### 2.3 API Services (FastAPI Backend)

| Data Type | Purpose | Retention |
|-----------|---------|-----------|
| **API request logs** | Debugging, security monitoring | 30 days |
| **Authentication tokens** | Access control | Session duration |
| **Usage telemetry** | Service reliability | 90 days |

## 3. Data We Do NOT Collect

- We do **not** sell personal data to third parties
- We do **not** use data for behavioral advertising
- We do **not** store payment card numbers (Stripe handles PCI compliance)
- We do **not** collect biometric data
- We do **not** track users across third-party websites

## 4. Third-Party Services

| Service | Purpose | Privacy Policy |
|---------|---------|----------------|
| **Google Cloud Platform** | Infrastructure, Firestore, Cloud Functions | [GCP Privacy](https://cloud.google.com/terms/cloud-privacy-notice) |
| **Google reCAPTCHA** | Bot protection | [reCAPTCHA Privacy](https://policies.google.com/privacy) |
| **Google Analytics** | Web analytics | [GA Privacy](https://support.google.com/analytics/answer/6004245) |
| **Stripe** | Payment processing | [Stripe Privacy](https://stripe.com/privacy) |
| **Firebase** | Hosting, authentication | [Firebase Privacy](https://firebase.google.com/support/privacy) |
| **GitHub** | Source code hosting | [GitHub Privacy](https://docs.github.com/en/site-policy/privacy-policies) |

## 5. Data Sovereignty

ShadowTag AI is built on a **total data sovereignty** model:

- All production data is stored in **Google Cloud Platform** (US regions by default)
- Firestore databases are configured with **zero-trust security rules** (deny-all default, admin-only access)
- No data is replicated to non-GCP infrastructure
- API keys and secrets are managed via **GCP Secret Manager** and **environment isolation**

## 6. Legal Compliance

### 6.1 GDPR (EU)
- **Legal basis**: Legitimate interest (analytics), consent (contact forms), contract (API services)
- **Data subject rights**: Access, rectification, erasure, portability, objection
- **Contact**: privacy@shadowtagai.com

### 6.2 CCPA (California)
- **Categories collected**: Identifiers, internet activity, commercial information
- **Do Not Sell**: We do not sell personal information
- **Contact**: privacy@shadowtagai.com

### 6.3 EU AI Act
- ShadowTag AI's **Judge 6 Shield** product is designed to help enterprises comply with EU AI Act requirements
- Our own AI systems follow transparency and accountability principles

## 7. Security Measures

- **Encryption in transit**: TLS 1.3 (HSTS preload enabled)
- **Encryption at rest**: GCP managed encryption keys
- **Access control**: IAM with least-privilege principle
- **Monitoring**: Cloud Logging + custom alerting policies
- **Incident response**: 72-hour breach notification commitment

## 8. Cookie Policy

| Cookie | Type | Duration | Purpose |
|--------|------|----------|---------|
| `_ga` | Analytics | 2 years | Google Analytics visitor ID |
| `_gid` | Analytics | 24 hours | Google Analytics session ID |
| `NID` | Functional | 6 months | reCAPTCHA anti-bot |
| `consent_preferences` | Necessary | 1 year | Cookie consent choice |

Users can manage cookies through browser settings or our on-site cookie consent banner.

## 9. Changes to This Policy

We may update this policy periodically. Material changes will be communicated via a notice on our websites and a commit to this repository.

## 10. Contact

For privacy inquiries, data subject requests, or concerns:

- **Email**: privacy@shadowtagai.com
- **GitHub Issues**: [ShadowTag-v2/Monorepo-Uphillsnowball](https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball/issues)

---

**License**: This document is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
