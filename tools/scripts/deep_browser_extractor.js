const { chromium } = require('playwright');

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
                console.log(`Expansion cycle ${i + 1}/11...`);
                const inputArea = page.locator('textarea').last();
                await inputArea.fill('yes');
                await page.keyboard.press('Enter');
                await page.waitForTimeout(8000); 
            }

            const finalPayload = await page.locator('body').innerText();
            console.log("✅ Deep Extraction Complete.");
            console.log(finalPayload.substring(0, 1000) + "... [TRUNCATED FOR LOGS]");
        } else {
            console.log("AI Mode tab not found. Defaulting to standard extraction.");
        }
    } catch (e) {
        console.error("Extraction failed:", e);
    } finally {
        await browser.close();
    }
}

extractDeepContext(process.argv[2] || "Next-generation spatial computing architectures");
