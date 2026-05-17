import { check, group, sleep } from "k6";
import http from "k6/http";

export const options = {
  scenarios: {
    cold_start: {
      executor: "per-vu-iterations",
      vus: 1,
      iterations: 1,
      maxDuration: "10s",
    },
    concurrency_test: {
      executor: "constant-vus",
      vus: 150, // Target concurrency to test limits
      duration: "30s",
      startTime: "5s", // Start after cold start check
    },
  },
  thresholds: {
    // Assertions for Quality Gate
    "http_req_duration{scenario:cold_start}": ["p(100)<2000"], // Cold start < 2s (relaxed for testing)
    http_req_failed: ["rate==0"], // 0% error rate required
    "http_req_duration{scenario:concurrency_test}": ["p(95)<500"], // 95% of requests < 500ms under load
  },
};

const BASE_URL = __ENV.STAGING_URL || "http://localhost:8080";

export default function () {
  group("Health Check", () => {
    const res = http.get(`${BASE_URL}/health`);

    check(res, {
      "status is 200": (r) => r.status === 200,
      "response is healthy": (r) => r.json("status") === "healthy",
    });
  });
}
