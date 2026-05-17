import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';

// Custom metrics
const p99Latency = new Trend('p99_latency_ms');
const healthzSuccess = new Rate('healthz_success');

export const options = {
  stages: [
    { duration: '10s', target: 5 },   // Ramp up
    { duration: '20s', target: 10 },   // Steady state
    { duration: '10s', target: 0 },    // Ramp down
  ],
  thresholds: {
    'http_req_duration{name:healthz}': ['p(99)<500'],  // p99 < 500ms
    'http_req_failed{name:healthz}': ['rate<0.01'],    // <1% error rate
  },
};

const BASE_URL = 'https://counselconduit-767252945109.us-central1.run.app';

export default function () {
  // Healthz probe
  const healthz = http.get(`${BASE_URL}/healthz`, {
    tags: { name: 'healthz' },
  });

  check(healthz, {
    'healthz returns 200': (r) => r.status === 200,
    'healthz returns healthy': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.status === 'healthy';
      } catch {
        return false;
      }
    },
  });

  p99Latency.add(healthz.timings.duration);
  healthzSuccess.add(healthz.status === 200);

  // Root endpoint
  const root = http.get(`${BASE_URL}/`, {
    tags: { name: 'root' },
  });

  check(root, {
    'root returns 200': (r) => r.status === 200,
  });

  sleep(0.5);
}
