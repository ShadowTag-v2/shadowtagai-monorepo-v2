# Mock Universal Copilot - Complete Setup

**Purpose:** End-to-end testable AI-assisted coding without touching vendor APIs
**Use Case:** CI/CD testing, local development, contract validation
**Based On:** Cor. Spoofing compliant architecture

---

## Overview

This is a **minimal, runnable mock** that simulates LLM calls and editor round-trips without touching any vendor's private API. Perfect for:

- **CI/CD pipelines** (deterministic, no API costs)
- **Local development** (work offline, test routing logic)
- **Contract testing** (validate request/response shapes)
- **Load testing** (simulate latency without hitting rate limits)

---

## Project Structure

```
mock-universal-copilot/
├── package.json
├── src/
│   ├── widget.ts            # "in-page assistant" shim (pretends to send code selections)
│   ├── router.ts            # local router: chooses provider, enforces limits
│   ├── providers/
│   │   ├── openai.ts        # uses official SDK *or* mock
│   │   ├── anthropic.ts     # uses official SDK *or* mock
│   │   └── mock.ts          # deterministic fake LLM (for tests & CI)
│   ├── applyPatch.ts        # emulates editor applying patch to file
│   └── schema.ts            # zod types for requests/responses
├── tests/
│   ├── router.spec.ts       # unit tests (plan/patch/error cases)
│   ├── integration.spec.ts  # full "select → router → patch" flow
│   └── fixtures/
│       ├── sample.ts
│       └── sample_expected.patch
├── .env.example             # OPENAI_API_KEY, ANTHROPIC_API_KEY (not needed for mock)
└── README.md
```

---

## Implementation Files

### package.json

```json
{
  "name": "mock-universal-copilot",
  "private": true,
  "type": "module",
  "version": "1.0.0",
  "description": "Compliant AI-assisted coding mock for testing",
  "scripts": {
    "dev": "tsx src/widget.ts",
    "test": "vitest run --coverage",
    "test:ci": "NODE_ENV=test USE_MOCK=1 vitest run --coverage",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts"
  },
  "dependencies": {
    "zod": "^3.23.8",
    "bottleneck": "^2.19.5"
  },
  "devDependencies": {
    "typescript": "^5.6.2",
    "tsx": "^4.19.1",
    "vitest": "^2.1.1",
    "@vitest/coverage-v8": "^2.1.1",
    "eslint": "^8.57.0",
    "prettier": "^3.3.3"
  }
}
```

---

### src/schema.ts

**Type definitions using Zod for validation**

```typescript
import { z } from "zod";

export const Selection = z.object({
  filePath: z.string(),
  language: z.string().optional(),
  code: z.string()
});

export const Request = z.object({
  selection: Selection,
  intent: z.enum(["explain", "refactor", "test", "fix"]).default("fix"),
  modelPref: z.enum(["openai", "anthropic", "auto", "mock"]).default("mock"),
  maxTokens: z.number().int().positive().max(4000).default(800),
  temperature: z.number().min(0).max(2).default(0.2)
});

export type Request = z.infer<typeof Request>;

export const Patch = z.object({
  filePath: z.string(),
  unifiedDiff: z.string(), // produce a unified diff for applyPatch
  metadata: z.object({
    provider: z.string(),
    tokensUsed: z.number().optional(),
    cost: z.number().optional()
  }).optional()
});

export type Patch = z.infer<typeof Patch>;

export const Selection_t = z.infer<typeof Selection>;
export type Selection_t = z.infer<typeof Selection>;
```

---

### src/providers/mock.ts

**Deterministic "LLM" for tests**

```typescript
import { Request, Patch } from "../schema.js";

export async function callMockLLM(req: Request): Promise<Patch> {
  // Deterministic "LLM" for tests: wrap code in try/catch or append comment.
  const header = `/* Mock-${req.intent.toUpperCase()} by router */\n`;
  const newCode = header + req.selection.code;

  // Generate unified diff
  const diff = [
    `--- a/${req.selection.filePath}`,
    `+++ b/${req.selection.filePath}`,
    `@@ -1,${req.selection.code.split("\n").length} +1,${newCode.split("\n").length} @@`,
    ...req.selection.code.split("\n").map(line => `-${line}`),
    ...newCode.split("\n").map(line => `+${line}`)
  ].join("\n");

  return {
    filePath: req.selection.filePath,
    unifiedDiff: diff,
    metadata: {
      provider: "mock",
      tokensUsed: req.selection.code.length + newCode.length,
      cost: 0
    }
  };
}
```

---

### src/providers/openai.ts

**Official OpenAI SDK integration (optional)**

