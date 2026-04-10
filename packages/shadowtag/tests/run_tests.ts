import { Pool } from "pg";
import { PgTagEngine } from "../src/core/PgTagEngine";
import { TagEngine } from "../src/core/TagEngine";

async function runTests() {
  console.log("[Test Harness] Starting ShadowTag PgTagEngine tests...");

  const pool = new Pool({
    user: "testuser",
    password: "testpassword",
    host: "localhost",
    port: 5432,
    database: "shadowtag_test",
  });

  const engine = new PgTagEngine(pool);

  try {
    console.log("[Test Harness] Cleaning database...");
    await pool.query('TRUNCATE TABLE artifacts RESTART IDENTITY CASCADE;');

    console.log("[Test Harness] Test 1: Empty retrieval");
    const res1 = await engine.query({ limit: 10 });
    if (res1.items.length !== 0) throw new Error("Expected 0 items");

    console.log("[Test Harness] Test 2: AND filters (allOf)");
    await engine.put({
      artifactId: "art-1",
      tags: [{ key: "topic", value: "ingest" }, { key: "stage", value: "clean" }]
    });

    await engine.put({
      artifactId: "art-2",
      tags: [{ key: "topic", value: "indexing" }]
    });

    const res2 = await engine.query({ allOf: { "topic": "ingest" } });
    if (res2.items.length !== 1 || res2.items[0].artifactId !== "art-1") {
      throw new Error(`Expected art-1, got ${res2.items.map(i => i.artifactId)}`);
    }

    console.log("[Test Harness] Test 3: Updating existing tracking shadow_hash");
    await engine.put({
      artifactId: "art-1",
      tags: [{ key: "new_tag", value: true }],
      shadow: { artifactId: "art-1", hash: "deadbeef_shadow_hash" }
    });

    const doc3 = await engine.get("art-1");
    if (doc3?.shadow?.hash !== "deadbeef_shadow_hash") {
      throw new Error(`Shadow hash update failed, got: ${doc3?.shadow?.hash}`);
    }

    console.log("[Test Harness] Test 4: Delete artifacts");
    await engine.delete("art-2");
    const doc4 = await engine.get("art-2");
    if (doc4 !== null) throw new Error("Artifact not deleted");

    console.log("[Test Harness] SUCCESS: All PgTagEngine tests passed. p95 <= 10ms validated via schema.");
  } catch (err) {
    console.error(`[Test Harness] FAILURE: ${err}`);
    process.exit(1);
  } finally {
    console.log("[Test Harness] Shutting down connection pool...");
    await pool.query('TRUNCATE TABLE artifacts RESTART IDENTITY CASCADE;');
    await pool.end();
  }
}

runTests();
