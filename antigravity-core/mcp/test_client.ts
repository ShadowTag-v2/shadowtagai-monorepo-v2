import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  console.log("Starting MCP Client...");
  const transport = new StdioClientTransport({
    command: "node",
    args: ["dist/index.js"],
    env: {
      ...process.env,
      // Need to make sure STRIPE_SECRET_KEY is provided
      STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY || "sk_test_123"
    }
  });

  const client = new Client(
    { name: "test-client", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  await client.connect(transport);
  console.log("Connected to MCP server.");

  const tools = await client.listTools();
  console.log("Available tools:", tools.tools.map((t: any) => t.name));

  console.log("Calling purchase_workflow_license...");
  try {
    const result = await client.callTool({
      name: "purchase_workflow_license",
      arguments: {
        videoId: "vid_test_123",
        agentWalletToken: "agnt_test_123"
      }
    });
    console.log("Result:", JSON.stringify(result, null, 2));
  } catch (err) {
    console.error("Error calling tool:", err);
  }

  process.exit(0);
}

main().catch(console.error);
