/* eslint-env node */
// UphillSnowball Relay Node Gateway
// Facilitates low-latency event forwarding from clients to the core engine.

const http = require("http");

const PORT = process.env.RELAY_PORT || 3001;

const server = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/relay") {
    let body = "";

    req.on("data", (chunk) => {
      body += chunk.toString();
    });

    req.on("end", () => {
      try {
        const payload = JSON.parse(body);
        console.log(`[Relay] Received payload from ${req.socket.remoteAddress}`);

        // Emulate forwarding to FastAPI backend

        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ status: "relayed", queued: true }));
      } catch (err) {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid JSON payload" }));
      }
    });
  } else {
    res.writeHead(404, { "Content-Type": "text/plain" });
    res.end("Not Found");
  }
});

server.listen(PORT, () => {
  console.log(`[UphillSnowball Relay] Gateway active on port ${PORT}`);
});
