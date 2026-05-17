import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, resolve } from "node:path";

const CLINE_CONFIG = resolve(
  homedir(),
  "Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json",
);
const ANTI_CONFIG = resolve(homedir(), ".gemini/antigravity/mcp_config.json");

async function sync() {
  console.log("⚡ Initiating Selective MCP Mirroring to Antigravity...");

  // Ensure Antigravity directory exists
  if (!existsSync(dirname(ANTI_CONFIG))) {
    mkdirSync(dirname(ANTI_CONFIG), { recursive: true });
  }

  // Ensure Antigravity JSON exists
  if (!existsSync(ANTI_CONFIG)) {
    writeFileSync(ANTI_CONFIG, JSON.stringify({ mcpServers: {} }, null, 2));
  }

  let clineData: any = { mcpServers: {} };
  if (existsSync(CLINE_CONFIG)) clineData = JSON.parse(readFileSync(CLINE_CONFIG, "utf8"));

  const antiData = JSON.parse(readFileSync(ANTI_CONFIG, "utf8"));
  if (!antiData.mcpServers) antiData.mcpServers = {};

  // Bridging ONLY the lightweight, Gemini-aliased tools
  const safeServers = ["gemini-graph-memory", "gemini-web-fetcher", "notebooklm-mcp"];

  let count = 0;
  for (const server of safeServers) {
    if (clineData.mcpServers[server]) {
      antiData.mcpServers[server] = clineData.mcpServers[server];
      console.log(`✅ Bridged: ${server} (Minimal Tool Footprint)`);
      count++;
    } else {
      console.warn(`⚠️ Skipping ${server}: Not found in Cline config.`);
    }
  }

  writeFileSync(ANTI_CONFIG, JSON.stringify(antiData, null, 2));
  console.log(
    `🎉 Selective Mirroring Complete. ${count} servers safely injected into Antigravity.`,
  );
  console.log(
    "⚠️ gemini-github-mcp intentionally omitted to protect Antigravity's 100-tool platform budget.",
  );
}

await sync();
