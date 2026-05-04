# 🛡️ Gitleaks Guardian — Audit Report

**Generated**: 2026-04-19T02:45:00Z
**Total Findings**: 859
**BLOCK**: 0 | **WARN**: 33 | **IGNORE**: 826

---

## ⚠️ WARN — Manual Review Recommended

| # | Rule | File | Line | Reason |
|---|------|------|------|--------|
| 1 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/configs/secrets.example.yml` | 16 | Generic pattern match — manual review recommended |
| 2 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 3 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 4 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 5 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 6 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 7 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 8 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 9 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 10 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infra/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 11 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 12 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 13 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 14 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 15 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 16 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 17 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 18 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 19 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/infrastructure/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 20 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 13 | Generic pattern match — manual review recommended |
| 21 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 24 | Generic pattern match — manual review recommended |
| 22 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.example` | 26 | Generic pattern match — manual review recommended |
| 23 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 31 | Generic pattern match — manual review recommended |
| 24 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 32 | Generic pattern match — manual review recommended |
| 25 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 35 | Generic pattern match — manual review recommended |
| 26 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 38 | Generic pattern match — manual review recommended |
| 27 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 41 | Generic pattern match — manual review recommended |
| 28 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/k8s/secrets.yaml.template` | 47 | Generic pattern match — manual review recommended |
| 29 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/nightly_intel_pipeline/kubernetes/secret.yaml.example` | 15 | Generic pattern match — manual review recommended |
| 30 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 17 | Test fixture — verify not using real credentials |
| 31 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/tests/test_config.py` | 107 | Test fixture — verify not using real credentials |
| 32 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 22 | Generic pattern match — manual review recommended |
| 33 | `generic-api-key-inline` | `apps/aiyou_stack/aiyou-fastapi-services/voice_consensus/k8s/05-secrets.yaml.template` | 25 | Generic pattern match — manual review recommended |

## ✅ IGNORE — Auto-classified (826 findings)

These were auto-classified as false positives and added to `.gitleaksignore`.

- **Third-party path: reference_architectures/**: 670 findings
- **Third-party path: docs/CANONICALIZATION_REPORT**: 114 findings
- **Third-party path: docs/AUDIT_REPORT\.md**: 23 findings
- **Third-party path: __pycache__/**: 9 findings
- **Third-party path: libs/cyberpunk_stack/**: 7 findings
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

