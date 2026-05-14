import { createShadowTagRouter } from "@shadowtag/api/routes";
import { PgTagEngine } from "@shadowtag/core/PgTagEngine";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import { Pool } from "pg";
import { createAiYouRouter } from "./api/routes";
import { PgRagGraph } from "./graph/PgRagGraph";

// Load environment variables (e.g. database URL)
dotenv.config();

/**
 * Configure dependencies and mount domain routers.
 */
export async function buildApp() {
  const app = express();

  // Middleware
  app.use(cors());
  app.use(express.json());

  // Healthcheck
  app.get("/health", (req, res) => {
    res.status(200).json({ status: "ok", service: "aiyou-core" });
  });

  // DB Initialization
  const pool = new Pool({
    // Standard PG env vars (PGHOST, PGUSER, PGPASSWORD, PGDATABASE, PGPORT)
    connectionString:
      process.env.DATABASE_URL || "postgres://testuser:testpassword@localhost:5432/shadowtag_test",
  });

  // Domain Engines
  const tagEngine = new PgTagEngine(pool);
  const ragGraph = new PgRagGraph(pool, tagEngine);

  // Ensure DB Migrations / Vector Schema exist
  // In production, migrations should run separately via Flyway/Liquibase or custom scripts.
  // For dev stability, we ensure the embedding schema exists.
  await ragGraph.ensureSchema();

  // Mount API Routers
  app.use("/api/v1/shadowtag", createShadowTagRouter(tagEngine));
  app.use("/api/v1/aiyou", createAiYouRouter(ragGraph));

  return { app, pool };
}

// Standalone boot script
if (require.main === module) {
  buildApp()
    .then(({ app }) => {
      const PORT = process.env.PORT || 8000;
      app.listen(PORT, () => {
        console.log(`[AiYou Server] Core APIs initialized and listening on port ${PORT}`);
      });
    })
    .catch((err) => {
      console.error("[AiYou Server] Failed to build app:", err);
      process.exit(1);
    });
}
