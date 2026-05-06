import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import path from 'path';
import url from 'url';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

async function deployWithJules() {
  const transport = new StdioClientTransport({
    command: 'python3',
    args: ['-m', 'jules_mcp_server'],
    env: {
      ...process.env,
      PYTHONPATH: path.join(__dirname, '../packages'),
    },
  });

  const client = new Client(
    { name: 'antigravity-jules-deploy', version: '1.0.0' },
    { capabilities: {} },
  );

  try {
    await client.connect(transport);
    console.log('Connected to Jules.');

    console.log('Executing task...');
    const taskResult = await client.callTool({
      name: 'jules_execute_task',
      arguments: {
        source_name: 'sources/github/ShadowTag-v2/Monorepo-Uphillsnowball',
        task_description:
          "Get the headfade landing page live. Build apps/headfade/pwa and deploy it via firebase.json's headfade target.",
        automation_mode: 'AUTO_CREATE_PR',
      },
    });
    console.log('Task executed:', JSON.stringify(taskResult, null, 2));
  } catch (error) {
    console.error('Failed:', error);
  } finally {
    process.exit(0);
  }
}
deployWithJules();
