/* eslint-env node */
// UphillSnowball Relay Node Gateway
// Facilitates low-latency event forwarding from clients to the core engine.

const http = require('node:http');

const PORT = process.env.RELAY_PORT || 3001;

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/relay') {
    let body = '';

    req.on('data', (chunk) => {
      body += chunk.toString();
    });

    req.on('end', () => {
      const { execFile } = require('node:child_process');
      const path = require('node:path');

      const VECTOR_RETRIEVAL_SCRIPT = path.join(__dirname, 'scripts', 'vector_retrieval.py');

      try {
        const payload = JSON.parse(body);
        console.log(`[Relay] Received payload from ${req.socket.remoteAddress}`);

        // Emulate forwarding to FastAPI backend / Sub-Routing
        if (payload.type === 'rag_query' && payload.query) {
          console.log(
            `[Relay] Triggering Vector Retrieval for query: "${payload.query.substring(0, 50)}..."`,
          );
          execFile(VECTOR_RETRIEVAL_SCRIPT, [payload.query], (error, stdout, stderr) => {
            if (error) {
              res.writeHead(500, { 'Content-Type': 'application/json' });
              return res.end(JSON.stringify({ error: 'Retrieval failed', details: stderr }));
            }
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(stdout);
          });
          return;
        }

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'relayed', queued: true }));
      } catch (_err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
      }
    });
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`[UphillSnowball Relay] Gateway active on port ${PORT}`);
});
