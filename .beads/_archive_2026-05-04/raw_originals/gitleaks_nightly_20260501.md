# 🛡️ Gitleaks Guardian — Audit Report

**Generated**: 2026-05-01T19:49:43Z
**Total Findings**: 1536
**BLOCK**: 1484 | **WARN**: 52 | **IGNORE**: 0

---

## 🚨 BLOCK — Immediate Action Required

> [!CAUTION]
> 1484 credential(s) detected in production code. Pipeline HALTED.

| # | Rule | File | Line | Secret (redacted) | Remediation |
|---|------|------|------|-------------------|-------------|
| 1 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.betterleaks.toml` | 68 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 2 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 2 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 3 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 146 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 4 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 9 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 5 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 9 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 6 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 10 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 7 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 10 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 8 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 11 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 9 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 11 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 10 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 12 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 11 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 12 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 12 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 13 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 13 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 13 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 14 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 14 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 15 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 14 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 16 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 15 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 17 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 15 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 18 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 16 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 19 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 16 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 20 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 17 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 21 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 17 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 22 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 18 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 23 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 18 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 24 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 19 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 25 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 19 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 26 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 20 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 27 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 20 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 28 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 21 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 29 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 21 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 30 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 22 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 31 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 22 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 32 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 23 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 33 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 23 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 34 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 24 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 35 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 24 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 36 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 25 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 37 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 25 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 38 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 26 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 39 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 26 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 40 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 27 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 41 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 27 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 42 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 28 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 43 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 28 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 44 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 29 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 45 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 29 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 46 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 30 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 47 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 30 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 48 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 31 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 49 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 31 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 50 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 32 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 51 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 32 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 52 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 33 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 53 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 33 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 54 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 34 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 55 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 34 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 56 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 35 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 57 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 35 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 58 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 36 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 59 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 36 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 60 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 37 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 61 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 37 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 62 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 38 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 63 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 38 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 64 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 39 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 65 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 39 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 66 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 40 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 67 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 40 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 68 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 41 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 69 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 41 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 70 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 42 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 71 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 42 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 72 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 43 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 73 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 43 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 74 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 44 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 75 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 44 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 76 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 45 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 77 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 45 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 78 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 46 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 79 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 46 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 80 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 47 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 81 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 47 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 82 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 48 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 83 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 48 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 84 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 49 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 85 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 49 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 86 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 50 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 87 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 50 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 88 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 51 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 89 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 51 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 90 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 52 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 91 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 52 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 92 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 53 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 93 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 53 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 94 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 54 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 95 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 54 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 96 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 55 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 97 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 55 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 98 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 56 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 99 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 56 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 100 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 57 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 101 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 57 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 102 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 58 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 103 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 58 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 104 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 59 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 105 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 59 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 106 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 60 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 107 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 60 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 108 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 61 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 109 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 61 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 110 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 62 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 111 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 62 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 112 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 63 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 113 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 63 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 114 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 64 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 115 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 64 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 116 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 65 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 117 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 65 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 118 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 66 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 119 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 66 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 120 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 67 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 121 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 67 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 122 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 68 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 123 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 68 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 124 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 69 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 125 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 69 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 126 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 70 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 127 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 70 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 128 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 71 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 129 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 71 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 130 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 72 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 131 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 72 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 132 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 73 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 133 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 73 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 134 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 74 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 135 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 74 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 136 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 75 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 137 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 75 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 138 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 76 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 139 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 76 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 140 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 77 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 141 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 77 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 142 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 78 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 143 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 78 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 144 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 79 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 145 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 79 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 146 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 80 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 147 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 80 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 148 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 81 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 149 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 81 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 150 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 82 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 151 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 82 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 152 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 83 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 153 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 83 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 154 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 84 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 155 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 84 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 156 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 85 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 157 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 85 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 158 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 86 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 159 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 86 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 160 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 87 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 161 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 87 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 162 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 88 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 163 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 88 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 164 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 89 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 165 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 89 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 166 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 90 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 167 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 90 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 168 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 91 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 169 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 91 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 170 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 92 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 171 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 92 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 172 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 93 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 173 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 93 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 174 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 94 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 175 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 94 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 176 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 95 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 177 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 95 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 178 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 96 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 179 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 96 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 180 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 103 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 181 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 103 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 182 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 104 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 183 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 104 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 184 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 105 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 185 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 105 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 186 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 106 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 187 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 106 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 188 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 107 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 189 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 107 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 190 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 108 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 191 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 108 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 192 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 109 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 193 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 109 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 194 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 110 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 195 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 110 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 196 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 111 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 197 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 111 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 198 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 112 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 199 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 112 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 200 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 113 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 201 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 113 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 202 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 114 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 203 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 114 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 204 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 115 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 205 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 115 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 206 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 116 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 207 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 116 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 208 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 117 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 209 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 117 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 210 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 118 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 211 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 118 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 212 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 119 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 213 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 119 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 214 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 120 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 215 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 120 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 216 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 121 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 217 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 121 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 218 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 122 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 219 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 122 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 220 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 123 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 221 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 123 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 222 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 124 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 223 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 124 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 224 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 125 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 225 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 125 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 226 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 126 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 227 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 126 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 228 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 129 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 229 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 129 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 230 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 130 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 231 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 130 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 232 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 131 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 233 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 131 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 234 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 132 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 235 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 132 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 236 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 135 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 237 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 135 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 238 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 136 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 239 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 136 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 240 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 137 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 241 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 137 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 242 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 141 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 243 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 141 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 244 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 142 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 245 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 142 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 246 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 150 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 247 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 150 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 248 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 151 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 249 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 151 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 250 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 152 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 251 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 152 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 252 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 153 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 253 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 153 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 254 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 154 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 255 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 154 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 256 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 155 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 257 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 155 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 258 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 156 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 259 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 156 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 260 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 157 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 261 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 157 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 262 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 158 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 263 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 158 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 264 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 159 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 265 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 159 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 266 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 160 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 267 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 160 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 268 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 161 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 269 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 161 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 270 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 162 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 271 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 162 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 272 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 163 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 273 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 163 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 274 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 164 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 275 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 164 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 276 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 165 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 277 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 165 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 278 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 166 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 279 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 166 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 280 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 167 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 281 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 167 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 282 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 168 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 283 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 168 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 284 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 169 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 285 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 169 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 286 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 170 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 287 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 170 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 288 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 171 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 289 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 171 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 290 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 172 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 291 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 172 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 292 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 173 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 293 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 173 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 294 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 174 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 295 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 174 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 296 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 175 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 297 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 175 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 298 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 176 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 299 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 176 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 300 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 177 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 301 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 177 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 302 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 178 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 303 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 178 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 304 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 179 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 305 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 179 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 306 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 180 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 307 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 180 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 308 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 181 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 309 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 181 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 310 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 182 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 311 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 182 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 312 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 183 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 313 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 183 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 314 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 184 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 315 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 184 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 316 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 185 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 317 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 194 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 318 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 194 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 319 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 195 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 320 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 195 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 321 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 196 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 322 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 196 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 323 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 197 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 324 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 197 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 325 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 198 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 326 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 198 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 327 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 199 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 328 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 199 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 329 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 200 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 330 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 200 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 331 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 201 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 332 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 201 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 333 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 202 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 334 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 202 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 335 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 203 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 336 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 203 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 337 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 204 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 338 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 204 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 339 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 205 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 340 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 205 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 341 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 206 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 342 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 206 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 343 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 207 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 344 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 207 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 345 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 208 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 346 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 208 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 347 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 209 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 348 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 209 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 349 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 220 | `AIza...2345` | Review and remediate per Cor.30 R3 |
| 350 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 220 | `AIza...2345` | Review and remediate per Cor.30 R3 |
| 351 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 230 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 352 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 230 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 353 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 231 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 354 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 231 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 355 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 232 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 356 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 232 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 357 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 233 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 358 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 233 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 359 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 234 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 360 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 234 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 361 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 235 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 362 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 235 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 363 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 236 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 364 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 236 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 365 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 237 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 366 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 237 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 367 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 238 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 368 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 238 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 369 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 239 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 370 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 239 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 371 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 240 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 372 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 240 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 373 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 241 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 374 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 241 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 375 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 242 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 376 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 242 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 377 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 243 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 378 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 243 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 379 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 244 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 380 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 244 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 381 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 245 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 382 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 245 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 383 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 246 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 384 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 246 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 385 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 247 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 386 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 247 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 387 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 248 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 388 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 248 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 389 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 249 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 390 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 249 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 391 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 250 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 392 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 250 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 393 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 251 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 394 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 251 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 395 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 252 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 396 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 252 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 397 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 253 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 398 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 253 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 399 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 254 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 400 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 254 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 401 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 255 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 402 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 255 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 403 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 256 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 404 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 256 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 405 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 257 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 406 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 257 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 407 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 258 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 408 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 258 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 409 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 259 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 410 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 259 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 411 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 260 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 412 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 260 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 413 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 261 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 414 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 261 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 415 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 262 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 416 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 262 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 417 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 263 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 418 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 263 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 419 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 264 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 420 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 264 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 421 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 265 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 422 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 267 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 423 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 267 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 424 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 268 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 425 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 268 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 426 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 269 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 427 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 269 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 428 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 270 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 429 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 270 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 430 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 271 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 431 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 271 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 432 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 272 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 433 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 272 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 434 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 273 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 435 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 273 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 436 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 274 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 437 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 274 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 438 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 275 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 439 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 275 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 440 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 276 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 441 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 276 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 442 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 277 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 443 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 277 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 444 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 278 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 445 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 278 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 446 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 279 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 447 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 279 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 448 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 280 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 449 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 280 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 450 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 281 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 451 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 281 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 452 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 282 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 453 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 282 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 454 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 97 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 455 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 98 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 456 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 99 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 457 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 100 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 458 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 101 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 459 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 102 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 460 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 127 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 461 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 128 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 462 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 133 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 463 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 134 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 464 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 138 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 465 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 139 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 466 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 140 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 467 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 143 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 468 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 144 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 469 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 145 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 470 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 187 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 471 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 188 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 472 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 189 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 473 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 190 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 474 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 191 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 475 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 210 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 476 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 211 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 477 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 212 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 478 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 213 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 479 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 214 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 480 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 215 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 481 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 216 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 482 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 217 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 483 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 218 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 484 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 219 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 485 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 223 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 486 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 224 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 487 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 225 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 488 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 226 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 489 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 227 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 490 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 57 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 491 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 81 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 492 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 105 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 493 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 494 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 495 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 33 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 496 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 34 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 497 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 129 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 498 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 130 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 499 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 153 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 500 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 154 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 501 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 177 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 502 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 178 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 503 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 201 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 504 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 202 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 505 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 225 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 506 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 226 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 507 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 249 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 508 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 250 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 509 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 273 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 510 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 274 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 511 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 297 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 512 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 298 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 513 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 321 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 514 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 322 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 515 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 345 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 516 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 346 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 517 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 369 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 518 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 370 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 519 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 393 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 520 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 394 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 521 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 417 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 522 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 418 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 523 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 441 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 524 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 442 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 525 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 465 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 526 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 466 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 527 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 489 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 528 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 490 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 529 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 513 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 530 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 514 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 531 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 537 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 532 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 538 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 533 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 561 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 534 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 562 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 535 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 585 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 536 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 586 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 537 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 609 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 538 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 610 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 539 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 633 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 540 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 634 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 541 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 657 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 542 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 658 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 543 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 681 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 544 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 682 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 545 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 705 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 546 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 706 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 547 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 729 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 548 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 730 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 549 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 753 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 550 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 754 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 551 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 777 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 552 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 778 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 553 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 801 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 554 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 802 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 555 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 825 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 556 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 826 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 557 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 849 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 558 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 850 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 559 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 873 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 560 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 874 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 561 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 897 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 562 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 898 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 563 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 921 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 564 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 922 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 565 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 945 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 566 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 946 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 567 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 969 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 568 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 970 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 569 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 993 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 570 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 994 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 571 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1017 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 572 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1018 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 573 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1041 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 574 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1042 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 575 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1065 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 576 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1066 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 577 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1089 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 578 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1090 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 579 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1113 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 580 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1114 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 581 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1137 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 582 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1138 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 583 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1161 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 584 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1162 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 585 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1185 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 586 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1186 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 587 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1209 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 588 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1210 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 589 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1233 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 590 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1234 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 591 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1257 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 592 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1258 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 593 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1281 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 594 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1282 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 595 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1305 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 596 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1306 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 597 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1329 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 598 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1330 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 599 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1353 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 600 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1354 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 601 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1377 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 602 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1378 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 603 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1401 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 604 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1402 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 605 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1425 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 606 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1426 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 607 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1449 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 608 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1450 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 609 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1473 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 610 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1474 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 611 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1497 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 612 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1498 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 613 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1521 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 614 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1522 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 615 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1545 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 616 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1546 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 617 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1569 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 618 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1570 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 619 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1593 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 620 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1594 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 621 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1617 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 622 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1618 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 623 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1641 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 624 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1642 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 625 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1665 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 626 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1666 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 627 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1689 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 628 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1690 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 629 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1713 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 630 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1714 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 631 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1737 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 632 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1738 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 633 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1761 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 634 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1762 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 635 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1785 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 636 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1786 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 637 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1809 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 638 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1810 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 639 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1833 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 640 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1834 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 641 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1857 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 642 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1858 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 643 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1881 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 644 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1882 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 645 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1905 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 646 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1906 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 647 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1929 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 648 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1930 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 649 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1953 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 650 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1954 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 651 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1977 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 652 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 1978 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 653 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2001 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 654 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2002 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 655 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2025 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 656 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2026 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 657 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2049 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 658 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2050 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 659 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2073 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 660 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2074 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 661 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2097 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 662 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2098 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 663 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2121 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 664 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2122 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 665 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2145 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 666 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2146 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 667 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2169 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 668 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2170 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 669 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2193 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 670 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2194 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 671 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2217 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 672 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2218 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 673 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2241 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 674 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2242 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 675 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2265 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 676 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2266 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 677 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2289 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 678 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2290 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 679 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2313 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 680 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2314 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 681 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2337 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 682 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2338 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 683 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2361 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 684 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2362 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 685 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2385 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 686 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2386 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 687 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2409 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 688 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2410 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 689 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2433 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 690 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2434 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 691 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2457 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 692 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2458 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 693 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2481 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 694 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2482 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 695 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2505 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 696 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2506 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 697 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2529 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 698 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2530 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 699 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2553 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 700 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2554 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 701 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2577 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 702 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2578 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 703 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2601 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 704 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2602 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 705 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2625 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 706 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2626 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 707 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2649 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 708 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2650 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 709 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2673 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 710 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2674 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 711 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2697 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 712 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2698 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 713 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2721 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 714 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2722 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 715 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2745 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 716 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2746 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 717 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2769 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 718 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2770 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 719 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2793 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 720 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2794 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 721 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2817 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 722 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2818 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 723 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2841 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 724 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2842 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 725 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2865 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 726 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2866 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 727 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2889 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 728 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2890 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 729 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2913 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 730 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2914 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 731 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2937 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 732 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2938 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 733 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2961 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 734 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2962 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 735 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2985 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 736 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 2986 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 737 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3009 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 738 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3010 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 739 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3033 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 740 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3034 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 741 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3057 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 742 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3058 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 743 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3081 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 744 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3082 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 745 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3105 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 746 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3106 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 747 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3129 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 748 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3130 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 749 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3153 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 750 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3154 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 751 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3177 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 752 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3178 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 753 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3201 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 754 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3202 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 755 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3225 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 756 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3226 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 757 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3249 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 758 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3250 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 759 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3273 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 760 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3274 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 761 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3297 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 762 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3298 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 763 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3321 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 764 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3322 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 765 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3345 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 766 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3346 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 767 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3369 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 768 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3370 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 769 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3393 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 770 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3394 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 771 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3417 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 772 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3418 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 773 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3441 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 774 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3442 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 775 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3465 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 776 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3466 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 777 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3489 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 778 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3490 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 779 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3513 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 780 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3514 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 781 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3537 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 782 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3538 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 783 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3561 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 784 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3562 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 785 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3585 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 786 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3586 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 787 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3609 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 788 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3610 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 789 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3633 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 790 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3634 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 791 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3657 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 792 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3658 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 793 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3681 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 794 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3682 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 795 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3705 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 796 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3706 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 797 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3729 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 798 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3730 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 799 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3753 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 800 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3754 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 801 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3777 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 802 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3778 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 803 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3801 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 804 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3802 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 805 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3825 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 806 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3826 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 807 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3849 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 808 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3850 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 809 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3873 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 810 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3874 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 811 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3897 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 812 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3898 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 813 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3921 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 814 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3922 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 815 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3945 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 816 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3946 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 817 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3969 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 818 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3970 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 819 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3993 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 820 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 3994 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 821 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4017 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 822 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4018 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 823 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4041 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 824 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4042 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 825 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4065 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 826 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4066 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 827 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4089 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 828 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4090 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 829 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4113 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 830 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4114 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 831 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4137 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 832 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4138 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 833 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4161 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 834 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4162 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 835 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4185 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 836 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4186 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 837 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4209 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 838 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4210 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 839 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4233 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 840 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4234 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 841 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4257 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 842 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4258 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 843 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4281 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 844 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4282 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 845 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4305 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 846 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4306 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 847 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4329 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 848 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4330 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 849 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4353 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 850 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4354 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 851 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4377 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 852 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4378 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 853 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4401 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 854 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4402 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 855 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4425 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 856 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4426 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 857 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4449 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 858 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4450 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 859 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4473 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 860 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4474 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 861 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4497 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 862 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4498 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 863 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4521 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 864 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4522 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 865 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4545 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 866 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4546 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 867 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4569 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 868 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4570 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 869 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4593 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 870 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4594 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 871 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4617 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 872 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4618 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 873 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4641 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 874 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4642 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 875 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4665 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 876 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4666 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 877 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4689 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 878 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4690 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 879 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4713 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 880 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4714 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 881 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4737 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 882 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4738 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 883 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4761 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 884 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4762 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 885 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4785 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 886 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4786 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 887 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4809 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 888 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4810 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 889 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4833 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 890 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4834 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 891 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4857 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 892 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4858 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 893 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4881 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 894 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4882 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 895 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4905 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 896 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4906 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 897 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4929 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 898 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4930 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 899 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4953 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 900 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4954 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 901 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4977 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 902 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 4978 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 903 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5001 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 904 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5002 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 905 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5025 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 906 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5026 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 907 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5049 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 908 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5050 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 909 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5073 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 910 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5074 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 911 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5097 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 912 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5098 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 913 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5121 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 914 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5122 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 915 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5145 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 916 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5146 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 917 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5169 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 918 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5170 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 919 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5193 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 920 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5194 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 921 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5217 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 922 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5218 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 923 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5241 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 924 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5242 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 925 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5265 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 926 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5266 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 927 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5289 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 928 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5290 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 929 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5313 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 930 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5314 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 931 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5337 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 932 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5338 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 933 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5361 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 934 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5362 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 935 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5385 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 936 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5386 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 937 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5409 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 938 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5410 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 939 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5433 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 940 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5434 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 941 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5457 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 942 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5458 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 943 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5481 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 944 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5482 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 945 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5505 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 946 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5506 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 947 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5529 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 948 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5530 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 949 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5553 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 950 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5554 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 951 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5577 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 952 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5578 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 953 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5601 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 954 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5602 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 955 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5625 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 956 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5626 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 957 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5649 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 958 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5650 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 959 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5673 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 960 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5674 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 961 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5697 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 962 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5698 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 963 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5721 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 964 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5722 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 965 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5745 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 966 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5746 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 967 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5769 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 968 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5770 | `AIza...BHiA` | Review and remediate per Cor.30 R3 |
| 969 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5793 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 970 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5794 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 971 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5817 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 972 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5818 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 973 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5841 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 974 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5842 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 975 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5865 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 976 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5866 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 977 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5889 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 978 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5890 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 979 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5913 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 980 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5914 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 981 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5937 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 982 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5938 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 983 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5961 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 984 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5962 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 985 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5985 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 986 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 5986 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 987 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6009 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 988 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6010 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 989 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6033 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 990 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6034 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 991 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6057 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 992 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6058 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 993 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6081 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 994 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6082 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 995 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6105 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 996 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6106 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 997 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6129 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 998 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6130 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 999 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6153 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1000 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6154 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1001 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6177 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1002 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6178 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1003 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6201 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1004 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6202 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1005 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6225 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1006 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6226 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1007 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6249 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1008 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6250 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1009 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6273 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1010 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6274 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1011 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6297 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1012 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6298 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1013 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6321 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1014 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6322 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1015 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6346 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1016 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6369 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1017 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6370 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1018 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6393 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1019 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6394 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1020 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6417 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1021 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6418 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1022 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6441 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1023 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6442 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1024 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6465 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1025 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6466 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1026 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6489 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1027 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6490 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1028 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6513 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1029 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6514 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1030 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6537 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1031 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6538 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1032 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6561 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1033 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6562 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1034 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6585 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1035 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6586 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1036 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6609 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1037 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6610 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1038 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6633 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1039 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6634 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1040 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6657 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1041 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6658 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1042 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6681 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1043 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6682 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1044 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6705 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1045 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6706 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1046 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6729 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1047 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6730 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1048 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6753 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1049 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6754 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1050 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6777 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1051 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6778 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1052 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6801 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1053 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6802 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1054 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6825 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1055 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6826 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1056 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6849 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1057 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6850 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1058 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6873 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1059 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6874 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1060 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6897 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1061 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6898 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1062 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6921 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1063 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6922 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1064 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6945 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1065 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6946 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1066 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6969 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1067 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6970 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1068 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6993 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1069 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 6994 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1070 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7017 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1071 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7018 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1072 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7041 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1073 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7042 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1074 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7065 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1075 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7066 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1076 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7089 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1077 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7090 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1078 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7113 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1079 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7114 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1080 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7137 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1081 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7138 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1082 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7161 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1083 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7162 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1084 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7185 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1085 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7186 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1086 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7209 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1087 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7210 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1088 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7233 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1089 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7234 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1090 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7257 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1091 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7258 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1092 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7281 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1093 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7282 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1094 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7305 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1095 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7306 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1096 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7329 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1097 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7330 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1098 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7353 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1099 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7354 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1100 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7377 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1101 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7378 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1102 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7401 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1103 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7402 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1104 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7425 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1105 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7426 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1106 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7449 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1107 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7450 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1108 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7473 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1109 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7474 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1110 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7497 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1111 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7498 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1112 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7521 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1113 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7522 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1114 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7545 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1115 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7546 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1116 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7569 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1117 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7570 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1118 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7593 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1119 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7594 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1120 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7617 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1121 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7618 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1122 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7641 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1123 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7642 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1124 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7665 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1125 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7666 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1126 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7689 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1127 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7690 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1128 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7713 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1129 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7714 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1130 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7737 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1131 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7738 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1132 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7761 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1133 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7762 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1134 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7785 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1135 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7786 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1136 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7809 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1137 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7810 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1138 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7833 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1139 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7834 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1140 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7857 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1141 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7858 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1142 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7881 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1143 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7882 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1144 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7905 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1145 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7906 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1146 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7929 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1147 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7930 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1148 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7953 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1149 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7954 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1150 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7977 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1151 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 7978 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1152 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8001 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1153 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8002 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1154 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8025 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1155 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8026 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1156 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8049 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1157 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8050 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1158 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8073 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1159 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8074 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1160 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8097 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1161 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8098 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1162 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8121 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1163 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8122 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1164 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8145 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1165 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8146 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1166 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8169 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1167 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8170 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1168 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8193 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1169 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8194 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1170 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8217 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1171 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8218 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1172 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8241 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1173 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8242 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1174 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8265 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1175 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8266 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1176 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8289 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1177 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8290 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1178 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8313 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1179 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8314 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1180 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8337 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1181 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8338 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1182 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8361 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1183 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8362 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1184 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8385 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1185 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8386 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1186 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8409 | `AIza...2345` | Review and remediate per Cor.30 R3 |
| 1187 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8410 | `AIza...2345` | Review and remediate per Cor.30 R3 |
| 1188 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8433 | `AIza...2345` | Review and remediate per Cor.30 R3 |
| 1189 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8434 | `AIza...2345` | Review and remediate per Cor.30 R3 |
| 1190 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8457 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1191 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8458 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1192 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8481 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1193 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8482 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1194 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8505 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1195 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8506 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1196 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8529 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1197 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8530 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1198 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8553 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1199 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8554 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1200 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8577 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1201 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8578 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1202 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8601 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1203 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8602 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1204 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8625 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1205 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8626 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1206 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8649 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1207 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8650 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1208 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8673 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1209 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8674 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1210 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8697 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1211 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8698 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1212 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8721 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1213 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8722 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1214 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8745 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1215 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8746 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1216 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8769 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1217 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8770 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1218 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8793 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1219 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8794 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1220 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8817 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1221 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8818 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1222 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8841 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1223 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8842 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1224 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8865 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1225 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8866 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1226 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8889 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1227 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8890 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1228 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8913 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1229 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8914 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1230 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8937 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1231 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8938 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1232 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8961 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1233 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8962 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1234 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8985 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1235 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 8986 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1236 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9009 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1237 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9010 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1238 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9033 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1239 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9034 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1240 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9057 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1241 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9058 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1242 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9081 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1243 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9082 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1244 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9105 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1245 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9106 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1246 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9129 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1247 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9130 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1248 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9153 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1249 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9154 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1250 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9177 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1251 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9178 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1252 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9201 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1253 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9202 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1254 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9225 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1255 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9226 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1256 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9249 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1257 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9250 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1258 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9273 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1259 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9274 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1260 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9297 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1261 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9298 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 1262 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9321 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1263 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9322 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1264 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9345 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1265 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9346 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1266 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9369 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1267 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9370 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1268 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9393 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1269 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9394 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1270 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9417 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1271 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9418 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1272 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9441 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1273 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9442 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1274 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9465 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1275 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9466 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1276 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9489 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1277 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9490 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1278 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9513 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1279 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9514 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1280 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9537 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1281 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9538 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1282 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9561 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1283 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9562 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1284 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9585 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1285 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9586 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1286 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9609 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1287 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9610 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1288 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9633 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1289 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9634 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1290 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9657 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1291 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9658 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1292 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9681 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1293 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9682 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1294 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9705 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1295 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9706 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1296 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9729 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1297 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9730 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1298 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9753 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1299 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9754 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1300 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9777 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1301 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9778 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1302 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9801 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1303 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9802 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1304 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9825 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1305 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9826 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1306 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9849 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1307 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9850 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1308 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9873 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1309 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9874 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1310 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9897 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1311 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9898 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1312 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9921 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1313 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9922 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1314 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9945 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1315 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9946 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1316 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9969 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1317 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9970 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1318 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9993 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1319 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 9994 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1320 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10017 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1321 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10018 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1322 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10041 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1323 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10042 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1324 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10065 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1325 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10066 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1326 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10089 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1327 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10090 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1328 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10113 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1329 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10114 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1330 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10137 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1331 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10138 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 1332 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10161 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1333 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10162 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1334 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10185 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1335 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10186 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 1336 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10209 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1337 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10210 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1338 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10233 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1339 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10234 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 1340 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10257 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1341 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10258 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1342 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10281 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1343 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10282 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 1344 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10305 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1345 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10306 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1346 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10329 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1347 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10330 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 1348 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10353 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1349 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10354 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1350 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10377 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1351 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10378 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 1352 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10401 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1353 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10402 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1354 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10425 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1355 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10426 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 1356 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10449 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1357 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10450 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1358 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10473 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1359 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10474 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 1360 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10497 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1361 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10498 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1362 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10521 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1363 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10522 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 1364 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10545 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1365 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10546 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1366 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10569 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1367 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10570 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 1368 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10593 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1369 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10594 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1370 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10617 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1371 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10618 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 1372 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10641 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1373 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10642 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1374 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10665 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1375 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10666 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 1376 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10689 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1377 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10690 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1378 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10713 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1379 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10714 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 1380 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10737 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1381 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10738 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1382 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10761 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1383 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10762 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 1384 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10785 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1385 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10786 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1386 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10809 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1387 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10810 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 1388 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10833 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1389 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10834 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1390 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10857 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1391 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10858 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 1392 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10881 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1393 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10882 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1394 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10905 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1395 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10906 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 1396 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10929 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1397 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10953 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1398 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 10977 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1399 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11001 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1400 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11025 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1401 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11049 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1402 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11073 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1403 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11097 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1404 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11121 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1405 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11145 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1406 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11169 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1407 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11193 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1408 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11217 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1409 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11241 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1410 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11265 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1411 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11289 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1412 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11313 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1413 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11337 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1414 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11361 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1415 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11385 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1416 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11409 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1417 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11433 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1418 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11457 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1419 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11481 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1420 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11505 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1421 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11529 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1422 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11553 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1423 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11577 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1424 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11601 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1425 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11625 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1426 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11649 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1427 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11673 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1428 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11697 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1429 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11721 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1430 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11745 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1431 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11769 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1432 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12801 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1433 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12802 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1434 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12825 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1435 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12826 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1436 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12849 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1437 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12850 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1438 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12873 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1439 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12874 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1440 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12897 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1441 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12898 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1442 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12921 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 1443 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12922 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 1444 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12945 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1445 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12946 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1446 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12969 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1447 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12970 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1448 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12993 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1449 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 12994 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1450 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13017 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1451 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13018 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1452 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13041 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1453 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13042 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1454 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13065 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 1455 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13066 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 1456 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13089 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1457 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13090 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1458 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13113 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1459 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13114 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1460 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13137 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1461 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13138 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1462 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13161 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1463 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13162 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1464 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13185 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1465 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13186 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1466 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13209 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 1467 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13210 | `AIza...RBBA` | Review and remediate per Cor.30 R3 |
| 1468 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13233 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1469 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13234 | `AIza...sl4U` | Review and remediate per Cor.30 R3 |
| 1470 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13257 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1471 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13258 | `AIza...gUfk` | Review and remediate per Cor.30 R3 |
| 1472 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13281 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1473 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13282 | `AIza...TGQg` | Review and remediate per Cor.30 R3 |
| 1474 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13305 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1475 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13306 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1476 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13329 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1477 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13330 | `AIza...H7UI` | Review and remediate per Cor.30 R3 |
| 1478 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13353 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1479 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13449 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1480 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13473 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1481 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13497 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 1482 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13521 | `***REDACTED***` | Move to Secret Manager (`STRIPE_SECRET_KEY`) |
| 1483 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13425 | `AIza...9012` | Review and remediate per Cor.30 R3 |
| 1484 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 13426 | `AIza...9012` | Review and remediate per Cor.30 R3 |

## ⚠️ WARN — Manual Review Recommended

| # | Rule | File | Line | Reason |
|---|------|------|------|--------|
| 1 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 192 | Generic pattern match — manual review recommended |
| 2 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 229 | Generic pattern match — manual review recommended |
| 3 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11793 | Generic pattern match — manual review recommended |
| 4 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11817 | Generic pattern match — manual review recommended |
| 5 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.reports/secrets/betterleaks-dir.json` | 11841 | Generic pattern match — manual review recommended |
| 6 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/huggingface_hub/inference/_client.py` | 2788 | Generic pattern match — manual review recommended |
| 7 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/huggingface_hub/inference/_generated/_async_client.py` | 2833 | Generic pattern match — manual review recommended |
| 8 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/_experimental/out/_next/static/chunks/a5ab01e86df55e55.js` | 10 | Generic pattern match — manual review recommended |
| 9 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/_experimental/out/_next/static/chunks/a5ab01e86df55e55.js` | 10 | Generic pattern match — manual review recommended |
| 10 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/spend_tracking/spend_tracking_utils.py` | 301 | Generic pattern match — manual review recommended |
| 11 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/spend_tracking/spend_tracking_utils.py` | 330 | Generic pattern match — manual review recommended |
| 12 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 13 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 14 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 15 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 16 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 17 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 18 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 19 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 20 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 21 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 22 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 23 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 24 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 25 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 26 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 27 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 28 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 29 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 30 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 31 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 32 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 33 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 34 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 35 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 36 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 37 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 38 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 39 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 40 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 41 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 17 | Test fixture — verify not using real credentials |
| 42 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 107 | Test fixture — verify not using real credentials |
| 43 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 44 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 45 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scratch/repos/everything-claude-code/tests/hooks/governance-capture.test.js` | 67 | Test fixture — verify not using real credentials |
| 46 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scratch/repos/everything-claude-code/tests/hooks/governance-capture.test.js` | 47 | Test fixture — verify not using real credentials |
| 47 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scratch/repos/everything-claude-code/tests/hooks/governance-capture.test.js` | 497 | Test fixture — verify not using real credentials |
| 48 | `stripe-secret-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tests/test_secret_scanner.py` | 50 | Test fixture — verify not using real credentials |
| 49 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tests/test_secret_scanner.py` | 44 | Test fixture — verify not using real credentials |
| 50 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tests/test_secret_scanner.py` | 66 | Test fixture — verify not using real credentials |
| 51 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tests/test_secret_scanner.py` | 66 | Test fixture — verify not using real credentials |
| 52 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/tests/test_block_allow_engine.py` | 177 | Test fixture — verify not using real credentials |

---

## 5-Layer Defense Status

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | Pre-commit hook (`.pre-commit-config.yaml`) | ✅ Active |
| 2 | Finish Changes pipeline (`finish_changes.py`) | ✅ Blocking |
| 3 | Omega Sync gate (`omega_sync.py`) | ✅ Blocking |
| 4 | CI/CD PR gate (`security-audit.yml`) | ✅ Active |
| 5 | On-demand audit (`/gitleaks-guardian`) | ✅ This scan |

