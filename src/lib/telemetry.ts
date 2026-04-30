/**
 * Telemetry Service — Cor.Re-Coding the Vibe
 *
 * Adapted from Claude Code's analytics/index.ts + sink.ts pattern:
 *   - Event queuing until sink attachment (prevents event loss during hydration)
 *   - PII-field stripping before general-access storage
 *   - Sampling support for high-volume events
 *   - Dual-mode: fire-and-forget sync + async with acknowledgment
 *
 * DESIGN: This module has ZERO import dependencies to prevent circular imports.
 * Events are queued in-memory until attachTelemetrySink() is called.
 *
 * Architecture:
 *   PanopticonProvider (client) → usePanopticon hook → telemetry.logEvent()
 *   Server Actions → telemetry.logEvent() (direct)
 *   Both → /api/ops/telemetry (HTTP sink)
 */

// ─────────────────────────────────────────────────────────────
// Type Definitions
// ─────────────────────────────────────────────────────────────

/**
 * Marker type forcing explicit verification that metadata values
 * don't contain code snippets, file paths, or PII.
 * Pattern from Claude Code: AnalyticsMetadata_I_VERIFIED_THIS_IS_NOT_CODE_OR_FILEPATHS
 */
export type VerifiedSafeMetadata = never;

/**
 * Event severity levels aligned with diagnostic tracking patterns.
 */
export type TelemetryEventSeverity = "info" | "warn" | "error" | "critical";

/**
 * Core event metadata — only primitives allowed to prevent accidental PII leakage.
 * Strings are forbidden unless cast through VerifiedSafeMetadata.
 */
export type TelemetryMetadata = {
  [key: string]: boolean | number | undefined;
};

/**
 * Full event payload sent to the telemetry endpoint.
 */
export interface TelemetryEvent {
  eventName: string;
  metadata: TelemetryMetadata;
  timestamp: number;
  sessionId: string;
  severity: TelemetryEventSeverity;
  source: "client" | "server" | "edge";
}

/**
 * Sink interface — the backend that actually dispatches events.
 * Mirrors Claude Code's AnalyticsSink pattern.
 */
