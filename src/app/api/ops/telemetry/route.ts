/**
 * Telemetry Ingestion API — /api/ops/telemetry
 *
 * Cor.Re-Coding the Vibe: This is the server-side ingestion endpoint
 * for all Panopticon telemetry events.
 *
 * Architecture (adapted from Claude Code's sink routing):
 *   PanopticonProvider → HTTP POST → this route → structured logging
 *
 * Security:
 *   - Rate limited via middleware.ts (Upstash sliding window)
 *   - Validates event structure with Zod
 *   - Strips any remaining PII fields server-side (defense in depth)
 *   - No raw user data stored — only hashed/numeric metadata
 *
 * Future: Route events to BigQuery, PostHog, or OpenTelemetry collectors.
 */

import { NextResponse, type NextRequest } from "next/server";
import { stripPiiFields, isTelemetryDisabled } from "@/lib/telemetry";

// ─────────────────────────────────────────────────────────────
// Validation (inline Zod-like validation without import weight)
// ─────────────────────────────────────────────────────────────

interface IncomingEvent {
  eventName: string;
  metadata: Record<string, boolean | number | undefined>;
  timestamp: number;
  sessionId: string;
  severity: string;
  source: string;
}

interface TelemetryPayload {
  events: IncomingEvent[];
}

const VALID_SEVERITIES = new Set(["info", "warn", "error", "critical"]);
const VALID_SOURCES = new Set(["client", "server", "edge"]);
const MAX_EVENTS_PER_BATCH = 50;
const MAX_EVENT_NAME_LENGTH = 128;
const MAX_METADATA_KEYS = 20;

function validateEvent(event: unknown): event is IncomingEvent {
  if (!event || typeof event !== "object") return false;
  const e = event as Record<string, unknown>;

  // Event name
  if (typeof e.eventName !== "string" || e.eventName.length === 0) return false;
  if (e.eventName.length > MAX_EVENT_NAME_LENGTH) return false;
  // Reject event names containing path separators or suspicious patterns
  if (/[/\\<>|]/.test(e.eventName)) return false;

  // Timestamp
  if (typeof e.timestamp !== "number" || !Number.isFinite(e.timestamp))
    return false;
  // Reject timestamps more than 1 hour in the past or future
  const now = Date.now();
  if (Math.abs(now - e.timestamp) > 3_600_000) return false;

  // Session ID (UUID format)
  if (typeof e.sessionId !== "string") return false;
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
      e.sessionId,
    )
  )
    return false;

  // Severity
  if (typeof e.severity !== "string" || !VALID_SEVERITIES.has(e.severity))
    return false;

  // Source
  if (typeof e.source !== "string" || !VALID_SOURCES.has(e.source))
    return false;

  // Metadata — only allow primitives (defense against injection)
  if (e.metadata && typeof e.metadata === "object") {
    const meta = e.metadata as Record<string, unknown>;
    const keys = Object.keys(meta);
    if (keys.length > MAX_METADATA_KEYS) return false;
    for (const key of keys) {
      const val = meta[key];
      if (
        val !== undefined &&
        typeof val !== "boolean" &&
        typeof val !== "number"
      ) {
        return false;
      }
    }
  }

  return true;
}

function validatePayload(body: unknown): body is TelemetryPayload {
  if (!body || typeof body !== "object") return false;
  const payload = body as Record<string, unknown>;

  if (!Array.isArray(payload.events)) return false;
  if (payload.events.length === 0 || payload.events.length > MAX_EVENTS_PER_BATCH)
    return false;

  return payload.events.every(validateEvent);
}

// ─────────────────────────────────────────────────────────────
// Route Handler
// ─────────────────────────────────────────────────────────────

export async function POST(request: NextRequest): Promise<NextResponse> {
  // Kill switch
  if (isTelemetryDisabled()) {
    return NextResponse.json({ accepted: 0 }, { status: 200 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid JSON" },
      { status: 400 },
    );
  }

  // Validate structure
  if (!validatePayload(body)) {
    return NextResponse.json(
      { error: "Invalid payload structure" },
      { status: 422 },
    );
  }

  // Process events
  const sanitizedEvents = body.events.map((event) => ({
    ...event,
    metadata: stripPiiFields(event.metadata),
    // Add server-side enrichment
    _server_received_at: Date.now(),
    _client_ip_hash: hashIp(
      request.headers.get("x-forwarded-for") ??
        request.headers.get("x-real-ip") ??
        "unknown",
    ),
  }));

  // ──────────────────────────────────────────────────────
  // Sink: Structured logging (production-ready)
  //
  // In production, this would fan out to:
  //   1. BigQuery (analytics)
  //   2. Cloud Logging (operational)
  //   3. PostHog (product analytics)
  //
  // For now, structured console output that Cloud Run captures
  // automatically as JSON in Cloud Logging.
  // ──────────────────────────────────────────────────────
  for (const event of sanitizedEvents) {
    const logEntry = {
      severity: event.severity === "error" ? "ERROR" : "INFO",
      message: `[Panopticon] ${event.eventName}`,
      "logging.googleapis.com/labels": {
        session_id: event.sessionId,
        source: event.source,
      },
      jsonPayload: {
        event_name: event.eventName,
        metadata: event.metadata,
        client_timestamp: event.timestamp,
        server_timestamp: event._server_received_at,
      },
    };

    // Structured logging compatible with Cloud Logging
    if (event.severity === "error" || event.severity === "critical") {
      console.error(JSON.stringify(logEntry));
    } else {
      console.log(JSON.stringify(logEntry));
    }
  }

  return NextResponse.json(
    { accepted: sanitizedEvents.length },
    { status: 200 },
  );
}

// ─────────────────────────────────────────────────────────────
// Utility
// ─────────────────────────────────────────────────────────────

/**
 * Hash IP address to prevent storing raw PII.
 * Only the hash is stored for session correlation.
 */
function hashIp(ip: string): number {
  let hash = 0;
  for (let i = 0; i < ip.length; i++) {
    const chr = ip.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0;
  }
  return Math.abs(hash);
}

// Also handle sendBeacon payloads (single-event text/plain)
export async function OPTIONS(): Promise<NextResponse> {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