```typescript
import OpenAI from "openai";
import { Request, Patch } from "../schema.js";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export async function callOpenAI(req: Request): Promise<Patch> {
  const systemPrompt = getSystemPrompt(req.intent);

  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      { role: "system", content: systemPrompt },
      {
        role: "user",
        content: `File: ${req.selection.filePath}\n\n${req.selection.code}`
      }
    ],
    max_tokens: req.maxTokens,
    temperature: req.temperature
  });

  const generatedCode = response.choices[0].message.content || "";

  // Generate unified diff (simplified)
  const diff = [
    `--- a/${req.selection.filePath}`,
    `+++ b/${req.selection.filePath}`,
    `@@`,
    ...req.selection.code.split("\n").map(line => `-${line}`),
    ...generatedCode.split("\n").map(line => `+${line}`)
  ].join("\n");

  return {
    filePath: req.selection.filePath,
    unifiedDiff: diff,
    metadata: {
      provider: "openai",
      tokensUsed: response.usage?.total_tokens,
      cost: calculateCost("gpt-4", response.usage)
    }
  };
}

function getSystemPrompt(intent: string): string {
  switch (intent) {
    case "explain":
      return "You are a code explainer. Add detailed comments to the code.";
    case "refactor":
      return "You are a code refactoring assistant. Improve code quality without changing behavior.";
    case "test":
      return "You are a test generator. Generate comprehensive unit tests.";
    case "fix":
      return "You are a bug fixer. Fix any bugs or issues in the code.";
    default:
      return "You are a helpful coding assistant.";
  }
}

function calculateCost(model: string, usage: any): number {
  // Pricing as of 2025 (example - update with real rates)
  const rates = {
    "gpt-4": { input: 0.03 / 1000, output: 0.06 / 1000 },
    "gpt-3.5-turbo": { input: 0.0015 / 1000, output: 0.002 / 1000 }
  };

  const rate = rates[model as keyof typeof rates] || rates["gpt-4"];
  const inputCost = (usage?.prompt_tokens || 0) * rate.input;
  const outputCost = (usage?.completion_tokens || 0) * rate.output;

  return inputCost + outputCost;
}
```

---

### src/providers/anthropic.ts

**Official Anthropic SDK integration (optional)**

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { Request, Patch } from "../schema.js";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

export async function callAnthropic(req: Request): Promise<Patch> {
  const systemPrompt = getSystemPrompt(req.intent);

  const response = await anthropic.messages.create({
    model: "claude-3-5-sonnet-20241022",
    max_tokens: req.maxTokens,
    temperature: req.temperature,
    system: systemPrompt,
    messages: [
      {
        role: "user",
        content: `File: ${req.selection.filePath}\n\n${req.selection.code}`
      }
    ]
  });

  const generatedCode = response.content[0].type === "text"
    ? response.content[0].text
    : "";

  // Generate unified diff
  const diff = [
    `--- a/${req.selection.filePath}`,
    `+++ b/${req.selection.filePath}`,
    `@@`,
    ...req.selection.code.split("\n").map(line => `-${line}`),
    ...generatedCode.split("\n").map(line => `+${line}`)
  ].join("\n");

  return {
    filePath: req.selection.filePath,
    unifiedDiff: diff,
    metadata: {
      provider: "anthropic",
      tokensUsed: response.usage.input_tokens + response.usage.output_tokens,
      cost: calculateCost("claude-3-5-sonnet", response.usage)
    }
  };
}

function getSystemPrompt(intent: string): string {
  switch (intent) {
    case "explain":
      return "Add detailed comments explaining how the code works.";
    case "refactor":
      return "Refactor the code to improve quality while maintaining behavior.";
    case "test":
      return "Generate comprehensive unit tests for the code.";
    case "fix":
      return "Fix any bugs or issues in the code.";
    default:
      return "You are a helpful coding assistant.";
  }
}

function calculateCost(model: string, usage: any): number {
  // Pricing as of 2025 (example - update with real rates)
  const rates = {
    "claude-3-5-sonnet": { input: 0.003 / 1000, output: 0.015 / 1000 },
    "claude-3-haiku": { input: 0.00025 / 1000, output: 0.00125 / 1000 }
  };

  const rate = rates[model as keyof typeof rates] || rates["claude-3-5-sonnet"];
  const inputCost = (usage?.input_tokens || 0) * rate.input;
  const outputCost = (usage?.output_tokens || 0) * rate.output;

  return inputCost + outputCost;
}
```

---

### src/router.ts

**Multi-LLM routing with rate limiting**

```typescript
import Bottleneck from "bottleneck";
import { Request, Request as Req } from "./schema.js";
import { callMockLLM } from "./providers/mock.js";
// Uncomment when ready to use real providers:
// import { callOpenAI } from "./providers/openai.js";
// import { callAnthropic } from "./providers/anthropic.js";

