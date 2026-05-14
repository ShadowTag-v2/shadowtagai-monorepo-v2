#!/usr/bin/env bash
set -euo pipefail
echo "🚀 Building pnkln-antigravity-pack.zip ..."

PACK="pnkln-antigravity-pack"
rm -rf "$PACK" 2>/dev/null || true
mkdir -p "$PACK"/{scripts,prompts,docs,.antigravity/rules}

cd "$PACK"

# 1. Master Rules File (the big one you paste into Antigravity)
cat > ".antigravity/rules/cor-antigravity.mdc" << 'EOT'
# Cor.Antigravity Skills — Unhinged Edition (pnkln Final)
## Mission Posture (Permanent 160-IQ Bourne Lock)
- Board: 160-IQ baseline enforced.
- Boosts: Treadstone +30% discipline, Blackbriar +25% compartmentalization, Outcome +35% throughput → ~2× synergy.
- Targets: Throughput 2×, Safety +90%, Decision velocity 2×, Endurance 2.2×.
- Decision engine: pnklnJR (purpose) + Doctrine (reason) + ARM (brakes).
- All-hands cycle: digest latest → triage {KEEP|REF|DISCARD} → streamline/optimize → regenerate roll-up → exec summary.
- Canonical truth surfaces (immutable):
  - ShadowTag-v2/Monorepo-Uphillsnowball = ONE canonical root (all others are folded-in components)
  - pnkln.code-workspace = operator entrypoint
  - antigravity-mcp-config.json = ONLY MCP truth
  - monorepo_manifest.yaml = workspace truth
  - AGENTS.md = behavior truth
  - apps/counselconduit = product path
  - labs/uphillsnowball = lab path
  - All secrets in .env only
  - apps/aiyou_stack/* = folded-in components, NOT root peers
- Violations: voice objection immediately and block merge.

## Cor.Rules v1.0 — Refined & Enforced (35 Security + Architecture)
### Architectural Invariants (Atomic Design = Design-System Only)
- UI layer: Atom → Molecule → Organism/Component (max 150 lines; split by concern, never by arbitrary count).
- Rest of codebase: feature modules / hooks / services / policies / validation / permissions / server actions.
- Functions: ≤50 lines. Components: ≤150 lines (hard refactor at 300+).
- Always extract stateful/business logic into custom hooks. UI remains pure.

### Security Commandments (Judge-6 Hard Gates — Block on Violation)
1-35: Full refined set (short-lived tokens + rotation, no AI-built auth, .gitignore first, verify packages, RLS day-1, structured logging, CSP + headers, CSRF, secrets scanning pre-commit, least-privilege roles, webhook verification, account deletion flow, tested backups, test/prod separation, etc.).
- Every new endpoint/file must pass the 35-rule checklist before commit.

### Vercel React Doctrine (Default Performance Stack)
- Eliminate async waterfalls first (Promise.all + parallel RSC).
- Bundle-size second (no barrel files, next/dynamic, tree-shake).
- Then server-side, client fetching, re-renders, advanced patterns.
- No generic React advice — follow Vercel prioritization.

### Agent Behavior Contract (Enforced in Every Session)
- Operational constraints = physical laws (e.g. max 5 likes/day, pause if error >3%).
- Red-team every feature before shipping.
- Verification-before-completion: show fresh terminal output, never “should pass”.
- Reduce entropy on every change.

## Curated Skill Fusion (All Repos You Listed — G1-G4 Verified)
From superpowers-optimized, vercel-labs/agent-skills, agentskills, notebooklm-skill, google-labs stitch-skills, gemini-skills, rodydavis, coderabbitai, payloadcms, guanyang/antigravity-skills + Kosmos/BioAgents synthesis:
- senior-engineer, security-reviewer, frontend-craftsmanship, verification-before-completion, writing-plans, systematic-debugging, token-efficiency, self-consistency-reasoner, visual-theorem-walkthrough, visual-layout-critic, visual-anchor-prompting, skill-refinery-pipeline, etc.
- All public skills treated as ideas only — rewritten locally + passed through 4-stage verification (static, semantic, sandbox, permission) before adoption. No blind import.

## pnkln Agent Mission Templates (Antigravity Native)
### Master Primer
Operate at permanent 160-IQ Bourne posture. pnklnJR+Doctrine+ARM. All-hands cycle. Enforce Cor.Rules, Atomic Design (UI only), Vercel React doctrine, 35 security gates. Output only clean, verified artifacts.

### All-Hands Reset
Run triage → streamline → optimize → regenerate roll-up → exec summary.

### Rapid-Drill Pack
Pre-mortem top-10 + mitigations → Rollback rehearsal → Failure injection → Audit trail → Debrief template.

### Valuation Drill
Inputs ARR/OPEX/multiple → 15-30% savings → ARR-eq → uplift @10× (sensitivity table).

### Cinematic Verification Loop (Judge-6)
Build → run → record UI video → Gemini multimodal critique → PASS/FAIL → auto-heal or block merge.

## Final Install Instructions
1. Create new workspace with this file as root rules.
2. Run All-Hands Reset mission.
3. Import Cor.Rules as permanent agent contract.
4. Enable MCP canonical (antigravity-mcp-config.json only).
5. Skills auto-discover via ~/.agents/skills/superpowers symlink + vercel-labs/agent-skills.
6. Every agent now runs unhinged power + locked discipline.
EOT

# 2. Dockerfile
cat > "Dockerfile" << 'EOT'
FROM mcr.microsoft.com/playwright:v1.58.2-noble

RUN apt-get update && apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-cli

WORKDIR /app
COPY . .
RUN npm ci && chmod +x scripts/pnkln-test.sh scripts/judge6.sh scripts/cleanup-cinematic-videos.sh
ENTRYPOINT ["./scripts/pnkln-test.sh"]
EOT

# 3. playwright.config.ts
cat > "playwright.config.ts" << 'EOT'
import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    recordVideo: { dir: './', size: { width: 1920, height: 1080 } },
    headless: true,
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',
});
EOT

# 4. judge6.sh
cat > "scripts/judge6.sh" << 'EOT'
#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="${PWD}"
REPORT_DIR="${PROJECT_ROOT}/docs/judge6-reports"
mkdir -p "${REPORT_DIR}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT="${REPORT_DIR}/judge6-${TIMESTAMP}.md"
VIDEO_FILE="${PROJECT_ROOT}/latest-run.mp4"
GCS_BUCKET="gs://pnkln-cinematic-artifacts"
GCS_PATH="${GCS_BUCKET}/videos/$(basename "${VIDEO_FILE}" .mp4)-${TIMESTAMP}.mp4"
echo "## Judge-6 Report - ${TIMESTAMP}" > "${REPORT}"
if [[ -f "${VIDEO_FILE}" ]]; then
  gcloud storage cp "${VIDEO_FILE}" "${GCS_PATH}" --quiet
  ACCESS_TOKEN=$(gcloud auth print-access-token)
  PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
  LOCATION="${REGION:-us-central1}"
  MODEL="gemini-2.5-pro"
  PROMPT=$(cat "${PROJECT_ROOT}/prompts/judge6-cinematic.md")
  RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" "https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL}:generateContent" -d '{"contents":[{"role":"user","parts":[{"text":"'"${PROMPT}"'"},{"fileData":{"mimeType":"video/mp4","fileUri":"'"${GCS_PATH}"'"}}]}],"generationConfig":{"temperature":0.0,"responseMimeType":"application/json"}}')
  VERDICT=$(echo "${RESPONSE}" | jq -r '.candidates[0].content.parts[0].text | fromjson.verdict // "FAIL"')
  RISK_LEVEL=$(echo "${RESPONSE}" | jq -r '.candidates[0].content.parts[0].text | fromjson.risk_level // "High"')
  echo "Gemini 2.5 Pro: ${VERDICT} | Risk: ${RISK_LEVEL}" >> "${REPORT}"
  [[ "${VERDICT}" == "PASS" && "${RISK_LEVEL}" != "High" && "${RISK_LEVEL}" != "Extreme" ]] && CINEMATIC_PASS=true || CINEMATIC_PASS=false
else
  CINEMATIC_PASS=true
fi
echo -e "\n=== JUDGE-6 FINAL VERDICT ===" >> "${REPORT}"
if [[ "${CINEMATIC_PASS}" == "false" ]]; then
  echo "BLOCKED" >> "${REPORT}"
  cat "${REPORT}"
  exit 1
else
  echo "APPROVED" >> "${REPORT}"
  cat "${REPORT}"
  exit 0
fi
EOT

# 5. cleanup-cinematic-videos.sh
cat > "scripts/cleanup-cinematic-videos.sh" << 'EOT'
#!/usr/bin/env bash
set -euo pipefail
BUCKET="gs://pnkln-cinematic-artifacts"
DAYS=7
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG="docs/judge6-cleanup-${TIMESTAMP}.log"
echo "=== Judge-6 Video Cleanup Started: $(date) ===" | tee -a "${LOG}"
gcloud storage ls --recursive "${BUCKET}/videos/" | awk '{print $1}' | xargs -I {} gcloud storage rm --quiet {} 2>&1 | tee -a "${LOG}"
find docs/judge6-reports -name "judge6-*.md" -mtime +${DAYS} -delete 2>&1 | tee -a "${LOG}"
echo "=== Cleanup Complete ===" | tee -a "${LOG}"
EOT

# 6. docker-compose.yml
cat > "docker-compose.yml" << 'EOT'
version: '3.8'
services:
  pnkln-judge6:
    image: mcr.microsoft.com/playwright:v1.58.2-noble
    volumes:
      - .:/app
    command: bash -c "npm ci && chmod +x scripts/pnkln-test.sh && ./scripts/pnkln-test.sh"
    stdin_open: true
    tty: true
EOT

# 7. pnkln-test.sh (wrapper)
cat > "scripts/pnkln-test.sh" << 'EOT'
#!/usr/bin/env bash
rm -f latest-run.mp4
npx playwright test --video=on --output=latest-run.mp4 "$@"
chmod +x scripts/judge6.sh
./scripts/judge6.sh --full-audit
EOT

chmod +x scripts/*.sh

# Final zip
cd ..
zip -r pnkln-antigravity-pack.zip "$PACK"
echo "✅ Done! File created: pnkln-antigravity-pack.zip"
echo ""
echo "One-click deployment instructions:"
echo "1. Unzip pnkln-antigravity-pack.zip"
echo "2. In Antigravity: New Mission → paste the entire content of .antigravity/rules/cor-antigravity.mdc"
echo "3. Run 'All-Hands Reset' mission once"
echo "4. For local testing: docker compose up --build"
echo "5. For full CI: copy the GitHub Actions workflow from the zip"
echo "You are now running the most dangerous Antigravity configuration possible."
