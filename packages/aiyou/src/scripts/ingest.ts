import fs from "fs";
import path from "path";

/**
 * ShadowTag-v2 Ingestion Daemon — Gemini-Primary (Zero-Drift Semantic Extraction)
 *
 * Embeds via Gemini text-embedding-004 (Generative Language API — API key auth).
 * Optionally extracts semantic structure via GEMINI_GEN_MODEL (default: gemini-2.0-pro).
 * No Vertex AI ADC required. No deterministic fallback — fails loudly on missing key.
 *
 * Provider matrix:
 *   Embed  : Gemini text-embedding-004  (GEMINI_API_KEY)
 *   Extract: Gemini GEMINI_GEN_MODEL    (GEMINI_API_KEY)
 *   Future : OPENAI_API_KEY → text-embedding-3-large / gpt-4o
 *            CLAUDE_API_KEY → claude-sonnet-4-6 (via Anthropic SDK)
 */

const REPO_ROOT = path.resolve(__dirname, "../../../../..");
const API_BASE = process.env.VITE_API_URL ?? "http://localhost:8000";
const GEMINI_API_KEY = process.env.GEMINI_API_KEY ?? "";
const GEMINI_GEN_MODEL = process.env.GEMINI_GEN_MODEL ?? "gemini-3.1-pro";
const GEMINI_EMBED_MODEL = "text-embedding-004";
const CHUNK_SIZE = 1500;
const CHUNK_OVERLAP = 200;
const ENABLE_EXTRACTION = process.env.ShadowTag-v2_EXTRACT === "1";

const SOURCE_DIRS = [
  path.join(REPO_ROOT, "docs/Strategic_Intelligence"),
  path.join(REPO_ROOT, "memory/erik-hancock-llm-memory/memory/snapshots"),
  path.join(REPO_ROOT, "operations/drive_ingest"),
  "/Users/pikeymickey/ShadowTag-v2-stack/recovered_assets/antigravity/brain/memory/snapshots",
];

type Tags = Record<string, string | number>;

interface ChunkPayload {
  artifactId: string;
  text: string;
  tags: Tags;
  embed: number[];
}

// ── Provider stubs for future multi-provider support ──────────────────────────

// Future: OpenAI embedding
// async function embedOpenAI(text: string): Promise<number[]> {
//   const { OpenAI } = await import("openai");
//   const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
//   const res = await client.embeddings.create({ model: "text-embedding-3-large", input: text });
//   return res.data[0].embedding;
// }

// Future: Claude / Anthropic (no embedding endpoint yet — use for generation/tagging)
// async function tagWithClaude(text: string): Promise<string> {
//   const Anthropic = (await import("@anthropic-ai/sdk")).default;
//   const client = new Anthropic({ apiKey: process.env.CLAUDE_API_KEY });
//   const msg = await client.messages.create({
//     model: "claude-sonnet-4-6",
//     max_tokens: 256,
//     messages: [{ role: "user", content: `Tag this for semantic search:\n${text.slice(0, 800)}` }],
//   });
//   return (msg.content[0] as { text: string }).text;
// }

// ── Gemini embedding ──────────────────────────────────────────────────────────

async function embedGemini(text: string): Promise<number[]> {
  if (!GEMINI_API_KEY) throw new Error("GEMINI_API_KEY not set — cannot embed.");
  const url =
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_EMBED_MODEL}:embedContent` +
    `?key=${GEMINI_API_KEY}`;
  const body = JSON.stringify({
    model: `models/${GEMINI_EMBED_MODEL}`,
    content: { parts: [{ text }] },
  });
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Gemini embed ${res.status}: ${err}`);
  }
  const json = await res.json() as { embedding: { values: number[] } };
  return json.embedding.values;
}

// ── Gemini generative extraction (optional) ───────────────────────────────────

async function extractWithGemini(text: string): Promise<string> {
  if (!GEMINI_API_KEY) return text;
  const url =
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_GEN_MODEL}:generateContent` +
    `?key=${GEMINI_API_KEY}`;
  const prompt = [
    "Extract the key facts, decisions, and entities from the following text.",
    "Return only a concise bullet list. No preamble.",
    "",
    text.slice(0, 3000),
  ].join("\n");
  const body = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { temperature: 0, maxOutputTokens: 512 },
  });
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  if (!res.ok) return text;
  const json = await res.json() as {
    candidates: Array<{ content: { parts: Array<{ text: string }> } }>;
  };
  return json.candidates?.[0]?.content?.parts?.[0]?.text ?? text;
}

// ── Text utilities ─────────────────────────────────────────────────────────────

function chunkText(text: string): string[] {
  const chunks: string[] = [];
  let start = 0;
  while (start < text.length) {
    chunks.push(text.slice(start, start + CHUNK_SIZE));
    start += CHUNK_SIZE - CHUNK_OVERLAP;
  }
  return chunks;
}

function extractTextFromSnapshot(raw: string): string {
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

// ── Core ingest ───────────────────────────────────────────────────────────────

async function ingestFile(filePath: string): Promise<void> {
  const raw = fs.readFileSync(filePath, "utf-8");
  const ext = path.extname(filePath).toLowerCase();
  let text = ext === ".json" ? extractTextFromSnapshot(raw) : raw;
  if (!text.trim()) return;

  if (ENABLE_EXTRACTION) {
    text = await extractWithGemini(text);
  }

  const chunks = chunkText(text);
  const base = path.basename(filePath);

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i];
    let embed: number[];
    try {
      embed = await embedGemini(chunk);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[ingest] embed failed for ${base} chunk ${i + 1}: ${msg}`);
      continue;
    }

    const payload: ChunkPayload = {
      artifactId: `${base}-chunk${i}-${Date.now()}`,
      text: chunk,
      tags: {
        source: filePath,
        chunk: i,
        total: chunks.length,
        ingestedAt: Date.now(),
        embedModel: GEMINI_EMBED_MODEL,
        ...(ENABLE_EXTRACTION ? { extracted: 1 } : {}),
      },
      embed,
    };

    try {
      const res = await fetch(`${API_BASE}/api/v1/ShadowTag-v2/graph/insert`, {
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
  if (!GEMINI_API_KEY) {
    console.error("[ingest] GEMINI_API_KEY is not set. Export it before running.");
    process.exit(1);
  }
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
