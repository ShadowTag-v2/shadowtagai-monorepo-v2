import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 }, // ramp up to 50 users
    { duration: '28m', target: 50 }, // stay at 50 for 28 minutes
    { duration: '2m', target: 0 }, // ramp down to 0 users
  ],
};

export default function () {
  // Use the Cloud Run URL for CounselConduit
  const res = http.get('https://counselconduit-767252945109.us-central1.run.app/enclave/v1/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