export interface TelemetrySink {
  logEvent: (event: TelemetryEvent) => void;
  logEventAsync: (event: TelemetryEvent) => Promise<void>;
  flush: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────
// Internal State
// ─────────────────────────────────────────────────────────────

interface QueuedEvent {
  event: TelemetryEvent;
  async: boolean;
}

const eventQueue: QueuedEvent[] = [];
let sink: TelemetrySink | null = null;
let sessionId: string = "";

// Maximum queue depth before we start dropping oldest events
const MAX_QUEUE_DEPTH = 500;

// ─────────────────────────────────────────────────────────────
// PII Protection (from Claude Code's stripProtoFields pattern)
// ─────────────────────────────────────────────────────────────

/**
 * Strip _PII_ prefixed keys from metadata before general-access storage.
 * PII-tagged fields are only routed to privileged BigQuery columns.
 * Returns same reference if no PII keys found (zero-alloc fast path).
 */
export function stripPiiFields<V>(
  metadata: Record<string, V>,
): Record<string, V> {
  let result: Record<string, V> | undefined;
  for (const key in metadata) {
    if (key.startsWith("_PII_")) {
      if (result === undefined) {
        result = { ...metadata };
      }
      delete result[key];
    }
  }
  return result ?? metadata;
}

// ─────────────────────────────────────────────────────────────
// Sampling (adapted from shouldSampleEvent)
// ─────────────────────────────────────────────────────────────

/**
 * Event sampling configuration.
 * High-frequency events (mousemove, scroll) are sampled to reduce volume.
 */
const SAMPLING_CONFIG: Record<string, number> = {
  "checkout.field_focus": 0.1, // 10% sampling
  "checkout.field_blur": 0.1,
  "ui.scroll": 0.01, // 1% sampling
  "ui.resize": 0.05,
};

/**
 * Determine if an event should be sampled.
 * Returns the sample rate if selected, 0 if dropped, null if no sampling applies.
 */
export function shouldSampleEvent(
  eventName: string,
): number | null {
  const sampleRate = SAMPLING_CONFIG[eventName];
  if (sampleRate === undefined) return null; // No sampling — always log
  if (Math.random() > sampleRate) return 0; // Dropped
  return sampleRate; // Selected — include rate for statistical correction
}

// ─────────────────────────────────────────────────────────────
// Session Management
// ─────────────────────────────────────────────────────────────

/**
 * Generate or retrieve session ID.
 * Server-side: crypto.randomUUID()
 * Client-side: sessionStorage persistence
 */
export function getSessionId(): string {
  if (sessionId) return sessionId;

  if (typeof window !== "undefined") {
    const stored = sessionStorage.getItem("panopticon_session_id");
    if (stored) {
      sessionId = stored;
      return sessionId;
    }
  }

  sessionId = crypto.randomUUID();

  if (typeof window !== "undefined") {
    sessionStorage.setItem("panopticon_session_id", sessionId);
  }

  return sessionId;
}

// ─────────────────────────────────────────────────────────────
// Sink Attachment (from Claude Code's attachAnalyticsSink)
// ─────────────────────────────────────────────────────────────

/**
 * Attach the telemetry sink that will receive all events.
 * Queued events are drained via queueMicrotask to avoid startup latency.
 *
 * Idempotent: subsequent calls are no-ops.
 */
export function attachTelemetrySink(newSink: TelemetrySink): void {
  if (sink !== null) return;
  sink = newSink;

  // Drain the queue asynchronously — pattern from Claude Code
  if (eventQueue.length > 0) {
    const queuedEvents = [...eventQueue];
    eventQueue.length = 0;

    queueMicrotask(() => {
      for (const { event, async: isAsync } of queuedEvents) {
        if (isAsync) {
          void sink!.logEventAsync(event);
        } else {
          sink!.logEvent(event);
        }
      }
    });
  }
}

// ─────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────

/**
 * Log a telemetry event (synchronous, fire-and-forget).
 *
 * If no sink is attached, events are queued (up to MAX_QUEUE_DEPTH).
 * Respects sampling configuration for high-frequency events.
 */
export function logEvent(
  eventName: string,
  metadata: TelemetryMetadata = {},
  severity: TelemetryEventSeverity = "info",
  source: TelemetryEvent["source"] = "client",
): void {
  // Sampling gate
  const sampleResult = shouldSampleEvent(eventName);
  if (sampleResult === 0) return;

  const enrichedMetadata =
    sampleResult !== null
      ? { ...metadata, sample_rate: sampleResult }
      : metadata;

  const event: TelemetryEvent = {
    eventName,
    metadata: enrichedMetadata,
    timestamp: Date.now(),
    sessionId: getSessionId(),
    severity,
    source,
  };

  if (sink === null) {
    // Bounded queue — drop oldest if at capacity
    if (eventQueue.length >= MAX_QUEUE_DEPTH) {
      eventQueue.shift();
    }
    eventQueue.push({ event, async: false });
    return;
  }

  sink.logEvent(event);
}

/**
 * Log a telemetry event (asynchronous, with acknowledgment).
 * Use for critical events where delivery confirmation matters.
 */
export async function logEventAsync(
  eventName: string,
  metadata: TelemetryMetadata = {},
  severity: TelemetryEventSeverity = "info",
  source: TelemetryEvent["source"] = "client",
): Promise<void> {
  const sampleResult = shouldSampleEvent(eventName);
  if (sampleResult === 0) return;

  const enrichedMetadata =
    sampleResult !== null
      ? { ...metadata, sample_rate: sampleResult }
      : metadata;

  const event: TelemetryEvent = {
    eventName,
    metadata: enrichedMetadata,
    timestamp: Date.now(),
    sessionId: getSessionId(),
    severity,
    source,
  };

  if (sink === null) {
    if (eventQueue.length >= MAX_QUEUE_DEPTH) {
      eventQueue.shift();
    }
    eventQueue.push({ event, async: true });
    return;
  }

  await sink.logEventAsync(event);
}

/**
 * Flush all pending events. Call before navigation or page unload.
 */
export async function flushTelemetry(): Promise<void> {
  if (sink) {
    await sink.flush();
  }
}

/**
 * Check if telemetry is disabled (test env or explicit opt-out).
 * Adapted from Claude Code's isAnalyticsDisabled().
 */
export function isTelemetryDisabled(): boolean {
  return (
    process.env.NODE_ENV === "test" ||
    process.env.DISABLE_TELEMETRY === "1" ||
    process.env.DISABLE_ERROR_REPORTING === "1"
  );
}

// ─────────────────────────────────────────────────────────────
// Convenience: Pre-defined Event Names (type-safe catalog)
// ─────────────────────────────────────────────────────────────

export const TELEMETRY_EVENTS = {
  // Checkout flow
  CHECKOUT_STARTED: "checkout.started",
  CHECKOUT_SUBMITTED: "checkout.submitted",
  CHECKOUT_SUCCESS: "checkout.success",
  CHECKOUT_ERROR: "checkout.error",
  CHECKOUT_DUPLICATE_BLOCKED: "checkout.duplicate_blocked",

  // Idempotency
  IDEMPOTENCY_LOCK_ACQUIRED: "idempotency.lock_acquired",
  IDEMPOTENCY_LOCK_REJECTED: "idempotency.lock_rejected",
  IDEMPOTENCY_LOCK_RELEASED: "idempotency.lock_released",

  // Rate limiting
  RATE_LIMIT_HIT: "rate_limit.hit",
  RATE_LIMIT_BYPASS: "rate_limit.bypass_attempt",

  // Page lifecycle
  PAGE_VIEW: "page.view",
  PAGE_UNLOAD: "page.unload",
  PAGE_VISIBILITY_CHANGE: "page.visibility_change",

  // Error tracking
  UNHANDLED_ERROR: "error.unhandled",
  ACTION_ERROR: "error.action",
  NETWORK_ERROR: "error.network",
} as const;

/**
 * Reset telemetry state — testing only.
 * @internal
 */
export function _resetForTesting(): void {
  sink = null;
  eventQueue.length = 0;
  sessionId = "";
}
