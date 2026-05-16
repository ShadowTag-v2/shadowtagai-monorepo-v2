import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { resolve } from 'node:path';

const ANTI_CONFIG = resolve(homedir(), '.gemini/antigravity/mcp_config.json');

async function forceInject() {
  console.log('⚡ [Bun Shell] Initiating Stateless MCP Injection...');

  if (!existsSync(ANTI_CONFIG)) {
    console.error(`❌ Antigravity config not found at: ${ANTI_CONFIG}`);
    process.exit(1);
  }

  const antiData = JSON.parse(readFileSync(ANTI_CONFIG, 'utf8'));
  if (!antiData.mcpServers) antiData.mcpServers = {};

  // 1. Inject Anthropic Memory (Knowledge Graph)
  antiData.mcpServers['anthropic-memory'] = {
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-memory'],
    transport: 'stdio',
  };

  // 2. Inject Anthropic Fetch (Web Scraper)
  antiData.mcpServers['anthropic-fetch'] = {
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-fetch'],
    transport: 'stdio',
  };

  writeFileSync(ANTI_CONFIG, JSON.stringify(antiData, null, 2));

  console.log('✅ Successfully injected @modelcontextprotocol/server-memory');
  console.log('✅ Successfully injected @modelcontextprotocol/server-fetch');
  console.log('🎉 Antigravity is now fully armed with Web Fetching and Persistent Memory.');
}

await forceInject();
