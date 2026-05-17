"use client";

/**
 * PanopticonProvider — Unified Telemetry Context
 *
 * Cor.Re-Coding the Vibe: This provider wires the telemetry sink on mount,
 * establishing the event pipeline from React components to the /api/ops/telemetry
 * endpoint.
 *
 * Architecture (adapted from Claude Code's initializeAnalyticsSink):
 *   1. On mount: attach the HTTP sink to the telemetry module
 *   2. All queued events (from SSR hydration gap) are drained
 *   3. Children gain access to usePanopticon() via this provider's context
 *   4. On unmount: flush all pending events
 *
 * Usage:
 *   <PanopticonProvider>
 *     <App />
 *   </PanopticonProvider>
 */

import { createContext, type ReactNode, useContext, useEffect, useRef } from "react";
import { type PanopticonActions, usePanopticon } from "@/hooks/usePanopticon";
import { createOtelSink } from "@/lib/otel-sink";
import {
  attachTelemetrySink,
  flushTelemetry,
  isTelemetryDisabled,
  stripPiiFields,
  type TelemetryEvent,
  type TelemetrySink,
} from "@/lib/telemetry";

// ─────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────

const PanopticonContext = createContext<PanopticonActions | null>(null);

/**
 * Access the Panopticon telemetry context.
 * Must be used within a PanopticonProvider.
 */
export function usePanopticonContext(): PanopticonActions {
  const ctx = useContext(PanopticonContext);
  if (!ctx) {
    throw new Error("usePanopticonContext must be used within a <PanopticonProvider>");
  }
  return ctx;
}

// ─────────────────────────────────────────────────────────────
// HTTP Sink Implementation
// ─────────────────────────────────────────────────────────────

/**
 * Batched HTTP sink that sends events to /api/ops/telemetry.
 * Adapted from Claude Code's dual-sink (Datadog + 1P) routing pattern,
 * but simplified to a single HTTP endpoint.
 */
function createHttpSink(): TelemetrySink {
  const buffer: TelemetryEvent[] = [];
  let flushTimer: ReturnType<typeof setTimeout> | null = null;
  const FLUSH_INTERVAL_MS = 5000;
  const BATCH_SIZE = 25;

  const sendBatch = async (events: TelemetryEvent[]): Promise<void> => {
    if (events.length === 0) return;

    // Strip PII fields before sending to general-access endpoint
    const sanitizedEvents = events.map((event) => ({
      ...event,
      metadata: stripPiiFields(event.metadata),
    }));

    try {
      const response = await fetch("/api/ops/telemetry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: sanitizedEvents }),
        // Use keepalive for unload scenarios
        keepalive: true,
      });

      if (!response.ok) {
      }
    } catch {
      // Silent failure — telemetry must never break the app
      // Events are lost, which is acceptable for observability data
    }
  };

  const scheduleFlush = () => {
    if (flushTimer) return;
    flushTimer = setTimeout(async () => {
      flushTimer = null;
      if (buffer.length > 0) {
        const batch = buffer.splice(0, BATCH_SIZE);
        await sendBatch(batch);
        // If there are remaining events, schedule another flush
        if (buffer.length > 0) {
          scheduleFlush();
        }
      }
    }, FLUSH_INTERVAL_MS);
  };

  return {
    logEvent: (event: TelemetryEvent) => {
      buffer.push(event);

      // Flush immediately if batch is full
      if (buffer.length >= BATCH_SIZE) {
        const batch = buffer.splice(0, BATCH_SIZE);
        void sendBatch(batch);
      } else {
        scheduleFlush();
      }
    },

    logEventAsync: async (event: TelemetryEvent) => {
      await sendBatch([event]);
    },

    flush: async () => {
      if (flushTimer) {
        clearTimeout(flushTimer);
        flushTimer = null;
      }
      if (buffer.length > 0) {
        const remaining = buffer.splice(0);
        await sendBatch(remaining);
      }
    },
  };
}

// ─────────────────────────────────────────────────────────────
// Provider Component
// ─────────────────────────────────────────────────────────────

interface PanopticonProviderProps {
  children: ReactNode;
  /** Disable telemetry (overrides env check) */
  disabled?: boolean;
}

export function PanopticonProvider({ children, disabled = false }: PanopticonProviderProps) {
  const sinkAttached = useRef(false);
  const panopticon = usePanopticon();

  // Attach the HTTP sink on mount (once)
  // Secondary OTel sink is wired in parallel if configured
  useEffect(() => {
    if (sinkAttached.current || disabled || isTelemetryDisabled()) return;

    const httpSink = createHttpSink();
    const otelSink = createOtelSink();

    // If OTel is configured, create a compound sink that dispatches to both
    const activeSink: TelemetrySink = otelSink
      ? {
          logEvent: (event: TelemetryEvent) => {
            httpSink.logEvent(event);
            try {
              otelSink.logEvent(event);
            } catch {
              // Silent — secondary must never break primary
            }
          },
          logEventAsync: async (event: TelemetryEvent) => {
            // Primary is awaited; secondary is fire-and-forget
            await httpSink.logEventAsync(event);
            otelSink.logEvent(event); // non-blocking
          },
          flush: async () => {
            await httpSink.flush();
            try {
              await otelSink.flush();
            } catch {
              // Silent
            }
          },
        }
      : httpSink;

    attachTelemetrySink(activeSink);
    sinkAttached.current = true;

    // Flush on unmount
    return () => {
      void flushTelemetry();
    };
  }, [disabled]);

  return <PanopticonContext.Provider value={panopticon}>{children}</PanopticonContext.Provider>;
}
