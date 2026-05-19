// k6 Quick Validation — CounselConduit /readyz
// 50 VUs, 5 minutes — spot-check scaling config
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.3/index.js';

const errorRate = new Rate('errors');
const readyzDuration = new Trend('readyz_duration', true);

export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Ramp up
    { duration: '4m', target: 50 },    // Sustain
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
    http_req_failed: ['rate<0.01'],
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
  });

  errorRate.add(!success);
  sleep(1);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
