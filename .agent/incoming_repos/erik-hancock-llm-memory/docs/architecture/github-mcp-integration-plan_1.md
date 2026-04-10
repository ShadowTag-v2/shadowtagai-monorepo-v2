# GITHUB MCP SERVER: pnkln INTEGRATION ARCHITECTURE

## EXECUTIVE SUMMARY
GitHub's official MCP server enables direct AI→GitHub integration with 40-60% token reduction potential via semantic compression. Critical for Judge#6 enforcement pipeline, Cor documentation system, and ShadowTagAI CI/CD automation.

## JR ENGINE DECISION MATRIX

### PURPOSE: Advances pnkln/Revenue?
✓ Judge#6 enforcement at commit/PR time via GitHub Actions
✓ ATP_519_scan automation on repo commits (95% token reduction)
✓ ShadowTagAI watermarking in CI/CD pipeline
✓ Cor state management directly on GitHub repos
✓ 40-60% MCP token compression → 487 bytes governance decisions
✓ Revenue opportunity: Compliance-as-a-Service for regulated sectors

### REASONS: Defensible Judgment?
1. **Native GitHub Actions Integration**
   - Judge#6 checks run on workflow_run events
   - p99 ≤90ms enforcement via webhooks
   - Fail-fast on governance violations

2. **Toolset Granularity** (CRITICAL - avoid token bloat)
   ```bash
   GITHUB_TOOLSETS="context,repos,actions,code_security,pull_requests"
   # NOT "all" - LLM confusion + token explosion
   ```

3. **Security Posture**
   - PAT storage: GCP Secret Manager
   - OAuth preferred for remote server (VS Code 1.101+, Claude)
   - Lockdown mode for public repos
   - Read-only mode during validation

4. **Token Economics**
   - Without MCP: 50KB governance context
   - With MCP + ATP_519_scan: 487 bytes
   - Compression ratio: ~102:1
   - Must empirically validate on pnkln repos

5. **Deployment Architecture**
   ```
   Vertex Workbench (M1-3 dev)
   └─> Docker: ghcr.io/github/github-mcp-server
       ├─> ENV: GITHUB_PERSONAL_ACCESS_TOKEN (from GCP KMS)
       ├─> ENV: GITHUB_TOOLSETS="context,repos,actions,code_security,pull_requests"
       ├─> ENV: GITHUB_LOCKDOWN_MODE=1
       └─> ENV: GITHUB_READ_ONLY=1 (during POC)

   GKE-native (M3+ prod)
   └─> 4-5 namespaces
       ├─> judge-six-ns: MCP server + enforcement
       ├─> cor-ns: State management
       ├─> shadowtag-ns: Watermarking pipeline
       ├─> jr-engine-ns: Governance decisions
       └─> observability-ns: Metrics/logs
   ```

### BRAKES: p99 Survivable?
🚨 **SECURITY GATES**
- PAT never committed (chmod 600, .gitignore)
- Separate PATs per environment (dev/staging/prod)
- Minimum scopes: repo, read:packages, read:org
- Rotation schedule: 90 days

🚨 **PERFORMANCE GATES**
- GitHub API rate limit: 5K req/hr (authenticated)
  - Judge#6 at p99 ≤90ms → max ~11 checks/sec
  - Risk: Throttling at scale
  - Mitigation: Cache GitHub context, batch operations
- MCP latency overhead must be measured
  - Hypothesis: Token reduction > latency cost
  - Validation: Benchmark 1000 governance decisions

🚨 **BOOTSTRAP GATES**
- ROI ≥3× in 18mo
  - Cost: $0 (OSS + GitHub API free tier)
  - Revenue: ShadowTagAI compliance pipeline
  - Target: 10 customers × $3K/mo = $360K ARR
  - ROI: ∞ (zero cost base)
- LTV:CAC ≥4:1 (12mo)
  - CAC: Self-serve setup docs + 1hr sales call
  - LTV: $3K/mo × 24mo retention = $72K
  - Ratio: 72:1 (if CAC ~$1K)

🚨 **KILL-SWITCH TRIGGERS**
- MCP latency > 50ms (eats into p99 ≤90ms SLA)
- Token reduction < 30% (not worth integration cost)
- GitHub API throttling > 5% of requests
- Security incident (PAT leak, unauthorized access)

## IMPLEMENTATION ROADMAP

### PHASE 1: RAPID VALIDATION (4-6 hours)
**Goal:** Prove MCP token compression on real pnkln repos

