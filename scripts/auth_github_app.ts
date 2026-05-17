/**
 * GitHub App Authentication — V25 Pinnacle (Bun-native)
 * Replaces Python auth_github_app.py with pure TypeScript.
 * Uses the 5-tier PEM fallback chain per github_doctrine.
 */

import { $ } from "bun";
import { existsSync, readFileSync } from "fs";
import * as jwt from "jsonwebtoken";

const APP_ID = process.env.GITHUB_APP_ID || "3018200";
const REPO = "ShadowTag-v2/Monorepo-Uphillsnowball";

/**
 * 5-tier PEM fallback chain per AGENTS.md github_doctrine.
 */
function resolvePemPath(): string {
  const candidates = [
    process.env.SHADOWTAG_PEM,
    "/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem",
    `${process.env.HOME}/.ssh/antigravity-shadowtag-manager.pem`,
  ].filter(Boolean) as string[];

  for (const p of candidates) {
    if (existsSync(p)) return p;
  }
  throw new Error("❌ No GitHub App PEM found in 5-tier fallback chain.");
}

/**
 * Generate a JWT for the GitHub App.
 */
function generateAppJwt(pem: string): string {
  const now = Math.floor(Date.now() / 1000);
  return jwt.sign({ iat: now - 60, exp: now + 10 * 60, iss: APP_ID }, pem, { algorithm: "RS256" });
}

/**
 * Get an installation access token from the JWT.
 */
async function getInstallationToken(appJwt: string): Promise<string> {
  const installRes = await fetch("https://api.github.com/app/installations", {
    headers: {
      Authorization: `Bearer ${appJwt}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!installRes.ok) throw new Error(`Failed to list installations: ${installRes.status}`);

  const installations = await installRes.json();
  if (!installations.length) throw new Error("No installations found for GitHub App.");

  const accessUrl = installations[0].access_tokens_url;
  const accessRes = await fetch(accessUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${appJwt}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!accessRes.ok) throw new Error(`Failed to create access token: ${accessRes.status}`);

  const { token } = await accessRes.json();
  return token;
}

/**
 * Push to Branch-Zero (main) via GitHub App installation token.
 */
async function authenticateAndPush() {
  console.log("🔐 V25 GitHub App Auth — Bun-native");

  const pemPath = resolvePemPath();
  console.log(`  PEM: ${pemPath}`);

  const pem = readFileSync(pemPath, "utf8");
  const appJwt = generateAppJwt(pem);
  const token = await getInstallationToken(appJwt);

  console.log("  ✅ Installation token acquired.");

  // Set GIT_ASKPASS to inject the token without leaking to logs
  const askpassScript = "/tmp/git_askpass_v25.sh";
  await Bun.write(askpassScript, `#!/bin/bash\necho "${token}"`);
  await $`chmod +x ${askpassScript}`;

  const result =
    await $`GIT_ASKPASS=${askpassScript} git push https://x-access-token:@github.com/${REPO}.git HEAD:main`.nothrow();

  if (result.exitCode === 0) {
    console.log("  ✅ Pushed to Branch-Zero via GitHub App Auth.");
  } else {
    console.error(`  ❌ Push failed (exit ${result.exitCode})`);
    process.exit(1);
  }
}

// CLI entry
if (process.argv.includes("--push")) {
  authenticateAndPush().catch((err) => {
    console.error(err);
    process.exit(1);
  });
} else {
  console.log("Usage: bun run scripts/auth_github_app.ts --push");
}
