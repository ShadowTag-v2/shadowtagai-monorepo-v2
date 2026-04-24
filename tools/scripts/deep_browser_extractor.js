const { chromium } = require('playwright');

/**
 * Deep Browser Extractor — 11x Google AI Mode Loop
 *
 * Uses Playwright to launch Chrome, navigate to Google, enter a query,
 * switch to AI mode, and iteratively deepen the extraction 11 times.
 *
 * Usage: node deep_browser_extractor.js "your query here"
 *
 * @see TRUE OBSIDIAN V14 — Phase 1
 */
async function extractDeepContext(query) {
    console.log(`Initiating Deep Extraction for: ${query}`);
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();
    try {
        await page.goto('https://www.google.com/');
        await page.fill('textarea[name="q"], input[name="q"]', query);
        await page.keyboard.press('Enter');
        await page.waitForLoadState('networkidle');
        const aiTab = page.locator('text="AI mode"').first();
        if (await aiTab.isVisible()) {
            await aiTab.click();
            await page.waitForTimeout(3000);
            for (let i = 0; i < 11; i++) {
                const inputArea = page.locator('textarea').last();
                await inputArea.fill('yes');
                await page.keyboard.press('Enter');
                await page.waitForTimeout(8000);
            }
            console.log("✅ Deep Extraction Complete:\n" + (await page.locator('body').innerText()).substring(0, 1000));
        } else {
            console.log("⚠️ AI mode tab not visible. Extracting standard results.");
            console.log((await page.locator('body').innerText()).substring(0, 1000));
        }
    } catch (e) {
        console.error("Extraction failed:", e);
    } finally {
        await browser.close();
    }
}

extractDeepContext(process.argv[2] || "Next-generation spatial computing architectures");
