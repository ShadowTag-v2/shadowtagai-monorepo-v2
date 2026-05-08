/**
 * tools/browser-subagent/dispatcher.js
 *
 * App-Layer Browser Sensorium — Subagent Dispatcher
 *
 * Connects to the authenticated Chrome instance on port 9222 (BeyondCorp),
 * executes visual generation tasks, and fires Pub/Sub events on completion.
 *
 * This handles APP-LAYER events (UI rendering, visual generation).
 * STORAGE-LAYER events are handled by Datastream CDC (scripts/provision_cdc_datastream.sh).
 *
 * Usage:
 *   node dispatcher.js --prompt "Generate a gavel animation" --url "https://labs.google/" --output video
 */

const puppeteer = require('puppeteer-core');
const { PubSub } = require('@google-cloud/pubsub');

const PROJECT_ID = 'shadowtag-omega-v4';
const UI_EVENTS_TOPIC = `projects/${PROJECT_ID}/topics/ui-events`;
const CHROME_DEBUG_PORT = process.env.CHROME_DEBUG_PORT || '9222';
const VIEWPORT = { width: 1920, height: 1080 };

// Hard timeout guardrails from SYSTEM_OVERRIDE.md
const POLL_CONFIG = {
  image: { intervalMs: 15000, maxAttempts: 10, hardTimeoutMs: 150000 },
  video: { intervalMs: 30000, maxAttempts: 15, hardTimeoutMs: 450000 },
};

/**
 * Executes a visual generation task via the authenticated browser instance.
 *
 * @param {string} prompt - The generation prompt to type into the target UI
 * @param {string} targetUrl - The URL to navigate to
 * @param {'image'|'video'} outputType - Determines polling cadence and timeouts
 * @returns {Promise<string>} Status message
 */
async function executeSubagentTask(prompt, targetUrl, outputType = 'image') {
  const config = POLL_CONFIG[outputType] || POLL_CONFIG.image;
  const pubsub = new PubSub({ projectId: PROJECT_ID });

  let browser;
  try {
    browser = await puppeteer.connect({
      browserURL: `http://localhost:${CHROME_DEBUG_PORT}`,
    });
  } catch (err) {
    console.error(`[Subagent] Cannot connect to Chrome on port ${CHROME_DEBUG_PORT}:`, err.message);
    return 'ABORT: Chrome instance not available.';
  }

  const page = await browser.newPage();

  try {
    await page.setViewport(VIEWPORT);
    await page.goto(targetUrl, { waitUntil: 'networkidle2', timeout: 30000 });

    // Validate viewport lock per SYSTEM_OVERRIDE coordinate drift guardrail
    await page.evaluate(() => window.resizeTo(1920, 1080));

    // Visual injection — type the prompt and submit
    // Coordinates are calibrated for the target UI at 1920x1080
    await page.mouse.click(450, 800);
    await page.keyboard.type(prompt, { delay: 20 });
    await page.mouse.click(1800, 800);

    // Polling loop with hard timeout
    let isComplete = false;
    let attempts = 0;
    const startTime = Date.now();

    while (!isComplete && attempts < config.maxAttempts) {
      const elapsed = Date.now() - startTime;
      if (elapsed > config.hardTimeoutMs) {
        console.warn(`[Subagent] Hard timeout reached (${config.hardTimeoutMs}ms). Breaking.`);
        break;
      }

      await new Promise((r) => setTimeout(r, config.intervalMs));
      attempts++;

      // Check for error states (red text, "Failed", "Safety block")
      const errorDetected = await page.evaluate(() => {
        const body = document.body.innerText;
        return body.includes('Failed') || body.includes('Safety block') || body.includes('Error');
      });

      if (errorDetected) {
        console.error(`[Subagent] Error state detected on attempt ${attempts}. Halting.`);
        break;
      }

      // Check for successful completion (download button visible)
      const successState = await page.evaluate(
        () => !!document.querySelector('button[aria-label="Download"]')
      );

      if (successState) {
        // Click download
        await page.mouse.click(1800, 950);
        isComplete = true;
        console.log(`[Subagent] Asset generated and download triggered on attempt ${attempts}.`);
      }
    }

    if (isComplete) {
      // Fire App-Layer Pub/Sub event
      try {
        const topic = pubsub.topic(UI_EVENTS_TOPIC);
        const eventPayload = {
          event: 'ASSETS_RENDERED_AND_DOWNLOADED',
          prompt: prompt.substring(0, 100),
          outputType,
          targetUrl,
          timestamp: new Date().toISOString(),
          attempts,
        };
        await topic.publishMessage({
          data: Buffer.from(JSON.stringify(eventPayload)),
        });
        console.log('[Subagent] App-Layer Pub/Sub event fired:', UI_EVENTS_TOPIC);
      } catch (pubsubErr) {
        console.warn('[Subagent] Pub/Sub publish failed (non-fatal):', pubsubErr.message);
      }

      return 'Asset egressed. App-Layer Pub/Sub event fired.';
    }

    return `Generation ${isComplete ? 'complete' : 'timeout'} after ${attempts} attempts.`;
  } catch (err) {
    console.error('[Subagent] Task execution error:', err.message);
    return `ABORT: ${err.message}`;
  } finally {
    await page.close().catch(() => {});
    await browser.disconnect().catch(() => {});
  }
}

// CLI entrypoint
if (require.main === module) {
  const args = process.argv.slice(2);
  const prompt = args.find((_, i) => args[i - 1] === '--prompt') || 'Generate a test image';
  const url = args.find((_, i) => args[i - 1] === '--url') || 'https://labs.google/fx/tools/image-fx';
  const output = args.find((_, i) => args[i - 1] === '--output') || 'image';

  executeSubagentTask(prompt, url, output).then((result) => {
    console.log(`\n[Subagent Result] ${result}`);
    process.exit(0);
  });
}

module.exports = { executeSubagentTask };
