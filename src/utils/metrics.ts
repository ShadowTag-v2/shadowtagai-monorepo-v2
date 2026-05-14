/**
 * Prometheus metrics for monitoring
 */

import client from "prom-client";
import type { Mode } from "../types";

// Enable default metrics (CPU, memory, etc.)
client.collectDefaultMetrics({ prefix: "pnkln_" });

// Custom metrics
const requestCounter = new client.Counter({
  name: "pnkln_requests_total",
  help: "Total number of requests processed",
  labelNames: ["mode", "status"],
});

const requestDuration = new client.Histogram({
  name: "pnkln_request_duration_seconds",
  help: "Request duration in seconds",
  labelNames: ["mode"],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
});

const vertexCallCounter = new client.Counter({
  name: "pnkln_vertex_calls_total",
  help: "Total number of Vertex AI API calls",
  labelNames: ["mode", "status"],
});

const vertexCallDuration = new client.Histogram({
  name: "pnkln_vertex_call_duration_seconds",
  help: "Vertex AI call duration in seconds",
  labelNames: ["mode"],
  buckets: [0.5, 1, 2, 5, 10, 20, 30],
});

const vertexTokensCounter = new client.Counter({
  name: "pnkln_vertex_tokens_total",
  help: "Total tokens used in Vertex AI calls",
  labelNames: ["type"], // 'input' or 'output'
});

const revenueGauge = new client.Gauge({
  name: "pnkln_revenue_dollars",
  help: "Revenue generated in dollars",
});

const costGauge = new client.Gauge({
  name: "pnkln_cost_dollars",
  help: "Cost incurred in dollars",
});

const profitGauge = new client.Gauge({
  name: "pnkln_profit_dollars",
  help: "Net profit in dollars",
});

class Metrics {
  /**
   * Record a request
   */
  recordRequest(mode: Mode, durationMs: number, success: boolean) {
    requestCounter.inc({
      mode,
      status: success ? "success" : "error",
    });

    requestDuration.observe({ mode }, durationMs / 1000);
  }

  /**
   * Record a Vertex AI call
   */
  recordVertexCall(mode: Mode, durationMs: number, inputTokens: number, outputTokens: number) {
    vertexCallCounter.inc({ mode, status: "success" });
    vertexCallDuration.observe({ mode }, durationMs / 1000);
    vertexTokensCounter.inc({ type: "input" }, inputTokens);
    vertexTokensCounter.inc({ type: "output" }, outputTokens);
  }

  /**
   * Record a Vertex AI error
   */
  recordVertexError(mode: Mode) {
    vertexCallCounter.inc({ mode, status: "error" });
  }

  /**
   * Record revenue impact
   */
  recordRevenueImpact(netProfit: number) {
    profitGauge.inc(netProfit);
  }

  /**
   * Update revenue gauge
   */
  setRevenue(amount: number) {
    revenueGauge.set(amount);
  }

  /**
   * Update cost gauge
   */
  setCost(amount: number) {
    costGauge.set(amount);
  }

  /**
   * Get all metrics in Prometheus format
   */
  async getMetrics(): Promise<string> {
    return client.register.metrics();
  }

  /**
   * Get metrics as JSON
   */
  async getMetricsJSON(): Promise<unknown> {
    const metrics = await client.register.getMetricsAsJSON();
    return metrics;
  }
}

export const metrics = new Metrics();
