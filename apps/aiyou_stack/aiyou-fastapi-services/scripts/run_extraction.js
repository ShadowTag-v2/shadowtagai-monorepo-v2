#!/usr/bin/env node

/**
 * Claude Web Conversation Extractor - Puppeteer Runner
 *
 * This script automates the extraction of Claude conversation data using Puppeteer.
 * It opens Claude.ai/code.claude.com, executes the extraction script, and saves the data.
 *
 * Usage:
 *   node scripts/run_extraction.js [options]
 *
 * Options:
 *   --url <url>       Target URL (default: https://claude.ai)
 *   --headless        Run in headless mode (default: false, shows browser)
 *   --output <dir>    Output directory for extracted data (default: ./extractions)
 *   --timeout <ms>    Navigation timeout in milliseconds (default: 60000)
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const getArg = (flag, defaultValue) => {
  const index = args.indexOf(flag);
  return index !== -1 && args[index + 1] ? args[index + 1] : defaultValue;
};

const config = {
  url: getArg('--url', 'https://claude.ai'),
  headless: args.includes('--headless'),
  outputDir: getArg('--output', './extractions'),
  timeout: parseInt(getArg('--timeout', '60000'), 10),
};

console.log('🚀 Claude Web Conversation Extractor - Automated Runner');
console.log('Configuration:', config);

(async () => {
  let browser;
  try {
    // Ensure output directory exists
    if (!fs.existsSync(config.outputDir)) {
      fs.mkdirSync(config.outputDir, { recursive: true });
      console.log(`📁 Created output directory: ${config.outputDir}`);
    }

    // Launch browser
    console.log('🌐 Launching browser...');
    browser = await puppeteer.launch({
      headless: config.headless,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
      ],
      defaultViewport: { width: 1280, height: 800 },
    });

    const page = await browser.newPage();

    // Set up download handling
    const client = await page.target().createCDPSession();
    await client.send('Page.setDownloadBehavior', {
      behavior: 'allow',
      downloadPath: path.resolve(config.outputDir),
    });

    console.log(`📍 Navigating to ${config.url}...`);
    await page.goto(config.url, {
      waitUntil: 'networkidle2',
      timeout: config.timeout,
    });

    console.log('⏳ Waiting for page to fully load...');
    await page.waitForTimeout(3000);

    // Check if user needs to log in
    const isLoggedIn = await page.evaluate(() => {
      return !window.location.pathname.includes('/login');
    });

    if (!isLoggedIn) {
      console.log('🔐 Login required. Please log in to Claude in the browser window.');
      console.log('⏳ Waiting for login... (checking every 5 seconds)');

      // Wait for user to log in (check every 5 seconds, max 5 minutes)
      let loggedIn = false;
      for (let i = 0; i < 60; i++) {
        await page.waitForTimeout(5000);
        loggedIn = await page.evaluate(() => {
          return !window.location.pathname.includes('/login');
        });
        if (loggedIn) {
          console.log('✅ Login detected!');
          await page.waitForTimeout(3000); // Wait for app to load
          break;
        }
      }

      if (!loggedIn) {
        throw new Error('Login timeout - please run the script again after logging in');
      }
    } else {
      console.log('✅ Already logged in');
    }

    // Read the extraction script
    const extractionScript = fs.readFileSync(path.join(__dirname, 'extract_claude_web.js'), 'utf8');

    console.log('🔍 Executing extraction script...');

    // Execute the extraction and get the data
    const extractionData = await page.evaluate((script) => {
      return new Promise((resolve, reject) => {
        try {
          (async function extractClaudeWebConversations() {
            const platform = window.location.hostname.includes('code.claude.com')
              ? 'claude-code-web'
              : 'claude-ai-web';

            // 1. LocalStorage
            const localStorageData = {};
            for (let i = 0; i < localStorage.length; i++) {
              const key = localStorage.key(i);
              if (
                key.includes('conversation') ||
                key.includes('chat') ||
                key.includes('message') ||
                key.includes('claude') ||
                key.includes('thread')
              ) {
                try {
                  localStorageData[key] = JSON.parse(localStorage.getItem(key));
                } catch (e) {
                  localStorageData[key] = localStorage.getItem(key);
                }
              }
            }

            // 2. IndexedDB
            const indexedDBData = {};
            const databases = await indexedDB.databases();
            for (const dbInfo of databases) {
              try {
                const db = await new Promise((res, rej) => {
                  const req = indexedDB.open(dbInfo.name);
                  req.onsuccess = () => res(req.result);
                  req.onerror = () => rej(req.error);
                });
                for (const storeName of Array.from(db.objectStoreNames)) {
                  if (
                    storeName.includes('conversation') ||
                    storeName.includes('chat') ||
                    storeName.includes('message')
                  ) {
                    const data = await new Promise((res, rej) => {
                      const tx = db.transaction(storeName, 'readonly');
                      const req = tx.objectStore(storeName).getAll();
                      req.onsuccess = () => res(req.result);
                      req.onerror = () => rej(req.error);
                    });
                    indexedDBData[`${dbInfo.name}.${storeName}`] = data;
                  }
                }
                db.close();
              } catch (e) {
                console.error(e);
              }
            }

            // 3. API Fetch
            let apiConversations = [];
            try {
              const resp = await fetch('/api/organizations/*/conversations');
              if (resp.ok) apiConversations = await resp.json();
            } catch (e) {}

            const extraction = {
              metadata: { platform, extracted_at: new Date().toISOString() },
              sources: {
                localStorage: { data: localStorageData },
                indexedDB: { data: indexedDBData },
                api: { conversations: apiConversations },
              },
            };

            resolve(extraction);
          })();
        } catch (error) {
          reject(error);
        }
      });
    }, extractionScript);

    // Save the extraction data
    const platform = extractionData.metadata.platform;
    const filename = `claude_web_extraction_${platform}_${Date.now()}.json`;
    const filepath = path.join(config.outputDir, filename);

    fs.writeFileSync(filepath, JSON.stringify(extractionData, null, 2));

    console.log('✅ Extraction complete!');
    console.log(`📄 Data saved to: ${filepath}`);
    console.log(`📊 Summary:`);
    console.log(`   - Platform: ${extractionData.metadata.platform}`);
    console.log(`   - Extracted at: ${extractionData.metadata.extracted_at}`);
    console.log(
      `   - LocalStorage keys: ${Object.keys(extractionData.sources.localStorage.data).length}`,
    );
    console.log(
      `   - IndexedDB stores: ${Object.keys(extractionData.sources.indexedDB.data).length}`,
    );
    console.log(
      `   - API conversations: ${Array.isArray(extractionData.sources.api.conversations) ? extractionData.sources.api.conversations.length : 'N/A'}`,
    );
  } catch (error) {
    console.error('❌ Error during extraction:', error.message);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Browser closed');
    }
  }
})();
