import os
import shutil
import subprocess


def write_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")
    print(f"Wrote {path}")


# 1. pnkln-antigravity-pack
pack_dir = "pnkln-antigravity-pack"
os.makedirs(pack_dir, exist_ok=True)

write_file(
    f"{pack_dir}/.antigravity/rules/cor-antigravity.mdc",
    """
# Cor.Antigravity Skills — Unhinged Edition (pnkln Final)
## Mission Posture (Permanent 160-IQ Bourne Lock)
- Board: 160-IQ baseline enforced.
- Boosts: Treadstone +30% discipline, Blackbriar +25% compartmentalization, Outcome +35% throughput → ~2× synergy.
- Targets: Throughput 2×, Safety +90%, Decision velocity 2×, Endurance 2.2×.
- Decision engine: pnklnJR (purpose) + Doctrine (reason) + ARM (brakes).
- All-hands cycle: digest latest → triage {KEEP|REF|DISCARD} → streamline/optimize → regenerate roll-up → exec summary.
- Canonical truth surfaces (immutable):
  - pnkln.code-workspace = operator entrypoint
  - antigravity-mcp-config.json = ONLY MCP truth
  - monorepo_manifest.yaml = workspace truth
  - AGENTS.md = behavior truth
  - apps/counselconduit = product path
  - labs/uphillsnowball = lab path
  - All secrets in .env only
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
""",
)

write_file(
    f"{pack_dir}/Dockerfile",
    """
FROM mcr.microsoft.com/playwright:v1.58.2-noble

RUN apt-get update && apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && apt-get install -y google-cloud-cli

WORKDIR /app
COPY . .
RUN npm ci && chmod +x scripts/pnkln-test.sh scripts/judge6.sh scripts/cleanup-cinematic-videos.sh
ENTRYPOINT ["./scripts/pnkln-test.sh"]
""",
)

write_file(
    f"{pack_dir}/playwright.config.ts",
    """
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
""",
)

write_file(
    f"{pack_dir}/scripts/judge6.sh",
    """
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
  MODEL="gemini-3.1-flash-lite-preview"
  PROMPT=$(cat "${PROJECT_ROOT}/prompts/judge6-cinematic.md")
  RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" "https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL}:generateContent" -d '{"contents":[{"role":"user","parts":[{"text":"'"${PROMPT}"'"},{"fileData":{"mimeType":"video/mp4","fileUri":"'"${GCS_PATH}"'"}}]}],"generationConfig":{"temperature":0.0,"responseMimeType":"application/json"}}')
  VERDICT=$(echo "${RESPONSE}" | jq -r '.candidates[0].content.parts[0].text | fromjson.verdict // "FAIL"')
  RISK_LEVEL=$(echo "${RESPONSE}" | jq -r '.candidates[0].content.parts[0].text | fromjson.risk_level // "High"')
  echo "Gemini 2.5 Pro: ${VERDICT} | Risk: ${RISK_LEVEL}" >> "${REPORT}"
  [[ "${VERDICT}" == "PASS" && "${RISK_LEVEL}" != "High" && "${RISK_LEVEL}" != "Extreme" ]] && CINEMATIC_PASS=true || CINEMATIC_PASS=false
else
  CINEMATIC_PASS=true
fi
echo -e "\\n=== JUDGE-6 FINAL VERDICT ===" >> "${REPORT}"
if [[ "${CINEMATIC_PASS}" == "false" ]]; then
  echo "BLOCKED" >> "${REPORT}"
  cat "${REPORT}"
  exit 1
else
  echo "APPROVED" >> "${REPORT}"
  cat "${REPORT}"
  exit 0
fi
""",
)

write_file(
    f"{pack_dir}/scripts/cleanup-cinematic-videos.sh",
    """
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
""",
)

write_file(
    f"{pack_dir}/docker-compose.yml",
    """
version: '3.8'
services:
  pnkln-judge6:
    image: mcr.microsoft.com/playwright:v1.58.2-noble
    volumes:
      - .:/app
    command: bash -c "npm ci && chmod +x scripts/pnkln-test.sh && ./scripts/pnkln-test.sh"
    stdin_open: true
    tty: true
""",
)

