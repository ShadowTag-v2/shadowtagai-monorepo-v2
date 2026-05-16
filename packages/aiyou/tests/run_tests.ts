import { PgTagEngine } from "@shadowtag/core/PgTagEngine";
import { Pool } from "pg";
import { PgRagGraph } from "../src/graph/PgRagGraph";
import type { InsertDoc } from "../src/graph/RagGraph";

async function runTests() {
  console.log("[Test Harness] Starting AiYou PgRagGraph tests...");

  const pool = new Pool({
    user: "testuser",
    password: "testpassword",
    host: "localhost",
    port: 5432,
    database: "shadowtag_test",
  });

  const tagEngine = new PgTagEngine(pool);
  const ragGraph = new PgRagGraph(pool, tagEngine);

  try {
    console.log("[Test Harness] Cleaning & Ensuring Schema...");
    await pool.query("TRUNCATE TABLE artifacts RESTART IDENTITY CASCADE;");
    // Drop the embeddings table if it exists to ensure clean state
    await pool.query("DROP TABLE IF EXISTS document_embeddings CASCADE;");
    await ragGraph.ensureSchema();

    console.log("[Test Harness] Test 1: Inserting documents (with simulated vectors)");

    // Create random mock vectors
    const mockVec1 = new Float32Array(1536).fill(0.1);
    const mockVec2 = new Float32Array(1536).fill(0.9);

    const doc1: InsertDoc = {
      artifactId: "rag-doc-1",
      text: "This is a document about parsing pipelines.",
      tags: { topic: "ingest", visibility: "public" },
      embed: mockVec1,
    };

    const doc2: InsertDoc = {
      artifactId: "rag-doc-2",
      text: "This document describes UI design aesthetics.",
      tags: { topic: "frontend", visibility: "public" },
      embed: mockVec2,
    };

    await ragGraph.insert(doc1);
    await ragGraph.insert(doc2);

    console.log("[Test Harness] Test 2: Retrieving with strict TagFilter");

    // Retrieve looking for "ingest", the filter should block doc2 even if semantic distance was close
    // Since mock retrieve hardcodes a 1536 vector of 0.01 for the query right now, it relies on filter logic

    const hits = await ragGraph.retrieve({
      q: "parsing pipelines",
      filter: { topic: "ingest" },
      k: 2,
    });

    if (hits.length !== 1) {
      throw new Error(`Expected exactly 1 hit due to filter, got ${hits.length}`);
    }

    if (hits[0].artifactId !== "rag-doc-1") {
      throw new Error(`Expected hit to be rag-doc-1, got ${hits[0].artifactId}`);
    }

    // Check tags hydrated
    if (hits[0].tags["visibility"] !== "public") {
      throw new Error(`Tag hydration failed for visibility.`);
    }

    console.log(
      "[Test Harness] Test 3: Retrieving without filter (returns both based on distance limits if k=2)",
    );
    const allHits = await ragGraph.retrieve({
      q: "general query",
      k: 2,
    });

    if (allHits.length !== 2) {
      throw new Error(`Expected 2 total hits across unfiltered pool, got ${allHits.length}`);
    }

    console.log(
      "[Test Harness] SUCCESS: AiYou PgRagGraph tests passed. Segregated AI-RAG verified.",
    );
  } catch (err) {
    console.error(`[Test Harness] FAILURE: ${err}`);
    process.exit(1);
  } finally {
    console.log("[Test Harness] Shutting down connection pool...");
    await pool.query("TRUNCATE TABLE artifacts RESTART IDENTITY CASCADE;");
    await pool.query("DROP TABLE IF EXISTS document_embeddings CASCADE;");
    await pool.end();
  }
}

runTests();
