const http = require("http");
const fs = require("fs");
const path = require("path");
const os = require("os");

// 1. Find Discovery File
const discoveryDir = path.join(os.tmpdir(), "gemini", "ide");
console.log(`[Test Client] Looking for discovery files in: ${discoveryDir}`);

// Wait for file to appear
let discoveryFile;
let attempts = 0;
const maxAttempts = 10;

const interval = setInterval(() => {
  attempts++;
  try {
    const files = fs.readdirSync(discoveryDir);
    const serverFile = files.find((f) => f.startsWith("gemini-ide-server-"));

    if (serverFile) {
      discoveryFile = path.join(discoveryDir, serverFile);
      clearInterval(interval);
      runTest(discoveryFile);
    } else if (attempts >= maxAttempts) {
      console.error("[Test Client] Timeout waiting for discovery file.");
      clearInterval(interval);
      process.exit(1);
    }
  } catch (e) {
    if (attempts >= maxAttempts) {
      console.error(`[Test Client] Error reading directory: ${e.message}`);
      clearInterval(interval);
      process.exit(1);
    }
  }
}, 1000);

function runTest(filePath) {
  console.log(`[Test Client] Found discovery file: ${filePath}`);
  const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
  const port = data.port;
  const authToken = data.authToken;

  console.log(`[Test Client] Connecting to port ${port} with token ${authToken}`);

  // 2. Connect via SSE (GET /messages)
  const options = {
    hostname: "localhost",
    port: port,
    path: "/messages",
    method: "GET",
    headers: {
      Authorization: `Bearer ${authToken}`,
      Accept: "text/event-stream",
    },
  };

  const req = http.request(options, (res) => {
    console.log(`[Test Client] SSE Connection Status: ${res.statusCode}`);

    if (res.statusCode !== 200) {
      console.error("[Test Client] Failed to connect to SSE stream");
      process.exit(1);
    }

    res.on("data", (chunk) => {
      const text = chunk.toString();
      console.log(`[Test Client] Received SSE Data: ${text}`);

      // Look for the 'endpoint' event which contains the session ID
      if (text.includes("event: endpoint")) {
        const match = text.match(/sessionId=([a-zA-Z0-9-]+)/);
        if (match) {
          const sessionId = match[1];
          console.log(`[Test Client] Captured Session ID: ${sessionId}`);

          // 3. Send Tool Call (POST /messages)
          sendToolCall(port, sessionId, authToken);
        }
      }

      // Look for the 'message' event which contains the JSON-RPC response
      if (text.includes("event: message")) {
        // Extract data: ...
        const lines = text.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const jsonStr = line.substring(6);
            try {
              const json = JSON.parse(jsonStr);
              console.log("[Test Client] Received JSON-RPC Message:", json);

              if (json.id === 1 && json.result && json.result.tools) {
                console.log("[Test Client] SUCCESS: Received tool list.");
                const toolNames = json.result.tools.map((t) => t.name);
                console.log(`[Test Client] Tools found: ${toolNames.join(", ")}`);

                if (toolNames.includes("openDiff") && toolNames.includes("closeDiff")) {
                  console.log("[Test Client] Verification PASSED.");
                  process.exit(0);
                }
              }
            } catch (e) {
              // Ignore parsing errors for partial chunks
            }
          }
        }
      }
    });
  });

  req.on("error", (e) => {
    console.error(`[Test Client] SSE Request Error: ${e.message}`);
  });

  req.end();
}

function sendToolCall(port, sessionId, authToken) {
  const postData = JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
    params: {},
  });

  const options = {
    hostname: "localhost",
    port: port,
    path: `/messages?sessionId=${sessionId}`,
    method: "POST",
    headers: {
      Authorization: `Bearer ${authToken}`,
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(postData),
    },
  };

  console.log(`[Test Client] Sending tools/list request...`);

  const req = http.request(options, (res) => {
    console.log(`[Test Client] POST Response Status: ${res.statusCode}`);
    // We don't expect the body here, just 202 Accepted
  });

  req.on("error", (e) => {
    console.error(`[Test Client] POST Request Error: ${e.message}`);
  });

  req.write(postData);
  req.end();
}
