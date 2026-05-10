# 🛡️ Gitleaks Guardian — Audit Report

**Generated**: 2026-04-21T12:01:44Z
**Total Findings**: 170
**BLOCK**: 113 | **WARN**: 57 | **IGNORE**: 0

---

## 🚨 BLOCK — Immediate Action Required

> [!CAUTION]
> 113 credential(s) detected in production code. Pipeline HALTED.

| # | Rule | File | Line | Secret (redacted) | Remediation |
|---|------|------|------|-------------------|-------------|
| 1 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.env` | 45 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 2 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/github.go` | 50 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 3 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/github.go` | 88 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 4 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/github.go` | 128 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 5 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/github.go` | 129 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 6 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/github.go` | 148 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 7 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1151 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 8 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1152 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 9 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1153 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 10 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1154 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 11 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1155 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 12 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1156 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 13 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1157 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 14 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1158 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 15 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1159 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 16 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1160 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 17 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1161 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 18 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1162 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 19 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1163 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 20 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1164 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 21 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1165 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 22 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/config/betterleaks.toml` | 1166 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 23 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 39 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 24 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 40 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 25 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 41 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 26 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 42 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 27 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 43 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 28 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 44 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 29 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 45 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 30 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 46 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 31 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 47 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 32 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 48 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 33 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 49 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 34 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 50 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 35 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 51 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 36 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 52 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 37 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 53 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 38 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 54 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 39 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 67 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 40 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 68 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 41 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 69 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 42 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 72 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 43 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 73 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 44 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 74 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 45 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 75 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 46 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 76 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 47 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 77 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 48 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 78 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 49 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 79 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 50 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 80 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 51 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 81 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 52 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 82 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 53 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 83 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 54 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 84 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 55 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 85 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 56 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 86 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 57 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 87 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 58 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/github.go` | 33 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 59 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/github.go` | 69 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 60 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/github.go` | 89 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 61 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/github.go` | 90 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 62 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/github.go` | 108 | `***REDACTED***` | Rotate immediately. Use GitHub App PEM instead |
| 63 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 39 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 64 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 40 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 65 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 41 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 66 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 42 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 67 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 43 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 68 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 44 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 69 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 45 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 70 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 46 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 71 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 47 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 72 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 48 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 73 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 49 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 74 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 50 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 75 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 51 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 76 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 52 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 77 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 53 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 78 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 54 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 79 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 67 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 80 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 68 | `AIza...vFDq` | Review and remediate per Cor.30 R3 |
| 81 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 69 | `AIza...aaaa` | Review and remediate per Cor.30 R3 |
| 82 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 72 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 83 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 73 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 84 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 74 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 85 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 75 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 86 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 76 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 87 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 77 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 88 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 78 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 89 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 79 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 90 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 80 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 91 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 81 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 92 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 82 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 93 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 83 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 94 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 84 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 95 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 85 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 96 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 86 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 97 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 87 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |
| 98 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 619 | `AIza...4567` | Review and remediate per Cor.30 R3 |
| 99 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 620 | `AIza...YyIs` | Review and remediate per Cor.30 R3 |
| 100 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 621 | `AIza...agEM` | Review and remediate per Cor.30 R3 |
| 101 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 622 | `AIza...DrlU` | Review and remediate per Cor.30 R3 |
| 102 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 623 | `AIza...hrh0` | Review and remediate per Cor.30 R3 |
| 103 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 624 | `AIza...bX4A` | Review and remediate per Cor.30 R3 |
| 104 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 625 | `AIza...wX7c` | Review and remediate per Cor.30 R3 |
| 105 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 626 | `AIza...mLd4` | Review and remediate per Cor.30 R3 |
| 106 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 627 | `AIza...DQgY` | Review and remediate per Cor.30 R3 |
| 107 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 628 | `AIza...4wtM` | Review and remediate per Cor.30 R3 |
| 108 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 629 | `AIza...P5sQ` | Review and remediate per Cor.30 R3 |
| 109 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 630 | `AIza...cS7g` | Review and remediate per Cor.30 R3 |
| 110 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 631 | `AIza...vvuU` | Review and remediate per Cor.30 R3 |
| 111 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 632 | `AIza...NXsw` | Review and remediate per Cor.30 R3 |
| 112 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 633 | `AIza...FmqE` | Review and remediate per Cor.30 R3 |
| 113 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/config/gitleaks.toml` | 634 | `AIza...0nvY` | Review and remediate per Cor.30 R3 |

## ⚠️ WARN — Manual Review Recommended

| # | Rule | File | Line | Reason |
|---|------|------|------|--------|
| 1 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 2 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 3 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 4 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 5 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 6 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 7 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 8 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 9 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 10 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 11 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 12 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 13 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 14 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 15 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 16 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 17 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 18 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 19 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 20 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 21 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 22 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 23 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 24 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 25 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 26 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 27 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 28 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 29 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 30 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 17 | Test fixture — verify not using real credentials |
| 31 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 107 | Test fixture — verify not using real credentials |
| 32 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 33 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |
| 34 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/heroku.go` | 42 | Generic pattern match — manual review recommended |
| 35 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/generic.go` | 222 | Generic pattern match — manual review recommended |
| 36 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/prefect.go` | 24 | Generic pattern match — manual review recommended |
| 37 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/readme.go` | 25 | Generic pattern match — manual review recommended |
| 38 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/greptile.go` | 26 | Generic pattern match — manual review recommended |
| 39 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/greptile.go` | 28 | Generic pattern match — manual review recommended |
| 40 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/cmd/generate/config/rules/gcp.go` | 69 | Generic pattern match — manual review recommended |
| 41 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/flyio.go` | 47 | Generic pattern match — manual review recommended |
| 42 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/gcp.go` | 69 | Generic pattern match — manual review recommended |
| 43 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/generic.go` | 221 | Generic pattern match — manual review recommended |
| 44 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/heroku.go` | 42 | Generic pattern match — manual review recommended |
| 45 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/readme.go` | 25 | Generic pattern match — manual review recommended |
| 46 | `generic-api-key-inline` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/gitleaks/cmd/generate/config/rules/prefect.go` | 24 | Generic pattern match — manual review recommended |
| 47 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 242 | Test fixture — verify not using real credentials |
| 48 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 242 | Test fixture — verify not using real credentials |
| 49 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 252 | Test fixture — verify not using real credentials |
| 50 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 252 | Test fixture — verify not using real credentials |
| 51 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 253 | Test fixture — verify not using real credentials |
| 52 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 254 | Test fixture — verify not using real credentials |
| 53 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 266 | Test fixture — verify not using real credentials |
| 54 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 266 | Test fixture — verify not using real credentials |
| 55 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 267 | Test fixture — verify not using real credentials |
| 56 | `github-token` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 268 | Test fixture — verify not using real credentials |
| 57 | `google-api-key` | `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/third_party/security/betterleaks/detect/detect_test.go` | 2964 | Test fixture — verify not using real credentials |

---

## 5-Layer Defense Status

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | Pre-commit hook (`.pre-commit-config.yaml`) | ✅ Active |
| 2 | Finish Changes pipeline (`finish_changes.py`) | ✅ Blocking |
| 3 | Omega Sync gate (`omega_sync.py`) | ✅ Blocking |
| 4 | CI/CD PR gate (`security-audit.yml`) | ✅ Active |
| 5 | On-demand audit (`/gitleaks-guardian`) | ✅ This scan |

