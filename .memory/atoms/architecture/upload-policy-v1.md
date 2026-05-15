---
id: "architecture-upload-policy-v1"
created: "2026-04-27T17:52:00Z"
updated: "2026-04-27T17:52:00Z"
category: architecture
tags: [upload, push-gates, git, gcs, lfs, artifact]
references:
  - file:///upload_policy.yaml
  - file:///scripts/push-with-app-gates.sh
  - file:///scripts/classify-upload-payload.sh
status: active
---

# Two-Lane Upload Doctrine

## Lanes

### Lane 1: Git Source
Canonical source, policy, small docs, tests, build metadata.
- Warning threshold: 50 MiB per file
- Hard block: 95 MiB per file (GitHub blocks at 100 MiB)
- No archives, no model files, no secrets

### Lane 2: Artifact Archive
Large payloads, source archives, generated outputs, reference mirrors.
- Storage: GCS (`gs://shadowtag-artifacts`)
- Git representation: manifest entry + SHA256 + owner + attribution

## Push Gate Enforcement

`scripts/push-with-app-gates.sh` enforces:
1. GitHub App JWT authentication (1-hour expiry)
2. File size limits (warn >50 MiB, block >95 MiB)
3. Betterleaks secret scan
4. Forbidden extension check (.zip, .onnx, .pt, .safetensors, etc.)
5. Forbidden path check (archive/, external_repos/, venv/, etc.)

## LFS Policy

LFS is forbidden by default. Allowed only by exception with:
- Owner declaration
- Reason documentation
- Budget check
- Proof that artifact archive was considered and rejected
