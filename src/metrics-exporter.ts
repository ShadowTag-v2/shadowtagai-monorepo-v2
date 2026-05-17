import type { Request, Response } from "express";

/**
 * Prometheus-compatible Metrics Exporter
 * Exposes metrics at /metrics in Prometheus text format
 */

// In-memory metrics store (replace with proper store in production)
const metricsStore = {
  http_requests_total: 0,
  http_request_duration_seconds: [] as number[],
  licenses_granted_total: 0,
  webhooks_received_total: 0,
  errors_total: 0,
  active_connections: 0,
};

export function updateMetric(name: keyof typeof metricsStore, value: number) {
  if (name === "http_request_duration_seconds") {
    metricsStore[name].push(value);
    // Keep only last 1000 values
    if (metricsStore[name].length > 1000) {
      metricsStore[name].shift();
    }
  } else {
    (metricsStore[name] as number) += value;
  }
}

export function getMetricsHandler(req: Request, res: Response) {
  const lines: string[] = [];

  // HTTP Requests Total
  lines.push("# HELP http_requests_total Total number of HTTP requests");
  lines.push("# TYPE http_requests_total counter");
  lines.push(`http_requests_total ${metricsStore.http_requests_total}`);

  // Request Duration
  if (metricsStore.http_request_duration_seconds.length > 0) {
    const durations = metricsStore.http_request_duration_seconds;
    const sum = durations.reduce((a, b) => a + b, 0);
    const count = durations.length;
    const avg = sum / count;

    lines.push("# HELP http_request_duration_seconds HTTP request duration in seconds");
    lines.push("# TYPE http_request_duration_seconds summary");
    lines.push(`http_request_duration_seconds_sum ${sum}`);
    lines.push(`http_request_duration_seconds_count ${count}`);
    lines.push(`http_request_duration_seconds_avg ${avg}`);
  }

  // Licenses Granted
  lines.push("# HELP licenses_granted_total Total number of A2A licenses granted");
  lines.push("# TYPE licenses_granted_total counter");
  lines.push(`licenses_granted_total ${metricsStore.licenses_granted_total}`);

  // Webhooks Received
  lines.push("# HELP webhooks_received_total Total number of Stripe webhooks received");
  lines.push("# TYPE webhooks_received_total counter");
  lines.push(`webhooks_received_total ${metricsStore.webhooks_received_total}`);

  // Errors
  lines.push("# HELP errors_total Total number of errors");
  lines.push("# TYPE errors_total counter");
  lines.push(`errors_total ${metricsStore.errors_total}`);

  // Active Connections
  lines.push("# HELP active_connections Current number of active connections");
  lines.push("# TYPE active_connections gauge");
  lines.push(`active_connections ${metricsStore.active_connections}`);

  res.set("Content-Type", "text/plain; version=0.0.4");
  res.send(lines.join("\n"));
}

// Helper to increment counters
export const metrics = {
  increment: (name: keyof typeof metricsStore) => {
    if (typeof metricsStore[name] === "number") {
      (metricsStore[name] as number)++;
    }
  },
  recordDuration: (duration: number) => {
    metricsStore.http_request_duration_seconds.push(duration);
    if (metricsStore.http_request_duration_seconds.length > 1000) {
      metricsStore.http_request_duration_seconds.shift();
    }
  },
};
