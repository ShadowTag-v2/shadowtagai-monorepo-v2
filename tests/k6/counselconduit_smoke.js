import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.1.0/index.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const healthLatency = new Trend('health_latency');

// Configuration
const BASE_URL = __ENV.COUNSELCONDUIT_URL || 'https://counselconduit-767252945109.us-central1.run.app';

export const options = {
  scenarios: {
    // Smoke test: 2 VUs for 30s
    smoke: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95th percentile < 2s
    error_rate: ['rate<0.1'],          // Error rate < 10%
  },
};

export default function () {
  // Health check endpoint
  const healthRes = http.get(`${BASE_URL}/health`);
  healthLatency.add(healthRes.timings.duration);

  check(healthRes, {
    'health status is 200 or 429': (r) => r.status === 200 || r.status === 429,
    'health latency < 1s': (r) => r.timings.duration < 1000,
  });
  errorRate.add(healthRes.status !== 200 && healthRes.status !== 429);

  // Docs/OpenAPI endpoint (if available)
  const docsRes = http.get(`${BASE_URL}/docs`, {
    redirects: 0,
    tags: { name: 'docs' },
  });
  check(docsRes, {
    'docs reachable': (r) => r.status === 200 || r.status === 301 || r.status === 404 || r.status === 429,
  });

  // Webhook endpoint (POST-only, expect 405 on GET)
  const webhookRes = http.get(`${BASE_URL}/webhooks/stripe`);
  check(webhookRes, {
    'webhook rejects GET': (r) => r.status === 405 || r.status === 429,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}
