# Vault Constitution

> Gideon OS Block 1 — Zero-Trust Policy Engine

## Purpose

Vault Constitution is the foundational policy engine that governs all access control, secret management, and authorization decisions across Gideon OS. It implements RBAC with jurisdiction-aware policies.

## Key Features

| Feature | Description |
|---------|-------------|
| RBAC Engine | Role-based access control for all Gideon OS blocks |
| Secret Rotation | Automated key rotation via GCP Secret Manager |
| Policy Evaluation | Real-time policy evaluation for every request |
| Audit Trail | Complete authorization decision logging |
| Jurisdiction Awareness | Cross-references with Jurisdiction Forge |

## Policy Hierarchy

1. **System Policies** — Immutable rules (no secret in code, no raw DB objects)
2. **Role Policies** — Per-role permissions (admin, operator, viewer)
3. **Resource Policies** — Per-resource access rules
4. **Jurisdiction Policies** — Data residency enforcement

## Integration Points

- **Shield1 Ingress**: Receives auth tokens for policy evaluation
- **All Blocks**: Every block queries Vault for authorization
- **GCP Secret Manager**: Backend for secret storage and rotation

## Status

🟢 Active — Policy engine operational, integrated with Shield1 and all service blocks.
