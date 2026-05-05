# 🛡️ Gitleaks Guardian — Audit Report

**Generated**: 2026-04-27T21:32:50Z
**Total Findings**: 556
**BLOCK**: 489 | **WARN**: 41 | **IGNORE**: 26

---

## 🚨 BLOCK — Immediate Action Required

> [!CAUTION]
> 489 credential(s) detected in production code. Pipeline HALTED.

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

## ⚠️ WARN — Manual Review Recommended

| # | Rule | File | Line | Reason |
|---|------|------|------|--------|
| 1 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 192 | Generic pattern match — manual review recommended |
| 2 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.beads/betterleaks_dir_audit_2026-04-24.csv` | 229 | Generic pattern match — manual review recommended |
| 3 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/huggingface_hub/inference/_generated/_async_client.py` | 2833 | Generic pattern match — manual review recommended |
| 4 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/huggingface_hub/inference/_client.py` | 2788 | Generic pattern match — manual review recommended |
| 5 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/_experimental/out/_next/static/chunks/a5ab01e86df55e55.js` | 10 | Generic pattern match — manual review recommended |
| 6 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/_experimental/out/_next/static/chunks/a5ab01e86df55e55.js` | 10 | Generic pattern match — manual review recommended |
| 7 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/spend_tracking/spend_tracking_utils.py` | 301 | Generic pattern match — manual review recommended |
| 8 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv-3.14-bak/lib/python3.14/site-packages/litellm/proxy/spend_tracking/spend_tracking_utils.py` | 330 | Generic pattern match — manual review recommended |
| 9 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 10 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 11 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 12 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 13 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 14 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 15 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 16 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 17 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 18 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 19 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 20 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 21 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 22 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 23 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 24 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 25 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 26 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 27 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 28 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 29 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 30 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 31 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 32 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 33 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 34 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 35 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 36 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 37 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 38 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 17 | Test fixture — verify not using real credentials |
| 39 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 107 | Test fixture — verify not using real credentials |
| 40 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 41 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |

## ✅ IGNORE — Auto-classified (26 findings)

These were auto-classified as false positives and added to `.gitleaksignore`.

- **Third-party path: docs/AUDIT_REPORT\.md**: 23 findings
- **Third-party path: \.agent/reports/**: 2 findings
- **Third-party path: \.stitch-sdk/**: 1 findings

---

## 5-Layer Defense Status

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | Pre-commit hook (`.pre-commit-config.yaml`) | ✅ Active |
| 2 | Finish Changes pipeline (`finish_changes.py`) | ✅ Blocking |
| 3 | Omega Sync gate (`omega_sync.py`) | ✅ Blocking |
| 4 | CI/CD PR gate (`security-audit.yml`) | ✅ Active |
| 5 | On-demand audit (`/gitleaks-guardian`) | ✅ This scan |

