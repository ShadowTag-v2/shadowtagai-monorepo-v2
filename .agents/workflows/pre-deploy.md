# /pre-deploy

**Execution Pipeline (Production Safety Net):**
1. **The 320px Reality Check:** Run the Playwright UI test simulating a 320px iPhone SE width on a throttled connection. If buttons are unclickable or it takes >30s, FAIL deployment.
2. **Works On My Machine Check:** Run `npm ci && npm run build` in a clean terminal environment to ensure Turbopack caching isn't hiding compilation errors.
3. **Mandatory Backups:** Warn the user: `🚨 STOP. Do you have a rollback plan?` Execute the DB snapshot bash script before permitting the Vercel/production merge.
