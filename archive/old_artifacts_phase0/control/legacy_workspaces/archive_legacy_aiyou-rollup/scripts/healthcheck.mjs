#!/usr/bin/env node
import fs from 'node:fs';
import https from 'node:https';

function request(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, { method: 'GET', headers }, (res) => {
      const chunks = [];
      res.on('data', (d) => chunks.push(d));
      res.on('end', () => resolve({ status: res.statusCode, body: Buffer.concat(chunks).toString('utf8') }));
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  const tokenPresent = Boolean(process.env.GITHUB_TOKEN || process.env.GH_TOKEN);
  let visible = false;
  let status = 0;
  try {
    const headers = tokenPresent ? { 'Authorization': `Bearer ${process.env.GITHUB_TOKEN || process.env.GH_TOKEN}`, 'User-Agent': 'bourne-healthcheck' } : { 'User-Agent': 'bourne-healthcheck' };
    const res = await request('https://api.github.com/rate_limit', headers);
    status = res.status || 0;
    visible = status >= 200 && status < 400;
  } catch (e) {
    visible = false;
  }

  const out = {
    githubVisible: visible,
    statusCode: status,
    tokenPresent,
    guidance: visible ? 'OK' : 'Set PAT/SSO for GitHub (GITHUB_TOKEN) and re-run.'
  };
  fs.writeFileSync('healthcheck.json', JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out));
  if (!visible) {
    process.exitCode = 1;
  }
}

main();
