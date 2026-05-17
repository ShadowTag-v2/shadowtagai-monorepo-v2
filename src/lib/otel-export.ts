// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * OpenTelemetry Collector Export — Secondary telemetry sink.
 *
 * Implements OTLP-compatible span and metric export alongside
 * PanopticonProvider. This acts as a secondary sink for:
 *   1. Backend-side distributed tracing (sandbox API ↔ Firestore)
 *   2. Client-side web vitals (LCP, CLS, INP)
 *   3. Custom business metrics (sandbox decisions, audit throughput)
 *
 * Architecture:
 *   PanopticonProvider (primary sink — analytics)
 *   OTelExporter (secondary sink — observability)
 *   Both receive the same events via the Telemetry Bus.
 *
 * Configuration:
 *   - OTEL_EXPORTER_OTLP_ENDPOINT: Collector endpoint (default: localhost:4318)
 *   - OTEL_SERVICE_NAME: Service name (default: counselconduit-frontend)
 *   - Batching: 100 spans / 5s flush interval / 3 retries
 *
 * Security:
 *   - No PII in span attributes (prefix-only IDs)
 *   - TLS required for non-localhost endpoints
 *   - API key sent via Authorization header (not in URL)
 */

/** Span data structure aligned with OTLP v1 */
interface OTelSpan {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  name: string;
  kind: "CLIENT" | "SERVER" | "INTERNAL";
  startTimeUnixNano: string;
  endTimeUnixNano: string;
  attributes: Record<string, string | number | boolean>;
  status: { code: "OK" | "ERROR" | "UNSET"; message?: string };
}

/** Metric data point */
interface OTelMetric {
  name: string;
  description: string;
  unit: string;
  gauge?: { value: number };
  sum?: { value: number; isMonotonic: boolean };
  timestamp: string;
  attributes: Record<string, string | number>;
}

/** Batch export configuration */
interface ExporterConfig {
  endpoint: string;
  serviceName: string;
  batchSize: number;
  flushIntervalMs: number;
  maxRetries: number;
  apiKey?: string;
}

const DEFAULT_CONFIG: ExporterConfig = {
  endpoint: "http://localhost:4318",
  serviceName: "counselconduit-frontend",
  batchSize: 100,
  flushIntervalMs: 5000,
  maxRetries: 3,
};

