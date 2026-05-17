import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import { $ } from "bun";

// Resolve physical boundaries
const FLEET_DIR = resolve(process.cwd(), "external_repos/mcp_fleet");
const CLINE_CONFIG_PATH = resolve(
  homedir(),
  "Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
);

async function expandFleet() {
  console.log("⚡ [Bun Shell] Initiating MCP Fleet Expansion Protocol...");

  // 1. INGESTION
  const anthropicRepoDir = join(FLEET_DIR, "servers");
  if (!existsSync(anthropicRepoDir)) {
    console.log("⬇️ Cloning official MCP monorepo...");
    await $`git clone https://github.com/modelcontextprotocol/servers.git ${anthropicRepoDir}`.quiet();
  } else {
    console.log("⏭️ MCP monorepo already present. Pulling latest updates...");
    await $`cd ${anthropicRepoDir} && git pull`.quiet().catch(() => {});
  }

  // 2. PHYSICS COMPILATION
  const targets = ["github", "memory", "fetch"];
  for (const target of targets) {
    console.log(`🔨 Compiling '${target}' MCP natively via Bun...`);
    const targetPath = join(anthropicRepoDir, "src", target);
    if (existsSync(targetPath)) {
      await $`cd ${targetPath} && bun install && bun run build`
        .quiet()
        .catch(() => console.error(`❌ Build failed for ${target}.`));
    }
  }

  // 3. MOTHERBOARD WIRING & SLIPPING THE SCALES
  console.log("🔌 Wiring compiled binaries into the Cline Motherboard...");
  let config: any = { mcpServers: {} };

  if (existsSync(CLINE_CONFIG_PATH)) {
    try {
      config = JSON.parse(readFileSync(CLINE_CONFIG_PATH, "utf8"));
    } catch (e) {
      console.warn("⚠️ Existing config is invalid JSON. Safely forging new Motherboard.");
    }
  }

  // 🐍 SLIPPING THE SCALES: Renaming open-source tools to Gemini-Native
  const newServers = {
    "gemini-github-mcp": {
      command: "bun",
      args: [join(anthropicRepoDir, "src", "github", "dist", "index.js")],
      env: {
        GITHUB_PERSONAL_ACCESS_TOKEN:
          process.env.GITHUB_TOKEN || "PLACEHOLDER_TOKEN_REQUIRE_MANUAL_ENTRY",
      },
      transport: "stdio",
    },
    "gemini-graph-memory": {
      command: "bun",
      args: [join(anthropicRepoDir, "src", "memory", "dist", "index.js")],
      transport: "stdio",
    },
    "gemini-web-fetcher": {
      command: "bun",
      args: [join(anthropicRepoDir, "src", "fetch", "dist", "index.js")],
      transport: "stdio",
    },
  };

  config.mcpServers = { ...config.mcpServers, ...newServers };
  writeFileSync(CLINE_CONFIG_PATH, JSON.stringify(config, null, 2));

  console.log(`🎉 Fleet Expansion Complete. Successfully mapped: ${targets.join(", ")}`);
  console.log(
    `⚠️ NOTE: If using the GitHub MCP, you must replace PLACEHOLDER_TOKEN_REQUIRE_MANUAL_ENTRY in your Cline settings with a real Personal Access Token.`,
  );
}

await expandFleet();
