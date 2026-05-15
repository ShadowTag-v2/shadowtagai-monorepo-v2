/**
 * Simple HTTP server with health endpoint
 * This is a minimal example - extend as needed for your application
 */

const http = require('http');

const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '0.0.0.0';

// Store startup time for uptime calculation
const startTime = Date.now();

// Request handler
const requestHandler = (req, res) => {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle OPTIONS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Health check endpoint
  if (req.url === '/health' || req.url === '/health/') {
    const health = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: (Date.now() - startTime) / 1000,
      environment: process.env.NODE_ENV || 'development',
      version: require('./package.json').version,
    };

    res.setHeader('Content-Type', 'application/json');
    res.writeHead(200);
    res.end(JSON.stringify(health, null, 2));
    return;
  }

  // Root endpoint
  if (req.url === '/' || req.url === '') {
    const welcome = {
      message: 'Welcome to shadowtag_v4-fastapi-services',
      version: require('./package.json').version,
      endpoints: {
        health: '/health',
        root: '/',
      },
      documentation: '/deployment/README.md',
    };

    res.setHeader('Content-Type', 'application/json');
    res.writeHead(200);
    res.end(JSON.stringify(welcome, null, 2));
    return;
  }

  // 404 for unknown routes
  res.setHeader('Content-Type', 'application/json');
  res.writeHead(404);
  res.end(
    JSON.stringify({
      error: 'Not Found',
      path: req.url,
    }),
  );
};

// Create server
const server = http.createServer(requestHandler);

// Error handling
server.on('error', (error) => {
  console.error('Server error:', error);
  process.exit(1);
});

// Graceful shutdown
const shutdown = () => {
  console.log('\nShutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error('Forced shutdown');
    process.exit(1);
  }, 10000);
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Start server
server.listen(PORT, HOST, () => {
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🚀 Server running
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Environment: ${process.env.NODE_ENV || 'development'}
  Host:        ${HOST}
  Port:        ${PORT}
  URL:         http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}
  Health:      http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  `);
});
