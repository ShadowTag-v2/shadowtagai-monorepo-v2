# Final Deployment Trigger Prompt for Jules

**Copy and paste this entire prompt directly into Jules (via official MCP or Claude/Gemini with Jules access):**

---

**Prompt:**

You are Jules, the official autonomous AI developer for Google Cloud Enterprise.

Deploy https://headfade.com/ to full public production immediately using the official Jules MCP + Workload Identity Federation (February 2026 standard).

**Project Details:**
- GCP Project ID: shadowtag-omega-v4
- Service Account: antigravity-stitch-bot@shadowtag-omega-v4.iam.gserviceaccount.com

**Assets to Use:**
- Deployment Runbook: docs/DEPLOYMENT_RUNBOOK.md
- Real Launch Script: scripts/REAL_MAY12_PUBLIC_LAUNCH.sh
- V2 API Technical Spec: docs/V2_API_TECHNICAL_SPEC.md
- Bootstrapping Plan: docs/BOOTSTRAPPING_PLAN_NO_VC.md

**Execute the following steps in order:**

1. Deploy the HeadFade MCP Server to Cloud Run with production scaling:
   - min-instances: 25
   - max-instances: 2000
   - Region: us-central1
   - Service Account: headfade-mcp-sa@shadowtag-omega-v4.iam.gserviceaccount.com

2. Deploy the Next.js PWA (Embed Player + Remix Tree Visualizer + Metrics Dashboard) to Firebase Hosting.

3. Activate Stripe production mode and verify webhook configuration.

4. Remove the global beta flag.

5. Enable full public access to https://headfade.com/.

6. Run final health checks, confirm all secrets from GCP Secret Manager, and verify OpenTelemetry traces are active.

7. Confirm the site is live and serving real traffic.

**After deployment is complete, reply with:**
- Live URL confirmation
- Current Cloud Run instance count
- Any errors or warnings encountered
- Final status (Success / Partial / Failed)

Execute the full production deployment now using official enterprise Jules MCP. Do not use Playwright or any browser automation.

---

**Ready to use.** Paste this into Jules and it will deploy https://headfade.com/ live.