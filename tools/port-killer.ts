#!/usr/bin/env bun
/**
 * port-killer.ts — Sovereign Process Sovereignty Tool
 *
 * Bun-native port killer extracted from productdevbook/port-killer's PortScanner.swift.
 * Algorithm: lsof TCP scan → PID extraction → SIGTERM (grace 500ms) → SIGKILL
 *
 * Usage:
 *   bun tools/port-killer.ts                    # List all listening ports
 *   bun tools/port-killer.ts 3000 8080 5173     # Kill specific ports
 *   bun tools/port-killer.ts --all              # Kill ALL non-system ports
 *   bun tools/port-killer.ts --force 3000       # Skip SIGTERM, go straight to SIGKILL
 *
 * @see https://github.com/productdevbook/port-killer
 * @license MIT
 */

interface PortInfo {
  port: number;
  pid: number;
  processName: string;
  address: string;
  user: string;
  command: string;
  fd: string;
}

// System ports that should NEVER be killed
const PROTECTED_PORTS = new Set([22, 53, 80, 443, 631]);
const PROTECTED_PROCESSES = new Set([
  "launchd",
  "loginwindow",
  "kernel_task",
  "sshd",
  "ControlCe", // macOS Control Center
  "mDNSResponder",
  "systemstats",
  "fseventsd",
]);

/**
 * Scans all listening TCP ports using lsof.
 * Mirrors PortScanner.swift scanPorts() — uses `lsof -iTCP -sTCP:LISTEN -P -n +c 0`
 */
async function scanPorts(): Promise<PortInfo[]> {
  const proc = Bun.spawn(
    ["/usr/sbin/lsof", "-iTCP", "-sTCP:LISTEN", "-P", "-n", "+c", "0"],
    { stdout: "pipe", stderr: "ignore" },
  );
  const output = await new Response(proc.stdout).text();
  await proc.exited;

  if (!output.trim()) return [];

  return parseLsofOutput(output);
}

/**
 * Parses lsof output into structured PortInfo objects.
 * Mirrors PortScanner.swift parseLsofOutput()
 */
function parseLsofOutput(output: string): PortInfo[] {
  const lines = output.split("\n");
  const ports: PortInfo[] = [];
  const seen = new Set<string>();

  // Skip header line
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;

    const components = line.split(/\s+/);
    if (components.length < 9) continue;

    const processName = decodeLsofEscapes(components[0]);
    const pid = parseInt(components[1], 10);
    if (isNaN(pid)) continue;

    const user = components[2];
    const fd = components[3];

    // Find address:port — search backwards for component with ":" that isn't device ID
    let addressPart = "";
    for (let j = components.length - 1; j >= 8; j--) {
      const comp = components[j];
      if (
        comp.includes(":") &&
        !comp.startsWith("0x") &&
        !comp.startsWith("0t")
      ) {
        addressPart = comp;
        break;
      }
    }

    if (!addressPart) continue;

    const parsed = parseAddress(addressPart);
    if (!parsed) continue;

    const key = `${parsed.port}-${pid}`;
    if (seen.has(key)) continue;
    seen.add(key);

    ports.push({
      port: parsed.port,
      pid,
      processName,
      address: parsed.address,
      user,
      command: processName, // We skip ps/sysctl for CLI simplicity
      fd,
    });
  }

  return ports.sort((a, b) => a.port - b.port);
}

/**
 * Parses address:port string. Handles IPv4 and IPv6 formats.
 * Mirrors PortScanner.swift parseAddress()
 */
function parseAddress(
  addr: string,
): { port: number; address: string } | null {
  if (addr.startsWith("[")) {
    // IPv6: [::1]:3000
    const bracketEnd = addr.indexOf("]");
    if (bracketEnd === -1) return null;
    const colonAfter = addr.indexOf(":", bracketEnd);
    if (colonAfter === -1) return null;
    const port = parseInt(addr.slice(colonAfter + 1), 10);
    if (isNaN(port)) return null;
    return { port, address: addr.slice(0, bracketEnd + 1) };
  }

  // IPv4: 127.0.0.1:3000 or *:8080
  const lastColon = addr.lastIndexOf(":");
  if (lastColon === -1) return null;
  const port = parseInt(addr.slice(lastColon + 1), 10);
  if (isNaN(port)) return null;
  const address = addr.slice(0, lastColon) || "*";
  return { port, address };
}

