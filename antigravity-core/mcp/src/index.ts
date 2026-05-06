import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { GoogleAuth } from "google-auth-library";
import { z } from "zod";

// Import tools
import { verifySyntheticVideo } from "./tools/verify_synthetic_video.js";
import { purchaseWorkflowLicense } from "./tools/purchase_workflow_license.js";

// Enterprise-grade authentication via Workload Identity Federation
const auth = new GoogleAuth({
  scopes: [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/jules.mcp.execute"
  ]
});

async function getAuthToken() {
  const client = await auth.getClient();
  const token = await client.getAccessToken();
  if (!token.token) throw new Error("Failed to obtain Workload Identity token");
  return token.token;
}

const server = new McpServer({
  name: "headfade-truth-oracle",
  version: "1.0.0"
});

// Register tools
server.tool(
  "verify_synthetic_video",
  "Fetch the Human Deception Index (HDI), AI models used, and Remix Family Tree for any synthetic video.",
  { videoId: z.string().describe("HeadFade video ID or hash") },
  async ({ videoId }) => {
    const token = await getAuthToken();
    return await verifySyntheticVideo(videoId, token);
  }
);

server.tool(
  "purchase_workflow_license",
  "Agent-to-Agent micro-license purchase ($2.99) for ComfyUI workflows and prompts.",
  {
    videoId: z.string(),
    agentWalletToken: z.string().describe("Calling agent's payment token")
  },
  async ({ videoId, agentWalletToken }) => {
    const token = await getAuthToken();
    return await purchaseWorkflowLicense(videoId, agentWalletToken, token);
  }
);

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);

console.log("✅ HeadFade Truth Oracle MCP Server running (Enterprise IAM mode)");