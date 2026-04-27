# Go-Live Integration Plan: Financials, Data & grounding

**Date:** 2026-01-28
**Subject:** Folding In Core Capabilities for Launch
**Persona:** Boardroom (IQ 160)

## I. Data Pipeline: Pub/Sub SMTs (Simple Message Transforms)
To replace complex Dataflow jobs for the Data Lake (`shadowtag-omega-v2`), we will use **Pub/Sub SMTs** and **Cloud Storage Subscriptions**.

### Implementation
1.  **Topic:** `omega-lake-ingest`
2.  **Subscription:** `omega-lake-gcs-sub`
3.  **Transform:** JavaScript UDF for PII Redaction (Judge 6 Logic).
    *   *Redacts:* email, ssn, phone.
4.  **Destination:** `gs://shadowtag-omega-v2-lake/raw/`

## II. Grounded Generation (Google Search)
We will integrate the "Vertex AI Grounded Generation" sample into `GCA_Core`.
*   **Source:** `https://docs.cloud.google.com/generative-ai-app-builder/docs/samples/genappbuilder-grounded-generation-google-search`
*   **Integration:** Update `src/antigravity/genkit_wrapper.py` to support `tools=[Tool.from_google_search_retrieval(grounding_service)]`.

## III. Financial Financial Integration (Stripe & Quicken)
### 1. Stripe (Payments)
*   **Service:** `src/libs/ShadowTag-v2/financial/stripe_wrapper.py`
*   **Features:** Subscription management for "God Mode Cycles".
*   **Webhook Handler:** `bin/n-autoresearch/Kosmos/BioAgentss-server.py` endpoint `/webhooks/stripe`.

### 2. Quicken Pro (Ledger)
*   **Export:** QIF/OFX generator for "Whale Data" ingestion.
*   **Location:** `src/libs/ShadowTag-v2/financial/quicken_exporter.py`

## IV. Billing & Optimization
*   **Project:** `shadowtag-omega-v2`
*   **Action:** Enable `Committed Use Discounts` (CUDs) for Cloud Run (we are committed to this architecture).
*   **API Enablement:** Auto-enable `search-console`, `billingbudgets`, `recommender`.

## V. Execution Order
1.  **Fix Cloud Run Blocker** (Priority 0).
2.  **Enable APIs**.
3.  **Deploy Pub/Sub SMTs**.
4.  **Integrate Stripe/Quicken**.
