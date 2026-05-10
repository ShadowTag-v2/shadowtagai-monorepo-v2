// k6 Load Test: NadirClaw Dispatch Endpoint
// Run: k6 run apps/counselconduit/tests/k6_dispatch_load.js
//
// Scenarios:
//   - smoke:   1 VU,  10s  — baseline sanity
//   - load:   50 VUs, 60s  — sustained throughput
//   - stress: 200 VUs, 30s — breaking point discovery

import { check, sleep } from 'k6';
import http from 'k6/http';
import { Rate, Trend } from 'k6/metrics';

// ── Custom Metrics ──────────────────────────────────────────────────────

const dispatchLatency = new Trend('dispatch_latency_ms');
const errorRate = new Rate('dispatch_errors');
const circuitBreakerHits = new Rate('circuit_breaker_hits');

// ── Configuration ───────────────────────────────────────────────────────

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '10s',
      startTime: '0s',
      tags: { scenario: 'smoke' },
    },
    load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '60s',
      startTime: '15s',
      tags: { scenario: 'load' },
    },
    stress: {
      executor: 'ramping-vus',
      startVUs: 10,
      stages: [
        { duration: '10s', target: 100 },
        { duration: '20s', target: 200 },
        { duration: '10s', target: 0 },
      ],
      startTime: '80s',
      tags: { scenario: 'stress' },
    },
  },
  thresholds: {
    dispatch_latency_ms: ['p(95)<50', 'p(99)<100'], // NadirClaw: <50ms p95
    dispatch_errors: ['rate<0.05'], // <5% error rate
    circuit_breaker_hits: ['rate<0.01'], // <1% circuit breaker
    http_req_duration: ['p(95)<200'], // overall HTTP <200ms p95
  },
};

// ── Test Data ───────────────────────────────────────────────────────────

const QUERIES = {
  simple: ['What is a deposition?', 'Define habeas corpus', 'What does pro bono mean?'],
  complex: [
    'Explain the difference between civil and criminal liability in tort cases',
    'What are the implications of the Chevron doctrine reversal for administrative law?',
    'How does attorney-client privilege interact with the crime-fraud exception?',
  ],
  agentic: [
    'Analyze this employment contract for non-compete clause enforceability across all 50 states. Draft a memo summarizing jurisdiction-specific risks and recommend amendments to protect the employee while maintaining reasonable employer protections.',
    'Review the attached merger agreement and compare its representations and warranties section against the ABA Model Stock Purchase Agreement. Find precedent from Delaware Chancery cases decided in the last 3 years.',
  ],
};

const FIRM_IDS = ['firm-001', 'firm-002', 'firm-003', 'firm-enterprise'];
const TIERS = ['trial', 'professional', 'enterprise'];

// ── Helper Functions ────────────────────────────────────────────────────

function randomFrom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function getRandomQuery() {
  const tier = randomFrom(['simple', 'complex', 'agentic']);
  return { query: randomFrom(QUERIES[tier]), expectedTier: tier };
}

// ── Main Test ───────────────────────────────────────────────────────────

export default function () {
  const { query, expectedTier } = getRandomQuery();
  const firmId = randomFrom(FIRM_IDS);
  const userTier = randomFrom(TIERS);

  const payload = JSON.stringify({
    query: query,
    firm_id: firmId,
    session_id: `sess-${__VU}-${__ITER}`,
    firm_allowed_models: ['gemini-flash', 'gemini-pro', 'claude-sonnet'],
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-User-Tier': userTier,
    },
    tags: { expected_tier: expectedTier },
  };

  const res = http.post(`${BASE_URL}/api/v1/dispatch`, payload, params);

  // Track custom metrics
  if (res.status === 200) {
    const body = JSON.parse(res.body);
    dispatchLatency.add(body.latency_ms || 0);
    errorRate.add(false);
    circuitBreakerHits.add(false);

    check(res, {
      'status is 200': (r) => r.status === 200,
      'has model': () => body.model !== undefined,
      'has provider': () => body.provider !== undefined,
      'has tier': () => body.tier !== undefined,
      'latency under 50ms': () => body.latency_ms < 50,
      'has rate-limit headers': (r) => r.headers['X-Ratelimit-Limit'] !== undefined,
    });
  } else if (res.status === 503) {
    circuitBreakerHits.add(true);
    errorRate.add(true);
  } else if (res.status === 429) {
    errorRate.add(false); // rate limit is expected behavior, not an error
  } else {
    errorRate.add(true);
  }

  sleep(0.1); // 100ms think time
}

// ── Metrics Endpoint Test ───────────────────────────────────────────────

export function metricsCheck() {
  const res = http.get(`${BASE_URL}/admin/metrics`);
  check(res, {
    'metrics status 200': (r) => r.status === 200,
    'has dispatch_counts': () => {
      const body = JSON.parse(res.body);
      return body.dispatch_counts !== undefined;
    },
    'has total_dispatches': () => {
      const body = JSON.parse(res.body);
      return body.total_dispatches >= 0;
    },
  });
}

// ── Circuit Breaker Status Test ─────────────────────────────────────────

export function circuitBreakerCheck() {
  const res = http.get(`${BASE_URL}/admin/circuit-breaker`);
  check(res, {
    'circuit breaker status 200': (r) => r.status === 200,
    'circuit breaker initially closed': () => {
      const body = JSON.parse(res.body);
      return body.open === false;
    },
  });
}
