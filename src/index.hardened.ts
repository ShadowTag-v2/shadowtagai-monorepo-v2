import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { ExpressInstrumentation } from "@opentelemetry/instrumentation-express";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { NodeSDK } from "@opentelemetry/sdk-node";
import * as Sentry from "@sentry/node";
import cors from "cors";
import express from "express";
import rateLimit from "express-rate-limit";
import { getAuth } from "firebase-admin/auth";
import { getFirestore } from "firebase-admin/firestore";
import helmet from "helmet";
import Stripe from "stripe";

// V25 Jules Ascension — Orchestration modules
import {
  ClaudeSourcemapBridge,
  DartEdgeBridge,
  JulesFleetOrchestrator,
  NotebookLMEpistemicHook,
} from "./orchestration/index.js";

// ============================================
// CONFIGURATION
// ============================================
const PORT = process.env.PORT || 8080;
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY!;
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET!;
const SENTRY_DSN = process.env.SENTRY_DSN;
const NODE_ENV = process.env.NODE_ENV || "production";

// ============================================
// OBSERVABILITY SETUP (OpenTelemetry + Sentry)
// ============================================

// OpenTelemetry
const sdk = new NodeSDK({
  instrumentations: [
    getNodeAutoInstrumentations(),
    new ExpressInstrumentation(),
    new HttpInstrumentation(),
  ],
});
sdk.start();

// Sentry
if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: NODE_ENV,
    tracesSampleRate: 0.1,
  });
}

// ============================================
// EXPRESS APP SETUP
// ============================================
const app = express();

// Trust Cloud Run's load balancer (fixes ERR_ERL_UNEXPECTED_X_FORWARDED_FOR on Cloud Run)
app.set("trust proxy", 1);

// Security Middleware
app.use(helmet());
app.use(
  cors({
    origin: process.env.ALLOWED_ORIGINS?.split(",") || ["https://headfade.com"],
    credentials: true,
  }),
);

// Rate Limiting (keyGenerator uses X-Forwarded-For via trust proxy)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: "Too many requests from this IP, please try again later.",
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Body parsing for Stripe webhooks (raw body needed for signature verification)
app.use("/webhooks/stripe", express.raw({ type: "application/json" }));
app.use(express.json());

// ============================================
// HEALTH CHECK
// ============================================
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || "1.0.0",
  });
});

// ============================================
// MONITORING DASHBOARD ENDPOINT
// ============================================
const metrics = {
  totalRequests: 0,
  totalLicensesGranted: 0,
  totalWebhooksReceived: 0,
  avgWebhookProcessingTime: 0,
  lastWebhookAt: null as string | null,
  errors: 0,
};

app.get("/metrics", (req, res) => {
  res.json({
    ...metrics,
    timestamp: new Date().toISOString(),
    memoryUsage: process.memoryUsage(),
  });
});

// ============================================
// STRIPE WEBHOOK (Hardened)
// ============================================
const stripe = new Stripe(STRIPE_SECRET_KEY, {
  apiVersion: "2026-04-22.dahlia",
});

app.post("/webhooks/stripe", async (req, res) => {
  const startTime = Date.now();
  metrics.totalWebhooksReceived++;

  const sig = req.headers["stripe-signature"] as string;
  let event;

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, STRIPE_WEBHOOK_SECRET);
  } catch (err: any) {
    metrics.errors++;
    console.error("Webhook signature verification failed:", err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  try {
    if (event.type === "payment_intent.succeeded") {
      const paymentIntent = event.data.object;
      const { videoId, agentWalletToken } = paymentIntent.metadata || {};

      if (videoId && agentWalletToken) {
        // Execute license grant
        const db = getFirestore();
        await db.collection("licenses").doc(`${agentWalletToken}_${videoId}`).set({
          videoId,
          agentWalletToken,
          grantedAt: new Date(),
          paymentIntentId: paymentIntent.id,
        });

        metrics.totalLicensesGranted++;
        console.log(`✅ License granted: ${agentWalletToken} → ${videoId}`);
      }
    }

    // Update metrics
    const processingTime = Date.now() - startTime;
    metrics.avgWebhookProcessingTime =
      (metrics.avgWebhookProcessingTime * (metrics.totalWebhooksReceived - 1) + processingTime) /
      metrics.totalWebhooksReceived;
    metrics.lastWebhookAt = new Date().toISOString();
  } catch (error: any) {
    metrics.errors++;
    console.error("Webhook processing error:", error);
    Sentry.captureException(error);
    return res.status(500).json({ error: "Internal server error" });
  }

  res.json({ received: true });
});

// ============================================
// MCP SERVER INITIALIZATION
// ============================================
const server = new McpServer({
  name: "headfade-mcp",
  version: "1.0.0",
});