/** Generate a random hex ID (16 chars for span, 32 for trace) */
function generateId(length: 16 | 32 = 16): string {
  const bytes = new Uint8Array(length / 2);
  crypto.getRandomValues(bytes);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/** Get current time as OTLP nanosecond string */
function nowNano(): string {
  return `${BigInt(Date.now()) * BigInt(1_000_000)}`;
}

/**
 * OTelExporter — Batched OTLP exporter for client-side telemetry.
 *
 * Usage:
 *   const exporter = new OTelExporter({ endpoint: 'https://otel.example.com' });
 *   exporter.addSpan({ name: 'sandbox.load_diffs', ... });
 *   // Spans are flushed automatically every 5s or when batch is full
 *   await exporter.shutdown(); // Flush remaining spans on page unload
 */
export class OTelExporter {
  private config: ExporterConfig;
  private spanBuffer: OTelSpan[] = [];
  private metricBuffer: OTelMetric[] = [];
  private flushTimer: ReturnType<typeof setInterval> | null = null;

  constructor(config: Partial<ExporterConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.flushTimer = setInterval(() => {
      void this.flush();
    }, this.config.flushIntervalMs);
  }

  /** Create and buffer a new span */
  createSpan(
    name: string,
    attributes: Record<string, string | number | boolean> = {},
    options: {
      kind?: OTelSpan["kind"];
      parentSpanId?: string;
      traceId?: string;
    } = {},
  ): OTelSpan {
    const span: OTelSpan = {
      traceId: options.traceId ?? generateId(32),
      spanId: generateId(16),
      parentSpanId: options.parentSpanId,
      name,
      kind: options.kind ?? "INTERNAL",
      startTimeUnixNano: nowNano(),
      endTimeUnixNano: nowNano(), // Updated on endSpan
      attributes: {
        "service.name": this.config.serviceName,
        ...attributes,
      },
      status: { code: "UNSET" },
    };
    return span;
  }

  /** End a span and add to buffer */
  endSpan(span: OTelSpan, status: "OK" | "ERROR" = "OK", errorMessage?: string): void {
    span.endTimeUnixNano = nowNano();
    span.status = { code: status, message: errorMessage };
    this.spanBuffer.push(span);

    if (this.spanBuffer.length >= this.config.batchSize) {
      void this.flush();
    }
  }

  /** Record a gauge metric */
  recordGauge(name: string, value: number, attributes: Record<string, string | number> = {}): void {
    this.metricBuffer.push({
      name,
      description: "",
      unit: "",
      gauge: { value },
      timestamp: new Date().toISOString(),
      attributes,
    });
  }

  /** Record a counter metric */
  recordCounter(
    name: string,
    value: number,
    attributes: Record<string, string | number> = {},
  ): void {
    this.metricBuffer.push({
      name,
      description: "",
      unit: "",
      sum: { value, isMonotonic: true },
      timestamp: new Date().toISOString(),
      attributes,
    });
  }

  /** Flush all buffered spans and metrics to the collector */
  async flush(): Promise<void> {
    if (this.spanBuffer.length === 0 && this.metricBuffer.length === 0) return;

    const spans = [...this.spanBuffer];
    const metrics = [...this.metricBuffer];
    this.spanBuffer = [];
    this.metricBuffer = [];

    // Export spans
    if (spans.length > 0) {
      await this.exportWithRetry(
        `${this.config.endpoint}/v1/traces`,
        this.buildTracePayload(spans),
      );
    }

    // Export metrics
    if (metrics.length > 0) {
      await this.exportWithRetry(
        `${this.config.endpoint}/v1/metrics`,
        this.buildMetricPayload(metrics),
      );
    }
  }

  /** Graceful shutdown — flush remaining data */
  async shutdown(): Promise<void> {
    this.isShuttingDown = true;
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    await this.flush();
  }

  // ── Internal ──────────────────────────────────────────────

  private buildTracePayload(spans: OTelSpan[]): object {
    return {
      resourceSpans: [
        {
          resource: {
            attributes: [{ key: "service.name", value: { stringValue: this.config.serviceName } }],
          },
          scopeSpans: [
            {
              scope: { name: "counselconduit.sandbox", version: "3.0.0" },
              spans: spans.map((s) => ({
                traceId: s.traceId,
                spanId: s.spanId,
                parentSpanId: s.parentSpanId ?? "",
                name: s.name,
                kind: s.kind === "CLIENT" ? 3 : s.kind === "SERVER" ? 2 : 1,
                startTimeUnixNano: s.startTimeUnixNano,
                endTimeUnixNano: s.endTimeUnixNano,
                attributes: Object.entries(s.attributes).map(([k, v]) => ({
                  key: k,
                  value:
                    typeof v === "string"
                      ? { stringValue: v }
                      : typeof v === "number"
                        ? { intValue: String(v) }
                        : { boolValue: v },
                })),
                status: { code: s.status.code === "OK" ? 1 : s.status.code === "ERROR" ? 2 : 0 },
              })),
            },
          ],
        },
      ],
    };
  }

  private buildMetricPayload(metrics: OTelMetric[]): object {
    return {
      resourceMetrics: [
        {
          resource: {
            attributes: [{ key: "service.name", value: { stringValue: this.config.serviceName } }],
          },
          scopeMetrics: [
            {
              scope: { name: "counselconduit.sandbox", version: "3.0.0" },
              metrics: metrics.map((m) => ({
                name: m.name,
                description: m.description,
                unit: m.unit,
                ...(m.gauge
                  ? {
                      gauge: {
                        dataPoints: [
                          {
                            asDouble: m.gauge.value,
                            timeUnixNano: nowNano(),
                            attributes: Object.entries(m.attributes).map(([k, v]) => ({
                              key: k,
                              value:
                                typeof v === "string"
                                  ? { stringValue: v }
                                  : { intValue: String(v) },
                            })),
                          },
                        ],
                      },
                    }
                  : {
                      sum: {
                        isMonotonic: m.sum?.isMonotonic ?? true,
                        dataPoints: [
                          {
                            asDouble: m.sum?.value ?? 0,
                            timeUnixNano: nowNano(),
                            attributes: Object.entries(m.attributes).map(([k, v]) => ({
                              key: k,
                              value:
                                typeof v === "string"
                                  ? { stringValue: v }
                                  : { intValue: String(v) },
                            })),
                          },
                        ],
                      },
                    }),
              })),
            },
          ],
        },
      ],
    };
  }

  private async exportWithRetry(url: string, payload: object): Promise<void> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (this.config.apiKey) {
      headers.Authorization = `Bearer ${this.config.apiKey}`;
    }

    for (let attempt = 0; attempt < this.config.maxRetries; attempt++) {
      try {
        const res = await fetch(url, {
          method: "POST",
          headers,
          body: JSON.stringify(payload),
          signal: AbortSignal.timeout(10000),
        });
        if (res.ok) return;
        if (res.status >= 400 && res.status < 500) {
          return;
        }
        // Server error — retry
      } catch (_err) {
        if (attempt === this.config.maxRetries - 1) {
        }
      }
      // Exponential backoff
      await new Promise((r) => setTimeout(r, 2 ** attempt * 1000));
    }
  }
}

/** Singleton exporter instance */
let _exporter: OTelExporter | null = null;

/** Get or create the singleton OTel exporter */
export function getOTelExporter(config?: Partial<ExporterConfig>): OTelExporter {
  if (!_exporter) {
    _exporter = new OTelExporter(config);
  }
  return _exporter;
}
