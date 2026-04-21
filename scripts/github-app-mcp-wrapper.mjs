#!/usr/bin/env node
/**
 * GitHub App MCP Wrapper — ShadowTag-v2 / Antigravity Manager
 *
 * Generates an Installation Access Token from the GitHub App PEM,
 * then spawns the official @modelcontextprotocol/server-github
 * with that token injected as GITHUB_PERSONAL_ACCESS_TOKEN.
 *
 * This replaces any PAT, OAuth, or `gh auth login` based auth
 * with strict headless App-based authentication.
 *
 * App ID: 3018200 | Client ID: Iv23ctYqrxPQIt2ir8gY
 * Installation ID: 114307210 (ShadowTag-v2)
 *
 * Env overrides:
 *   GITHUB_APP_ID, GITHUB_INSTALLATION_ID, GITHUB_PEM_PATH
 *
 * Usage:
 *   node scripts/github-app-mcp-wrapper.mjs          # spawns MCP server with App token
 *   node scripts/github-app-mcp-wrapper.mjs --token   # prints token only
 */

import { spawn, execSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { homedir, tmpdir } from "node:os";
import { createSign } from "node:crypto";

// ─── Constants ───────────────────────────────────────────────────────────────

const APP_ID = process.env.GITHUB_APP_ID || "3018200";
const INSTALLATION_ID = process.env.GITHUB_INSTALLATION_ID || "114307210";
const TOKEN_CACHE = join(tmpdir(), "gh_app_mcp_token.json");
const TOKEN_TTL_MS = 50 * 60 * 1000; // 50 minutes (tokens last 1hr, refresh early)

// ─── PEM Discovery (5-tier fallback, identical to auth_github_app.py) ────────

function findPem() {
  const candidates = [
    process.env.GITHUB_PEM_PATH,
    join(resolve(import.meta.dirname, ".."), "keys", "shadowtag-manager.pem"),
    join(homedir(), "Downloads", "antigravity-shadowtag-manager.2026-03-17.private-key.pem"),
    join(homedir(), ".ssh", "antigravity-shadowtag-manager.2026-03-17.private-key.pem"),
    process.env.SHADOWTAG_PEM,
  ].filter(Boolean);

  for (const p of candidates) {
    if (existsSync(p) && statSync(p).isFile()) {
      return readFileSync(p, "utf8");
    }
  }

  // Tier 0: GCP Secret Manager (production/CI)
  try {
    const gcloudPath = "/opt/homebrew/share/google-cloud-sdk/bin/gcloud";
    if (existsSync(gcloudPath)) {
      const result = execSync(
        `${gcloudPath} secrets versions access latest --secret=github-app-shadowtag-v2-pem --project=shadowtag-omega-v4`,
        { timeout: 10_000, encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }
      );
      if (result.trim()) return result;
    }
  } catch {
    // Secret Manager unavailable, continue to fallbacks
  }

  throw new Error(
    `PEM not found. Checked: GITHUB_PEM_PATH, keys/shadowtag-manager.pem, ~/Downloads, ~/.ssh, $SHADOWTAG_PEM, GCP Secret Manager`
  );
}

// ─── JWT Generation (RS256, no external deps) ───────────────────────────────

function base64url(buf) {
  return buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function generateJwt(pemContent) {
  const now = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", typ: "JWT" };
  const payload = { iat: now - 60, exp: now + 600, iss: APP_ID };

  const segments = [
    base64url(Buffer.from(JSON.stringify(header))),
    base64url(Buffer.from(JSON.stringify(payload))),
  ];

  const sign = createSign("RSA-SHA256");
  sign.update(segments.join("."));
  const signature = base64url(sign.sign(pemContent));

  return `${segments.join(".")}.${signature}`;
}

// ─── Installation Token Exchange ────────────────────────────────────────────

async function getInstallationToken(jwt) {
  const url = `https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${jwt}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`GitHub API ${resp.status}: ${body}`);
  }

  const data = await resp.json();
  return { token: data.token, expiresAt: data.expires_at };
}

// ─── Token Cache Layer ──────────────────────────────────────────────────────

function getCachedToken() {
  try {
    if (!existsSync(TOKEN_CACHE)) return null;
    const cache = JSON.parse(readFileSync(TOKEN_CACHE, "utf8"));
    const expiry = new Date(cache.expiresAt).getTime();
    if (expiry - Date.now() > 2 * 60 * 1000) {
      // 2min buffer
      return cache.token;
    }
  } catch {
    // Cache corrupted, regenerate
  }
  return null;
}

function cacheToken(token, expiresAt) {
  writeFileSync(TOKEN_CACHE, JSON.stringify({ token, expiresAt, generatedAt: new Date().toISOString() }));
}

// ─── Main Token Acquisition ─────────────────────────────────────────────────

async function acquireToken() {
  // Try cache first
  const cached = getCachedToken();
  if (cached) {
    process.stderr.write("[github-app-mcp] Using cached token\n");
    return cached;
  }

  process.stderr.write("[github-app-mcp] Generating fresh Installation Access Token...\n");
  const pem = findPem();
  const jwt = generateJwt(pem);
  const { token, expiresAt } = await getInstallationToken(jwt);
  cacheToken(token, expiresAt);
  process.stderr.write(`[github-app-mcp] Token acquired, expires ${expiresAt}\n`);
  return token;
}

// ─── MCP Server Spawn ───────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);

  // --token mode: just print the token and exit
  if (args.includes("--token")) {
    const token = await acquireToken();
    process.stdout.write(token);
    process.exit(0);
  }

  // --export mode: print shell export statements
  if (args.includes("--export")) {
    const token = await acquireToken();
    process.stdout.write(`export GITHUB_TOKEN=${token}\nexport GH_TOKEN=${token}\n`);
    process.exit(0);
  }

  // Default: spawn the official GitHub MCP server with the App token
  const token = await acquireToken();

  // Find the MCP server binary
  const mcpServerPaths = [
    join(homedir(), ".npm-global", "bin", "github-mcp-server"),
    join(homedir(), ".nvm", "versions", "node"),
  ];

  // Use npx to resolve the server
  const child = spawn(
    "npx",
    ["-y", "@modelcontextprotocol/server-github"],
    {
      env: {
        ...process.env,
        GITHUB_PERSONAL_ACCESS_TOKEN: token,
        // Prevent any PAT override
        GH_TOKEN: token,
        GITHUB_TOKEN: token,
      },
      stdio: ["pipe", "pipe", "pipe"],
    }
  );

  // Pipe stdin/stdout for MCP protocol, stderr for diagnostics
  process.stdin.pipe(child.stdin);
  child.stdout.pipe(process.stdout);
  child.stderr.pipe(process.stderr);

  child.on("error", (err) => {
    process.stderr.write(`[github-app-mcp] Server spawn error: ${err.message}\n`);
    process.exit(1);
  });

  child.on("exit", (code) => {
    process.stderr.write(`[github-app-mcp] Server exited with code ${code}\n`);
    process.exit(code || 0);
  });

  // Token refresh timer (refresh 10min before expiry)
  setInterval(async () => {
    try {
      process.stderr.write("[github-app-mcp] Refreshing token...\n");
      const newToken = await acquireToken();
      // Note: the running MCP server process uses the initial token.
      // For long-running sessions, a restart is needed.
      // We update the cache so the NEXT spawn gets a fresh token.
      process.stderr.write("[github-app-mcp] Token cache refreshed\n");
    } catch (err) {
      process.stderr.write(`[github-app-mcp] Token refresh failed: ${err.message}\n`);
    }
  }, TOKEN_TTL_MS);

  // Handle shutdown
  process.on("SIGINT", () => child.kill("SIGINT"));
  process.on("SIGTERM", () => child.kill("SIGTERM"));
}

main().catch((err) => {
  process.stderr.write(`[github-app-mcp] Fatal: ${err.message}\n`);
  process.exit(1);
});