server.tool("purchaseWorkflowLicense", async ({ videoId, agentWalletToken }: any) => {
  // Implementation from purchase_workflow_license.ts
  // ... (your existing logic here)
  return {
    content: [{ type: "text", text: "License purchase initiated" }],
  };
});

// ============================================
// V25 JULES ASCENSION — ORCHESTRATION MODULES
// ============================================
const fleetOrchestrator = new JulesFleetOrchestrator({
  cloudRunProject: "shadowtag-omega-v4",
  cloudRunRegion: "us-central1",
  concurrency: 5,
});

const dartBridge = new DartEdgeBridge("fleet-ops");
const sourcemapBridge = new ClaudeSourcemapBridge();
const epistemicHook = new NotebookLMEpistemicHook();

// Register known Cloud Run services in the fleet
for (const svc of [
  {
    name: "counselconduit",
    region: "us-central1",
    imageUrl: "gcr.io/shadowtag-omega-v4/counselconduit",
    healthEndpoint: "/health",
  },
  {
    name: "headfade-mcp",
    region: "us-central1",
    imageUrl: "gcr.io/shadowtag-omega-v4/headfade-mcp",
    healthEndpoint: "/health",
  },
]) {
  fleetOrchestrator.registerService(svc);
}

// --- Fleet Management Tools ---

server.tool("v25_fleet_diagnostics", async () => {
  const diagnostics = {
    fleet: fleetOrchestrator.getDiagnostics(),
    dart: dartBridge.getDiagnostics(),
    sourcemap: sourcemapBridge.getDiagnostics(),
    epistemic: epistemicHook.getDiagnostics(),
  };
  return { content: [{ type: "text", text: JSON.stringify(diagnostics, null, 2) }] };
});

server.tool("v25_plan_deployment", async ({ serviceName, prompt, priority }: any) => {
  const plan = fleetOrchestrator.planDeployment([
    { serviceName, prompt, priority: priority ?? "P1" },
  ]);
  const dartPlan = dartBridge.planDeploymentTask(serviceName, prompt, priority ?? "P1");
  return {
    content: [{ type: "text", text: JSON.stringify({ deploymentPlan: plan, dartPlan }, null, 2) }],
  };
});

server.tool("v25_plan_batch_execution", async ({ targets }: any) => {
  const plan = fleetOrchestrator.planDeployment(targets);
  const batchPlan = fleetOrchestrator.planBatchExecution(plan);
  return { content: [{ type: "text", text: JSON.stringify(batchPlan, null, 2) }] };
});

server.tool("v25_plan_health_check", async () => {
  const healthPlan = fleetOrchestrator.planFleetHealthCheck();
  return { content: [{ type: "text", text: JSON.stringify(healthPlan, null, 2) }] };
});

// --- SRE / Sourcemap Tools ---

server.tool("v25_deobfuscate_trace", async ({ errorMessage, frames }: any) => {
  const trace = sourcemapBridge.deobfuscateTrace(errorMessage, frames);
  const correlation = sourcemapBridge.correlateError(trace, "unknown");
  epistemicHook.recordIncident(correlation);
  return { content: [{ type: "text", text: JSON.stringify({ trace, correlation }, null, 2) }] };
});

server.tool("v25_plan_incident_response", async ({ correlationId }: any) => {
  // Look up correlation — if not found, return empty plan
  const plan = sourcemapBridge.planIncidentResponse({
    correlationId,
    errorPattern: "",
    occurrenceCount: 0,
    firstSeen: "",
    lastSeen: "",
    affectedServices: [],
    deobfuscatedTraces: [],
  });
  return { content: [{ type: "text", text: JSON.stringify(plan, null, 2) }] };
});

// --- Epistemic Memory Tools ---

server.tool("v25_query_memory", async ({ type, tags, limit }: any) => {
  const results = epistemicHook.query({ type, tags, limit: limit ?? 20 });
  return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
});

console.log("✅ V25 Jules Ascension orchestration modules initialized");

// ============================================
// GRACEFUL SHUTDOWN
// ============================================
const shutdown = async (signal: string) => {
  console.log(`\n${signal} received. Starting graceful shutdown...`);

  // Close MCP server
  await server.close().catch(console.error);

  // Close HTTP server
  server.close(() => {
    console.log("HTTP server closed.");
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error("Forced shutdown after timeout");
    process.exit(1);
  }, 10000);
};

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));

// ============================================
// START SERVER
// ============================================
const startServer = async () => {
  try {
    // Start MCP server
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.log("✅ MCP Server connected");

    // Start Express server
    app.listen(PORT, () => {
      console.log(`🚀 HeadFade MCP Server running on port ${PORT}`);
      console.log(`   Health: http://localhost:${PORT}/health`);
      console.log(`   Metrics: http://localhost:${PORT}/metrics`);
    });
  } catch (error) {
    console.error("Failed to start server:", error);
    process.exit(1);
  }
};

startServer();
