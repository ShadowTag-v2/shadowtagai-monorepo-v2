import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const healthLatency = new Trend('health_latency');

export const options = {
  stages: [
    { duration: '10s', target: 5 },   // ramp up
    { duration: '20s', target: 10 },   // sustained
    { duration: '5s', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95th percentile < 2s
    errors: ['rate<0.1'],              // <10% error rate
  },
};

const BASE_URL = 'https://counselconduit-6byqzjbd7a-uc.a.run.app';

export default function () {
  // Health check
  const health = http.get(`${BASE_URL}/health`);
  healthLatency.add(health.timings.duration);
  check(health, {
    'health status 200': (r) => r.status === 200,
    'health latency < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);

  // API docs endpoint
  const docs = http.get(`${BASE_URL}/docs`);
  check(docs, {
    'docs status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);
}
