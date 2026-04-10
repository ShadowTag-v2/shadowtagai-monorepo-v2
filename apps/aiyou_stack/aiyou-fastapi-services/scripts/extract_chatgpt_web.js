/**
 * ChatGPT Web Conversation Extractor v2.1 (Safe Mode)
 *
 * Extracts conversations from chatgpt.com
 *
 * USAGE:
 * 1. Navigate to chatgpt.com
 * 2. Open Console (F12)
 * 3. Paste this ENTIRE script
 * 4. Press Enter
 */

(async () => {
  console.clear();
  console.log(
    "%c🚀 ChatGPT Stealth Extractor v3.1 (Auth Fix)",
    "font-size: 20px; font-weight: bold; color: #10a37f;",
  );

  var platform = "chatgpt-web-stealth-auth";
  var MAX_CONVERSATIONS = 3000;
  var AUTH_TOKEN = null;

  function sleep(min, max) {
    var ms = Math.floor(Math.random() * (max - min + 1)) + min;
    return new Promise((resolve) => {
      setTimeout(resolve, ms);
    });
  }

  // STEP 0: Get Auth Token using their internal session endpoint
  try {
    console.log("🔑 Step 0: Attempting to get Auth Token...");
    var sessionResp = await fetch("/api/auth/session");
    if (sessionResp.ok) {
      var sessionData = await sessionResp.json();
      AUTH_TOKEN = sessionData.accessToken;
      if (AUTH_TOKEN) {
        console.log("   ✅ Auth Token acquired!");
      } else {
        console.warn("   ⚠️ No access token in session data. Continuing with cookies only...");
      }
    } else {
      console.warn("   ⚠️ Failed to fetch session. Status: " + sessionResp.status);
    }
  } catch (e) {
    console.warn("   ⚠️ Session fetch error: " + e.message);
  }

  var headers = {
    "Content-Type": "application/json",
  };
  if (AUTH_TOKEN) {
    headers["Authorization"] = "Bearer " + AUTH_TOKEN;
  }

  // STEP 1: Fetch Conversation List
  console.log("\n📄 Step 1: Scanning conversation list...");
  var conversationMetas = [];
  var offset = 0;
  var limit = 50; // Try lower limit if 50 fails?
  var hasMore = true;
  var listErrors = [];

  try {
    while (hasMore && conversationMetas.length < MAX_CONVERSATIONS) {
      var url =
        "/backend-api/conversations?offset=" + offset + "&limit=" + limit + "&order=updated";
      var response = await fetch(url, { method: "GET", headers: headers });

      if (response.ok) {
        var data = await response.json();
        var items = data.items || [];

        if (items.length === 0) {
          hasMore = false;
        } else {
          conversationMetas = conversationMetas.concat(items);
          offset += limit;
          console.log("   Found " + conversationMetas.length + " conversations...");
          await sleep(1000, 2000);
        }
      } else {
        console.error("   ❌ List fetch error: " + response.status);
        listErrors.push(response.status);
        if (response.status === 401 || response.status === 403) {
          alert(
            "Authentication Error (" +
              response.status +
              "). Please refresh the page and log in again, then retry.",
          );
          return; // Stop immediately
        }
        if (response.status === 429) {
          console.log("   ⚠️ Rate limited. Waiting 30s...");
          await sleep(30000, 30000);
        } else {
          hasMore = false;
        }
      }
    }
  } catch (e) {
    console.error("   ❌ Critical list error: " + e.message);
    alert("Critical Error: " + e.message);
    return;
  }

  console.log("✅ Found total: " + conversationMetas.length + " conversations.");

  if (conversationMetas.length === 0) {
    alert(
      "Zero conversations found! Please check the console for header errors or refresh the page.",
    );
  }

  // STEP 2: Fetch Details
  console.log("\n📥 Step 2: Extracting message history...");
  var fullConversations = [];
  var successCount = 0;
  var failCount = 0;

  for (var i = 0; i < conversationMetas.length; i++) {
    var meta = conversationMetas[i];
    var progress = "[" + (i + 1) + "/" + conversationMetas.length + "]";

    try {
      var resp = await fetch("/backend-api/conversation/" + meta.id, {
        method: "GET",
        headers: headers,
      });

      if (resp.ok) {
        var detail = await resp.json();
        fullConversations.push({
          id: meta.id,
          title: meta.title,
          create_time: meta.create_time,
          mapping: detail.mapping,
          current_node: detail.current_node,
        });
        successCount++;
        console.log(progress + " OK: " + (meta.title || "Untitled").substring(0, 30));
      } else {
        console.log(progress + " FAIL (" + resp.status + "): " + meta.id);
        fullConversations.push({ id: meta.id, title: meta.title, error: resp.status });
        failCount++;

        if (resp.status === 429) {
          console.log("   🛑 Rate limit hit. Pausing 60 seconds...");
          await sleep(60000, 60000);
          i--;
          continue;
        }
      }
    } catch (err) {
      console.error(progress + " Error: " + err.message);
      failCount++;
    }

    await sleep(3000, 7000);
  }

  // STEP 3: Download
  var extraction = {
    metadata: {
      platform: platform,
      extracted_at: new Date().toISOString(),
      total_scanned: conversationMetas.length,
      success_count: successCount,
      fail_count: failCount,
      auth_method: AUTH_TOKEN ? "bearer" : "cookie",
    },
    data: {
      api_conversations: fullConversations,
    },
  };

  var blob = new Blob([JSON.stringify(extraction, null, 2)], { type: "application/json" });
  var downloadUrl = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = downloadUrl;
  a.download = "chatgpt_backup_v3_" + Date.now() + ".json";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);

  alert(
    "Extraction Complete!\nSaved: " +
      a.download +
      "\nSuccess: " +
      successCount +
      "\nFailed: " +
      failCount,
  );
})();
