// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Tengu Telemetry Gates — Non-blocking analytics configuration.
 *
 * All telemetry gates use `getFeatureValue_CACHED_MAY_BE_STALE` because:
 * 1. Telemetry is never user-blocking — stale config is acceptable
 * 2. These values are read in hot paths (every event emission)
 * 3. The `reactive: true` flag means changes propagate via the
 *    GrowthBook `refreshed` signal to rebuild LoggerProviders
 *
 * @see src/services/analytics/firstPartyEventLogger.ts for batch config consumer
 * @see src/services/analytics/sink.ts for killswitch consumer
 */

import { getFeatureValue_CACHED_MAY_BE_STALE } from "../services/analytics/growthbook.js";
import { logForDebugging } from "../utils/debug.js";
import { TENGU_GATES } from "./tengu_registry.js";

// ─── Batch Config ──────────────────────────────────────────────────

export interface EventBatchConfig {
  /** Maximum events per batch before auto-flush. */
  readonly maxBatchSize?: number;
  /** Flush interval in milliseconds. */
  readonly flushIntervalMs?: number;
  /** Maximum queue depth before dropping events. */
  readonly maxQueueDepth?: number;
  /** Whether to enable compression. */
  readonly compress?: boolean;
}

/**
 * Get the first-party event batch configuration.
 *
 * Returns the remote config or defaults. This value is read once
 * during LoggerProvider construction and refreshed via the
 * `refreshed` signal.
 */
export function getEventBatchConfig(): EventBatchConfig {
  const raw = getFeatureValue_CACHED_MAY_BE_STALE(
    TENGU_GATES.event_batch_config.key,
    TENGU_GATES.event_batch_config.defaultValue,
  ) as Record<string, unknown>;

  return {
    maxBatchSize: typeof raw.maxBatchSize === "number" ? raw.maxBatchSize : 100,
    flushIntervalMs: typeof raw.flushIntervalMs === "number" ? raw.flushIntervalMs : 30_000,
    maxQueueDepth: typeof raw.maxQueueDepth === "number" ? raw.maxQueueDepth : 5000,
    compress: typeof raw.compress === "boolean" ? raw.compress : false,
  };
}

// ─── Event Sampling ────────────────────────────────────────────────

/**
 * Get the sampling rate for a specific event type.
 *
 * Returns a number between 0 (never sample) and 1 (always sample).
 * Events not in the config default to 1.0 (always sample).
 */
export function getEventSamplingRate(eventName: string): number {
  const config = getFeatureValue_CACHED_MAY_BE_STALE(
    TENGU_GATES.event_sampling.key,
    TENGU_GATES.event_sampling.defaultValue,
  ) as Record<string, number>;

  const rate = config[eventName];
  if (typeof rate === "number" && rate >= 0 && rate <= 1) {
    return rate;
  }
  return 1.0; // Default: sample everything
}

/**
 * Check if an event should be sampled (for hot-path use).
 *
 * Uses Math.random() against the configured sampling rate.
 * Deterministic sampling (hash-based) should be used for
 * events that need consistency within a session.
 */
export function shouldSampleEvent(eventName: string): boolean {
  const rate = getEventSamplingRate(eventName);
  if (rate >= 1) return true;
  if (rate <= 0) return false;
  return Math.random() < rate;
}

// ─── Sink Killswitch ───────────────────────────────────────────────

/**
 * Check if analytics sinks are killed (emergency shutdown).
 *
 * When true, all analytics sinks should stop accepting events.
 * This is an emergency control for when telemetry infra is causing
 * user-facing issues (e.g., blocking the main loop, disk fills).
 */
export function isSinkKilled(): boolean {
  return getFeatureValue_CACHED_MAY_BE_STALE(
    TENGU_GATES.sink_killswitch.key,
    TENGU_GATES.sink_killswitch.defaultValue as boolean,
  );
}

// ─── Diagnostics ───────────────────────────────────────────────────

/**
 * Get a diagnostic summary of all telemetry gates.
 *
 * Useful for `/debug telemetry` output or health checks.
 */
export function getTelemetryDiagnostics(): Record<string, unknown> {
  const batchConfig = getEventBatchConfig();
  const sinkKilled = isSinkKilled();

  const diagnostics = {
    batchConfig,
    sinkKilled,
    samplingConfigPresent:
      Object.keys(
        getFeatureValue_CACHED_MAY_BE_STALE(
          TENGU_GATES.event_sampling.key,
          TENGU_GATES.event_sampling.defaultValue,
        ) as Record<string, unknown>,
      ).length > 0,
    timestamp: new Date().toISOString(),
  };

  logForDebugging(`[tengu-telemetry] ${JSON.stringify(diagnostics)}`);
  return diagnostics;
}
