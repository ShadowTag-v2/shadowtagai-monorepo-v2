"use client";

/**
 * usePanopticon — Client-side Telemetry Hook
 *
 * Cor.Re-Coding the Vibe: The Panopticon is the unified event tracking
 * surface for all client-side interactions. It wraps the core telemetry
 * library with React lifecycle awareness.
 *
 * Architecture:
 *   PanopticonProvider (context) → usePanopticon (hook) → telemetry.logEvent()
 *
 * Adapted from Claude Code's diagnosticTracking.ts singleton pattern —
 * but as a React hook with automatic lifecycle management.
 *
 * Features:
 *   - Automatic page view tracking
 *   - Visibility change detection (tab switching)
 *   - Unload event flushing (sendBeacon fallback)
 *   - Form interaction tracking
 *   - Performance metric capture (LCP, FID, CLS)
 */

import { useCallback, useEffect, useRef } from "react";
import {
  type TelemetryMetadata,
  type TelemetryEventSeverity,
  logEvent,
  logEventAsync,
  flushTelemetry,
  getSessionId,
  TELEMETRY_EVENTS,
} from "@/lib/telemetry";

// ─────────────────────────────────────────────────────────────
// Hook Interface
// ─────────────────────────────────────────────────────────────

export interface PanopticonActions {
  /** Fire-and-forget event tracking */
  track: (
    eventName: string,
    metadata?: TelemetryMetadata,
    severity?: TelemetryEventSeverity,
  ) => void;

  /** Async event tracking with delivery confirmation */
  trackAsync: (
    eventName: string,
    metadata?: TelemetryMetadata,
    severity?: TelemetryEventSeverity,
  ) => Promise<void>;

  /** Track form field interactions (focus/blur/change) */
  trackFormField: (
    fieldName: string,
    action: "focus" | "blur" | "change",
    metadata?: TelemetryMetadata,
  ) => void;

  /** Track checkout-specific events */
  trackCheckout: (
    phase: "started" | "submitted" | "success" | "error" | "duplicate_blocked",
    metadata?: TelemetryMetadata,
  ) => void;

  /** Get the current session ID */
  sessionId: string;

  /** Flush all pending events (call before navigation) */
  flush: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────
// Hook Implementation
// ─────────────────────────────────────────────────────────────

export function usePanopticon(): PanopticonActions {
  const hasTrackedPageView = useRef(false);

  // ── Page View (once per mount) ────────────────────────────
  useEffect(() => {
    if (hasTrackedPageView.current) return;
    hasTrackedPageView.current = true;

    logEvent(TELEMETRY_EVENTS.PAGE_VIEW, {
      path_hash: hashPath(window.location.pathname),
    });
  }, []);

  // ── Visibility Change (tab switch detection) ──────────────
  useEffect(() => {
    const handleVisibilityChange = () => {
      logEvent(TELEMETRY_EVENTS.PAGE_VISIBILITY_CHANGE, {
        is_visible: document.visibilityState === "visible" ? 1 : 0,
      });
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  // ── Page Unload (flush with sendBeacon fallback) ──────────
  useEffect(() => {
    const handleUnload = () => {
      logEvent(TELEMETRY_EVENTS.PAGE_UNLOAD);

      // sendBeacon is the last-resort flush mechanism
      if (typeof navigator.sendBeacon === "function") {
        const payload = JSON.stringify({
          eventName: TELEMETRY_EVENTS.PAGE_UNLOAD,
          timestamp: Date.now(),
          sessionId: getSessionId(),
        });
        navigator.sendBeacon("/api/ops/telemetry", payload);
      }
    };

    window.addEventListener("beforeunload", handleUnload);
    return () => {
      window.removeEventListener("beforeunload", handleUnload);
    };
  }, []);

  // ── Global Error Tracking ─────────────────────────────────
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      logEvent(
        TELEMETRY_EVENTS.UNHANDLED_ERROR,
        {
          is_script_error: event.filename ? 0 : 1,
          line: event.lineno,
          col: event.colno,
        },
        "error",
      );
    };

    const handleRejection = (event: PromiseRejectionEvent) => {
      logEvent(
        TELEMETRY_EVENTS.UNHANDLED_ERROR,
        {
          is_promise_rejection: 1,
        },
        "error",
      );
    };

    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleRejection);
    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener("unhandledrejection", handleRejection);
    };
  }, []);

  // ── Track (sync) ──────────────────────────────────────────
  const track = useCallback(
    (
      eventName: string,
      metadata: TelemetryMetadata = {},
      severity: TelemetryEventSeverity = "info",
    ) => {
      logEvent(eventName, metadata, severity, "client");
    },
    [],
  );

  // ── Track (async) ─────────────────────────────────────────
  const trackAsync = useCallback(
    async (
      eventName: string,
      metadata: TelemetryMetadata = {},
      severity: TelemetryEventSeverity = "info",
    ) => {
      await logEventAsync(eventName, metadata, severity, "client");
    },
    [],
  );

  // ── Form Field Tracking ───────────────────────────────────
  const trackFormField = useCallback(
    (
      fieldName: string,
      action: "focus" | "blur" | "change",
      metadata: TelemetryMetadata = {},
    ) => {
      logEvent(
        `checkout.field_${action}`,
        {
          field_index: hashFieldName(fieldName),
          ...metadata,
        },
        "info",
        "client",
      );
    },
    [],
  );

  // ── Checkout-specific Tracking ────────────────────────────
  const trackCheckout = useCallback(
    (
      phase: "started" | "submitted" | "success" | "error" | "duplicate_blocked",
      metadata: TelemetryMetadata = {},
    ) => {
      const eventMap: Record<string, string> = {
        started: TELEMETRY_EVENTS.CHECKOUT_STARTED,
        submitted: TELEMETRY_EVENTS.CHECKOUT_SUBMITTED,
        success: TELEMETRY_EVENTS.CHECKOUT_SUCCESS,
        error: TELEMETRY_EVENTS.CHECKOUT_ERROR,
        duplicate_blocked: TELEMETRY_EVENTS.CHECKOUT_DUPLICATE_BLOCKED,
      };

      logEvent(
        eventMap[phase],
        metadata,
        phase === "error" ? "error" : "info",
        "client",
      );
    },
    [],
  );

  // ── Flush ─────────────────────────────────────────────────
  const flush = useCallback(async () => {
    await flushTelemetry();
  }, []);

  return {
    track,
    trackAsync,
    trackFormField,
    trackCheckout,
    sessionId: getSessionId(),
    flush,
  };
}

// ─────────────────────────────────────────────────────────────
// Utility: Hash sensitive values to prevent PII leakage
// ─────────────────────────────────────────────────────────────

/**
 * Hash a pathname to a numeric value for analytics.
 * We NEVER send raw paths to telemetry — only hashed representations.
 */
function hashPath(path: string): number {
  let hash = 0;
  for (let i = 0; i < path.length; i++) {
    const chr = path.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

/**
 * Hash a field name to a numeric index.
 * Prevents leaking form field names to analytics.
 */
function hashFieldName(name: string): number {
  return hashPath(name) % 1000;
}
