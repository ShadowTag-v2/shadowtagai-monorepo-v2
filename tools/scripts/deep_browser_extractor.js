/**
 * Deep Browser Extractor — 11x Latent Space Exhaustion Tool
 *
 * Purpose: Physically manipulate the Google Chrome "AI Mode" UI to bypass
 * API truncation limits, forcing the underlying model to unroll its entire
 * latent knowledge space into an exhaustive master thesis.
 *
 * This is NOT a replacement for MCP search — it serves a fundamentally
 * different purpose: deep context extraction via iterative expansion.
 *
 * Usage: node tools/scripts/deep_browser_extractor.js "your query here"
 *
 * Prerequisites: npm install playwright
 */

const { chromium } = require("playwright");

const EXPANSION_CYCLES = 11;
const CYCLE_WAIT_MS = 8000;
const AI_MODE_WAIT_MS = 3000;

async function extractDeepContext(query) {
  console.log(`\n🔬 Deep Context Extraction — 11x Latent Space Exhaustion`);
  console.log(`   Query: "${query}"`);
  console.log(`   Cycles: ${EXPANSION_CYCLES}`);
  console.log(`   Estimated time: ~${(EXPANSION_CYCLES * CYCLE_WAIT_MS) / 1000 + 10}s\n`);

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  });
  const page = await context.newPage();

  try {
    // Navigate to Google
    await page.goto("https://www.google.com/", { waitUntil: "networkidle" });
    console.log("✅ Google loaded");

    // Enter search query
    const searchInput = page.locator('textarea[name="q"], input[name="q"]');
    await searchInput.fill(query);
    await page.keyboard.press("Enter");
    await page.waitForLoadState("networkidle");
    console.log("✅ Search results loaded");

    // Attempt to activate AI Mode
    const aiTab = page.locator('text="AI mode"').first();
    const aiTabVisible = await aiTab
      .isVisible({ timeout: 5000 })
      .catch(() => false);

    if (aiTabVisible) {
      await aiTab.click();
      await page.waitForTimeout(AI_MODE_WAIT_MS);
      console.log("✅ AI Mode activated\n");

      // 11x Expansion Loop
      for (let i = 0; i < EXPANSION_CYCLES; i++) {
        const cycleNum = i + 1;
        console.log(
          `   ⚡ Expansion cycle ${cycleNum}/${EXPANSION_CYCLES}...`
        );

        try {
          const inputArea = page.locator("textarea").last();
          await inputArea.fill("yes, continue with more detail");
          await page.keyboard.press("Enter");
          await page.waitForTimeout(CYCLE_WAIT_MS);
        } catch (cycleErr) {
          console.log(
            `   ⚠️  Cycle ${cycleNum} encountered resistance: ${cycleErr.message}`
          );
          // Continue — some cycles may hit rate limits
        }
      }

      // Extract final payload
      const finalPayload = await page.locator("body").innerText();
      const outputPath = `tools/scripts/extraction_${Date.now()}.txt`;

      // Write to file
      const fs = require("fs");
      fs.writeFileSync(outputPath, finalPayload, "utf-8");

      console.log(`\n✅ Deep Extraction Complete.`);
      console.log(`   Output: ${outputPath}`);
      console.log(`   Payload size: ${finalPayload.length} chars`);
      console.log(
        `   Preview: ${finalPayload.substring(0, 500)}...\n`
      );
    } else {
      console.log(
        "⚠️  AI Mode tab not found. Extracting standard search results instead."
      );
      const standardPayload = await page.locator("body").innerText();
      console.log(`   Extracted ${standardPayload.length} chars from SERP`);
    }
  } catch (e) {
    console.error("❌ Extraction failed:", e.message);
    process.exitCode = 1;
  } finally {
    await browser.close();
    console.log("🔒 Browser closed.");
  }
}

// Entry point
const query =
  process.argv[2] || "Next-generation spatial computing architectures";
extractDeepContext(query);
