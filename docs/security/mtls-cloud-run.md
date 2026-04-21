# mTLS Between Cloud Run Services

## Current State
- Service-to-service auth uses OIDC tokens (identity-based)
- Cloud Run services authenticate via `Authorization: Bearer <OIDC_TOKEN>`
- This is Google's recommended approach for Cloud Run

## Why Not Traditional mTLS
Cloud Run uses Google-managed TLS termination at the ingress layer.
Traditional mTLS (mutual certificate exchange) is NOT how Cloud Run
service-to-service works — Google handles it differently:

### Google's Approach: Identity-Based Auth
```
Service A → [OIDC Token in header] → Cloud Run Ingress → Service B
                                      ↑ TLS terminated here
```

- All traffic is TLS-encrypted (Google-managed certificates)
- Authentication is identity-based (OIDC tokens from IAM)
- Authorization is role-based (IAM `roles/run.invoker`)

### Current Service-to-Service Setup
```bash
# Cloud Scheduler → Cloud Run (OIDC)
gcloud scheduler jobs create http ... \
  --oidc-service-account-email="counselconduit-sa@..." \
  --oidc-token-audience="https://counselconduit-..."

# Cloud Tasks → Cloud Run (OIDC)
gcloud tasks create-http-task ... \
  --oidc-service-account-email="counselconduit-sa@..." \
  --oidc-token-audience="https://counselconduit-..."
```

### Ingress Controls (Defense in Depth)
```bash
# Restrict to internal + load balancer only
gcloud run services update counselconduit \
  --ingress=internal-and-cloud-load-balancing
```

## If True mTLS Is Required (Enterprise/FedRAMP)
Use [Cloud Service Mesh](https://cloud.google.com/service-mesh/docs/overview)
with Istio sidecars. This is a Phase 4 (Enterprise) feature.
