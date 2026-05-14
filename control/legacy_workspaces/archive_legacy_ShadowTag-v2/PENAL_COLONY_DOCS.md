# Penal Colony Sovereign: Operational Guide & Architecture

## 1. Flux Deployment for Kubernetes Sovereign Cluster

### Steps
1. **Install FluxCD CLI**.
2. **Bootstrap Flux**:
   ```bash
   flux bootstrap git --url=<your-repo-url>
   ```
3. **Configure GitRepository**: Create a CRD pointing to your config repo.
4. **Environment Kustomization**: Create Kustomization CRDs for each environment.
5. **Credentials**: Store SSH/PAT as Kubernetes secrets.
6. **Verify**: Run `flux check`.
7. **Apply**: Push to Git to trigger GitOps sync.

## 2. OPA Gatekeeper Multi-tenancy Pitfalls

- **Misconfigured Constraints**: missing trailing slashes in repo policies leading to bypasses.
- **Namespace Bypass**: Attackers exploiting namespace misconfigurations.
- **Subdomain Bypass**: Imprecise domain matching.
- **Resource Contention**: Poorly scoped quotas causing denial-of-service.

## 3. Capsule vs OPA Gatekeeper Comparison

| Feature | Capsule | OPA Gatekeeper |
| :--- | :--- | :--- |
| **Isolation** | Logical, namespace-based | Policy-based, cross-namespace |
| **Quotas** | Built-in, easy | Requires custom Rego |
| **Language** | K8s-native (YAML) | Rego (Turing-complete) |
| **Use Case** | Simple multi-tenancy | Complex compliance logic |
| **Security** | Strong RBAC isolation | Fine-grained customization |
| **Complexity** | Low | Medium/High |

> **Verdict**: Capsule for straightforward quota/tenant management. OPA for complex, fine-grained policy enforcement.

## 4. Kyverno vs OPA Gatekeeper for Flux

| Feature | Kyverno | OPA Gatekeeper |
| :--- | :--- | :--- |
| **Policy Language** | YAML | Rego |
| **Mutation** | Excellent (Native) | Limited |
| **Overhead** | Low (Single controller) | Higher (Sidecars/Constraints) |
| **Flux Fit** | Auto-provisioning SAs | Validation/Constraints |

## 5. Next Steps for Production

1. **Finalize Policies**: Ensure OPA, Vault, Flux, Capsule, and Kyverno policies are tested.
2. **Deploy Core**: Install FluxCD and Capsule on the cluster.
3. **Bootstrap OPA**: Import Rego policies via Gatekeeper.
4. **Integrate Vault**: Configure secrets management.
5. **Observability**: Set up alerting for policy violations.
6. **Audit**: Conduct security penetration testing.
7. **Rollout**: Phased production deployment.

## 6. Troubleshooting OPA Gatekeeper Performance

- **Parallel Calls**: Limit concurrent audits to reduce RAM/CPU usage.
- **Throttling**: Monitor API requests; adjust `auditInterval` and replicas.
- **Resources**: Ensure sufficient CPU/Mem; scale replicas horizontally.
- **Optimization**: Cache data, avoid wildcards, use gRPC.

## 7. OPA Vault Integration (Rego)

```rego
package vault_example
import data.vault
default allow := false

allow {
    secret := vault.send({"address": "http://vault:8200", "token": "dev-token", "kv2_get": {"mount_path": "secret", "path": "opa/license"}})
    secret.data.value == "valid-license"
}
```

## 8. Flux GitOps for Air-Gapped Clusters

1. **Offline Install**: Download binaries/images on connected host, transfer to air-gapped.
2. **Manual Sync**: Disable auto-sync; control via manual triggers.
3. **Internal Git/Registry**: Host manifests and images internally.

## 9. Network Policy using OPA

```rego
package network_policy
default allow := false
allow {
    input.kind == "NetworkPolicy"
    input.spec.podSelector.matchLabels["tenant"] == input.metadata.namespace
}
```

## 15. Vault Rego Bundles (Production)

- **Structure**: Secret policies + Access Control.
- **Manifest**:
  ```json
  {"roots": ["vault/secrets", "vault/access"], "rego_version": "v0.38.0"}
  ```
