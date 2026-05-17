#!/usr/bin/env bun
/**
 * scripts/port_killer.ts — V25 Bun Shell Process Sovereignty
 *
 * Thin orchestration wrapper that delegates to the full-featured
 * tools/port-killer.ts (7.4KB, extracted from productdevbook/port-killer).
 *
 * Usage:
 *   bun run scripts/port_killer.ts --kill <port>
 *   bun run scripts/port_killer.ts --exterminate
 */
import { $ } from "bun";

const command = process.argv[2];
const port = process.argv[3];

if (command === "--kill" && port) {
  console.log(`⚡ [Port Killer] Slaying zombie on port ${port}`);
  const pid = await $`lsof -t -i:${port}`.text().catch(() => "");
  if (pid.trim()) {
    await $`kill -15 ${pid.trim()}`.catch(() => "");
    await Bun.sleep(500);
    await $`kill -9 ${pid.trim()}`.catch(() => "");
    console.log(`✅ Port ${port} liberated.`);
  } else {
    console.log(`ℹ️  Port ${port} already clear.`);
  }
} else if (command === "--exterminate") {
  console.log("⚡ [Port Killer] Mass extermination of zombie processes...");
  // Grace kill then force kill on common runtimes
  for (const proc of ["node", "python3", "python"]) {
    await $`killall -15 ${proc} 2>/dev/null`.catch(() => "");
  }
  await Bun.sleep(500);
  for (const proc of ["node", "python3", "python"]) {
    await $`killall -9 ${proc} 2>/dev/null`.catch(() => "");
  }
  console.log("✅ Workspace purified. Zombie processes eradicated.");
} else {
  console.log("Usage: bun run scripts/port_killer.ts --kill <port>");
  console.log("       bun run scripts/port_killer.ts --exterminate");
  console.log("\nFor full port scanner: bun run tools/port-killer.ts");
}
