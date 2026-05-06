import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import url from 'url';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

/**
 * Connects to the local Jules MCP API via its stdio endpoint.
 */
async function connectJules() {
  console.log('Initializing connection to Jules MCP API via stdio...');

  const transport = new StdioClientTransport({
    command: 'python3',
    args: ['-m', 'jules_mcp_server'],
    env: {
      ...process.env,
      PYTHONPATH: path.join(__dirname, '../packages'),
    },
  });

  const client = new Client(
    { name: 'antigravity-jules-connector', version: '1.0.0' },
    { capabilities: {} },
  );

  try {
    await client.connect(transport);
    console.log('✅ Successfully connected to Jules MCP.');

    // Retrieve available tools from the remote Jules MCP
    const tools = await client.listTools();
    console.log('🛠️  Available Tools:');
    console.dir(tools, { depth: null });
  } catch (error) {
    console.error('❌ Failed to connect to Jules MCP API:', error);
    process.exit(1);
  } finally {
    process.exit(0);
  }
}

connectJules();