/**
 * Decodes lsof hex escape sequences (\xHH).
 * Mirrors PortScanner.swift decodeLsofEscapes()
 */
function decodeLsofEscapes(input: string): string {
  return input.replace(/\\x([0-9a-fA-F]{2})/g, (_match, hex) =>
    String.fromCharCode(parseInt(hex, 16)),
  );
}

/**
 * Kills a process with SIGTERM→SIGKILL cascade.
 * Mirrors PortScanner.swift killProcessGracefully()
 */
async function killProcessGracefully(
  pid: number,
  force: boolean = false,
): Promise<boolean> {
  try {
    if (force) {
      process.kill(pid, "SIGKILL");
      return true;
    }

    // Stage 1: SIGTERM (graceful)
    process.kill(pid, "SIGTERM");

    // Stage 2: Wait 500ms grace period
    await Bun.sleep(500);

    // Stage 3: SIGKILL (force)
    try {
      process.kill(pid, "SIGKILL");
    } catch {
      // Process already exited from SIGTERM — success
    }
    return true;
  } catch {
    return false;
  }
}

/**
 * Checks if a port/process is protected from killing.
 */
function isProtected(info: PortInfo): boolean {
  return (
    PROTECTED_PORTS.has(info.port) ||
    PROTECTED_PROCESSES.has(info.processName) ||
    info.pid <= 1
  );
}

// ─── CLI Entry Point ─────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const forceMode = args.includes("--force");
  const listOnly = args.length === 0;
  const killAll = args.includes("--all");
  const targetPorts = args
    .filter((a) => !a.startsWith("--"))
    .map((a) => parseInt(a, 10))
    .filter((n) => !isNaN(n));

  console.log("⚡ Port-Killer v1.0.0 (Bun-native, from productdevbook/port-killer)");
  console.log("─".repeat(72));

  const ports = await scanPorts();

  if (ports.length === 0) {
    console.log("✅ No listening TCP ports found. System is clean.");
    return;
  }

  // Display port table
  console.log(
    `\n${"PORT".padEnd(8)}${"PID".padEnd(10)}${"PROCESS".padEnd(25)}${"ADDRESS".padEnd(20)}USER`,
  );
  console.log("─".repeat(72));

  for (const p of ports) {
    const protected_ = isProtected(p);
    const marker = protected_ ? "🔒" : "  ";
    console.log(
      `${marker}${String(p.port).padEnd(6)}${String(p.pid).padEnd(10)}${p.processName.padEnd(25)}${p.address.padEnd(20)}${p.user}`,
    );
  }

  if (listOnly) {
    console.log(`\n📊 ${ports.length} listening port(s) found.`);
    console.log("   Use: bun tools/port-killer.ts <port> [port...] to kill.");
    return;
  }

  // Determine which ports to kill
  const toKill = ports.filter((p) => {
    if (isProtected(p)) return false;
    if (killAll) return true;
    return targetPorts.includes(p.port);
  });

  if (toKill.length === 0) {
    console.log("\n⚠️  No killable ports matched your criteria.");
    return;
  }

  console.log(
    `\n🔫 Killing ${toKill.length} process(es)${forceMode ? " (FORCE MODE)" : ""}...`,
  );

  let killed = 0;
  let failed = 0;

  for (const p of toKill) {
    const ok = await killProcessGracefully(p.pid, forceMode);
    if (ok) {
      console.log(
        `   ✅ Killed PID ${p.pid} (${p.processName}) on port ${p.port}`,
      );
      killed++;
    } else {
      console.log(
        `   ❌ Failed to kill PID ${p.pid} (${p.processName}) on port ${p.port}`,
      );
      failed++;
    }
  }

  console.log(`\n📊 Results: ${killed} killed, ${failed} failed.`);
}

main().catch(console.error);
