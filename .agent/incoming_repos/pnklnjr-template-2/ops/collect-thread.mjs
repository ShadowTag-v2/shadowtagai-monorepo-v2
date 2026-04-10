import { promises as fs } from "node:fs";
import { glob } from "node:fs/promises";

const out = { items: [] };
for await (const p of glob("docs/thread/**/*.md")) {
  const text = await fs.readFile(p, "utf8");
  out.items.push({ path: p, text });
}
await fs.mkdir("build", { recursive: true });
await fs.writeFile("build/thread.json", JSON.stringify(out, null, 2));
console.log(`Collected ${out.items.length} thread files → build/thread.json`);