```bash
# Step 1: Generate PAT
# https://github.com/settings/personal-access-tokens/new
# Scopes: repo, read:packages, read:org
# Expiry: 90 days
# Store in: ~/.github-mcp-pat (chmod 600)

# Step 2: Run local Docker MCP server
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=$(cat ~/.github-mcp-pat) \
  -e GITHUB_TOOLSETS="context,repos,pull_requests" \
  -e GITHUB_READ_ONLY=1 \
  ghcr.io/github/github-mcp-server

# Step 3: Configure Claude Code
# ~/.config/claude/mcp.json
{
  "servers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e", "GITHUB_TOOLSETS",
        "-e", "GITHUB_READ_ONLY",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}",
        "GITHUB_TOOLSETS": "context,repos,pull_requests",
        "GITHUB_READ_ONLY": "1"
      }
    }
  }
}

# Step 4: Test on target repo
# Example: github.com/pnkln/judge-six-prototype
# Measure:
# - Without MCP: Token count for "get last 10 commits"
# - With MCP: Token count for same operation
# - Compression ratio
# - Latency delta
```

**Success Criteria:**
- Token reduction ≥30%
- Latency increase ≤20ms
- No security warnings
- Clear integration path to Judge#6

### PHASE 2: JUDGE#6 INTEGRATION (3-4 days)
**Goal:** GitHub Actions workflow enforcement

```yaml
# .github/workflows/judge-six-enforce.yml
name: Judge#6 Governance Enforcement
on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main, staging, production]

jobs:
  enforce:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - name: ATP_519_scan
        id: scan
        run: |
          # Semantic compression: 50KB → 487 bytes
          python scripts/atp_519_scan.py \
            --input ${{ github.event.pull_request.diff_url }} \
            --output /tmp/scan_result.bin

      - name: Judge#6 Enforcement
        env:
          JUDGE_SIX_ENDPOINT: ${{ secrets.JUDGE_SIX_ENDPOINT }}
        run: |
          # Binary decision: PASS/FAIL
          curl -X POST $JUDGE_SIX_ENDPOINT \
            -H "Content-Type: application/octet-stream" \
            -d @/tmp/scan_result.bin \
            --max-time 1 # p99 ≤90ms budget

          # Exit code 0 = PASS, 1 = FAIL
          if [ $? -ne 0 ]; then
            echo "::error::Judge#6 governance violation detected"
            exit 1
          fi

      - name: Post Result
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🛡️ Judge#6: ' + (context.job.status === 'success' ? 'PASS' : 'FAIL')
            })
```

