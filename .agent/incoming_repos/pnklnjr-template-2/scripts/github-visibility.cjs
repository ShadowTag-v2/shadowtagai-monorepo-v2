#!/usr/bin/env node
const { execSync } = require('child_process')

function fail(msg){ console.error(`❌ ${msg}`); process.exit(2) }
function ok(msg){ console.log(`✅ ${msg}`) }

try {
  const remote = execSync('git config --get remote.origin.url', { stdio: ['ignore','pipe','pipe'] }).toString().trim()
  if(!remote) fail('GitHub not visible: no origin remote set.')
  try { execSync('git ls-remote -h origin HEAD', { stdio: 'ignore' }); ok(`GitHub visible: ${remote}`) }
  catch { fail(`GitHub not visible or auth blocked for: ${remote}`) }
} catch {
  fail('Git repository not initialized. Run: git init && git remote add origin <url>')
}

