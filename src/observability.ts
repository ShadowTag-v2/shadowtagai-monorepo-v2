import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { ExpressInstrumentation } from "@opentelemetry/instrumentation-express";
import { HttpInstrumentation } from "@opentelemetry/instrumentation-http";
import { Resource } from "@opentelemetry/resources";
import { NodeSDK } from "@opentelemetry/sdk-node";
import {
  SEMRESATTRS_SERVICE_NAME,
  SEMRESATTRS_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";
import * as Sentry from "@sentry/node";

/**
 * Initialize Observability (Sentry + OpenTelemetry)
 * Call this once at application startup.
 */
export function initializeObservability() {
  const SENTRY_DSN = process.env.SENTRY_DSN;
  const NODE_ENV = process.env.NODE_ENV || "production";
  const SERVICE_NAME = "headfade-mcp";
  const SERVICE_VERSION = process.env.npm_package_version || "1.0.0";

  // ============================================
  // OPEN TELEMETRY
  // ============================================
  const sdk = new NodeSDK({
    resource: new Resource({
      [SEMRESATTRS_SERVICE_NAME]: SERVICE_NAME,
      [SEMRESATTRS_SERVICE_VERSION]: SERVICE_VERSION,
    }),
    instrumentations: [
      getNodeAutoInstrumentations(),
      new ExpressInstrumentation(),
      new HttpInstrumentation(),
    ],
  });

  sdk.start();
  console.log("✅ OpenTelemetry initialized");

  // ============================================
  // SENTRY
  // ============================================
  if (SENTRY_DSN) {
    Sentry.init({
      dsn: SENTRY_DSN,
      environment: NODE_ENV,
      tracesSampleRate: NODE_ENV === "production" ? 0.1 : 1.0,
      integrations: [
        new Sentry.Integrations.Http({ tracing: true }),
        new Sentry.Integrations.Express({ app: undefined }), // Will be set later
      ],
    });
    console.log("✅ Sentry initialized");
  } else {
    console.log("⚠️  Sentry DSN not provided — skipping Sentry initialization");
  }

  // Graceful shutdown for OpenTelemetry
  process.on("SIGTERM", async () => {
    await sdk.shutdown();
    console.log("OpenTelemetry SDK shut down");
  });
}
