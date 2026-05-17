/**
 * Claude Web Conversation Extractor
 *
 * Extracts all conversations from:
 * - Claude.ai (regular chat)
 * - Claude Code for web
 *
 * USAGE:
 * 1. Navigate to claude.ai or code.claude.com
 * 2. Open browser DevTools (F12)
 * 3. Go to Console tab
 * 4. Paste this entire script
 * 5. Press Enter
 * 6. Wait for extraction to complete
 * 7. Download will start automatically
 */
(async function extractClaudeWebConversations() {
  console.log("%c🚀 Claude Web Conversation Extractor v1.1", "font-size: 16px; font-weight: bold;");
  console.log("%c-----------------------------------------", "color: #888;");
  console.log('%cNOTE: Ignore any red "CORS" or "NetworkError" messages.', "color: yellow;");
  console.log(
    "%cThese are from the website's background checks, NOT this script.",
    "color: yellow;",
  );
  console.log("%c-----------------------------------------", "color: #888;");

  const platform = window.location.hostname.includes("code.claude.com")
    ? "claude-code-web"
    : "claude-ai-web";

  console.log(`📍 Platform detected: ${platform}`);

  // ========================================
  // STEP 1: Extract from localStorage
  // ========================================
  console.log("\n🔍 Step 1: Scanning localStorage...");
  const localStorageData = {};
  const relevantKeys = [];

  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (
      key.includes("conversation") ||
      key.includes("chat") ||
      key.includes("message") ||
      key.includes("claude") ||
      key.includes("thread")
    ) {
      relevantKeys.push(key);
      try {
        localStorageData[key] = JSON.parse(localStorage.getItem(key));
      } catch (e) {
        localStorageData[key] = localStorage.getItem(key);
      }
    }
  }

  console.log(`   Found ${relevantKeys.length} relevant localStorage keys`);

  // ========================================
  // STEP 2: Extract from IndexedDB
  // ========================================
  console.log("\n🔍 Step 2: Scanning IndexedDB...");
  const indexedDBData = {};

  try {
    const databases = await indexedDB.databases();
    console.log(`   Found ${databases.length} IndexedDB databases`);

    for (const dbInfo of databases) {
      try {
        const db = await openDatabase(dbInfo.name);
        const storeNames = Array.from(db.objectStoreNames);

        console.log(`   📦 Database: ${dbInfo.name} (${storeNames.length} stores)`);

        for (const storeName of storeNames) {
          if (
            storeName.includes("conversation") ||
            storeName.includes("chat") ||
            storeName.includes("message")
          ) {
            try {
              const data = await getAllFromStore(db, storeName);
              indexedDBData[`${dbInfo.name}.${storeName}`] = data;
              console.log(`      ✓ ${storeName}: ${data.length} records`);
            } catch (err) {
              console.warn(`      ⚠️ Could not read store ${storeName}:`, err.message);
            }
          }
        }

        db.close();
      } catch (e) {
        console.error(`   ✗ Error reading ${dbInfo.name}:`, e.message);
      }
    }
  } catch (e) {
    console.error(
      "   ✗ Could not list databases (browser security restriction likely):",
      e.message,
    );
  }

  // ========================================
  // STEP 3: Extract from DOM (visible conversations)
  // ========================================
  console.log("\n🔍 Step 3: Scanning DOM for visible conversations...");
  const domConversations = [];

  // Try multiple selectors for different Claude interfaces
  const selectors = [
    '[data-testid="conversation"]',
    '[data-testid="chat-message"]',
    ".conversation-item",
    ".chat-message",
    '[role="article"]',
    "[data-conversation-id]",
  ];

  for (const selector of selectors) {
    const elements = document.querySelectorAll(selector);
    if (elements.length > 0) {
      console.log(`   Found ${elements.length} elements with selector: ${selector}`);

      elements.forEach((el, idx) => {
        domConversations.push({
          index: idx,
          selector: selector,
          innerHTML: el.innerHTML.substring(0, 1000), // First 1000 chars to save space
          textContent: el.textContent.substring(0, 5000),
          attributes: getElementAttributes(el),
          dataset: el.dataset,
        });
      });
    }
  }

  console.log(`   Extracted ${domConversations.length} DOM conversation elements`);

  // ========================================
  // STEP 4: Extract from sessionStorage
  // ========================================
  console.log("\n🔍 Step 4: Scanning sessionStorage...");
  const sessionStorageData = {};

  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    if (key.includes("conversation") || key.includes("chat")) {
      try {
        sessionStorageData[key] = JSON.parse(sessionStorage.getItem(key));
      } catch (e) {
        sessionStorageData[key] = sessionStorage.getItem(key);
      }
    }
  }

  console.log(`   Found ${Object.keys(sessionStorageData).length} relevant sessionStorage keys`);

  // ========================================
  // STEP 5: Try to fetch via Network API (if available)
  // ========================================
  console.log("\n🔍 Step 5: Attempting to fetch conversations via API...");
  const apiConversations = await tryFetchConversationsAPI();

  // ========================================
  // STEP 6: Consolidate and structure data
  // ========================================
  console.log("\n📦 Consolidating extraction results...");

  const extraction = {
    metadata: {
      platform: platform,
      extracted_at: new Date().toISOString(),
      url: window.location.href,
      user_agent: navigator.userAgent,
      extractor_version: "1.1.0",
    },
    sources: {
      localStorage: {
        keys_found: relevantKeys.length,
        data: localStorageData,
      },
      indexedDB: {
        databases_scanned: Object.keys(indexedDBData).length, // Approximate
        data: indexedDBData,
      },
      dom: {
        conversations_found: domConversations.length,
        data: domConversations,
      },
      sessionStorage: {
        keys_found: Object.keys(sessionStorageData).length,
        data: sessionStorageData,
      },
      api: apiConversations,
    },
    statistics: {
      total_sources: 5,
      localStorage_keys: relevantKeys.length,
      indexedDB_records: Object.values(indexedDBData).flat().length,
      dom_elements: domConversations.length,
      sessionStorage_keys: Object.keys(sessionStorageData).length,
      api_conversations: apiConversations?.conversations?.length || 0,
    },
  };

  // ========================================
  // STEP 7: Download results
  // ========================================
  console.log("\n💾 Generating download...");

  const filename = `claude_web_extraction_${platform}_${Date.now()}.json`;
  const blob = new Blob([JSON.stringify(extraction, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  console.log(`\n✅ Extraction complete!`);
  console.log(`📊 Statistics:`);
  console.log(`   - Platform: ${platform}`);
  console.log(`   - localStorage keys: ${extraction.statistics.localStorage_keys}`);
  console.log(`   - IndexedDB records: ${extraction.statistics.indexedDB_records}`);
  console.log(`   - DOM elements: ${extraction.statistics.dom_elements}`);
  console.log(`   - sessionStorage keys: ${extraction.statistics.sessionStorage_keys}`);
  console.log(`   - API conversations: ${extraction.statistics.api_conversations}`);
  console.log(`\n📥 Downloaded: ${filename}`);
  console.log(`\n💡 Next steps:`);
  console.log(`   1. Move ${filename} to erik-hancock-llm-memory/extractions/`);
  console.log(`   2. Run: python scripts/merge_web_extractions.py`);
  console.log(`   3. This will merge with existing 0xSero data`);

  return extraction;

  // ========================================
  // Helper Functions
  // ========================================

  function openDatabase(name) {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(name);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  function getAllFromStore(db, storeName) {
    return new Promise((resolve, reject) => {
      const transaction = db.transaction(storeName, "readonly");
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  function getElementAttributes(el) {
    const attrs = {};
    for (const attr of el.attributes) {
      attrs[attr.name] = attr.value;
    }
    return attrs;
  }

  async function tryFetchConversationsAPI() {
    console.group("📡 Scanning API Endpoints (Safe Mode)");
    // Common endpoints for Claude web interfaces
    const apiEndpoints = [
      "/api/organizations/*/conversations",
      "/api/conversations",
      "/api/v1/conversations",
      "/backend-api/conversations",
    ];

    for (const endpoint of apiEndpoints) {
      try {
        // Short timeout to differentiate between blocked (fast fail) and hanging (slow)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);

        console.log(`   👉 Probing: ${endpoint}...`);

        const response = await fetch(endpoint, {
          headers: { Accept: "application/json" },
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          const data = await response.json();
          console.log(`   ✅ SUCCESS: Found conversations at ${endpoint}`);
          console.groupEnd();
          return {
            endpoint: endpoint,
            status: response.status,
            conversations: data,
          };
        }
      } catch (e) {
        // Ignore network errors - likely CORS or 404
        // console.log(`      (Skipping ${endpoint}: ${e.message})`);
      }
    }

    console.log(`   ℹ️  No accessible API endpoints found (using LocalStorage only)`);
    console.groupEnd();
    return { endpoint: null, conversations: [] };
  }
})();
