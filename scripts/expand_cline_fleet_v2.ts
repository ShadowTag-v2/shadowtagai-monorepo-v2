import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, resolve } from 'node:path';

const CLINE_CONFIG_PATH = resolve(
  homedir(),
  'Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json',
);

const ANTHROPIC_REPO = resolve(homedir(), 'external_repos/mcp_fleet/servers');

async function expandClineFleet() {
  console.log('⚡ [Bun Shell] Expanding Cline Heavy Cruiser Fleet (Servers 6–19)...\n');

  // Read existing Cline config
  let config: any = { mcpServers: {} };
  if (existsSync(CLINE_CONFIG_PATH)) {
    try {
      config = JSON.parse(readFileSync(CLINE_CONFIG_PATH, 'utf8'));
    } catch {
      console.warn('⚠️ Existing Cline config invalid. Forging new one.');
    }
  }
  if (!config.mcpServers) config.mcpServers = {};

  // ──────────────────────────────────────────────
  // NPM-based servers (stateless via npx/uvx)
  // ──────────────────────────────────────────────

  // #11 — anthropic-memory (Knowledge Graph)
  config.mcpServers['anthropic-memory'] = {
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-memory'],
    transport: 'stdio',
  };
  console.log('✅ #11 anthropic-memory — @modelcontextprotocol/server-memory');

  // #18 — notebooklm-mcp (Epistemic RAG)
  config.mcpServers['notebooklm-mcp'] = {
    command: 'uvx',
    args: ['--from', 'notebooklm-mcp-cli', 'notebooklm-mcp'],
    transport: 'stdio',
  };
  console.log('✅ #18 notebooklm-mcp — notebooklm-mcp-cli (uvx)');

  // #13 — stripe-mcp
  config.mcpServers['stripe-mcp'] = {
    command: 'npx',
    args: ['-y', '@stripe/mcp'],
    transport: 'stdio',
  };
  console.log('✅ #13 stripe-mcp — @stripe/mcp');

  // #12 — storage (Google Cloud Storage)
  config.mcpServers['storage'] = {
    command: 'npx',
    args: ['-y', '@google-cloud/storage-mcp'],
    transport: 'stdio',
  };
  console.log('✅ #12 storage — @google-cloud/storage-mcp');

  // ──────────────────────────────────────────────
  // Compiled from Anthropic monorepo (local dist/)
  // ──────────────────────────────────────────────

  // Anthropic GitHub MCP — heavy (15+ tools), Cline only
  const githubDist = join(ANTHROPIC_REPO, 'src', 'github', 'dist', 'index.js');
  if (existsSync(githubDist)) {
    config.mcpServers['anthropic-github'] = {
      command: 'bun',
      args: [githubDist],
      env: {
        GITHUB_PERSONAL_ACCESS_TOKEN:
          process.env.GITHUB_TOKEN || 'PLACEHOLDER_REQUIRE_MANUAL_ENTRY',
      },
      transport: 'stdio',
    };
    console.log('✅ anthropic-github — compiled from monorepo');
  } else {
    console.warn(
      "⚠️ anthropic-github dist not found — run 'bun install && bun run build' in src/github/",
    );
  }

  // Anthropic Fetch MCP — web scraper
  const fetchDist = join(ANTHROPIC_REPO, 'src', 'fetch', 'dist', 'index.js');
  if (existsSync(fetchDist)) {
    config.mcpServers['anthropic-fetch'] = {
      command: 'bun',
      args: [fetchDist],
      transport: 'stdio',
    };
    console.log('✅ anthropic-fetch — compiled from monorepo');
  } else {
    console.warn(
      "⚠️ anthropic-fetch dist not found — run 'bun install && bun run build' in src/fetch/",
    );
  }

  // ──────────────────────────────────────────────
  // Servers already present (preserve, don't overwrite)
  // ──────────────────────────────────────────────
  const preserved = ['cloud-run', 'gcloud', 'observability'].filter((s) => s in config.mcpServers);
  if (preserved.length > 0) {
    console.log(`\n⏭️ Preserved existing: ${preserved.join(', ')}`);
  }

  // ──────────────────────────────────────────────
  // Skipped servers (require local source or don't exist)
  // ──────────────────────────────────────────────
  console.log('\n📋 Skipped (manual setup required):');
  console.log('   #6  jules-mcp-server — Local Python module (needs source)');
  console.log('   #7  stitch-mcp-server — Merged into StitchMCP (no-op)');
  console.log('   #8  jules-fleet — Local build (needs source)');
  console.log('   #9  gcloud-mcp — Unified under mcp-toolbox Go binary');
  console.log('   #10 observability — Unified under mcp-toolbox Go binary');
  console.log('   #14 semantic-scalpel — Local ast-grep-mcp (needs source)');
  console.log('   #15 workspace-intake — Local Bun handler (needs source)');
  console.log('   #16 dart-compiler — Does NOT exist as npm package');
  console.log('   #17 autonomic-insights — Unified under mcp-toolbox Go binary');
  console.log('   #19 pomelli-swarm — Local flpomp-team (needs source)');

  // Write the merged config
  writeFileSync(CLINE_CONFIG_PATH, JSON.stringify(config, null, 2));

  const total = Object.keys(config.mcpServers).length;
  console.log(`\n🎉 Cline Fleet Expansion Complete. Total servers: ${total}`);
}

await expandClineFleet();
