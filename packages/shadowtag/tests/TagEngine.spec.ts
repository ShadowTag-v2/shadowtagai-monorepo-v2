import { Pool } from "pg";
import { PgTagEngine } from "../src/core/PgTagEngine";
import type { TagEngine } from "../src/core/TagEngine";

describe("PgTagEngine Acceptance Tests", () => {
  let engine: TagEngine;
  let pool: Pool;

  beforeAll(async () => {
    pool = new Pool({
      user: "testuser",
      password: "testpassword",
      host: "localhost",
      port: 5432,
      database: "shadowtag_test",
    });

    engine = new PgTagEngine(pool);

    // Ensure table is clean before tests run
    await pool.query("TRUNCATE TABLE artifacts RESTART IDENTITY CASCADE;");
  });

  afterAll(async () => {
    // Teardown logic
    await pool.query("TRUNCATE TABLE artifacts RESTART IDENTITY CASCADE;");
    await pool.end();
  });

  it("should output zero results gracefully on empty tables", async () => {
    const res = await engine.query({ limit: 10 });
    expect(res.items.length).toBe(0);
  });

  it("should filter tags using AND (allOf) combinations", async () => {
    await engine.put({
      artifactId: "art-1",
      tags: [
        { key: "topic", value: "ingest" },
        { key: "stage", value: "clean" },
      ],
    });

    await engine.put({
      artifactId: "art-2",
      tags: [{ key: "topic", value: "indexing" }],
    });

    const res = await engine.query({ allOf: { topic: "ingest" } });
    expect(res.items.length).toBe(1);
    expect(res.items[0].artifactId).toBe("art-1");
  });

  it("should retrieve artifacts efficiently by exactly matching multiple constraints", async () => {
    const res = await engine.query({ allOf: { topic: "ingest", stage: "clean" } });
    expect(res.items.length).toBe(1);
    expect(res.items[0].artifactId).toBe("art-1");
  });

  it("should update existing artifacts accurately and preserve un-updated metadata", async () => {
    // Add shadow hash to art-1
    await engine.put({
      artifactId: "art-1",
      tags: [{ key: "new_tag", value: true }],
      shadow: { artifactId: "art-1", hash: "deadbeef" },
    });

    const doc = await engine.get("art-1");
    expect(doc).toBeDefined();
    expect(doc?.shadow?.hash).toBe("deadbeef");

    // Check tags merged properly
    const keys = doc?.tags.map((t) => t.key);
    expect(keys).toContain("topic");
    expect(keys).toContain("new_tag");
  });

  it("should paginate correctly using limit and cursor rollover", async () => {
    // Inject bulk batch
    const batch = [];
    for (let i = 10; i < 60; i++) {
      batch.push({
        artifactId: `bulk-${i}`,
        tags: [{ key: "source", value: "batch" }],
      });
    }
    await engine.bulkPut(batch);

    // Query limit 10
    const res1 = await engine.query({ allOf: { source: "batch" }, limit: 10 });
    expect(res1.items.length).toBe(10);
    expect(res1.nextCursor).toBeDefined();

    // Query next 10 using cursor
    const res2 = await engine.query({
      allOf: { source: "batch" },
      limit: 10,
      cursor: res1.nextCursor,
    });
    expect(res2.items.length).toBe(10);
    expect(res2.items[0].artifactId).not.toBe(res1.items[0].artifactId); // Ensure progression
  });

  it("should delete artifacts", async () => {
    await engine.delete("art-2");
    expect(await engine.get("art-2")).toBeNull();
  });
});
