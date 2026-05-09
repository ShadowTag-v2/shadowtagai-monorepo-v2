/**
 * ═══════════════════════════════════════════════════════════════
 * V17 Archon-Bun Hyper-Core — Workspace Intake Webhook
 * ═══════════════════════════════════════════════════════════════
 *
 * Dual-channel intake handler running on Bun.serve():
 * - Prose Intent: Google Docs → UTF-8 decode → Gemini File Memory
 * - Tabular Ledger: Excel/CSV → SheetJS parse → structured CSV → Gemini File Memory
 *
 * Runtime: Bun 1.3.11 (Zig-compiled, mimalloc-backed)
 * Port: 8080
 */

import { read, utils } from "xlsx";

const PORT = Number(Bun.env.WEBHOOK_PORT ?? "8080");
const GEMINI_UPLOAD_ENABLED = Bun.env.GEMINI_UPLOAD_ENABLED === "true";

/**
 * Detects whether the incoming payload is a tabular ledger (Excel/CSV)
 * or a prose document, and processes accordingly.
 */
async function processPayload(
  docName: string,
  rawData: string
): Promise<{ text: string; type: "tabular" | "prose" }> {
  const lowerName = docName.toLowerCase();

  if (lowerName.endsWith(".xlsx") || lowerName.endsWith(".xls")) {
    console.log(`📊 Tabular Ledger detected: ${docName}`);
    const buffer = Buffer.from(rawData, "base64");
    const workbook = read(buffer, { type: "buffer" });
    const firstSheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[firstSheetName];
    const csv = utils.sheet_to_csv(sheet);
    console.log(
      `✅ SheetJS ingestion complete: ${firstSheetName} (${csv.length} chars)`
    );
    return { text: csv, type: "tabular" };
  }

  if (lowerName.endsWith(".csv")) {
    console.log(`📊 CSV Ledger detected: ${docName}`);
    const text = Buffer.from(rawData, "base64").toString("utf-8");
    return { text, type: "tabular" };
  }

  // Default: prose document
  console.log(`📝 Prose Intent detected: ${docName}`);
  const text = Buffer.from(rawData, "base64").toString("utf-8");
  return { text, type: "prose" };
}

/**
 * Optionally uploads processed text to Gemini File API for vector search.
 * Only active when GEMINI_UPLOAD_ENABLED=true.
 */
async function uploadToGeminiFileApi(
  docName: string,
  processedText: string
): Promise<void> {
  if (!GEMINI_UPLOAD_ENABLED) {
    console.log(`⏸ Gemini upload skipped (GEMINI_UPLOAD_ENABLED=false)`);
    return;
  }

  try {
    const { GoogleGenAI } = await import("@google/genai");
    const ai = new GoogleGenAI({});
    const tmpPath = `/tmp/${docName.replace(/[^a-zA-Z0-9._-]/g, "_")}.txt`;
    await Bun.write(tmpPath, processedText);
    await ai.files.upload({ file: tmpPath, config: { displayName: docName } });
    console.log(`✅ Uploaded to Gemini File API: ${docName}`);
  } catch (err) {
    console.error(`⚠️ Gemini upload failed: ${(err as Error).message}`);
  }
}

// ─── Bun.serve() — Sub-millisecond cold start ───────────────────

console.log(`⚡ Bun Hyper-Core Webhook Active on port ${PORT}`);
console.log(
  `   Gemini Upload: ${GEMINI_UPLOAD_ENABLED ? "ENABLED" : "DISABLED"}`
);

Bun.serve({
  port: PORT,
  async fetch(req: Request): Promise<Response> {
    const url = new URL(req.url);

    // Health check endpoint
    if (url.pathname === "/health") {
      return Response.json({
        status: "healthy",
        runtime: "bun",
        version: Bun.version,
        uptime: process.uptime(),
      });
    }

    // Workspace push endpoint (Pub/Sub → webhook)
    if (url.pathname === "/workspace-push" && req.method === "POST") {
      try {
        const body = await req.json();
        const docName: string =
          body.message?.attributes?.document_title ?? "Unknown_Payload";
        const rawData: string = body.message?.data ?? "";

        if (!rawData) {
          return Response.json(
            { error: "No data in message payload" },
            { status: 400 }
          );
        }

        const { text, type } = await processPayload(docName, rawData);

        // Write to local temp for debugging
        const tmpPath = `/tmp/${docName.replace(/[^a-zA-Z0-9._-]/g, "_")}.txt`;
        await Bun.write(tmpPath, text);
        console.log(`💾 Cached locally: ${tmpPath} (${text.length} chars)`);

        // Upload to Gemini for vector search
        await uploadToGeminiFileApi(docName, text);

        return Response.json({
          status: "ok",
          document: docName,
          type,
          chars: text.length,
          runtime: "bun",
        });
      } catch (err) {
        console.error(`❌ Webhook error: ${(err as Error).message}`);
        return Response.json(
          { error: (err as Error).message },
          { status: 500 }
        );
      }
    }

    return Response.json({ error: "Not Found" }, { status: 404 });
  },
});
