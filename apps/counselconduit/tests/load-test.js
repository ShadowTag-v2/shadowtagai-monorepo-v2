// apps/counselconduit/tests/load-test.js
// k6 Load Test Suite — CounselConduit Dispatch & Health
//
// Usage:
//   k6 run --vus 5 --duration 60s apps/counselconduit/tests/load-test.js
//   k6 run --vus 20 --duration 120s apps/counselconduit/tests/load-test.js  # stress
//
// Environment:
//   BASE_URL - override the target URL (default: production Cloud Run)

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'https://counselconduit-767252945109.us-central1.run.app';

// Custom metrics
const dispatchDuration = new Trend('dispatch_duration_ms');
const healthDuration = new Trend('health_duration_ms');
const dispatchErrors = new Counter('dispatch_errors');
const successRate = new Rate('check_success_rate');

export let options = {
  stages: [
    { duration: '10s', target: 5 },   // ramp up
    { duration: '40s', target: 10 },   // sustained load
    { duration: '10s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    health_duration_ms: ['p(99)<500'],
    dispatch_duration_ms: ['p(95)<2000'],
    check_success_rate: ['rate>0.90'],
  },
};

export default function () {
  // 1. Health check (lightweight)
  let health = http.get(`${BASE_URL}/health`);
  healthDuration.add(health.timings.duration);
  let healthOk = check(health, {
    'health status 200': (r) => r.status === 200,
    'health body has status': (r) => JSON.parse(r.body).status === 'healthy',
  });
  successRate.add(healthOk);

  // 2. Dispatch routing
  let payload = JSON.stringify({
    query: 'Analyze the privilege implications under Upjohn v. United States for in-house counsel communications.',
    firm_id: `k6-firm-${__VU}`,
    session_id: `k6-session-${__VU}-${__ITER}`,
  });

  let dispatch = http.post(`${BASE_URL}/api/v1/dispatch`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  dispatchDuration.add(dispatch.timings.duration);

  let dispatchOk = check(dispatch, {
    'dispatch status 200': (r) => r.status === 200,
    'dispatch has model': (r) => {
      try { return JSON.parse(r.body).model !== undefined; } catch { return false; }
    },
    'dispatch has tier': (r) => {
      try { return ['simple', 'complex', 'agentic'].includes(JSON.parse(r.body).tier); } catch { return false; }
    },
    'has rate-limit headers': (r) => r.headers['X-Ratelimit-Limit'] !== undefined,
  });

  if (!dispatchOk) {
    dispatchErrors.add(1);
  }
  successRate.add(dispatchOk);

  sleep(1);
}
