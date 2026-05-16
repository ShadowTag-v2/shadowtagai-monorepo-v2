import { $ } from "bun";

const TARGET_URL = "https://kovelai.web.app/";
const ARTIFACT_PATH = "./docs/performance/baselines/kovelai-live-baseline.json";

async function executePhaseZero() {
  console.log(`⚡ [V24 Bun Shell] Initiating Sovereign Lighthouse Audit on ${TARGET_URL}`);

  // 1. Native Port-Killer Sovereignty
  console.log(`⚡ Slaying zombie Chrome processes to unlock DevTools profile...`);
  await $`pkill -9 -f "HeadlessChrome"`.quiet().catch(() => {});
  await $`pkill -9 -f "chrome-devtools-mcp"`.quiet().catch(() => {});
  await Bun.sleep(500);

  // 2. Edge CDN Warmup
  console.log(`⚡ Warming Fastly/Firebase Edge CDN (Bypassing Cold Start)...`);
  await $`curl -s -o /dev/null ${TARGET_URL}`;
  await $`curl -s -o /dev/null ${TARGET_URL}`;
  await $`curl -s -o /dev/null ${TARGET_URL}`;

  // 3. Execute Headless Lighthouse via NPX
  console.log(`⚡ Executing Headless Chrome Audit...`);
  try {
    await $`npx -y lighthouse ${TARGET_URL} \
            --output=json \
            --output-path=${ARTIFACT_PATH} \
            --chrome-flags="--headless=new --no-sandbox --disable-dev-shm-usage" \
            --only-categories=performance`;

    console.log(`✅ [SUCCESS] Mathematical Baseline securely written to: ${ARTIFACT_PATH}`);
  } catch (error) {
    console.error(`❌ Audit Failed. Check network or npx execution.`, error);
  }
}

await executePhaseZero();
