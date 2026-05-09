// CounselConduit Staging Smoke Tests
// Validates core API functionality on staging before production canary

import { expect, test } from '@playwright/test';

const BASE_URL =
  process.env.STAGING_URL || 'https://counselconduit-staging-767252945109.us-central1.run.app';

test.describe('Smoke Tests', () => {
  test('GET /health returns 200', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty('status', 'healthy');
  });

  test('GET /health/providers returns provider status', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/health/providers`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty('providers');
  });

  test('GET /openapi.json returns valid spec', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/openapi.json`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.info.version).toMatch(/^\d+\.\d+\.\d+$/);
  });

  test('GET / returns root info', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/`);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty('service', 'counselconduit');
  });

  test('POST /admin/firm-policy without auth returns 401', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/admin/firm-policy`, {
      data: {
        firm_id: 'test-firm',
        allowed_models: ['gemini'],
        max_rpm: 10,
        max_daily: 100,
        byok: { enabled: false },
      },
    });
    // Should be 401 (not 500) on unauthenticated requests
    expect(response.status()).toBe(401);
  });
});
