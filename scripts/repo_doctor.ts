#!/usr/bin/env bun
/**
 * scripts/repo_doctor.ts — V25 Bun-Native Workspace Diagnostics
 *
 * Replaces repo_doctor.py with zero-Python diagnostics.
 * Checks: index lock, git status, stale branches, MCP config validity.
 *
 * Usage:
 *   bun run scripts/repo_doctor.ts
 */
import { $ } from "bun";

interface DiagnosticResult {
  check: string;
  status: "PASS" | "WARN" | "FAIL";
  detail: string;
}

const results: DiagnosticResult[] = [];

async function check(name: string, fn: () => Promise<string | null>): Promise<void> {
  try {
    const warning = await fn();
    if (warning) {
      results.push({ check: name, status: "WARN", detail: warning });
    } else {
      results.push({ check: name, status: "PASS", detail: "OK" });
    }
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    results.push({ check: name, status: "FAIL", detail: msg });
  }
}

console.log("🩺 V25 Repo Doctor — Diagnostic Scan Starting...\n");

await check("Index Lock", async () => {
  const exists = await Bun.file(".git/index.lock").exists();
  return exists ? "Stale index.lock detected! Remove before commit." : null;
});

await check("Working Tree", async () => {
  const status = await $`git status --porcelain`.text();
  return status.trim() ? `${status.trim().split("\n").length} modified files` : null;
});

await check("Branch Alignment", async () => {
  const branch = (await $`git branch --show-current`.text()).trim();
  return branch !== "main" ? `Not on main — currently on '${branch}'` : null;
});

await check("Stale Remote Branches", async () => {
  const remotes = await $`git branch -r --merged`.text();
  const stale = remotes
    .split("\n")
    .filter((b) => b.includes("origin/") && !b.includes("main") && !b.includes("HEAD"));
  return stale.length > 5 ? `${stale.length} merged remote branches could be pruned` : null;
});

await check("MCP Config", async () => {
  const configFile = Bun.file("antigravity-mcp-config.json");
  if (!(await configFile.exists())) return "Missing antigravity-mcp-config.json";
  const config = await configFile.json();
  const servers = Object.keys(config.mcpServers || config.servers || {});
  return servers.length < 3 ? `Only ${servers.length} MCP servers configured` : null;
});

await check("Node Modules", async () => {
  const exists = await Bun.file("node_modules/.package-lock.json").exists();
  return exists ? null : "node_modules may be stale — run bun install";
});

await check("AST-Grep Config", async () => {
  const exists = await Bun.file("sgconfig.yml").exists();
  return exists ? null : "Missing sgconfig.yml — ast-grep rules won't run";
});

// Report
console.log("─".repeat(60));
for (const r of results) {
  const icon = r.status === "PASS" ? "✅" : r.status === "WARN" ? "⚠️" : "❌";
  console.log(`${icon} [${r.check}] ${r.detail}`);
}
console.log("─".repeat(60));

const failures = results.filter((r) => r.status === "FAIL");
if (failures.length > 0) {
  console.log(`\n❌ ${failures.length} FAILURES detected. Address before sync.`);
  process.exit(1);
} else {
  console.log(`\n✅ Repo Doctor: ${results.length} checks passed. Workspace healthy.`);
}
