# Kyverno Generate Flux HelmRelease Capsule Multi-Tenancy Guide

## 1. Kyverno Generate Policy for Flux

Auto-generate tenant-specific `ServiceAccounts` and `RoleBindings` when `Capsule` namespaces are created.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: generate-flux-multi-tenant-resources
spec:
  background: false
  rules:
  - name: generate-serviceaccount-rolebinding
    match:
      resources:
        kinds:
        - Namespace
        selector:
          matchLabels:
            toolkit.fluxcd.io/tenant: ""
    generate:
      kind: ServiceAccount
      name: flux-reconciler
      namespace: "{{request.object.metadata.name}}"
      data: {}
    - name: generate-rolebinding
      match:
        resources:
          kinds:
          - Namespace
          selector:
            matchLabels:
              toolkit.fluxcd.io/tenant: ""
      generate:
        kind: RoleBinding
        name: flux-reconciler
        namespace: "{{request.object.metadata.name}}"
        data:
          roleRef:
            apiGroup: rbac.authorization.k8s.io
            kind: ClusterRole
            name: flux-reconciler
          subjects:
          - kind: ServiceAccount
            name: flux-reconciler
            namespace: "{{request.object.metadata.name}}"
```

## 2. Capsule ResourcePool for CPU Quota

Enforce CPU quotas per tenant using Capsule `ResourcePool`.

```yaml
apiVersion: capsule.clastix.io/v1beta1
kind: ResourcePool
metadata:
  name: tenant-a-pool
spec:
  nodeSelector:
    pool: tenant-a
  resourceQuota:
    hard:
      requests.cpu: "4"
      limits.cpu: "8"
```

## 3. Kyverno vs OPA Gatekeeper for Flux Multi-tenancy

| Feature | Kyverno | OPA Gatekeeper |
| :--- | :--- | :--- |
| **Policy Language** | YAML (K8s-native) | Rego (General-purpose) |
| **Mutation/Generation** | Excellent (Native) | Limited (Validation focus) |
| **Resource Efficiency** | Low overhead | Higher overhead (Sidecars) |
| **Multi-tenancy** | Auto-provisioning, Quotas | Complex Validation |
| **Flexibility** | K8s-Specific | Multi-Environment |
| **Maintenance** | Simple (YAML) | Complex (Rego) |

**Verdict**: Kyverno is superior for K8s-native auto-provisioning and quotas (Flux/Capsule). OPA is better for complex cross-stack compliance.

## 4. Troubleshooting: Flux Dry-Run Conflicts

- **Issue**: Flux Dry-Run triggers Kyverno mutations repeatedly, causing high load/diff noise.
- **Fix**: Tune Flux `interval` (e.g., 5-10m) to reduce reconciliation frequency. Kyverno applies mutations on every dry-run diff calculation.

## 5. EKS/GKE Multi-tenancy Setup Flow

1.  **Install**: Capsule + Kyverno.
2.  **Configure**: Apply `ResourcePool` (Capsule) and `ClusterPolicy` (Kyverno).
3.  **Onboard**: Label Namespaces with `toolkit.fluxcd.io/tenant`.
4.  **Enforce**: Kyverno ensures RBAC/Quotas are stamped out automatically.
