# HeadFade Deployment Runbook

## 1. Build & Test
```bash
cd antigravity-core/mcp
npm run build
npm test
```

## 2. Workload Identity Verification
Ensure `headfade-mcp-sa` is properly assigned Workload Identity roles.

## 3. Stripe Webhook Configuration
Verify Stripe webhook points to `/api/webhooks/stripe`.

## 4. Cloud Run Deployment
Run `scripts/deploy-mcp.sh` to deploy the Truth Oracle MCP Server.

## 5. Final Smoke Tests
Test the `/api/mcp/purchase` and Data Connect integrations in staging.

## 6. Post-Deployment Monitoring
Verify OpenTelemetry traces in GCP Operations Suite.
