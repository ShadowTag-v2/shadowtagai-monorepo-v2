# GOOGLE-NATIVE INSIDER RISK PLATFORM: REFERENCE IMPLEMENTATION

> **CLASSIFICATION**: TIER 1 CORE
> **VERSION**: 1.0 (Feb 2026)
> **STATUS**: PRODUCTION BLUEPRINT

## EXECUTIVE SUMMARY

A pure Google Cloud-native insider threat detection and compliance platform.
**Goal**: Identify insider threats, harassment, retaliation, fraud, self-harm, and physical supply chain risks using ZERO external vendors.
**Economics**: $2.1K/mo dev -> $8.4K/mo prod (4x cheaper than DTEX/Middesk/LexisNexis stack).
**Exit Valuation**: $100M - $200M (Differentiation is INTEGRATION, not tools).

---

## 1. COMPONENT STACK (100% GCP)

| Capability | Vendor Replacement | Google Native Solution |
| :--- | :--- | :--- |
| **UEBA / Insider Threat** | DTEX InTERCEPT | **Google Security Operations (Chronicle) + Vertex AI Agents** |
| **Self-Harm Prevention** | External Mods | **Vertex AI Safety Filters + Gemini Grounding (988)** |
| **Deepfake Detection** | Hive | **Vertex AI Vision + Video Intelligence API** |
| **Watermarking** | Digimarc | **SynthID (Native)** |
| **Minor Protection (CA)** | Yoti / AgeID | **Vertex AI Behavioral Age Inference + Cloud Armor** |
| **EU AI Act Compliance** | OneTrust AI | **Cloud Logging + BigQuery (Automated Art. 13)** |
| **Biz Judgment (Risk)** | Palisade @Risk | **Vertex AI Workbench + BigQuery Monte Carlo** |
| **VPN / Tunneling** | NordLayer | **Cloud IDS + Cloud Armor + Gemini Behavioral** |
| **Zero Trust** | Zscaler | **BeyondCorp Enterprise + Access Context Manager** |
| **KYB / KYE Vetting** | LexisNexis / Middesk | **Vertex AI Agents (Web Scraping / GNews / Open Data)** |
| **Supply Chain (Physical)** | Carrier411 | **Maps API + Vision API + FMCSA API** |

---

## 2. KEY IMPLEMENTATION MODULES

### A. Insider Threat Agent (`vertex_ueba_agent.py`)
**Function**: Real-time User and Entity Behavior Analytics (UEBA) using Chronicle data and Gemini 1.5 Pro.
**Core Logic**:
*   Queries Chronicle Data Lake for user activity (hours, geo, data transfer).
*   Prompts Gemini: "Analyze for ATP 5-19 insider threat indicators."
*   Checks HRIS (Workday/Admin SDK) for employment status anomalies.
*   **Cost**: ~$1,200/mo base.

### B. Suicide Prevention Filter (`suicide_prevention_filter.py`)
**Function**: Safety layer intercepting "end it" or "kill myself" prompts.
**Core Logic**:
*   Uses `HarmCategory.HARM_CATEGORY_SELF_HARM`.
*   Blocks response.
*   Returns strictly: "Your message was blocked... Call 988."
*   Logs incident to Chronicle for HR review.

### C. Deepfake Detector (`deepfake_detector.py`)
**Function**: Scans video/images for manipulation without Hive.
**Core Logic**:
*   **Video Intelligence API**: Detects object tracking anomalies.
*   **Vision API**: Face detection confidence < 0.8 (common synthetic tell).
*   **Multimodal Embeddings**: Checks for synthetic patterns.

### D. Supply Chain Guard (`supply_chain_agent.py`)
**Function**: Cyber-physical fusion for logistics.
**Core Logic**:
*   **Vision API**: OCRs driver's license (Expiration check).
*   **FMCSA API**: Checks carrier "AllowToOperate" status (Free).
*   **Maps API**: Grounds pickup address (detects fake storefronts via Street View OCR).
*   **Logic**: "If Carrier Name NOT on Storefront Signage -> FLAG."

### E. KYB/KYE Continuous Vetting (`kyb_kye_agent.py`)
**Function**: Background checks without LexisNexis fees.
**Core Logic**:
*   **Gemini Agent Tools**:
    *   `search_court_records` (PACER/CourtListener/Scraping).
    *   `check_business_license` (Secretary of State APIs).
    *   `scan_adverse_media` (Google News API).
*   **Cost**: ~$0/check (vs ~$100).

---

## 3. PRICING & EXIT STRATEGY

**Enterprise Pricing Model**:
*   **Base Layer**: $3k - $8k / month (Includes Core Cyber).
*   **Premiums**:
    *   Self-Harm/Deepfake: +20%
    *   EU AI Act / CA Minor: +30%
    *   Supply Chain: +35%
    *   KYB/KYE: +40%

**Total Contract Value**: ~$10k - $30k / month per mid-size enterprise.
**Exit**: Acquisition by Google (CapitalG), Palo Alto, or Microsoft in 2-3 years.
**Target Valuation**: 10x - 20x Revenue Multiple ($100M+).
