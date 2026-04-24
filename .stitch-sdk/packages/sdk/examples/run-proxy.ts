/**
 * Run an MCP Proxy for Stitch, passing through requests over stdio.
 *
 * Usage:
 *   STITCH_API_KEY=your-key bun packages/sdk/examples/run-proxy.ts
 */
import './_require-key.js';
import { StitchProxy } from '@google/stitch-sdk';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const proxy = new StitchProxy();
const transport = new StdioServerTransport();

// Handle graceful shutdown
process.on('SIGINT', async () => {
  await proxy.close();
  process.exit(0);
});

await proxy.start(transport);