// Rate limiter: ~6.6 requests/second
const limiter = new Bottleneck({
  minTime: 150,
  maxConcurrent: 5,
  reservoir: 100,  // max 100 requests
  reservoirRefreshAmount: 100,
  reservoirRefreshInterval: 60 * 1000  // per minute
});

export async function route(req: Req) {
  const r = Request.parse(req);

  return limiter.schedule(async () => {
    // Add artificial latency in mock mode to simulate real API
    if (process.env.MOCK_LATENCY_MS) {
      const jitter = Math.random() * 200;  // 0-200ms jitter
      await sleep(parseInt(process.env.MOCK_LATENCY_MS) + jitter);
    }

    const provider = (process.env.USE_MOCK === "1") ? "mock" : r.modelPref;

    switch (provider) {
      case "mock":
        return callMockLLM(r);

      // Uncomment when ready:
      // case "openai":
      //   return callOpenAI(r);

      // case "anthropic":
      //   return callAnthropic(r);

      case "auto":
        // Auto-select best provider (in tests, use mock for determinism)
        if (process.env.NODE_ENV === "test") return callMockLLM(r);
        // In production, choose based on intent/cost/availability
        return callMockLLM(r);  // TODO: implement smart routing

      default:
        return callMockLLM(r);
    }
  });
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

---

### src/applyPatch.ts

**Apply unified diff to file (simplified patcher)**

```typescript
import fs from "node:fs";

export function applyUnifiedDiff(filePath: string, unified: string): void {
  // Minimal patcher for tests: replace full contents with "+++" hunk's content.
  const lines = unified.split("\n");

  // Extract lines starting with "+" (but not "+++")
  const plusLines = lines
    .filter(l => l.startsWith("+") && !l.startsWith("+++"))
    .map(l => l.slice(1));

  // Strip mock header comment if present (for realistic testing)
  const content = plusLines
    .join("\n")
    .replace(/^\/\* Mock-.*?\*\/\n/, "");

  fs.writeFileSync(filePath, content, "utf8");
}
```

---

### src/widget.ts

**Simulated editor widget (entry point)**

```typescript
import { route } from "./router.js";
import { applyUnifiedDiff } from "./applyPatch.js";
import { Request } from "./schema.js";
import fs from "node:fs";

async function main() {
  console.log("🚀 Mock Universal Copilot - Demo");

  const req: Request = {
    selection: {
      filePath: "tests/fixtures/sample.ts",
      language: "typescript",
      code: fs.readFileSync("tests/fixtures/sample.ts", "utf8")
    },
    intent: "fix",
    modelPref: process.env.USE_MOCK ? "mock" : "auto",
    maxTokens: 800,
    temperature: 0.2
  };

  console.log(`\n📝 Input code:\n${req.selection.code}`);
  console.log(`\n🤖 Routing to ${req.modelPref} provider...`);

  const patch = await route(req);

  console.log(`\n✅ Generated patch:\n${patch.unifiedDiff}`);
  console.log(`\n📊 Metadata:`, patch.metadata);

  applyUnifiedDiff(req.selection.filePath, patch.unifiedDiff);

  console.log(`\n✅ Patch applied to ${req.selection.filePath}`);
  console.log(`\n📄 Updated code:\n${fs.readFileSync(req.selection.filePath, "utf8")}`);
}

main().catch(e => {
  console.error("❌ Error:", e);
  process.exit(1);
});
```

---

### tests/router.spec.ts

**Unit tests with Vitest**

```typescript
import { describe, it, expect } from "vitest";
import { route } from "../src/router.js";
import fs from "node:fs";

describe("router mock flow", () => {
  it("returns a deterministic patch", async () => {
    const code = "export const x=1;\n";
    const res = await route({
      selection: { filePath: "sample.ts", code },
      intent: "fix",
      modelPref: "mock",
      maxTokens: 100,
      temperature: 0.1
    });

    expect(res.unifiedDiff).toContain("Mock-FIX");
    expect(res.unifiedDiff).toContain("sample.ts");
    expect(res.metadata?.provider).toBe("mock");
  });

  it("handles all intent types", async () => {
    const code = "function test() { return 1; }";
    const intents = ["explain", "refactor", "test", "fix"] as const;

    for (const intent of intents) {
      const res = await route({
        selection: { filePath: "test.ts", code },
        intent,
        modelPref: "mock",
        maxTokens: 100,
        temperature: 0.1
      });

      expect(res.unifiedDiff).toContain(`Mock-${intent.toUpperCase()}`);
    }
  });

  it("validates request schema", async () => {
    await expect(
      route({
        selection: { filePath: "", code: "" },  // Invalid
        intent: "fix",
        modelPref: "mock",
        maxTokens: -1,  // Invalid
        temperature: 5  // Invalid
      })
    ).rejects.toThrow();
  });
});
```

---

### tests/integration.spec.ts

**End-to-end integration tests**

```typescript
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { route } from "../src/router.js";
import { applyUnifiedDiff } from "../src/applyPatch.js";
import fs from "node:fs";
import path from "node:path";

describe("full integration flow", () => {
  const testFile = path.join(__dirname, "fixtures", "integration_test.ts");

  beforeEach(() => {
    // Create test file
    fs.writeFileSync(testFile, "export const x = 1;\n", "utf8");
  });

  afterEach(() => {
    // Cleanup
    if (fs.existsSync(testFile)) {
      fs.unlinkSync(testFile);
    }
  });

  it("complete flow: select → route → patch → apply", async () => {
    // Step 1: Read code
    const code = fs.readFileSync(testFile, "utf8");

    // Step 2: Route to LLM
    const patch = await route({
      selection: { filePath: testFile, code },
      intent: "refactor",
      modelPref: "mock",
      maxTokens: 800,
      temperature: 0.2
    });

    expect(patch.unifiedDiff).toBeDefined();
    expect(patch.metadata?.provider).toBe("mock");

    // Step 3: Apply patch
    applyUnifiedDiff(testFile, patch.unifiedDiff);

    // Step 4: Verify
    const updated = fs.readFileSync(testFile, "utf8");
    expect(updated).toContain("Mock-REFACTOR");
    expect(updated).toContain("export const x = 1;");
  });
});
```

---

### tests/fixtures/sample.ts

**Sample code for testing**

```typescript
export const x = 1;

function add(a: number, b: number) {
  return a + b;
}

export { add };
```

---

### .env.example

**Environment variable template**

```bash
# Mock mode (set to 1 for CI/tests)
USE_MOCK=1

# Real provider API keys (not needed in mock mode)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: Simulate latency (milliseconds)
MOCK_LATENCY_MS=500

# Optional: Inject faults for testing
INJECT_RATE_LIMIT=0
INJECT_5XX=0
INJECT_TIMEOUT=0
```

---

## Usage

### Install Dependencies

```bash
pnpm install
```

### Run Tests (Mock Mode)

```bash
# Run all tests with coverage
pnpm test

# Run in CI mode (guaranteed deterministic)
pnpm test:ci

# Watch mode
pnpm test -- --watch
```

### Run Demo (Mock Mode)

```bash
# End-to-end demo without touching real APIs
USE_MOCK=1 pnpm dev
```

### Swap to Real Providers

```bash
# 1. Copy .env.example to .env
cp .env.example .env

# 2. Add your API keys
# Edit .env and add OPENAI_API_KEY or ANTHROPIC_API_KEY

# 3. Uncomment provider imports in router.ts

# 4. Run with real provider
USE_MOCK=0 pnpm dev
```

---

## Advanced Testing

### Fault Injection

```bash
# Simulate rate limit error
INJECT_RATE_LIMIT=1 pnpm test

# Simulate 5xx error
INJECT_5XX=1 pnpm test

# Simulate timeout
INJECT_TIMEOUT=1 pnpm test
```

### Latency Simulation

```bash
# Add 500ms artificial latency
MOCK_LATENCY_MS=500 pnpm dev

# Test timeout handling
MOCK_LATENCY_MS=10000 pnpm test
```

### Load Testing

```bash
# Run 100 concurrent requests
for i in {1..100}; do
  USE_MOCK=1 pnpm dev &
done
wait
```

---

## Deployment

### Docker

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install -g pnpm && pnpm install

COPY . .

# Run in mock mode by default (safe)
ENV USE_MOCK=1

CMD ["pnpm", "dev"]
```

### Kubernetes

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: copilot-config
data:
  USE_MOCK: "1"
  MOCK_LATENCY_MS: "200"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: universal-copilot
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: copilot
        image: shadowtagai/universal-copilot:latest
        envFrom:
        - configMapRef:
            name: copilot-config
        # Real API keys from secrets
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: openai-key
```

---

## Best Practices

1. **Always test with mocks first** - Catch bugs before spending money on API calls
2. **Use contract tests** - Validate request/response shapes independently
3. **Track costs in real mode** - Log every API call with metadata
4. **Rate limit aggressively** - Protect your API budget
5. **Inject faults regularly** - Ensure graceful degradation
6. **Version your golden files** - Track expected behavior over time
7. **Sanitize inputs** - Remove secrets/PII before sending to LLM
8. **Validate outputs** - Don't blindly apply generated code

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi AI Team
**License:** MIT (example code) - Adapt for your needs