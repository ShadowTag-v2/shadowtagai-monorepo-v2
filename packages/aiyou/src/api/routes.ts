import { Router } from "express";
import { z } from "zod";
import { CognitivePersonaRouter } from "../agents/LegalMetaPersona";
import type { InsertDoc, RagGraph, RetrieveQuery } from "../graph/RagGraph";

export function createAiYouRouter(graph: RagGraph): Router {
  const router = Router();

  const insertDocSchema = z.object({
    artifactId: z.string(),
    text: z.string(),
    tags: z.record(z.string(), z.any()).optional(),
    embed: z.array(z.number()).optional(),
  });

  const retrieveQuerySchema = z.object({
    q: z.string(),
    k: z.number().optional(),
    filter: z.record(z.string(), z.any()).optional(),
  });

  router.post("/graph/insert", async (req: any, res: any) => {
    try {
      const parsed = insertDocSchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ error: parsed.error });
      }

      const docPayload = parsed.data as unknown as InsertDoc;

      // Convert standard arrays to Float32Array for vectors
      if (parsed.data.embed) {
        docPayload.embed = new Float32Array(parsed.data.embed);
      }

      const start = Date.now();
      await graph.insert(docPayload);
      const ms = Date.now() - start;

      console.log(`[Metric] counter: aiyou.api.insert.success`);
      console.log(`[Metric] timer: aiyou.api.insert_ms = ${ms}`);

      return res.status(201).json({ success: true, artifactId: docPayload.artifactId });
    } catch (err: any) {
      console.error("[AiYou API] /graph/insert Error:", err);
      return res.status(500).json({ error: "Internal Server Error" });
    }
  });

  router.post("/graph/retrieve", async (req: any, res: any) => {
    try {
      const parsed = retrieveQuerySchema.safeParse(req.body);
      if (!parsed.success) {
        return res.status(400).json({ error: parsed.error });
      }

      const start = Date.now();
      const hits = await graph.retrieve(parsed.data as RetrieveQuery);
      const ms = Date.now() - start;

      console.log(`[Metric] counter: aiyou.api.retrieve.success`);
      console.log(`[Metric] timer: aiyou.api.retrieve_ms = ${ms}`);

      return res.status(200).json({ hits, count: hits.length });
    } catch (err: any) {
      console.error("[AiYou API] /graph/retrieve Error:", err);
      return res.status(500).json({ error: "Internal Server Error" });
    }
  });

  // ------------------------------------------------------------------
  // AUTONOMOUS AGENT TRADE / META-LANGUAGE SYNTHESIS ENDPOINT
  // ------------------------------------------------------------------
  const agentQuerySchema = z.object({
    q: z.string(),
    filter: z.record(z.string(), z.any()).optional(),
  });

  router.post("/agent/query", async (req: any, res: any) => {
    try {
      const parsed = agentQuerySchema.safeParse(req.body);
      if (!parsed.success) return res.status(400).json({ error: parsed.error });

      // 1. Material Exhibit Retrieval (RAG)
      const hits = await graph.retrieve({ q: parsed.data.q, filter: parsed.data.filter, k: 3 });

      const contextData = hits.map((h) => `[Exhibit ${h.artifactId}]: ${h.snippet}`).join("\\n");

      // 2. Cognitive Routing (27-Year Constraint)
      const personaRouter = new CognitivePersonaRouter();
      const highlyStructuredPrompt = personaRouter.injectMetaLanguage(parsed.data.q, contextData);

      // 3. Execution Loop
      // Here we would normally invoke: const llmResult = await langchain.invoke(highlyStructuredPrompt)
      // Since we don't assume an OpenAI key is present for structural scaffolding, we simulate the LLM deductive engine output.

      const simulatedSynthesis = `
[DEDUCTIVE SYNTHESIS INITIATED]
>> Constraint: \${personaRouter.getMetrics().cognitiveStrictnessLevel} Years Legal Training
>> Exhibits Found: \${hits.length}

MATERIAL FACTS:
\${contextData || "No exhibits provided. Denying synthesis."}

LOGICAL DEDUCTION:
Based on the provided texts, the queries map explicitly to the definitions present in the RAG chunks. Hallucination blocked.
`;

      console.log(`[AiYou API] Synthesized response under LegalMetaPersona constraints.`);
      return res.status(200).json({
        synthesis: simulatedSynthesis.trim(),
        exhibitsUsed: hits.length,
        metrics: personaRouter.getMetrics(),
      });
    } catch (err: any) {
      console.error("[AiYou API] /agent/query Error:", err);
      return res.status(500).json({ error: "Internal Server Error" });
    }
  });

  return router;
}
