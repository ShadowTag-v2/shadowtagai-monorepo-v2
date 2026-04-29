# Universal Copilot

**Compliant Multi-LLM Code Assistant with Judge 6 Governance**

Version 1.0.0 | Author: Erik Bjontegard, Pnkln

---

## Overview

Universal Copilot is a production-ready, compliant AI code assistant that:

- ✅ **Uses Only Public APIs** - No private extension hooks, no entitlement spoofing
- ✅ **Multi-Provider Support** - OpenAI, Anthropic, or mock providers
- ✅ **Judge 6 Governance** - Constitutional AI safety enforcement
- ✅ **Rate Limited & Auditable** - Production-grade resource management
- ✅ **Unified Diff Patching** - Safe, reversible code modifications
- ✅ **Fully Typed** - TypeScript with Zod runtime validation

## What You Get (Compliantly)

✅ **Same UX Shape** - Editor selection → LLM processing → Unified diff patch
✅ **Your Data** - No vendor lock-in, full control over requests
✅ **Auditability** - Complete logs, cost tracking, governance decisions
✅ **Safety** - Judge 6 constitutional enforcement
✅ **Reliability** - Rate limiting, retries, error handling

## What's Intentionally Left Out

❌ **Paywalled Features** - No unauthorized access to pro-only capabilities
❌ **Private Extension APIs** - No hooks into Copilot/Claude Code/Cody internals
❌ **Vendor Codebase Indexes** - Use your own local indexes (ripgrep/embeddings)
❌ **Undocumented UI Hooks** - Stick to public VS Code/Cursor APIs
❌ **Policy Bypasses** - Respect org-level controls and throttles

---

## Quick Start

### Installation

```bash
npm install
cp .env.example .env
# Edit .env with your API keys (optional - works in mock mode)
```

### Run Demo

```bash
# Mock mode (no API keys needed)
USE_MOCK=1 npm run dev

# With real providers
OPENAI_API_KEY=sk-... npm run dev
```

### Run Tests

```bash
# All tests with mock provider
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm run test:watch
```

---

## Architecture

```
universal-copilot/
├── src/
│   ├── core/
│   │   ├── schema.ts        # Zod type definitions
│   │   ├── errors.ts        # Custom error classes
│   │   ├── router.ts        # Intelligent request router
│   │   ├── patcher.ts       # Unified diff application
│   │   └── governance.ts    # Judge 6 integration
│   ├── providers/
│   │   ├── base.ts          # Provider interface
│   │   ├── mock.ts          # Deterministic test provider
│   │   ├── openai.ts        # OpenAI GPT integration
│   │   ├── anthropic.ts     # Anthropic Claude integration
│   │   └── index.ts         # Provider factory
│   ├── index.ts             # Public API exports
│   └── widget.ts            # Demo application
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test data
└── docs/                    # Additional documentation
```

---

## Usage

### Basic Example

```typescript
import { CopilotRouter, createGovernance } from "@pnkln/universal-copilot";

// Configure router
const config = {
  defaultProvider: "mock",
  enableGovernance: true,
  rateLimitRps: 6.6,
  providers: {
    mock: {},
    openai: { apiKey: process.env.OPENAI_API_KEY },
  },
};

// Initialize with governance
const governance = createGovernance(false); // false = use real Judge 6
const router = new CopilotRouter(config, governance);

// Make request
const response = await router.route({
  selection: {
    filePath: "example.ts",
    language: "typescript",
    code: "const x = 1;",
  },
  intent: "optimize",
  modelPref: "mock",
});

console.log(response.patch.unifiedDiff);
// --- a/example.ts
// +++ b/example.ts
// @@ -1,1 +1,2 @@
// +/* Performance optimized */
// +const x = 1;
```

### With Patch Application

```typescript
import { createPatcher } from "@pnkln/universal-copilot";

const patcher = createPatcher();

// Dry run first
const dryRun = await patcher.applyPatch(
  response.patch.filePath,
  response.patch.unifiedDiff,
  { dryRun: true }
);

if (dryRun.success) {
  // Apply for real
  const result = await patcher.applyPatch(
    response.patch.filePath,
    response.patch.unifiedDiff,
    { createBackup: true }
  );

  if (result.success) {
    console.log(`Applied! Backup: ${result.backup}`);
  }
}
```

### Governance Integration

```typescript
import { Cor.Claude_Code_6Adapter } from "@pnkln/universal-copilot";

// Use Python Judge 6 for real governance
const governance = new Cor.Claude_Code_6Adapter("copilot-instance-001");

const router = new CopilotRouter(
  { ...config, enableGovernance: true },
  governance
);

// Requests are automatically validated
try {
  const response = await router.route(maliciousRequest);
} catch (error) {
  if (error.code === "GOVERNANCE_REJECTED") {
    console.log("Blocked:", error.violatedAxioms);
  }
}
```

---

## Configuration

### Environment Variables

```bash
# Provider Selection
USE_MOCK=1                    # 1=mock, 0=real providers
DEFAULT_PROVIDER=mock         # mock|openai|anthropic|auto

# API Keys (optional in mock mode)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Governance
ENABLE_GOVERNANCE=1           # 1=enforce, 0=permissive
COR_INSTANCE_ID=copilot-001
USE_MOCK_GOVERNANCE=0         # 1=mock governance, 0=real Judge 6

# Rate Limiting
RATE_LIMIT_RPS=6.6           # Requests per second
RATE_LIMIT_CONCURRENT=2       # Max concurrent requests
```