- **Build**: Use `opa build` and serve via internal Nginx.

## 16. Flux Mirror Cache (Air-Gapped)

1. **Mirror Registry**: Use Harbor/Artifactory.
2. **Bootstrap**:
   ```bash
   flux bootstrap git \
     --registry=registry.internal/fluxcd \
     --url=ssh://git@internal/repo \
     --private-key-file=key \
     --path=clusters/my-cluster
   ```
3. **Image Pull Secret**: Auto-configured by Flux CLI.

## 17. Benchmarking Gatekeeper

- **Metrics**:
  - `gatekeeper_violations`
  - `gatekeeper_webhook_duration_seconds_bucket`
  - `gatekeeper_webhook_request_count`
- **Tuning**: Adjust `GOMAXPROCS` and Rego complexity.

## 18. OPA External Data (HTTP)

```rego
package external_data
import future.keywords.in
data := http.send({"method": "GET", "url": "http://vault:8200/v1/secret/data/opa/license"})["body"]
default allow := false
allow { data.value == "valid-license" }
```

## 19. Troubleshooting Flux Offline

- **Logs**: Check controller logs for connectivity errors.
- **Manual Sync**: Trigger to diagnose.
- **Credentials**: rotate if bootstrap fails.

## 15. Vault Rego Bundles (Production)

- **Structure**: Secret policies + Access Control.
- **Manifest**:
  ```json
  {"roots": ["vault/secrets", "vault/access"], "rego_version": "v0.38.0"}
  ```
- **Build**: Use `opa build` and serve via internal Nginx.

## 16. Flux Mirror Cache (Air-Gapped)

1. **Mirror Registry**: Use Harbor/Artifactory.
2. **Bootstrap**:
   ```bash
   flux bootstrap git \
     --registry=registry.internal/fluxcd \
     --url=ssh://git@internal/repo \
     --private-key-file=key \
     --path=clusters/my-cluster
   ```
3. **Image Pull Secret**: Auto-configured by Flux CLI.

## 17. Benchmarking Gatekeeper

- **Metrics**:
  - `gatekeeper_violations`
  - `gatekeeper_webhook_duration_seconds_bucket`
  - `gatekeeper_webhook_request_count`
- **Tuning**: Adjust `GOMAXPROCS` and Rego complexity.

## 18. OPA External Data (HTTP)

```rego
package external_data
import future.keywords.in
data := http.send({"method": "GET", "url": "http://vault:8200/v1/secret/data/opa/license"})["body"]
default allow := false
allow { data.value == "valid-license" }
```

## 19. Troubleshooting Flux Offline

- **Logs**: Check controller logs for connectivity errors.
- **Manual Sync**: Trigger to diagnose.
- **Credentials**: rotate if bootstrap fails.

## 20. Production Vault Rego Policy

```rego
package vault_policy
default allow := false
allow {
    input.operation == "read"
    input.path == "secret/data/production"
    input.auth.token_roles[_] == "trusted_troop"
    input.auth.token_ttl > 3600
}
```

## 21. Flux Air-Gapped Bootstrap (Detailed)

1. **Download**: Get CLI/Images on internet host.
2. **Copy**: Push to internal separate registry.
3. **Transfer**: Move binary to air-gapped host.
4. **Bootstrap**:
   ```bash
   flux bootstrap git \
     --registry=registry.internal/fluxcd \
     --url=ssh://git@internal/repo \
     --private-key-file=key \
     --path=clusters/my-cluster
   ```

## 22. Rego Optimization

- **Automated**: Rely on OPA's compiler optimization.
- **Best Practices**: Correctness > "Cleverness".
- **Indexing**: Use OPA's partial evaluation.

## 23. OPA External Data (Caching)

- **HTTP Send**: Fetch external data.
- **Caching**: configure response caching to avoid latency similar to:
  `http.send({"method": "GET", "url": "...", "cache": true})`

## 24. Vault HA Helm Chart

