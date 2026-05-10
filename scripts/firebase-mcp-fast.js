#!/usr/bin/env node
// firebase-mcp-fast.js — Direct MCP entrypoint bypassing full Firebase CLI bootstrap.
// Eliminates ~3-5s CLI framework initialization that causes context canceled timeouts.

const { mcp } = require('firebase-tools/lib/bin/mcp');
mcp().catch((err) => {
  process.stderr.write(`Firebase MCP fatal: ${err.message}\n`);
  process.exit(1);
});
