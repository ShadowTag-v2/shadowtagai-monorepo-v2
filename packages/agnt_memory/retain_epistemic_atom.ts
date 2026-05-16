import { randomUUID } from "node:crypto";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const MEMORY_DIR = ".agents/memory_kernel";
if (!existsSync(MEMORY_DIR)) mkdirSync(MEMORY_DIR, { recursive: true });

export async function retainEpistemicAtom(
  atomType: string,
  confidence: number,
  ttlDays: number,
  content: string,
) {
  const id = randomUUID().split("-")[0];
  const timestamp = new Date().toISOString();
  const expiry =
    ttlDays === 0 ? "PERMANENT" : new Date(Date.now() + ttlDays * 86400000).toISOString();

  // Construct the Typed Knowledge Atom with YAML frontmatter
  const payload = `---
id: ${id}
atom_type: ${atomType}
confidence: ${confidence.toFixed(1)}
created_at: ${timestamp}
expires_at: ${expiry}
---
# Epistemic Content
${content}
`;

  const filename = join(MEMORY_DIR, `${atomType}_${id}.md`);
  writeFileSync(filename, payload);

  console.log(`🧠 [Memory Kernel] Epistemic Atom (${atomType}) crystallized to ${filename}`);
  return JSON.stringify({ status: "success", id, file: filename });
}

// Native execution interface for Antigravity's tool engine
if (import.meta.main) {
  const args = process.argv.slice(2);
  if (args.length >= 4) {
    retainEpistemicAtom(args[0], parseFloat(args[1]), parseInt(args[2], 10), args[3]);
  } else {
    console.error("❌ Usage: bun run retain_epistemic_atom.ts <type> <confidence> <ttl> <content>");
    process.exit(1);
  }
}
