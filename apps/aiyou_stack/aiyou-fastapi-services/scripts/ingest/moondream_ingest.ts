#!/usr/bin/env node
/**
 * Moondream Ingestion Pipeline
 *
 * Processes visual documents (images, PDFs, screenshots) using Moondream
 * for fast, local OCR and layout understanding.
 *
 * Outputs JSON Lines format for downstream processing.
 */

import fg from "fast-glob";
import fs from "fs-extra";
import path from "node:path";
import crypto from "node:crypto";
import { request } from "undici";

// Configuration
const ROOTS = (process.env.INGEST_ROOTS || "C:/Users;E:/;F:/").split(";");
const OUT = process.env.INGEST_OUT || "ingest/out/downloads.jsonl";
const SEEN = process.env.INGEST_SEEN || "ingest/out/.seen.txt";
const MOONDREAM_URL = process.env.MOONDREAM_URL || "http://localhost:7777/extract";

const SUPPORTED_EXTS = [
  ".png",
  ".jpg",
  ".jpeg",
  ".pdf",
  ".tiff",
  ".bmp",
  ".webp",
  ".gif",
  ".heic",
  ".txt",
  ".md",
  ".csv",
  ".json",
  ".html",
];

// Load seen hashes
const seen = new Set<string>(
  fs.existsSync(SEEN) ? fs.readFileSync(SEEN, "utf8").split("\n").filter(Boolean) : [],
);

function sha256(buf: Buffer): string {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

async function parseWithMoondream(filePath: string): Promise<{
  text: string;
  json: unknown | null;
  meta: Record<string, any>;
}> {
  const ext = path.extname(filePath).toLowerCase();

  // Plain text files - no need for Moondream
  if ([".txt", ".md", ".csv", ".json", ".html"].includes(ext)) {
    const text = await fs.readFile(filePath, "utf8");
    return {
      text,
      json: ext === ".json" ? JSON.parse(text) : null,
      meta: { mode: "plain" },
    };
  }

  // Visual files - use Moondream HTTP API
  try {
    const fileStream = fs.createReadStream(filePath);
    const response = await request(MOONDREAM_URL, {
      method: "POST",
      body: fileStream,
      headers: {
        "Content-Type": "application/octet-stream",
      },
    });

    const result = await response.body.json();
    return {
      text: result.text || "",
      json: result.data || null,
      meta: { ...result.meta, mode: "moondream" },
    };
  } catch (error: unknown) {
    console.error(`[Moondream] Error processing ${filePath}:`, error.message);
    return {
      text: "",
      json: null,
      meta: { mode: "error", error: error.message },
    };
  }
}

async function main() {
  await fs.ensureDir(path.dirname(OUT));
  const outStream = fs.createWriteStream(OUT, { flags: "a" });

  let processed = 0;
  let skipped = 0;

  for (const root of ROOTS) {
    if (!fs.existsSync(root)) {
      console.log(`[Ingest] Skipping non-existent root: ${root}`);
      continue;
    }

    console.log(`[Ingest] Scanning: ${root}`);

    const files = await fg(["**/*"], {
      cwd: root,
      dot: false,
      onlyFiles: true,
      absolute: true,
      followSymbolicLinks: false,
      ignore: ["**/node_modules/**", "**/.git/**", "**/dist/**"],
    });

    for (const filePath of files) {
      const ext = path.extname(filePath).toLowerCase();
      if (!SUPPORTED_EXTS.includes(ext)) {
        continue;
      }

      let buf: Buffer;
      try {
        buf = await fs.readFile(filePath);
      } catch (error) {
        console.error(`[Ingest] Cannot read ${filePath}`);
        continue;
      }

      const hash = sha256(buf);
      if (seen.has(hash)) {
        skipped++;
        continue;
      }

      const parsed = await parseWithMoondream(filePath);

      const record = {
        sha256: hash,
        path: filePath,
        ext,
        size: buf.length,
        mtime: Math.floor((await fs.stat(filePath)).mtimeMs / 1000),
        text: parsed.text || undefined,
        data: parsed.json || undefined,
        meta: parsed.meta || undefined,
        now: Math.floor(Date.now() / 1000),
        source: "moondream-ingest",
      };

      outStream.write(JSON.stringify(record) + "\n");
      seen.add(hash);
      processed++;

      if (processed % 100 === 0) {
        console.log(`[Ingest] Processed: ${processed}, Skipped: ${skipped}`);
      }
    }
  }

  outStream.end();
  await fs.outputFile(SEEN, [...seen].join("\n"));

  console.log(`\n[Ingest] Complete!`);
  console.log(`  Processed: ${processed}`);
  console.log(`  Skipped (seen): ${skipped}`);
  console.log(`  Output: ${OUT}`);
}

main().catch((error) => {
  console.error("[Ingest] Fatal error:", error);
  process.exit(1);
});
