# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests/api_limit.test.js >> captureLead blocks on 11th request (429)
- Location: tests/api_limit.test.js:3:1

# Error details

```
Error: apiRequestContext.post: connect ECONNREFUSED 127.0.0.1:5001
Call log:
  - → POST http://127.0.0.1:5001/shadowtag-omega-v4/us-central1/captureLead
    - user-agent: Playwright/1.59.1 (arm64; macOS 26.4) node/22.22
    - accept: */*
    - accept-encoding: gzip,deflate,br
    - content-type: application/json
    - content-length: 92

```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  |
  3  | test('captureLead blocks on 11th request (429)', async ({ request }) => {
  4  |   const payload = {
  5  |     name: 'Spammer',
  6  |     email: 'spam@test.com',
  7  |     message: 'Spam message spanning required length',
  8  |   };
  9  |
  10 |   for(let i = 0; i < 10; i++) {
> 11 |     const res = await request.post('http://127.0.0.1:5001/shadowtag-omega-v4/us-central1/captureLead', { data: payload });
     |                               ^ Error: apiRequestContext.post: connect ECONNREFUSED 127.0.0.1:5001
  12 |   }
  13 |   const blockRes = await request.post('http://127.0.0.1:5001/shadowtag-omega-v4/us-central1/captureLead', { data: payload });
  14 |   expect(blockRes.status()).toBe(429);
  15 | });
  16 |
```
