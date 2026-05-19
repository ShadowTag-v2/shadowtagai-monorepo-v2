// k6 validation script — 5-min, 50 VUs on /readyz
// Validates rate-limiter fix: expect 0% error rate
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseDuration = new Trend('response_duration');

export const options = {
  vus: 50,
  duration: '5m',
  thresholds: {
    errors: ['rate==0'],          // 0% error rate
    http_req_duration: ['p(95)<500'], // 95th percentile < 500ms
  },
};

export default function () {
  const res = http.get('https://counselconduit-767252945109.us-central1.run.app/readyz');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'body contains healthy': (r) => r.body && r.body.includes('healthy'),
    'not rate limited': (r) => r.status !== 429,
  });
  
  errorRate.add(res.status !== 200);
  responseDuration.add(res.timings.duration);
  
  sleep(0.1); // 10 RPS per VU = ~500 total RPS
}
