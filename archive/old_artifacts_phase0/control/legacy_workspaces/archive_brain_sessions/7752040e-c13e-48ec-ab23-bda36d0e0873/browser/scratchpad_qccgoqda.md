# Task: Check Cloud Run costs and domain mappings

## Plan
1. [ ] Extract Cloud Run cost for February 2026 from the billing cost table for project `shadowtag-omega-v4`.
2. [ ] Navigate to `https://console.cloud.google.com/run/domains?project=shadowtag-omega-v4`.
3. [ ] List active domain mappings and their status.
4. [ ] Report findings to the user.

## Findings
- Cloud Run Cost (Feb 2026): $0.00 for project `shadowtag-omega-v4`.
- Domain Mappings:
  - `api.shadowtagai.com` mapped to `judge-sentinel` (us-central1) - **Status: Error** (likely DNS or SSL issue).
  - `shadowtagai.com` mapped to `judge-sentinel` (us-central1) - **Status: Ready**.
  - `www.shadowtagai.com` mapped to `shadowtag-web` (us-central1) - **Status: Ready**.
- Worker Pools: Currently empty (following deletion by user).
- Cost Insight: Cloud Workstation charges ($225) are separate from Cloud Run and were the primary driver in February.
