# /pre-deploy — The 2 AM Savior Pipeline

> **Purpose:** Prevents deployment disasters by enforcing autonomous pre-flight checks before ANY deployment or merge to main.
> **Invocation:** `/pre-deploy`
> **Cross-references:** `cor-meatbridge-eviction` (browser automation), `BLAST Pipeline` (Build→Lint→Audit→Scan→Test), `senior-dev` rule

## Steps

### Step 1: The iPhone 5S Check (Mobile Viewport)
Using Chrome DevTools MCP (NOT asking the user to manually check):

1. Launch the browser and navigate to the deployment target URL (localhost or staging).
2. Resize the viewport to 320px width (iPhone SE).
3. Navigate through all primary user flows:
   - Can all primary CTA buttons be tapped?
   - Does the navigation render without overflow?
   - Are form inputs accessible and usable?
4. Take a screenshot artifact as proof of mobile compatibility.
5. **FAIL** if any primary button is obscured or the layout is broken.

```
Tool: chrome-devtools-mcp → resize_page(width=320, height=568)
Tool: chrome-devtools-mcp → take_screenshot()
```

### Step 2: Clean Build Verification ("Works On My Machine" Prevention)
Run a clean install and production build in the terminal to verify the app compiles outside the local dev cache:

```bash
# For the target app (detect package manager)
npm ci && npm run build
# OR
pnpm install --frozen-lockfile && pnpm run build
```

- **FAIL** if the build produces any errors.
- **WARN** if the build produces TypeScript or lint warnings.
- This catches: missing dependencies, import resolution errors, type errors that dev mode ignores.

### Step 3: Lint & Security Gate
Run the monorepo's standard lint and security checks:

```bash
# Python
ruff check --select F401,F841 apps/ packages/ tests/
# TypeScript
npx biome check apps/kovelai/
# Secrets
betterleaks detect --baseline .gitleaksignore
```

- **FAIL** if any lint errors or secret leaks are detected.

### Step 4: Test Suite Verification
Run the existing test suite to catch regressions:

```bash
/opt/homebrew/bin/python3.14 -m pytest tests/ -x --timeout=30
```

- **FAIL** if any previously-passing test now fails.
- Report: X passed, Y failed, Z skipped.

### Step 5: Session & Auth Audit
Verify authentication configuration:
- Firebase Auth session `maxAge` is strictly enforced.
- No hardcoded API keys in the deployment artifact.
- CORS, CSP, HSTS headers are configured for the target domain.

### Step 6: Mandatory Backup Acknowledgment
Output a prominent warning:

```
🚨 STOP — PRE-DEPLOYMENT CHECKPOINT 🚨

Before proceeding with deployment:
1. Do you have a database rollback plan?
2. Is the previous deployment version tagged and accessible?
3. Are monitoring alerts configured for error rate spikes?

Type 'DEPLOY' to proceed or 'ABORT' to cancel.
```

**PAUSE** and wait for explicit user approval before running any deployment command.

### Step 7: Lighthouse Audit (Post-Deploy)
After deployment succeeds, run a Lighthouse audit on the live URL:

```
Tool: chrome-devtools-mcp → lighthouse_audit(device="mobile")
```

Minimum thresholds:
- Performance: >85
- Accessibility: >90
- Best Practices: >90
- SEO: >90

Report results and flag any regressions from previous scores.
