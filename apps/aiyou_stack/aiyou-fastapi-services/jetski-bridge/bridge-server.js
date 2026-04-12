// bridge-server.js
// Dependencies: npm install fastify ws
const fastify = require("fastify")({ logger: true });
const WebSocket = require("ws");

// 1. WEBSOCKET SERVER (Port 8081)
// The extension connects here and waits for instructions.
const wss = new WebSocket.Server({ port: 8081 });
let activeExtensionSocket = null;

wss.on("connection", (ws) => {
  console.log("Extension connected via WebSocket");
  activeExtensionSocket = ws;

  // MV3 Keep-Alive: Ping every 20s to prevent Service Worker sleep
  const keepAlive = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) ws.ping();
  }, 20000);

  ws.on("close", () => {
    console.log("Extension disconnected");
    activeExtensionSocket = null;
    clearInterval(keepAlive);
  });

  // Handle responses from the extension
  ws.on("message", (msg) => {
    try {
      const data = JSON.parse(msg);
      console.log(`Result for ${data.id}:`, data.result);
    } catch (e) {
      console.error("Failed to parse message from extension:", msg);
    }
  });
});

// 2. HTTP CONTROL ENDPOINT (Port 8080)
// Your Agent/Script hits this endpoint to drive the browser.
fastify.post("/control", async (request, reply) => {
  if (!activeExtensionSocket) {
    return reply.status(503).send({ error: "Browser extension not connected" });
  }

  const commandId = Date.now().toString();
  const command = {
    id: commandId,
    action: request.body.action, // e.g., "navigate", "click", "extract"
    payload: request.body.payload,
  };

  // Send command to Extension via WebSocket
  activeExtensionSocket.send(JSON.stringify(command));

  return { status: "command_sent", commandId };
});

// Start the HTTP Bridge
const start = async () => {
  try {
    // Listen on 0.0.0.0 to be accessible inside the container network
    // Use PORT env var if available (Cloud Run default), otherwise 8080
    const port = process.env.PORT || 8080;
    await fastify.listen({ port: port, host: "0.0.0.0" });
    console.log(`Bridge Bridge running on HTTP :${port} and WS :8081`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};
start();
