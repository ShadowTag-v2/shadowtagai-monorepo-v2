/**
 * Deep Browser Extractor — 11x Chrome AI Mode Expansion Loop
 *
 * Drives Google's AI Mode through 11 consecutive expansion cycles
 * to extract maximally deep context on any research topic.
 *
 * Usage: node tools/scripts/deep_browser_extractor.js "your query here"
 *
 * IMPORTANT: This script launches a VISIBLE browser window.
 * It is designed for local R&D workstation use only.
 * Never deploy to CI/CD or headless environments.
 *
 * Dependencies: npx playwright install chromium
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const EXPANSION_CYCLES = 11;
const CYCLE_WAIT_MS = 8000;
const AI_MODE_WAIT_MS = 3000;
const OUTPUT_DIR = path.join(__dirname, '..', '..', '.beads', 'extractions');

async function extractDeepContext(query) {
  console.log(`🔬 Initiating Deep Extraction for: "${query}"`);
  console.log(`   Cycles: ${EXPANSION_CYCLES} | Wait: ${CYCLE_WAIT_MS}ms per cycle`);

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  });
  const page = await context.newPage();
  let finalPayload = '';

  try {
    await page.goto('https://www.google.com/', { waitUntil: 'networkidle' });

    // Enter query
    const searchInput = page.locator('textarea[name="q"], input[name="q"]').first();
    await searchInput.fill(query);
    await page.keyboard.press('Enter');
    await page.waitForLoadState('networkidle');

    // Attempt AI Mode activation
    const aiTab = page.locator('text="AI Mode"').first();
    if (await aiTab.isVisible({ timeout: 5000 }).catch(() => false)) {
      console.log('🧠 AI Mode detected — activating...');
      await aiTab.click();
      await page.waitForTimeout(AI_MODE_WAIT_MS);

      for (let i = 0; i < EXPANSION_CYCLES; i++) {
        console.log(`   ↳ Expansion cycle ${i + 1}/${EXPANSION_CYCLES}...`);
        const inputArea = page.locator('textarea').last();
        await inputArea.fill('yes, expand further with more detail and examples');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(CYCLE_WAIT_MS);
      }

      finalPayload = await page.locator('body').innerText();
      console.log('✅ Deep Extraction Complete.');
    } else {
      console.log('⚠️  AI Mode tab not found. Extracting standard search results.');
      finalPayload = await page.locator('body').innerText();
    }

    // Save extraction
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const sanitizedQuery = query.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50);
    const outFile = path.join(OUTPUT_DIR, `extraction_${sanitizedQuery}_${timestamp}.txt`);
    fs.writeFileSync(outFile, finalPayload);
    console.log(`📄 Saved to: ${outFile}`);
    console.log(`   Length: ${finalPayload.length} chars`);
  } catch (e) {
    console.error('❌ Extraction failed:', e.message);
  } finally {
    await browser.close();
  }

  return finalPayload;
}

// CLI entry point
const query = process.argv[2] || 'Next-generation spatial computing architectures';
extractDeepContext(query).then(() => process.exit(0));
