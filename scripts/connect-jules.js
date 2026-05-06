import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

/**
 * Connects to the remote Jules MCP API via its SSE endpoint.
 */
async function connectJules() {
  console.log("Initializing connection to Jules MCP API via SSE...");

  // Instantiate the SSE client transport
  const transport = new SSEClientTransport(new URL("https://mcp.jules.googleapis.com/v1/sse"), {
    // Add auth headers if needed
    // requestInit: { headers: { "X-Goog-Api-Key": process.env.JULES_API_KEY } }
  });

  const client = new Client(
    { name: "antigravity-jules-connector", version: "1.0.0" },
    { capabilities: {} }
  );

  try {
    await client.connect(transport);
    console.log("✅ Successfully connected to Jules MCP.");

    // Retrieve available tools from the remote Jules MCP
    const tools = await client.listTools();
    console.log("🛠️  Available Tools:", tools);
    
  } catch (error) {
    console.error("❌ Failed to connect to Jules MCP API:", error);
    process.exit(1);
  } finally {
    process.exit(0);
  }
}

connectJules();
