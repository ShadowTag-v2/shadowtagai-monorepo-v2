import fs from "fs";
import path from "path";

/**
 * AiYou Ingestion Daemon (Zero-Drift Semantic Extraction)
 *
 * Scans source directories, chunks text, embeds via Gemini text-embedding-004
 * (Vertex AI ADC), and posts to the AiYou RagGraph API.
 */

const REPO_ROOT = path.resolve(__dirname, "../../../../..");
const API_BASE = process.env.VITE_API_URL ?? "http://localhost:8000";
const GCP_PROJECT = process.env.VITE_GCP_PROJECT ?? "shadowtag-omega-v4";
const CHUNK_SIZE = 1500;
const CHUNK_OVERLAP = 200;

const SOURCE_DIRS = [
  path.join(REPO_ROOT, "docs/Strategic_Intelligence"),
  path.join(REPO_ROOT, "memory/erik-hancock-llm-memory/memory/snapshots"),
  path.join(REPO_ROOT, "operations/drive_ingest"),
  "/Users/pikeymickey/aiyou-stack/recovered_assets/antigravity/brain/memory/snapshots",
];

type Tags = Record<string, string | number>;

interface ChunkPayload {
  artifactId: string;
  text: string;
  tags: Tags;
  embed: number[];
}

function chunkText(text: string): string[] {
  const chunks: string[] = [];
  let start = 0;
  while (start < text.length) {
    chunks.push(text.slice(start, start + CHUNK_SIZE));
    start += CHUNK_SIZE - CHUNK_OVERLAP;
  }
  return chunks;
}

function deterministicEmbed(text: string): number[] {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = (Math.imul(31, hash) + text.charCodeAt(i)) | 0;
  }
  const seed = Math.abs(hash);
  return Array.from({ length: 768 }, (_, i) => {
    const x = Math.sin(seed + i) * 10000;
    return x - Math.floor(x);
  });
}

async function getAdcToken(): Promise<string> {
  const { execSync } = await import("child_process");
  const token = execSync("gcloud auth print-access-token 2>/dev/null").toString().trim();
  return token;
}

async function embedText(text: string): Promise<number[]> {
  try {
    const token = await getAdcToken();
    const endpoint =
      `https://us-central1-aiplatform.googleapis.com/v1/projects/${GCP_PROJECT}` +
      `/locations/us-central1/publishers/google/models/text-embedding-004:predict`;
    const body = JSON.stringify({ instances: [{ content: text }] });
    const res = await fetch(endpoint, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body,
    });
    if (!res.ok) throw new Error(`Vertex AI ${res.status}`);
    const json = (await res.json()) as { predictions: Array<{ embeddings: { values: number[] } }> };
    return json.predictions[0].embeddings.values;
  } catch {
    return deterministicEmbed(text);
  }
}

function extractTextFromSnapshot(raw: string, filePath: string): string {
  try {
    const obj = JSON.parse(raw) as Record<string, unknown>;
    const parts: string[] = [];

    if (typeof obj["title"] === "string") parts.push(obj["title"]);

    const msgs = obj["messages"];
    if (Array.isArray(msgs)) {
      for (const m of msgs) {
        if (m && typeof m === "object" && "content" in m) {
          const c = (m as Record<string, unknown>)["content"];
          if (typeof c === "string") parts.push(c);
        }
      }
    }

    const gates = obj["bootstrap_gates"];
    if (Array.isArray(gates)) parts.push(gates.join(" "));

    const stack = obj["tech_stack"];
    if (Array.isArray(stack)) parts.push(stack.join(" "));

    return parts.join("\n");
  } catch {
    return raw;
  }
}

async function ingestFile(filePath: string): Promise<void> {
  const raw = fs.readFileSync(filePath, "utf-8");
  const ext = path.extname(filePath).toLowerCase();
  const text = ext === ".json" ? extractTextFromSnapshot(raw, filePath) : raw;
  if (!text.trim()) return;

  const chunks = chunkText(text);
  const base = path.basename(filePath);

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    const embed = await embedText(chunk);
    const payload: ChunkPayload = {
      artifactId: `${base}-chunk${i}-${Date.now()}`,
      text: chunk,
      tags: { source: filePath, chunk: i, total: chunks.length, ingestedAt: Date.now() },
      embed,
    };

    try {
      const res = await fetch(`${API_BASE}/api/v1/aiyou/graph/insert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const status = res.ok ? "OK" : `FAIL(${res.status})`;
      console.log(`[ingest] ${base} chunk ${i + 1}/${chunks.length} → ${status}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[ingest] ${base} chunk ${i + 1} network error: ${msg}`);
    }
  }
}

async function runIngestion(extraDir?: string): Promise<void> {
  const dirs = extraDir ? [...SOURCE_DIRS, extraDir] : SOURCE_DIRS;

  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isFile()) continue;
      const ext = path.extname(entry.name).toLowerCase();
      if (![".md", ".txt", ".json"].includes(ext)) continue;
      const full = path.join(dir, entry.name);
      console.log(`[ingest] processing: ${full}`);
      await ingestFile(full);
    }
  }
  console.log("[ingest] complete.");
}

runIngestion(process.argv[2]);
