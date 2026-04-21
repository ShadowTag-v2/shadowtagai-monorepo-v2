// k6 Load Test — CounselConduit Production Smoke Test
// Run: k6 run scripts/k6_counselconduit_smoke.js

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");

export const options = {
  stages: [
    { duration: "10s", target: 5 },   // Ramp up to 5 VUs
    { duration: "30s", target: 10 },   // Hold at 10 VUs
    { duration: "10s", target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<2000"],  // 95% of requests under 2s
    errors: ["rate<0.1"],               // Error rate under 10%
  },
};

const BASE_URL = "https://counselconduit-767252945109.us-central1.run.app";

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    "health status 200": (r) => r.status === 200,
  });
  errorRate.add(healthRes.status !== 200);

  // OpenAPI docs
  const docsRes = http.get(`${BASE_URL}/docs`);
  check(docsRes, {
    "docs accessible": (r) => r.status === 200,
  });
  errorRate.add(docsRes.status !== 200);

  // Billing tiers
  const tiersRes = http.get(`${BASE_URL}/api/v1/billing/tiers`);
  check(tiersRes, {
    "tiers endpoint responds": (r) => r.status < 500,
  });
  errorRate.add(tiersRes.status >= 500);

  sleep(1);
}
