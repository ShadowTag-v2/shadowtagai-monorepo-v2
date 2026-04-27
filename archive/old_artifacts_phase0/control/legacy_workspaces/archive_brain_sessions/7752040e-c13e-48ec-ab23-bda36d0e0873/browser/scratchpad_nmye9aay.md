# Billing Research Plan

- [x] Navigate to GCP Billing Overview
- [x] Review Cost Trends and project-level distribution
- [x] Investigate February 2026 charges (last major cycle)
- [x] Investigate March 2026 charges (unbilled/active)
- [ ] Identify top services and projects incurring costs
- [ ] Summarize findings

## Findings (as of March 13, 2026)

### February 2026 (Total: $625.93)
- **Top Project:** `shadowtag-omega-v4` (only one with major costs)
- **Top Services:**
  - Cloud Workstations: $225.00
  - Gemini API: $147.96
  - AlloyDB: $100.71
  - Memorystore for Redis: $54.73

### March 1-13, 2026 (Total: $519.29)
- **Top Project:** `shadowtag-omega-v4`
- **Top Services:**
  - AlloyDB: $171.20
  - Cloud Workstations: $164.93
  - Memorystore for Redis: $83.84
  - Gemini API: $39.75
  - Compute Engine: ~$25
  - Cloud SQL: ~$10

**Note:** Workstations, AlloyDB, and Redis were deleted on March 13. These charges represent usage *before* deletion.
- [ ] Verify if other projects had costs in February.