```yaml
server:
  ha:
    enabled: true
    raft:
      enabled: true
      setNodeId: true
  replicaCount: 3
  resources:
    requests:
      memory: "1Gi"
      cpu: "500m"
    limits:
      memory: "2Gi"
      cpu: "1000m"
```

## 25. Flux Bootstrap (Refined)

- **Private Registry**: Use internal registry for all images.
- **Pull Secret**: Auto-created in `flux-system` namespace.
- **Manual Sync**: Disable auto-sync for air-gapped control.

## 26. Gatekeeper Profiling

- **Command**: `opa eval --data rbac.rego --profile-limit 5 --format=pretty 'data.rbac.allow'`
- **Optimization**: Avoid deep nesting; leverage OPA's auto-optimization.

## 27. Vault HA Best Practices

- **StatefulSet**: Required for stable/unique network IDs.
- **Integrated Storage**: Use Raft for HA.
- **Security**: Strict KMS/HSM access controls for auto-unseal.

## 28. Flux Operator (Air-Gapped)

1. **Download**: Helm chart/binary.
2. **Transfer**: Move to secure env.
3. **Install**:
   ```bash
   helm install flux-operator ./chart -n flux-system
   ```
4. **Mirror**: Ensure images match private registry.

## 29. Gatekeeper Template Optimization

- **Schemas**: Use Structural Schemas.
- **Logic**: Use Rego OR CEL (don't mix).
- **Params**: Fine-tune via code array.

## 30. OPA External Data (Vault)

- **Bundle**: Periodic updates via OPA Bundle.
- **Push**: Real-time updates to OPA.
- **Dynamic**: `http.send()` at eval time.

## 31. Air-Gapped Case Study (Finance)

- **Strategy**: Mirror Registry + Manual Sync + Internal Git.
- **Result**: Compliant, secure GitOps without internet.

## 32. Advanced Rego Profiling

- **Profile**: `opa eval --profile-limit 5 ...`
- **Monitors**: Prometheus (latency, violations) + Detailed Logs.

## 33. Flux Operator Verification

1. **Pods**: `kubectl get pods -n flux-system`
2. **Images**: Check for private registry usage.
3. **Sync**: Confirm manual sync applies manifests.

## 34. Gatekeeper Audit vs Enforce

- **Audit**: Detect violations without blocking (`--audit-match-kind-only=true`).
- **Enforce**: Block violations real-time.
- **Workflow**: Audit -> Analyze -> Enforce.

## 35. OPA Vault Troubleshooting

- **Config**: Check Admission Controller webhook.
- **Integrity**: Verify bundle checksums.
- **Network**: Test OPA -> Vault connectivity.
- **Logs**: `kubectl logs -n gatekeeper-system ...`

## 36. Production Air-Gapped Configs

- Mirror Registry + Manual Sync + Internal Git.
- **Success Story**: Financial inst. used this exact stack for compliance.

## 37. Advanced Rego Constraint Patterns

- **Params**: Use `parameters` field for reuse.
- **Schemas**: Validated Structural Schemas.
- **Docs**: detailed usage examples in Template.

## 38. Flux Operator Air-Gapped Mirroring

- **Digests**: Use immutable image digests.
- **Automation**: Script the mirroring process.
- **Manifest**: maintain a list of all dependencies.

## 39. Gatekeeper Enforce Mode Rollout

- **Warn Mode**: Set `enforcementAction: warn` initially.
- **Dry-Run**: Audit first, then enforce.
- **Gradual**: Roll out by namespace severity.

## 40. Vault Dynamic Secrets (Rego)

Rotate credentials automatically:
```rego
package vault_dynamic
import data.vault
default allow := false
allow {
    secret := vault.send({"address": "...", "dynamic_get": {"role": "dynamic-role"}})
    secret.data.value != ""
}
```

## 41. Production Dashboards

- **Prometheus**: Scrape Gatekeeper/Flux metrics.
- **Grafana**: Visualize Reconciliations & Violations.
- **Alerting**: PagerDuty on Policy Failure.

## 42. Scaling OPA + Vault

- **Strategy**: Centralized Policy Mgmt + Vault Integration.
- **Automation**: Rotate secrets across multi-cluster.
