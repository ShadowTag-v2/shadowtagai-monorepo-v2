// agent.js - The "Brain" of the operation
const puppeteer = require('puppeteer-core');
const axios = require('axios');
require('dotenv').config(); // Load your GEMINI_API_KEY or OPENAI_API_KEY

// CONFIGURATION
const CHROME_DEBUG_URL = 'http://127.0.0.1:9222'; // Port enabled by --remote-debugging-port
const BRIDGE_CONTROL_URL = 'http://127.0.0.1:8080/control';
const GOAL = "Go to Google Cloud Console, search for 'VM Instances', and click the first result.";

async function runAgentLoop() {
  console.log('🤖 Agent started. Connecting to Chrome...');

  // 1. CONNECT TO CHROME (The "Eyes")
  // We use puppeteer-core to connect to the existing browser instance
  const browser = await puppeteer.connect({
    browserURL: CHROME_DEBUG_URL,
  });
  const page = (await browser.pages())[0]; // Grab the first open tab

  console.log('✅ Connected to active tab:', await page.url());

  // THE AGENT LOOP
  let step = 0;
  const MAX_STEPS = 5;

  while (step < MAX_STEPS) {
    console.log(`\n--- STEP ${step + 1} ---`);

    // A. TAKE SCREENSHOT
    const screenshotBase64 = await page.screenshot({ encoding: 'base64' });
    console.log('📸 Screenshot captured.');

    // B. THINK (Call LLM)
    const action = await askLLM(GOAL, screenshotBase64);
    console.log('🧠 LLM Decided:', action);

    if (action.type === 'finish') {
      console.log('🎉 Goal achieved!');
      break;
    }

    // C. ACT (Send Command to Bridge)
    // We send the command to our HTTP Bridge (which talks to the Extension)
    // Note: We could use Puppeteer to click, but using the Bridge mimics the "Jetski" architecture
    // and allows for extension-specific capabilities (like managing downloads/cookies easily).
    try {
      await axios.post(BRIDGE_CONTROL_URL, {
        action: action.type,
        payload: action.payload,
      });
      console.log('🚀 Command sent to Bridge.');
    } catch (err) {
      console.error('❌ Bridge Error:', err.message);
    }

    // Wait for the browser to react (simple delay)
    await new Promise((r) => setTimeout(r, 3000));
    step++;
  }

  await browser.disconnect();
}

// MOCK LLM FUNCTION (Replace with actual API call to Gemini/OpenAI)
async function askLLM(goal, imageBase64) {
  // INSTRUCTION: In a real scenario, send 'imageBase64' and 'goal' to the API.
  // The System Prompt should be:
  // "You are a browser automation agent. Based on the screenshot, output a JSON object
  // with a 'type' (navigate, click, exec, finish) and 'payload'."

  // --- PSEUDO-CODE FOR GEMINI API ---
  /*
  const model = genAI.getGenerativeModel({ model: "gemini-3.1-flash-lite-preview" });
  const result = await model.generateContent([
    `Goal: ${goal}. Return JSON only.`,
    { inlineData: { data: imageBase64, mimeType: "image/png" } }
  ]);
  return JSON.parse(result.response.text());
  */

  // --- HARDCODED DEMO LOGIC (For testing without API Key) ---
  const stepLogic = [
    { type: 'navigate', payload: { url: 'https://console.cloud.google.com' } },
    {
      type: 'exec',
      payload: {
        code: `document.querySelector('input[type="text"]').value = 'VM Instances';`,
      },
    }, // Simplified search
    {
      type: 'exec',
      payload: {
        code: `document.querySelector('button[aria-label="Search"]').click();`,
      },
    },
    { type: 'finish', payload: {} },
  ];

  // Return a random step for demonstration if logic isn't implemented
  return stepLogic[Math.min(global.stepCounter++ || 0, stepLogic.length - 1)];
}

// Global counter for the demo mock
global.stepCounter = 0;

runAgentLoop();
