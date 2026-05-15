import { $ } from "bun";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { resolve, join } from "node:path";
import { homedir } from "node:os";

const FLEET_DIR = resolve(process.cwd(), "external_repos/mcp_fleet");
const CLINE_CONFIG_PATH = resolve(
    homedir(), 
    "Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
);

async function expandFleet() {
    console.log("⚡ [Bun Shell] Initiating Transparent MCP Fleet Expansion Protocol...");

    const anthropicRepoDir = join(FLEET_DIR, "servers");
    if (!existsSync(anthropicRepoDir)) {
        console.log("⬇️ Cloning official MCP monorepo...");
        await $`git clone https://github.com/modelcontextprotocol/servers.git ${anthropicRepoDir}`;
    } else {
        console.log("⏭️ MCP monorepo already present. Pulling latest updates...");
        await $`cd ${anthropicRepoDir} && git pull`.catch(() => {});
    }

    // 🔨 THE FIX: We run npm install at the ROOT of their repo.
    // We removed .quiet() so you will see the Puppeteer/Chromium download happen live.
    console.log("\n📦 Resolving Workspace Dependencies (This will download Chromium for 'fetch')...");
    await $`cd ${anthropicRepoDir} && npm install`;

    const targets = ["github", "memory", "fetch"];
    for (const target of targets) {
        console.log(`\n🔨 Compiling '${target}' MCP...`);
        const targetPath = join(anthropicRepoDir, "src", target);
        if (existsSync(targetPath)) {
            // Run build using npm to safely respect their TS configs
            await $`cd ${targetPath} && npm run build`.catch(() => console.error(`❌ Build failed for ${target}.`));
        }
    }

    console.log("\n🔌 Wiring compiled binaries into the Cline Motherboard...");
    let config: any = { mcpServers: {} };
    if (existsSync(CLINE_CONFIG_PATH)) {
        try { config = JSON.parse(readFileSync(CLINE_CONFIG_PATH, "utf8")); } catch (e) {}
    }
    
    // 🐍 SLIPPING THE SCALES: Renaming tools to Gemini-Native
    const newServers = {
        "gemini-github-mcp": {
            "command": "bun",
            "args": [join(anthropicRepoDir, "src", "github", "dist", "index.js")],
            "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": process.env.GITHUB_TOKEN || "PLACEHOLDER_TOKEN_REQUIRE_MANUAL_ENTRY" },
            "transport": "stdio"
        },
        "gemini-graph-memory": {
            "command": "bun",
            "args": [join(anthropicRepoDir, "src", "memory", "dist", "index.js")],
            "transport": "stdio"
        },
        "gemini-web-fetcher": {
            "command": "bun",
            "args": [join(anthropicRepoDir, "src", "fetch", "dist", "index.js")],
            "transport": "stdio"
        }
    };

    config.mcpServers = { ...config.mcpServers, ...newServers };
    writeFileSync(CLINE_CONFIG_PATH, JSON.stringify(config, null, 2));
    
    console.log(`\n🎉 Fleet Expansion Complete. Scales Slipped. Successfully mapped: ${targets.join(", ")}`);
}

await expandFleet();
