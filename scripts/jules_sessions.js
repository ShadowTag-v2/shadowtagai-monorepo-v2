import path from 'node:path';
import url from 'node:url';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

async function listSessions() {
  const transport = new StdioClientTransport({
    command: 'python3',
    args: ['-m', 'jules_mcp_server'],
    env: {
      ...process.env,
      PYTHONPATH: path.join(__dirname, '../packages'),
    },
  });

  const client = new Client({ name: 'test', version: '1.0.0' }, { capabilities: {} });

  try {
    await client.connect(transport);

    // First, list sources
    const tools = await client.callTool({
      name: 'jules_list_sources',
      arguments: {},
    });
    console.log('Sources:', JSON.stringify(tools, null, 2));
  } catch (error) {
    console.error('Failed:', error);
  } finally {
    process.exit(0);
  }
}
listSessions();
