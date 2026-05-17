import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";
import { GoogleAuth } from "google-auth-library";

// Project Configuration
const GCP_PROJECT_ID = "shadowtag-omega-v4";
const _SERVICE_ACCOUNT = "antigravity-stitch-bot@shadowtag-omega-v4.iam.gserviceaccount.com";

// Enterprise-Grade IAM Authentication via Workload Identity Federation
const auth = new GoogleAuth({
  scopes: [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/jules.mcp.execute",
  ],
});

async function connectToJulesMCP() {
  console.log("🔒 [Antigravity] Requesting short-lived IAM token via Workload Identity...");

  const authClient = await auth.getClient();
  const tokenInfo = await authClient.getAccessToken();

  if (!tokenInfo.token) {
    throw new Error("Fatal: Failed to obtain Workload Identity token.");
  }

  console.log("✅ [Antigravity] Short-lived token acquired. Connecting to Jules MCP...");

  // Official MCP SSE Transport (Enterprise Endpoint)
  const transport = new SSEClientTransport(new URL("https://mcp.jules.googleapis.com/v1/sse"), {
    headers: {
      Authorization: `Bearer ${tokenInfo.token}`,
      "X-Goog-User-Project": GCP_PROJECT_ID,
      "Content-Type": "application/json",
    },
  });

  const mcpClient = new Client(
    {
      name: "HeadFade-Stitch-Orchestrator",
      version: "2.0.0",
    },
    {
      capabilities: {
        roots: { listChanged: true },
      },
    },
  );

  await mcpClient.connect(transport);

  console.log("✅ [Antigravity] Direct Enterprise IAM connection to Jules established via MCP.");
  console.log("🚀 HeadFade is now ready to deploy https://headfade.com/ using official Jules.");

  return mcpClient;
}

connectToJulesMCP().catch(console.error);
```