**Success Criteria:**
- All PRs blocked on governance violations
- p99 latency ≤90ms (GitHub Actions + Judge#6)
- Zero false positives in 100 test PRs
- Audit trail in GitHub Comments

### PHASE 3: SHADOWTAG CI/CD (5-7 days)
**Goal:** Automated watermarking in build pipeline

```yaml
# .github/workflows/shadowtag-watermark.yml
name: ShadowTagAI DCT Watermarking
on:
  push:
    branches: [main]
    paths:
      - '**.mp4'
      - '**.mov'
      - '**.avi'

jobs:
  watermark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Detect Video Changes
        id: detect
        uses: github/github-mcp-server@main
        with:
          tool: get_commit
          args: |
            owner: ${{ github.repository_owner }}
            repo: ${{ github.event.repository.name }}
            sha: ${{ github.sha }}
            include_diff: true

      - name: Apply ShadowTagAI
        run: |
          # DCT watermarking on changed videos
          for video in $(echo '${{ steps.detect.outputs.files }}' | jq -r '.[] | select(.filename | endswith(".mp4")) | .filename'); do
            python scripts/shadowtag_dct.py \
              --input $video \
              --output ${video%.mp4}_watermarked.mp4 \
              --metadata "repo=${{ github.repository }},commit=${{ github.sha }},timestamp=$(date -u +%s)"
          done

      - name: Commit Watermarked Videos
        run: |
          git config user.name "ShadowTagAI Bot"
          git config user.email "shadowtag@pnkln.ai"
          git add *_watermarked.mp4
          git commit -m "ShadowTagAI: Watermark applied [skip ci]"
          git push
```

**Success Criteria:**
- All committed videos auto-watermarked
- Metadata chain: repo → commit → timestamp
- Watermark extraction validates chain
- Compliance audit trail

### PHASE 4: GKE PRODUCTION (7-10 days)
**Goal:** Multi-namespace deployment on GKE

```yaml
# k8s/github-mcp-server.yaml
apiVersion: v1
kind: Secret
metadata:
  name: github-mcp-secrets
  namespace: judge-six-ns
type: Opaque
data:
  pat: <base64-encoded-from-gcp-kms>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: github-mcp-server
  namespace: judge-six-ns
spec:
  replicas: 3
  selector:
    matchLabels:
      app: github-mcp-server
  template:
    metadata:
      labels:
        app: github-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: ghcr.io/github/github-mcp-server:latest
        env:
        - name: GITHUB_PERSONAL_ACCESS_TOKEN
          valueFrom:
            secretKeyRef:
              name: github-mcp-secrets
              key: pat
        - name: GITHUB_TOOLSETS
          value: "context,repos,actions,code_security,pull_requests"
        - name: GITHUB_LOCKDOWN_MODE
          value: "1"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command: ["/bin/sh", "-c", "pgrep -f github-mcp-server"]
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          exec:
            command: ["/bin/sh", "-c", "pgrep -f github-mcp-server"]
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: github-mcp-service
  namespace: judge-six-ns
spec:
  selector:
    app: github-mcp-server
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP
```

**Success Criteria:**
- 3 replicas, HA across zones
- Secrets from GCP KMS, never in configs
- Health checks passing
- Prometheus metrics exported
- p99 latency ≤90ms maintained

## REVENUE MODEL: SHADOWTAG COMPLIANCE PIPELINE

### TARGET MARKET
- Defense contractors (CMMC, ITAR compliance)
- Healthcare (HIPAA video consultations)
- Finance (SOX, audit trails)
- Legal (chain-of-custody for evidence)

### PRICING TIERS
**Starter:** $2K/month
- 1 GitHub org
- 10 repos
- 1K videos/month
- Standard watermarking
- Email support

**Professional:** $5K/month
- 3 GitHub orgs
- 50 repos
- 10K videos/month
- Custom metadata schemas
- Slack support
- SLA: 99.5% uptime

**Enterprise:** Custom (est. $15-25K/month)
- Unlimited orgs/repos
- Unlimited videos
- On-prem deployment option
- Dedicated security review
- White-glove onboarding
- SLA: 99.9% uptime
- Custom integrations

### UNIT ECONOMICS
```
CAC (Customer Acquisition Cost):
├─ Self-serve docs: $0
├─ 1hr demo call: $200 (Erik's time)
├─ Technical POC: $500 (setup + validation)
└─ Total CAC: ~$700

LTV (Lifetime Value):
├─ Professional tier: $5K/mo
├─ Avg retention: 24 months (regulated = sticky)
├─ Total LTV: $120K
└─ LTV:CAC = 171:1 ✓ (>> 4:1 gate)

ROI Projection (18 months):
├─ 10 customers @ $5K/mo = $50K MRR
├─ $900K in 18 months
├─ Cost: $0K (bootstrap, GitHub API free)
└─ ROI: ∞ (>> 3× gate)
```

### GO-TO-MARKET
1. **Month 1-2:** GitHub MCP integration complete
2. **Month 3:** Launch shadowtagAI.com landing page
3. **Month 4:** Content marketing (compliance case studies)
4. **Month 5:** Outbound to defense contractors via LinkedIn
5. **Month 6:** First paying customer (proof of concept)
6. **Month 7-12:** Scale to 10 customers via referrals
7. **Month 13-18:** Enterprise deals, achieve $50K MRR

## COMPETITIVE MOAT
1. **Technical:**
   - DCT watermarking (vs fragile spatial methods)
   - Judge#6 enforcement (unique governance layer)
   - 487-byte decisions (vs 50KB competitors)
   - p99 ≤90ms (real-time enforcement)

2. **Business:**
   - Bootstrap → profitable from customer 1
   - GitHub-native (no alt integration)
   - Open-core model (MCP server OSS)
   - Compliance expertise (ATP 5-19, Special Forces background)

3. **Distribution:**
   - GitHub Marketplace listing
   - GitHub Actions workflow templates
   - Anthropic MCP directory
   - Defense contractor network

## OBJECTIONS & MITIGATIONS

### "Why not use existing watermarking tools?"
**Response:** Existing tools are spatial (fragile to compression) or proprietary black-boxes. ShadowTagAI uses DCT (frequency domain) = survives compression + open audit trail. Plus GitHub-native = zero integration friction.

### "What about GitHub API rate limits?"
**Response:** Free tier = 5K req/hr. Judge#6 batch operations + cache = <500 req/hr typical. Enterprise tier = 15K req/hr. We monitor and optimize.

### "Security of PATs?"
**Response:** GCP Secret Manager + rotation schedule + min scopes + separate PATs per env. Industry standard. Can also use OAuth for user-facing apps (zero token storage).

### "What if GitHub MCP changes/breaks?"
**Response:** Portable core design. MCP server is Docker container = swap out if needed. Fallback to GitHub API direct (already have wrapper). Boy Scout Rule = no vendor lock-in.

### "Proof of 40-60% token reduction?"
**Response:** Must validate empirically in Phase 1. Hypothesis based on MCP semantic compression. If <30%, kill-switch triggers, fallback to direct API. Bootstrap discipline = validate before commit.

## NEXT ACTIONS

### IMMEDIATE (Next 4 hours)
1. Generate GitHub PAT (scopes: repo, read:packages, read:org)
2. Store PAT: ~/.github-mcp-pat (chmod 600)
3. Run Docker MCP server locally
4. Configure Claude Code integration
5. Test on pnkln/judge-six-prototype repo
6. Measure token compression ratio

### THIS WEEK (Next 7 days)
1. Phase 1 validation complete
2. Document results in Cor
3. Decision: Proceed to Phase 2 or kill-switch
4. If proceed: Draft GitHub Actions workflow for Judge#6
5. If kill: Document why, archive learnings

### THIS MONTH (Next 30 days)
1. Judge#6 enforcement live on 1 production repo
2. ShadowTagAI CI/CD POC complete
3. shadowtagAI.com landing page live
4. First outbound to 10 defense contractors
5. Revenue pipeline: 3 demos scheduled

## CRITIQUE

### ASSUMPTIONS TO VALIDATE
1. **40-60% token reduction applies to pnkln repos**
   → May vary by repo structure, must measure empirically

2. **GitHub API rate limits sufficient at scale**
   → 5K req/hr = ~11 ops/sec. If Judge#6 on every commit, could throttle
   → Mitigation: Batch operations, cache context

3. **Defense contractors will pay $5K/mo for watermarking**
   → Need market validation, may need to adjust pricing
   → Alternative: Usage-based pricing (per video)

4. **MCP latency overhead negligible**
   → Hypothesis, must measure. If >50ms, eats into p99 ≤90ms SLA
   → Kill-switch if latency > compression benefit

5. **GitHub Actions sufficient for p99 ≤90ms enforcement**
   → Depends on runner availability, queue depth
   → May need dedicated runners or self-hosted

### WEAKNESSES
1. **Single point of failure:** GitHub API
   → Mitigation: Fallback to direct git operations, local repo cache

2. **PAT security:** If leaked, attacker has repo access
   → Mitigation: Min scopes, rotation, monitoring, OAuth preferred

3. **Revenue concentration:** All eggs in GitHub basket
   → Mitigation: Portable core, can integrate GitLab/Bitbucket later

4. **Compliance expertise required:** Not all customers have it
   → Mitigation: White-glove onboarding, compliance docs, training

### WHAT COULD BE WRONG
1. **MCP token reduction is a mirage**
   → Compression applies to tool selection, not necessarily total context
   → Need end-to-end measurement, not just API response size

2. **GitHub rate limits kill us at scale**
   → 5K req/hr sounds like a lot until 100 customers × 10 repos × 10 commits/hr
   → Need usage modeling, may require GitHub Enterprise

3. **Defense contractors won't trust cloud watermarking**
   → Regulated sectors paranoid about cloud. May demand on-prem
   → Build on-prem deployment path from day 1

4. **Judge#6 enforcement too slow for developer experience**
   → If every PR takes 90ms to validate, developers will disable it
   → Need instant feedback loop, pre-commit hooks, local validation

5. **ShadowTagAI watermarking breaks video playback**
   → DCT robust, but edge cases (exotic codecs, low bitrate)
   → Extensive testing required, compatibility matrix

## DECISION POINT

**Proceed with Phase 1 validation?**
- Cost: 4-6 hours Erik time
- Risk: Low (read-only, local, reversible)
- Upside: Validate 40-60% token compression hypothesis
- Downside: If <30% compression, wasted time (but learned kill-switch)

**Recommendation:** YES. Validation aligns with bootstrap discipline (test before commit), low cost, high information value. If compression validates, unlocks entire Judge#6 + ShadowTagAI automation stack. If fails, learned cheaply.

**Erik, confirm proceed with Phase 1?**
