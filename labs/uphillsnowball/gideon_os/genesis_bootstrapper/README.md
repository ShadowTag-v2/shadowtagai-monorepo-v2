# Genesis Bootstrapper

> Gideon OS Block 14 — Zero-to-One Infrastructure Provisioner

## Purpose

Genesis Bootstrapper is the initial provisioning system that creates a fully operational Gideon OS instance from a bare GCP project. It orchestrates the sequence of Terraform, Firebase, Cloud Run, and secret provisioning steps required to stand up the full stack.

## Architecture

```
┌───────────────────────────────────────────────┐
│            Genesis Bootstrapper               │
├───────────────────────────────────────────────┤
│                                               │
│  Phase 1: GCP Project Setup                   │
│    → Enable APIs (Cloud Run, Firestore, etc.) │
│    → Create Service Accounts                  │
│    → Configure IAM Bindings                   │
│                                               │
│  Phase 2: Secret Provisioning                 │
│    → GCP Secret Manager population            │
│    → Firebase Admin SA key generation          │
│    → GitHub App PEM distribution               │
│                                               │
│  Phase 3: Infrastructure Deployment           │
│    → Sovereign Infra TF apply                 │
│    → Firebase Hosting init + deploy           │
│    → Cloud Run service deployment             │
│                                               │
│  Phase 4: Verification                        │
│    → Health checks on all endpoints           │
│    → Lighthouse CI assertion suite            │
│    → Egress scan + betterleaks                │
│                                               │
└───────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| Idempotent Runs | Safe to re-run — checks existing state before creating |
| Secret Rotation | Automated key rotation via GCP Secret Manager |
| Health Verification | Post-deploy health checks on all services |
| Rollback Support | Terraform state management for safe rollback |
| Multi-Environment | dev/staging/prod environment isolation |

## Usage

```bash
# Full bootstrap (new project)
python labs/uphillsnowball/gideon_os/genesis_bootstrapper/bootstrap.py \
  --project shadowtag-omega-v4 \
  --region us-central1 \
  --phase all

# Single phase re-run
python genesis_bootstrapper/bootstrap.py --phase secrets
```

## Prerequisites

- `gcloud` CLI authenticated with Owner role
- Terraform >= 1.5.0
- Firebase CLI (`firebase-tools`)
- GitHub App PEM at `$SHADOWTAG_PEM`

## Status

🔶 Scaffolded — Phase 1-2 scripts operational, Phase 3-4 pending live integration testing.
