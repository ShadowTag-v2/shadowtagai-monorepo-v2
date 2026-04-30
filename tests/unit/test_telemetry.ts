/**
 * Unit tests for src/lib/telemetry.ts
 *
 * Tests stripPiiFields, shouldSampleEvent, and _resetForTesting utility.
 * Uses vitest-compatible patterns (no external runner dependency).
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  stripPiiFields,
  shouldSampleEvent,
  _resetForTesting,
  logEvent,
  attachTelemetrySink,
  isTelemetryDisabled,
  getSessionId,
  type TelemetrySink,
  type TelemetryEvent,
} from "@/lib/telemetry";

// ─────────────────────────────────────────────────────────────
// stripPiiFields
// ─────────────────────────────────────────────────────────────

describe("stripPiiFields", () => {
  it("returns same reference when no PII keys present", () => {
    const metadata = { count: 1, active: true };
    const result = stripPiiFields(metadata);
    expect(result).toBe(metadata); // Same reference — zero-alloc fast path
  });

  it("removes _PII_ prefixed keys", () => {
    const metadata = {
      count: 1,
      _PII_email: "user@example.com",
      _PII_name: "John Doe",
      active: true,
    };
    const result = stripPiiFields(metadata);
    expect(result).toEqual({ count: 1, active: true });
    expect("_PII_email" in result).toBe(false);
    expect("_PII_name" in result).toBe(false);
  });

  it("does not mutate the original object", () => {
    const metadata = { _PII_secret: "hidden", visible: "yes" };
    const result = stripPiiFields(metadata);
    expect(metadata).toHaveProperty("_PII_secret");
    expect(result).not.toHaveProperty("_PII_secret");
  });

  it("handles empty object", () => {
    const metadata = {};
    const result = stripPiiFields(metadata);
    expect(result).toEqual({});
    expect(result).toBe(metadata); // Same ref for empty
  });

  it("handles object with only PII keys", () => {
    const metadata = { _PII_a: 1, _PII_b: 2 };
    const result = stripPiiFields(metadata);
    expect(result).toEqual({});
  });

  it("preserves keys that start with _PII but not _PII_", () => {
    const metadata = { _PIInoUnderscore: "safe", _PII_danger: "unsafe" };
    const result = stripPiiFields(metadata);
    expect(result).toHaveProperty("_PIInoUnderscore");
    expect(result).not.toHaveProperty("_PII_danger");
  });
});

// ─────────────────────────────────────────────────────────────
// shouldSampleEvent
// ─────────────────────────────────────────────────────────────

describe("shouldSampleEvent", () => {
  it("returns null for events not in sampling config", () => {
    expect(shouldSampleEvent("checkout.started")).toBeNull();
    expect(shouldSampleEvent("page.view")).toBeNull();
    expect(shouldSampleEvent("unknown.event")).toBeNull();
  });

  it("returns rate or 0 for sampled events", () => {
    // Run multiple times to cover both paths
    const results = new Set<number | null>();
    for (let i = 0; i < 100; i++) {
      results.add(shouldSampleEvent("checkout.field_focus"));
    }
    // Should contain either 0.1 (selected) or 0 (dropped) — never null
    for (const r of results) {
      expect(r).not.toBeNull();
      expect([0, 0.1]).toContain(r);
    }
  });

  it("respects 1% sampling for ui.scroll", () => {
    const results: (number | null)[] = [];
    for (let i = 0; i < 1000; i++) {
      results.push(shouldSampleEvent("ui.scroll"));
    }
    const selected = results.filter((r) => r !== 0);
    // Statistically, ~10 out of 1000 should be selected (1%)
    // Allow wide margin for randomness
    expect(selected.length).toBeLessThan(100);
    // All selected should have rate 0.01
    for (const r of selected) {
      expect(r).toBe(0.01);
    }
  });
});

// ─────────────────────────────────────────────────────────────
// _resetForTesting
// ─────────────────────────────────────────────────────────────

describe("_resetForTesting", () => {
  beforeEach(() => {
    _resetForTesting();
  });

  it("clears session ID", () => {
    // First call generates a session ID
    const id1 = getSessionId();
    expect(id1).toBeTruthy();

    // Reset clears it
    _resetForTesting();
    const id2 = getSessionId();
    expect(id2).toBeTruthy();
    expect(id2).not.toBe(id1);
  });

  it("clears attached sink", () => {
    const events: TelemetryEvent[] = [];
    const mockSink: TelemetrySink = {
      logEvent: (e) => events.push(e),
      logEventAsync: async (e) => {
        events.push(e);
      },
      flush: async () => {},
    };

    attachTelemetrySink(mockSink);
    logEvent("test.event", { count: 1 });
    expect(events.length).toBe(1);

    // Reset — sink should be cleared, events now queue
    _resetForTesting();
    logEvent("test.after_reset", { count: 2 });
    // Event should NOT have reached the old sink
    expect(events.length).toBe(1);
  });
});

// ─────────────────────────────────────────────────────────────
// Event Queuing (integration-level)
// ─────────────────────────────────────────────────────────────

describe("logEvent queuing", () => {
  beforeEach(() => {
    _resetForTesting();
  });

  it("queues events before sink attachment", () => {
    logEvent("queued.event", { count: 1 });
    logEvent("queued.event2", { count: 2 });
    // No sink — events are queued internally (no crash)
    // We can verify by attaching a sink and checking drain
  });

  it("drains queued events after sink attachment", async () => {
    const events: TelemetryEvent[] = [];
    logEvent("pre.sink", { count: 1 });

    const mockSink: TelemetrySink = {
      logEvent: (e) => events.push(e),
      logEventAsync: async (e) => {
        events.push(e);
      },
      flush: async () => {},
    };

    attachTelemetrySink(mockSink);

    // queueMicrotask drain — wait a tick
    await new Promise((resolve) => setTimeout(resolve, 10));
    expect(events.length).toBe(1);
    expect(events[0].eventName).toBe("pre.sink");
  });
});

// ─────────────────────────────────────────────────────────────
// isTelemetryDisabled
// ─────────────────────────────────────────────────────────────

describe("isTelemetryDisabled", () => {
  it("returns true in test environment", () => {
    // NODE_ENV is 'test' during vitest runs
    expect(isTelemetryDisabled()).toBe(true);
  });
});
