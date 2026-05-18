// k6 Soak Test — CounselConduit /readyz
// 50 VUs, 30 minutes, thresholds on p95 latency and error rate
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const readyzDuration = new Trend('readyz_duration', true);

export const options = {
  stages: [
    { duration: '2m', target: 50 },    // Ramp up to 50 VUs over 2 minutes
    { duration: '26m', target: 50 },   // Sustain 50 VUs for 26 minutes
    { duration: '2m', target: 0 },     // Ramp down over 2 minutes
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],  // p95 < 500ms, p99 < 1s
    errors: ['rate<0.01'],                             // Error rate < 1%
    http_req_failed: ['rate<0.01'],                    // HTTP failures < 1%
  },
};

const BASE_URL = __ENV.TARGET_URL || 'https://counselconduit-767252945109.us-central1.run.app';

export default function () {
  const res = http.get(`${BASE_URL}/readyz`, {
    tags: { name: 'readyz' },
    timeout: '10s',
  });

  readyzDuration.add(res.timings.duration);

  const success = check(res, {
    'status is 200': (r) => r.status === 200,
    'body contains healthy': (r) => r.body && r.body.includes('healthy'),
    'response time < 500ms': (r) => r.timings.duration < 500,
    'firestore connected': (r) => r.body && r.body.includes('connected'),
  });

  errorRate.add(!success);
  sleep(1);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.3/index.js';
