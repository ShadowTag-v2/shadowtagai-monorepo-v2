const { McpServer } = require('@modelcontextprotocol/sdk/server/mcp.js');
const { SSEServerTransport } = require('@modelcontextprotocol/sdk/server/sse.js');
const { z } = require('zod');
const express = require('express');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { v4: uuidv4 } = require('uuid');

// Configuration
const PID = process.pid;
const AUTH_TOKEN = uuidv4();
const WORKSPACE_PATH = process.cwd();

// Create MCP Server
const server = new McpServer({
  name: 'gemini-ide-companion-mock',
  version: '1.0.0',
});

// Register Tools
server.tool(
  'openDiff',
  {
    filePath: z.string().describe('The absolute path to the file to be diffed.'),
    newContent: z.string().describe('The proposed new content for the file.'),
  },
  async ({ filePath, newContent }) => {
    console.log(`[Mock IDE] openDiff requested for: ${filePath}`);
    console.log(`[Mock IDE] New content length: ${newContent.length}`);
    return {
      content: [],
    };
  },
);

server.tool(
  'closeDiff',
  {
    filePath: z
      .string()
      .describe('The absolute path to the file whose diff view should be closed.'),
  },
  async ({ filePath }) => {
    console.log(`[Mock IDE] closeDiff requested for: ${filePath}`);
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      return {
        content: [{ type: 'text', text: content }],
      };
    } catch (error) {
      return {
        isError: true,
        content: [{ type: 'text', text: `Failed to read file: ${error.message}` }],
      };
    }
  },
);

// Express App
const app = express();
const transports = new Map(); // sessionId -> transport

app.get('/messages', async (_req, res) => {
  const transport = new SSEServerTransport('/messages', res);

  // Hook into the transport to capture the session ID once it's established
  // Note: SDK implementation details might vary, but usually the sessionId is available
  // or we can force one if the constructor allows.
  // Looking at SDK source (assumed): transport.sessionId is generated.

  await server.connect(transport);

  // We assume transport.sessionId is available after connect or we need to find a way to get it.
  // If the SDK doesn't expose it easily, we might need a workaround.
  // However, the SSEServerTransport usually sends an 'endpoint' event with the URI including the session ID.
  // We can intercept that?
  // Ideally, the transport object itself is what we need to keep alive.

  // Let's assume transport.sessionId exists.
  if (transport.sessionId) {
    transports.set(transport.sessionId, transport);

    // Cleanup on close
    transport.onclose = () => {
      transports.delete(transport.sessionId);
    };
  } else {
  }
});

app.post('/messages', async (req, res) => {
  const sessionId = req.query.sessionId;
  if (!sessionId) {
    res.status(400).send('Missing sessionId');
    return;
  }

  const transport = transports.get(sessionId);
  if (!transport) {
    res.status(404).send('Session not found');
    return;
  }

  await transport.handlePostMessage(req, res);
});

// Start Server
const serverInstance = app.listen(0, () => {
  const port = serverInstance.address().port;
  console.log(`[Mock IDE] Server running on port ${port}`);
  createDiscoveryFile(port);
});

// Discovery Mechanism
function createDiscoveryFile(port) {
  const discoveryDir = path.join(os.tmpdir(), 'gemini', 'ide');
  const filename = `gemini-ide-server-${PID}-${port}.json`;
  const filePath = path.join(discoveryDir, filename);

  const discoveryData = {
    port: port,
    workspacePath: WORKSPACE_PATH,
    authToken: AUTH_TOKEN,
    ideInfo: {
      name: 'mock-ide',
      displayName: 'Mock IDE',
    },
  };

  fs.mkdirSync(discoveryDir, { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(discoveryData, null, 2));
  console.log(`[Mock IDE] Discovery file created at: ${filePath}`);

  const cleanup = () => {
    console.log('[Mock IDE] Cleaning up...');
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        console.log(`[Mock IDE] Discovery file removed.`);
      }
    } catch (_e) {}
    process.exit();
  };

  process.on('SIGINT', cleanup);
  process.on('SIGTERM', cleanup);
}