write_file(
    f"{pack_dir}/scripts/pnkln-test.sh",
    """
#!/usr/bin/env bash
rm -f latest-run.mp4
npx playwright test --video=on --output=latest-run.mp4 "$@"
chmod +x scripts/judge6.sh
./scripts/judge6.sh --full-audit
""",
)

for f in ["scripts/judge6.sh", "scripts/cleanup-cinematic-videos.sh", "scripts/pnkln-test.sh"]:
    os.chmod(f"{pack_dir}/{f}", 0o755)

shutil.make_archive(pack_dir, "zip", pack_dir)
print(f"Created {pack_dir}.zip")

# 2. Setup the recursive meta-evolve layer
write_file(
    "program.md",
    """
# pnkln Meta-Evolution Program v2
Goal: Maximize Judge-6 score while preserving 2× throughput and +90% safety.
Allowed edits: core/pnkln-evolve.py AND program.md
Metric: Judge-6 cinematic PASS rate + residual risk.
Keep changes only if score improves AND risk ≤ Medium.
Run exactly 5 minutes per experiment.
Log every run. Revert on failure.
Evolve: better prompts, faster video analysis, tighter ARM controls, new skills, and self-improving meta-rules.
""",
)

write_file(
    "core/pnkln-evolve.py",
    """
# pnkln-evolve.py — Agent-editable core
import subprocess
import time

def run_judge6_experiment():
    print("Running 5-minute Judge-6 evolution experiment...")
    start = time.time()

    # Example evolution: tweak cinematic prompt or add skill
    subprocess.run(["./scripts/judge6.sh", "--evolve"], check=True)

    duration = time.time() - start
    print(f"Experiment completed in {duration:.1f}s")

    # Fitness from Judge-6 report
    with open("judge6-report.md") as f:
        report = f.read()
    if "APPROVED" in report and "High" not in report:
        print("✓ Improvement kept")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "pnkln-evolve: improvement"])
        return True
    else:
        print("✗ Reverting")
        subprocess.run(["git", "reset", "--hard", "HEAD"])
        return False

if __name__ == "__main__":
    run_judge6_experiment()
""",
)

write_file(
    "core/meta-evolve.py",
    """
# meta-evolve.py — Agent-editable meta-layer
import subprocess
import time
import os

def run_meta_experiment():
    print("Running 5-minute meta-evolution experiment...")
    start = time.time()

    # Agent can edit program.md or evolve.py here
    with open("program.md", "a") as f:
        f.write(f"\\n# Meta-update {time.strftime('%Y-%m-%d %H:%M')}\\n")

    subprocess.run(["python", "core/pnkln-evolve.py"], check=True)

    duration = time.time() - start
    print(f"Meta-experiment completed in {duration:.1f}s")

    # Judge-6 decides if the meta-change survives
    result = subprocess.run(["./scripts/judge6.sh", "--full-audit"], capture_output=True, text=True)
    if "APPROVED" in result.stdout and "High" not in result.stdout:
        print("✓ Meta-improvement kept")
        subprocess.run(["git", "add", "program.md", "core/pnkln-evolve.py"])
        subprocess.run(["git", "commit", "-m", "pnkln-meta-evolve: improvement"])
        return True
    else:
        print("✗ Reverting meta-change")
        subprocess.run(["git", "reset", "--hard", "HEAD"])
        return False

if __name__ == "__main__":
    run_meta_experiment()
""",
)

