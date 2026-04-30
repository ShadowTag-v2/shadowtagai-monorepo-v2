import { Router } from 'express';
import { z } from 'zod';
import type { TagEngine, TagQuery, TagWrite } from '../core/TagEngine';

export function createShadowTagRouter(engine: TagEngine): Router {
  const router = Router();

  // Zod schemas for input validation
  const tagWriteSchema = z.object({
    artifactId: z.string(),
    tags: z.array(
      z.object({
        key: z.string(),
        value: z.union([z.string(), z.number(), z.boolean(), z.array(z.string())]),
        confidence: z.number().optional(),
      }),
    ),
    shadow: z
      .object({
        artifactId: z.string(),
        hash: z.string(),
      })
      .optional(),
    ts: z.number().optional(),
  });

  const tagQuerySchema = z.object({
    allOf: z.record(z.string(), z.any()).optional(),
    anyOf: z.record(z.string(), z.any()).optional(),
    not: z.record(z.string(), z.any()).optional(),
    textContains: z.string().optional(),
    limit: z.number().optional(),
    cursor: z.string().optional(),
  });

  router.post('/tags', async (req: any, res: any) => {
    try {
      const parsed = z.array(tagWriteSchema).safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ error: parsed.error });
      }

      const start = Date.now();
      await engine.bulkPut(parsed.data as TagWrite[]);
      const ms = Date.now() - start;

      // Metrics hook simulation
      console.log(`[Metric] counter: shadowtag.api.bulkPut.success`);
      console.log(`[Metric] timer: shadowtag.api.bulkPut_ms = ${ms}`);

      return res.status(201).json({ success: true, count: parsed.data.length });
    } catch (_err: any) {
      return res.status(500).json({ error: 'Internal Server Error' });
    }
  });

  router.post('/tags/query', async (req: any, res: any) => {
    try {
      const parsed = tagQuerySchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ error: parsed.error });
      }

      const start = Date.now();
      const results = await engine.query(parsed.data as TagQuery);
      const ms = Date.now() - start;

      // Metrics hook simulation
      console.log(`[Metric] counter: shadowtag.api.query.success`);
      console.log(`[Metric] timer: shadowtag.api.query_ms = ${ms}`);

      return res.status(200).json(results);
    } catch (_err: any) {
      return res.status(500).json({ error: 'Internal Server Error' });
    }
  });

  return router;
}
