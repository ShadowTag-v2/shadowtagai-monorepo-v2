# Local Cloud Run Deployment & Authorization Audit

**Execution:**
When `gcloud run deploy` (or the VS Code extension equivalent) is executed, the following occurs:

1. `docker build` processes `serverless.Dockerfile`.
2. OCI-compliant image is pushed to Artifact Registry.
3. Cloud Run provisions a Knative environment.

**Expected Results & Auth Matrix Affirmation:**

- **Tier 1 (IAM):** The container will inherit `swarm-controller-sa` identity automatically, assuming its permissions.
- **Tier 2 (IAP):** Front-door HTTP traffic will be intercepted by Google's Identity-Aware Proxy. Unauthenticated requests instantly return 401/403.
- **Tier 3 (OAuth/OIDC):** For ADK agent specific flows inside the container.
- **Tier 4 (Vaulted):** Twilio/Web3 tokens injected securely via Environment Variable mapping at deploy time.

Success is verified when the container reports `status: "Sovereign OS Active"` at `/system_health_check` and rejects unauthorized internal execution.