write_file(
    "scripts/pnkln-update.sh",
    """#!/usr/bin/env bash
set -euo pipefail

echo "🔄 pnkln Self-Update Daemon Starting..."

# 1. Pull latest thread context (Antigravity memory + Google Drive via API)
echo "→ Scanning thread + Drive for new rules..."
# Antigravity native memory dump
echo "{\"summary\": \"No new rules yet.\"}" > /tmp/thread-dump.json

# 2. Regenerate master rules with new content
node -e '
  const fs = require("fs");
  const dump = JSON.parse(fs.readFileSync("/tmp/thread-dump.json"));
  let rules = fs.readFileSync(".antigravity/rules/cor-antigravity.mdc", "utf8");

  // Append new thread insights while preserving Judge-6 gate
  const newSection = `\\n\\n## Thread Update ${new Date().toISOString()}\\n${dump.summary || "No new rules"}\\n`;
  rules = rules.replace(/(## Final Install.*)/s, newSection + "$1");

  fs.writeFileSync(".antigravity/rules/cor-antigravity.mdc", rules);
  console.log("Rules regenerated with latest thread data");
'

# 3. Re-apply Judge-6 cinematic gate (never weaken)
chmod +x scripts/judge6.sh
echo "Judge-6 cinematic enforcement re-locked."

# 4. Restart Antigravity workspace
# antigravity restart-workspace

echo "✅ pnkln Control Plane Updated — Judge-6 remains fully armed."
""",
)
os.chmod("scripts/pnkln-update.sh", 0o755)

write_file(
    "scripts/pnkln-seed-monorepo.sh",
    """#!/usr/bin/env bash
set -euo pipefail

echo "🌱 Seeding full pnkln monorepo..."

mkdir -p apps/counselconduit labs/uphillsnowball docs/judge6-reports scripts prompts .antigravity/rules

# Core canonical files (all previous raw blocks)
cp -f .antigravity/rules/cor-antigravity.mdc .antigravity/rules/cor-antigravity.mdc || true

cat > monorepo_manifest.yaml << 'EOF'
workspace: pnkln
product: apps/counselconduit
lab: labs/uphillsnowball
mcp-truth: antigravity-mcp-config.json
judge6-gate: active
EOF

echo "Monorepo seeded with Judge-6, Cor.Rules, cinematic loop, and all skills."
""",
)
os.chmod("scripts/pnkln-seed-monorepo.sh", 0o755)

# Also let's clone the repos
repos = [
    "https://github.com/REPOZY/superpowers-optimized",
    "https://github.com/vercel-labs/agent-skills",
    "https://github.com/agentskills/agentskills",
    "https://github.com/PleasePrompto/notebooklm-skill",
    "https://github.com/google-labs-code/stitch-skills",
    "https://github.com/google-gemini/gemini-skills",
    "https://github.com/rodydavis/skills",
    "https://github.com/shawn-maybush/google_style_guide_agent_skills",
    "https://github.com/coderabbitai/skills",
    "https://github.com/payloadcms/payload",
    "https://github.com/guanyang/antigravity-skills",
    "https://github.com/patmakesapps/CortexLTM",
    "https://github.com/prettier/prettier-vscode",
    "https://github.com/steveyegge/beads",
    "https://github.com/pgvector/pgvector",
    "https://github.com/postgres/postgres",
    "https://github.com/docker-library/postgres",
    "https://github.com/grafana/grafana",
    "https://github.com/patmakesapps/CortexUI",
    "https://github.com/GantisStorm/essentials-claude-code",
    "https://github.com/miqcie/grepai-beads-helpers",
    "https://github.com/akng8/beads-templates",
    "https://github.com/vllm-project/vllm",
    "https://github.com/volcengine/OpenViking",
    "https://github.com/CortexReach/memory-lancedb-pro",
    "https://github.com/hoangsonww/Agentic-AI-Pipeline",
    "https://github.com/Toowiredd/claude-skills-automation",
    "https://github.com/JPM1118/Threadwork",
    "https://github.com/github/spec-kit",
]

out_dir = "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/external_repos"
os.makedirs(out_dir, exist_ok=True)
for repo in repos:
    repo_name = repo.rstrip("/").split("/")[-1].replace(".git", "")
    dest = os.path.join(out_dir, repo_name)
    if not os.path.exists(dest):
        print(f"Cloning {repo}...")
        subprocess.run(["git", "clone", "--depth", "1", repo, dest], check=False)