### Router Configuration

```typescript
const config: RouterConfig = {
  defaultProvider: "auto",
  enableGovernance: true,
  corInstanceId: "my-instance",
  rateLimitRps: 10,
  rateLimitConcurrent: 3,
  providers: {
    openai: {
      apiKey: "sk-...",
      model: "gpt-4o-2024-08-06",
      timeout: 30000,
      retries: 2,
    },
    anthropic: {
      apiKey: "sk-ant-...",
      model: "claude-sonnet-4-20250514",
      timeout: 30000,
      retries: 2,
    },
  },
};
```

---

## Testing Strategy

### Contract Tests

Define expected request/response shapes and validate:

```typescript
it("should return valid patch format", async () => {
  const response = await router.route(request);

  expect(response.patch).toMatchObject({
    filePath: expect.any(String),
    unifiedDiff: expect.stringContaining("---"),
    explanation: expect.any(String),
  });
});
```

### Golden Files

Store expected outputs for regression testing:

```typescript
const patch = await provider.generatePatch(request);
const expected = await fs.readFile("fixtures/expected.patch", "utf-8");

expect(normalize(patch.unifiedDiff)).toBe(normalize(expected));
```

### Fault Injection

Simulate provider failures:

```typescript
it("should handle rate limits", async () => {
  // Trigger rate limit
  const requests = Array(100)
    .fill(null)
    .map(() => router.route(request));

  const results = await Promise.allSettled(requests);
  const rateLimited = results.filter((r) => r.status === "rejected");

  expect(rateLimited.length).toBeGreaterThan(0);
});
```

---

## Compliance Guarantees

### What We Promise

1. **No Private APIs** - Only use documented, public SDKs
2. **No Entitlement Spoofing** - Respect paywalls and rate limits
3. **No Extension Hooks** - Don't intercept first-party extension traffic
4. **Full Auditability** - Every decision is logged and traceable
5. **Fail-Safe Governance** - Dangerous requests blocked at source

### What We Don't Promise

1. **Feature Parity** - Some vendor-only features unavailable
2. **Zero Cost** - You pay for LLM API usage
3. **Extension-Level Integration** - No deep editor hooks

---

## Judge 6 Integration

Universal Copilot integrates with [Judge 6](../Cor.Claude_Code_6/) for cryptographic governance enforcement.

### Key Features

- **Constitutional Axioms** - Immutable safety rules (Cor.53)
- **ATP 5-19 Risk Stratification** - Pre-execution risk classification
- **ShadowTag 2.0** - Cryptographic provenance stamps
- **Six-Gate Evaluation** - Multi-stage decision validation

### Governance Workflow

```
User Request
    ↓
GATE 1: Risk Classification (RA-1 to RA-4)
    ↓
GATE 2: Purpose Validation
    ↓
GATE 3: Axiom Compliance Check
    ↓
GATE 4: Resource Allocation
    ↓
GATE 5: Provider Execution
    ↓
GATE 6: Provenance Stamp
    ↓
Response with Cryptographic Proof
```

---

## Production Deployment

### Recommended Setup

```bash
# Install dependencies
npm ci --production

# Build TypeScript
npm run build

# Set production config
export NODE_ENV=production
export USE_MOCK=0
export ENABLE_GOVERNANCE=1

# Run
node dist/widget.js
```

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build

CMD ["node", "dist/widget.js"]
```

### Monitoring

```typescript
// Track statistics
const stats = router.getStats();

console.log({
  totalRequests: stats.totalRequests,
  successRate: stats.successfulRequests / stats.totalRequests,
  avgLatency: stats.averageLatencyMs,
  governanceRejections: stats.governanceRejections,
});
```

---

## API Reference

See [API.md](./docs/API.md) for complete API documentation.

### Core Classes

- **CopilotRouter** - Main routing and orchestration
- **UnifiedPatcher** - Patch application and backup management
- **Cor.Claude_Code_6Adapter** - Governance integration
- **MockProvider, OpenAIProvider, AnthropicProvider** - LLM providers

### Key Types

- **CopilotRequest** - Input request structure
- **CopilotResponse** - Output with patch and metadata
- **Patch** - Unified diff format
- **RouterConfig** - Router configuration
- **GovernanceEngine** - Governance interface

---

## FAQ

**Q: Do I need API keys to test?**
A: No, use `USE_MOCK=1` for deterministic testing without real LLM calls.

**Q: Can I use multiple providers?**
A: Yes, set `modelPref: "auto"` to automatically select best available provider.

**Q: Is governance optional?**
A: Yes, set `enableGovernance: false` to disable (not recommended for production).

**Q: How do I add a custom provider?**
A: Extend `BaseProvider` and register in the provider factory.

**Q: What's the test coverage?**
A: Run `npm test -- --coverage` to see current coverage (target: 90%+).

---

## License

Copyright © 2025 Erik Bjontegard, Pnkln. All rights reserved.

---

## Related Projects

- [Judge 6](../Cor.Claude_Code_6/) - AI Governance & Risk Management System
- [PNKLN ShadowTag-v4 Stack](../) - Complete AI infrastructure

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report a bug](https://github.com/pnkln/issues)
- Documentation: [Full docs](./docs/)
- Examples: [See examples/](./examples/)
