const { test, expect } = require('@playwright/test');

test('captureLead blocks on 11th request (429)', async ({ request }) => {
  const payload = {
    name: 'Spammer',
    email: 'spam@test.com',
    message: 'Spam message spanning required length',
  };
  
  for(let i = 0; i < 10; i++) {
    const res = await request.post('http://127.0.0.1:5001/shadowtag-omega-v4/us-central1/captureLead', { data: payload });
  }
  const blockRes = await request.post('http://127.0.0.1:5001/shadowtag-omega-v4/us-central1/captureLead', { data: payload });
  expect(blockRes.status()).toBe(429);
});
