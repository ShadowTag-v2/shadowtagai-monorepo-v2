import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { homedir } from "node:os";

const CLINE_CONFIG = resolve(homedir(), "Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json");
const ANTI_CONFIG = resolve(homedir(), ".gemini/antigravity/mcp_config.json");

async function sync() {
    console.log("⚡ [Bun Shell] Initiating Selective MCP Mirroring to Antigravity...");

    if (!existsSync(ANTI_CONFIG)) {
        console.error(`❌ Antigravity config not found at: ${ANTI_CONFIG}`);
        process.exit(1);
    }

    let clineData: any = { mcpServers: {} };
    if (existsSync(CLINE_CONFIG)) {
        clineData = JSON.parse(readFileSync(CLINE_CONFIG, "utf8"));
    }
    
    let antiData = JSON.parse(readFileSync(ANTI_CONFIG, "utf8"));
    if (!antiData.mcpServers) antiData.mcpServers = {};

    // Define the lightweight payload (Excluding GitHub to protect the 100-tool limit)
    const safeServers = ["anthropic-memory", "anthropic-fetch", "notebooklm-mcp"];

    let count = 0;
    for (const server of safeServers) {
        if (clineData.mcpServers[server]) {
            antiData.mcpServers[server] = clineData.mcpServers[server];
            console.log(`✅ Bridged: ${server} (Minimal Tool Footprint)`);
            count++;
        }
    }

    // Write back to Antigravity's physical config
    writeFileSync(ANTI_CONFIG, JSON.stringify(antiData, null, 2));
    
    console.log(`🎉 Selective Mirroring Complete. ${count} servers safely injected.`);
    console.log("⚠️ GitHub MCP intentionally omitted to protect Antigravity's 100-tool platform budget.");
}

await sync();
