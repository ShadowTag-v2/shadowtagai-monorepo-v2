import { promises as fs } from "node:fs";
import { glob } from "node:fs/promises";
import path from "node:path";

const cfg = JSON.parse(await fs.readFile("./ops/rollup.config.json", "utf8"));
const chunks = [];

async function pull(pattern) {
  for await (const f of glob(pattern)) {
    const t = await fs.readFile(f, "utf8");
    chunks.push(`\n---\n\n## Source: ${f}\n\n${t.trim()}\n`);
  }
}

for (const pattern of cfg.sources) await pull(pattern);

const header = `# Mega Roll-Up\n\n> Generated: ${new Date().toISOString()}\n\n`;
const body = chunks.join("\n");
await fs.writeFile(cfg.output, header + body);
console.log(`Wrote ${cfg.output} (${chunks.length} sections)`);
