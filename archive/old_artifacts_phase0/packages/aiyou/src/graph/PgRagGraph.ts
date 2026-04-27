import type { TagEngine } from '@shadowtag/core/TagEngine';
import { ArtifactId } from '@shared/types';
import type { Pool } from 'pg';
import type { Edge, InsertDoc, RagGraph, RetrieveHit, RetrieveQuery } from './RagGraph';

/**
 * PgRagGraph
 * Implements the ShadowTag-v2 semantic retrieval graph using pgvector and ShadowTag.
 *
 * Execution Flow (Retrieve):
 * 1. Filter viable artifact IDs via ShadowTag (metadata spine).
 * 2. Perform Approximate Nearest Neighbor (ANN) search strictly bounded to those IDs.
 * 3. Return ranked hits.
 */
export class PgRagGraph implements RagGraph {
  constructor(
    private pool: Pool,
    private tagEngine: TagEngine,
  ) {}

  /**
   * Initialize pgvector embeddings table
   */
  async ensureSchema(): Promise<void> {
    const query = `
      CREATE TABLE IF NOT EXISTS document_embeddings (
        artifact_id TEXT PRIMARY KEY,
        text_content TEXT NOT NULL,
        embedding vector(1536) -- Default OpenAI dim, adapt as needed
      );

      -- Optional HNSW index for ANN speed
      CREATE INDEX IF NOT EXISTS idx_doc_embeddings_hnsw
      ON document_embeddings USING hnsw (embedding vector_cosine_ops);
    `;
    await this.pool.query(query);
  }

  async insert(doc: InsertDoc): Promise<void> {
    // 1. Tag the document on the truth layer
    await this.tagEngine.put({
      artifactId: doc.artifactId,
      tags: Object.entries(doc.tags || {}).map(([key, value]) => ({ key, value })),
    });

    // 2. Upsert vector + text payload
    if (doc.embed && doc.embed instanceof Float32Array) {
      const vectorString = `[${doc.embed.join(',')}]`;
      const query = `
        INSERT INTO document_embeddings (artifact_id, text_content, embedding)
        VALUES ($1, $2, $3::vector)
        ON CONFLICT (artifact_id) DO UPDATE SET
          text_content = EXCLUDED.text_content,
          embedding = EXCLUDED.embedding
      `;
      await this.pool.query(query, [doc.artifactId, doc.text, vectorString]);
    }
  }

  async link(edges: Edge[]): Promise<void> {
    // A network link table can be implemented later.
    // For MVP RAG, this is stubbed as we focus on semantic vector hits.
    console.log(`[RagGraph] Stubbed link operation for ${edges.length} edges.`);
  }

  async retrieve(query: RetrieveQuery): Promise<RetrieveHit[]> {
    // 1. Prefilter metadata via ShadowTag Engine
    let allowedIds: string[] | null = null;
    if (query.filter && Object.keys(query.filter).length > 0) {
      const preFilter = await this.tagEngine.query({ allOf: query.filter, limit: 10000 });
      allowedIds = preFilter.items.map((i) => i.artifactId);

      // If filters are applied but yield zero matches, early return.
      if (allowedIds.length === 0) return [];
    }

    // Since we omit the actual query embedding here (assuming query.q is text),
    // in a real system we would embed(query.q) first. For MVP simulation
    // assuming query.q receives a mock vector or relies on external embedder hook.
    // E.g., const embedVector = await externalEmbed(query.q);

    // For scaffolding the pgvector call structure (simulated vector):
    const mockVectorString = `[${new Array(1536).fill(0.01).join(',')}]`;

    // 2. Fetch via pgvector (cosine distance filtering)
    let sql = `
      SELECT artifact_id, text_content,
             1 - (embedding <=> $1::vector) AS score
      FROM document_embeddings
    `;
    const params: any[] = [mockVectorString];

    if (allowedIds) {
      sql += ` WHERE artifact_id = ANY($2)`;
      params.push(allowedIds);
    }

    sql += ` ORDER BY embedding <=> $1::vector LIMIT $${params.length + 1}`;
    params.push(query.k || 5);

    const res = await this.pool.query(sql, params);

    // 3. Hydrate outputs
    const hits: RetrieveHit[] = [];
    for (const row of res.rows) {
      const tagDoc = await this.tagEngine.get(row.artifact_id);

      const tagSet: Record<string, any> = {};
      if (tagDoc) {
        tagDoc.tags.forEach((t) => (tagSet[t.key] = t.value));
      }

      hits.push({
        artifactId: row.artifact_id,
        snippet: row.text_content,
        score: parseFloat(row.score),
        tags: tagSet,
      });
    }

    return hits;
  }
}
