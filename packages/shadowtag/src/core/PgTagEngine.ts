import type { ArtifactId, TagSet } from "@shared/types";
import type { Pool } from "pg";
import type { TagEngine, TagQuery, TagResult, TagWrite } from "./TagEngine";

export class PgTagEngine implements TagEngine {
  constructor(private pool: Pool) {}

  async put(input: TagWrite): Promise<void> {
    const { artifactId, tags, shadow, ts } = input;
    // Tags are converted to a simple key-value object for JSONB
    const tagsObj: TagSet = {};
    for (const t of tags) {
      tagsObj[t.key] = t.value;
    }

    const query = `
      INSERT INTO artifacts (id, tags, shadow_hash, updated_at)
      VALUES ($1, $2, $3, to_timestamp($4 / 1000.0))
      ON CONFLICT (id) DO UPDATE SET
        tags = artifacts.tags || EXCLUDED.tags,
        shadow_hash = COALESCE(EXCLUDED.shadow_hash, artifacts.shadow_hash),
        updated_at = EXCLUDED.updated_at;
    `;

    await this.pool.query(query, [
      artifactId,
      JSON.stringify(tagsObj),
      shadow?.hash || null,
      ts || Date.now(),
    ]);
  }

  async bulkPut(batch: TagWrite[]): Promise<void> {
    // In a real app, use pg-format for multi-row inserts
    for (const b of batch) {
      await this.put(b);
    }
  }

  async get(artifactId: ArtifactId): Promise<TagResult | null> {
    const res = await this.pool.query(`SELECT id, tags, shadow_hash FROM artifacts WHERE id = $1`, [
      artifactId,
    ]);
    if (res.rows.length === 0) return null;

    const row = res.rows[0];
    const tagObj = row.tags as TagSet;
    const tags = Object.entries(tagObj).map(([key, value]) => ({ key, value }));

    return {
      artifactId: row.id,
      tags,
      shadow: row.shadow_hash ? { artifactId: row.id, hash: row.shadow_hash } : undefined,
    };
  }

  async query(q: TagQuery): Promise<{ items: TagResult[]; nextCursor?: string }> {
    let sql = `SELECT id, tags, shadow_hash FROM artifacts WHERE 1=1`;
    const params: any[] = [];
    let paramIndex = 1;

    // allOf -> AND condition (JSONB containment)
    if (q.allOf && Object.keys(q.allOf).length > 0) {
      sql += ` AND tags @> $${paramIndex}`;
      params.push(JSON.stringify(q.allOf));
      paramIndex++;
    }

    // anyOf -> OR condition (JSONB existence/overlap)
    // To properly support key/value anyOf we could use jsonb_path_ops or an array
    // Here we'll do a simplified approach testing if the jsonb overlaps or satisfies
    // In Postgres 14+, ?| or similar operators exist for keys.
    // Implementing a generic key-value match OR requires unwrapping or multiple conditions.
    if (q.anyOf && Object.keys(q.anyOf).length > 0) {
      const orConditions = [];
      for (const [k, v] of Object.entries(q.anyOf)) {
        orConditions.push(`tags @> $${paramIndex}`);
        params.push(JSON.stringify({ [k]: v }));
        paramIndex++;
      }
      sql += ` AND (${orConditions.join(" OR ")})`;
    }

    // not -> NOT condition
    if (q.not && Object.keys(q.not).length > 0) {
      sql += ` AND NOT (tags @> $${paramIndex})`;
      params.push(JSON.stringify(q.not));
      paramIndex++;
    }

    // Cursor pagination (keyset based on id for simplicity)
    if (q.cursor) {
      sql += ` AND id > $${paramIndex}`;
      params.push(q.cursor);
      paramIndex++;
    }

    sql += ` ORDER BY id ASC LIMIT $${paramIndex}`;
    params.push(q.limit || 50);

    const res = await this.pool.query(sql, params);

    const items: TagResult[] = res.rows.map((row) => {
      const tags = Object.entries(row.tags as TagSet).map(([k, v]) => ({ key: k, value: v }));
      return {
        artifactId: row.id,
        tags,
        shadow: row.shadow_hash ? { artifactId: row.id, hash: row.shadow_hash } : undefined,
      };
    });

    const nextCursor =
      items.length === (q.limit || 50) ? items[items.length - 1].artifactId : undefined;

    return { items, nextCursor };
  }

  async delete(artifactId: ArtifactId): Promise<void> {
    await this.pool.query(`DELETE FROM artifacts WHERE id = $1`, [artifactId]);
  }
}
