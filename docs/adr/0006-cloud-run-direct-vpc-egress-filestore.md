# ADR-0006: Cloud Run Direct VPC Egress for Filestore Access

- **Status:** Accepted
- **Date:** 2026-04-27
- **Deciders:** ShadowTag Architecture Board
- **Supersedes:** N/A

## Context

CounselConduit (Cloud Run, revision `counselconduit-00037-7mf`) needs to access
GCP Filestore for persistent file storage (uploaded legal documents, generated
reports, client attachments). Cloud Run services run in a managed environment
without direct VPC access by default.

### Options Evaluated

1. **Serverless VPC Access Connector** — Managed connector, 200Mbps per instance,
   ~$0.01/GB egress. Google-managed scaling. Latency: ~2ms additional.

2. **Direct VPC Egress** — Cloud Run instances get a NIC directly in the VPC.
   No connector overhead. Native VPC bandwidth. GA since 2024.

3. **Cloud Storage as intermediary** — Upload to GCS, process asynchronously.
   Avoids VPC entirely but adds latency and complexity.

4. **Filestore CSI via GKE** — Move to GKE for native Filestore mounts. Rejected:
   over-engineered for our scale.

## Decision

**Option 2: Direct VPC Egress.**

### Rationale

- **Cost:** Eliminates the VPC Access Connector billing ($0.01/GB + instance hours).
- **Performance:** Native VPC bandwidth vs connector's 200Mbps cap.
- **Simplicity:** Fewer moving parts. Cloud Run gets direct NIC attachment.
- **Alignment:** Google's recommended path for new Cloud Run services (GA 2024).

## Implementation

### Cloud Run Service Configuration

```yaml
# In cloudbuild.yaml or gcloud deploy command
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: counselconduit
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/vpc-access-egress: all-traffic
        run.googleapis.com/network-interfaces: |
          [{"network":"shadowtag-vpc","subnetwork":"us-central1-run"}]
```

### Filestore Instance

```
Instance: shadowtag-filestore
Tier: BASIC_HDD (1TB, $0.20/GB/mo)
Network: shadowtag-vpc
Zone: us-central1-a
Mount: /mnt/filestore/counselconduit
```

### Network Requirements

- VPC: `shadowtag-vpc` (existing)
- Subnet: `us-central1-run` (Cloud Run dedicated, /28 minimum)
- Firewall: Allow TCP 2049 (NFS) from Cloud Run subnet to Filestore IP
- IAM: Service account needs `roles/file.editor`

## Consequences

### Positive

- Zero additional infrastructure (no connector to manage).
- Full VPC bandwidth for file transfers.
- Compatible with existing Firestore + Cloud Tasks architecture.

### Negative

- Cloud Run instances consume VPC IP addresses (plan subnet sizing).
- Direct VPC egress requires specifying network at deploy time (immutable per revision).
- Filestore minimum is 1TB BASIC_HDD (~$204/mo) — evaluate vs Cloud Storage for
  small workloads.

### Risks

- **Risk #84:** Filestore 1TB minimum cost for pre-revenue phase. Mitigated by
  using BASIC_HDD tier and monitoring utilization via Cloud Monitoring.
- Subnet exhaustion if Cloud Run scales aggressively — monitor IP allocation.

## References

- [Cloud Run Direct VPC Egress](https://cloud.google.com/run/docs/configuring/vpc-direct-vpc)
- [Filestore Overview](https://cloud.google.com/filestore/docs/overview)
- CounselConduit architecture: `BUSINESS_CONTEXT_LOCKED.md`
- Production URL: `https://counselconduit-767252945109.us-central1.run.app`
