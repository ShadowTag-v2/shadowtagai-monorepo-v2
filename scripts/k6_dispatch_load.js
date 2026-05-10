// k6 Load Test — CounselConduit Dispatch Endpoint
// Install: brew install k6
// Run: k6 run scripts/k6_dispatch_load.js

import { check, sleep } from 'k6';
import http from 'k6/http';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const dispatchDuration = new Trend('dispatch_duration');

export const options = {
  stages: [
    { duration: '30s', target: 10 }, // Ramp to 10 VUs
    { duration: '1m', target: 25 }, // Ramp to 25 VUs
    { duration: '30s', target: 50 }, // Peak at 50 VUs
    { duration: '1m', target: 50 }, // Hold peak
    { duration: '30s', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // 95% of requests < 3s
    http_req_failed: ['rate<0.01'], // <1% failure rate
    errors: ['rate<0.01'],
  },
};

const BASE_URL = 'https://counselconduit-767252945109.us-central1.run.app';

const QUERIES = [
  { query: 'What is attorney-client privilege?', tier: 'simple' },
  { query: 'Hello', tier: 'simple' },
  { query: 'Explain the concept of mens rea in criminal law', tier: 'simple' },
  {
    query:
      'Draft a comprehensive analysis of the doctrine of equitable estoppel and tolling provisions under federal bankruptcy code',
    tier: 'agentic',
  },
  {
    query:
      'Analyze SEC Rule 10b-5 implications for insider trading with a detailed memo on recent circuit splits',
    tier: 'agentic',
  },
];

export default function () {
  const query = QUERIES[Math.floor(Math.random() * QUERIES.length)];
  const firmId = `load-test-firm-${__VU}`;

  const payload = JSON.stringify({
    query: query.query,
    firm_id: firmId,
    session_id: `k6-session-${__VU}-${__ITER}`,
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { tier: query.tier },
  };

  const res = http.post(`${BASE_URL}/api/v1/dispatch`, payload, params);

  const passed = check(res, {
    'status is 200': (r) => r.status === 200,
    'has model field': (r) => JSON.parse(r.body).model !== undefined,
    'has tier field': (r) => JSON.parse(r.body).tier !== undefined,
    'latency < 3s': (r) => r.timings.duration < 3000,
  });

  if (!passed) {
    errorRate.add(1);
  }

  dispatchDuration.add(res.timings.duration);
  sleep(0.5 + Math.random());
}

export function handleSummary(data) {
  return {
    stdout: JSON.stringify(data, null, 2),
    'scripts/k6_results.json': JSON.stringify(data, null, 2),
  };
}
