// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * OpenTelemetry Sink — OTLP/HTTP Event Export
 *
 * Secondary telemetry sink that exports events to an OpenTelemetry
 * Collector via the OTLP/HTTP protocol. Runs alongside the primary
 * PanopticonProvider HTTP sink.
 *
 * Architecture:
 *   React Component → PanopticonProvider → HTTP Sink (primary)
 *                                        → OTel Sink (secondary, this module)
 *
 * Configuration:
 *   - NEXT_PUBLIC_OTEL_ENDPOINT: OTLP/HTTP endpoint URL
 *   - NEXT_PUBLIC_OTEL_ENABLED: Enable/disable OTel export (default: false)
 *
 * Protocol:
 *   Events are mapped to OpenTelemetry Log records and batched to the
 *   /v1/logs endpoint. The mapping preserves:
 *   - event_name → LogRecord.body
 *   - metadata → LogRecord.attributes
 *   - timestamp → LogRecord.timeUnixNano
 *   - severity → LogRecord.severityNumber
 *
 * Security:
 *   - PII fields are stripped before export (same pipeline as HTTP sink)
 *   - No auth tokens in client-side code — collector handles auth
 *   - Events are fire-and-forget (no acks)
 */

import type { TelemetryEvent, TelemetrySink } from '@/lib/telemetry';
import { stripPiiFields } from '@/lib/telemetry';

// ── Configuration ────────────────────────────────────────────

const OTEL_ENDPOINT =
  typeof window !== 'undefined' ? (process.env.NEXT_PUBLIC_OTEL_ENDPOINT ?? '') : '';

const OTEL_ENABLED =
  typeof window !== 'undefined' &&
  process.env.NEXT_PUBLIC_OTEL_ENABLED === 'true' &&
  OTEL_ENDPOINT.length > 0;

// ── Severity Mapping ─────────────────────────────────────────

const SEVERITY_MAP: Record<string, number> = {
  info: 9, // SEVERITY_NUMBER_INFO
  warn: 13, // SEVERITY_NUMBER_WARN
  error: 17, // SEVERITY_NUMBER_ERROR
  debug: 5, // SEVERITY_NUMBER_DEBUG
};

// ── OTel Log Record ──────────────────────────────────────────

interface OtelLogRecord {
  timeUnixNano: string;
  severityNumber: number;
  severityText: string;
  body: { stringValue: string };
  attributes: Array<{
    key: string;
    value: { stringValue?: string; intValue?: string; doubleValue?: number; boolValue?: boolean };
  }>;
}

interface OtelLogPayload {
  resourceLogs: Array<{
    resource: {
      attributes: Array<{ key: string; value: { stringValue: string } }>;
    };
    scopeLogs: Array<{
      scope: { name: string; version: string };
      logRecords: OtelLogRecord[];
    }>;
  }>;
}

// ── Event → OTel Mapping ─────────────────────────────────────

function eventToLogRecord(event: TelemetryEvent): OtelLogRecord {
  const sanitizedMeta = stripPiiFields(event.metadata);
  const severity = event.severity ?? 'info';
  const nowNano = BigInt(Date.now()) * BigInt(1_000_000);

  const attributes = Object.entries(sanitizedMeta).map(([key, value]) => {
    if (typeof value === 'number') {
      return Number.isInteger(value)
        ? { key, value: { intValue: String(value) } }
        : { key, value: { doubleValue: value } };
    }
    if (typeof value === 'boolean') {
      return { key, value: { boolValue: value } };
    }
    return { key, value: { stringValue: String(value) } };
  });

  return {
    timeUnixNano: nowNano.toString(),
    severityNumber: SEVERITY_MAP[severity] ?? 9,
    severityText: severity.toUpperCase(),
    body: { stringValue: event.eventName },
    attributes,
  };
}

function buildPayload(events: TelemetryEvent[]): OtelLogPayload {
  return {
    resourceLogs: [
      {
        resource: {
          attributes: [
            { key: 'service.name', value: { stringValue: 'counselconduit-frontend' } },
            { key: 'service.version', value: { stringValue: '14.6' } },
          ],
        },
        scopeLogs: [
          {
            scope: { name: 'panopticon', version: '1.0.0' },
            logRecords: events.map(eventToLogRecord),
          },
        ],
      },
    ],
  };
}

// ── Sink Implementation ──────────────────────────────────────

/**
 * Creates an OpenTelemetry-compatible telemetry sink.
 *
 * Events are batched and sent to the OTLP/HTTP /v1/logs endpoint.
 * Returns null if OTel is not configured.
 */
export function createOtelSink(): TelemetrySink | null {
  if (!OTEL_ENABLED) return null;

  const buffer: TelemetryEvent[] = [];
  let flushTimer: ReturnType<typeof setTimeout> | null = null;
  const FLUSH_INTERVAL_MS = 10_000; // 10s batch window (longer than primary)
  const BATCH_SIZE = 50;

  const endpoint = `${OTEL_ENDPOINT.replace(/\/+$/, '')}/v1/logs`;

  const sendBatch = async (events: TelemetryEvent[]): Promise<void> => {
    if (events.length === 0) return;

    const payload = buildPayload(events);

    try {
      await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        keepalive: true,
      });
    } catch {
      // Silent failure — OTel export must never break the app
    }
  };

  const scheduleFlush = () => {
    if (flushTimer) return;
    flushTimer = setTimeout(async () => {
      flushTimer = null;
      if (buffer.length > 0) {
        const batch = buffer.splice(0, BATCH_SIZE);
        await sendBatch(batch);
        if (buffer.length > 0) scheduleFlush();
      }
    }, FLUSH_INTERVAL_MS);
  };

  return {
    logEvent: (event: TelemetryEvent) => {
      buffer.push(event);
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
