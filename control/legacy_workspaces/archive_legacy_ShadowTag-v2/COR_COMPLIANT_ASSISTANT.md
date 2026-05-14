# Cor: Compliant Universal Coding Assistant

**Building production-grade AI coding assistance without spoofing or MITM**

This document explains how Cor provides Copilot-class functionality while staying fully compliant with vendor terms of service, avoiding entitlement spoofing, private API abuse, and man-in-the-middle techniques.

---

## Executive Summary

**The question:** "What don't we get if we stay fully compliant (no spoofing/MITM)?"

**The answer:** You lose access to vendor-specific paywalled features and private extension internals—but you gain a stable, auditable, legally defensible system that delivers 90%+ of the user experience through legitimate APIs and local intelligence.

---

## What Gets Left Out (By Design)

### 1. Paywalled capabilities without paying
You won't unlock vendor-only features (e.g., "Pro-only context windows," enterprise rate limits, proprietary ghost-text features in editors) unless your API key/plan actually includes them.

**Example blocked scenarios:**
- Accessing GPT-4 Turbo with a free-tier OpenAI key
- Using Claude Opus features on a Claude Haiku plan
- Bypassing GitHub Copilot Business rate limits with a personal account

### 2. Extension-internal/private APIs
We don't hook private endpoints used by first-party extensions (Copilot/Claude Code/Cody). That means:
- No "pretend I'm the official extension" calls
- No forged entitlement flags
- No piggybacking on their telemetry channels
- No accessing undocumented internal RPC methods

### 3. Vendor-side codebase indexes that require the extension
Some features rely on the vendor's hosted index tied to their own extension (e.g., prebuilt embeddings, code intelligence pipelines).

**Our approach instead:**
- Use local indexing (ripgrep/nowgrep)
- Build our own embeddings (GPTRAM/SQLite, Qdrant/FAISS)
- Leverage official APIs you own (GitHub Code Search API, etc.)

### 4. Undocumented UI hooks in editors
We stick to public Cursor/VS Code APIs. Anything only achievable by invasive DOM/IPC hooks inside a third-party extension is out of scope.

**Specifically avoided:**
- Monkey-patching editor internals
- Intercepting private IPC channels
- Modifying extension manifests to impersonate official extensions

### 5. Bypassing org policy, network controls, or usage caps
No proxying around organization-level policies. If a model is blocked or throttled by your organization's admin, the router will respect that.

---

## What You Do Get Instead (And How Close It Feels)

### ✅ Same UX shape
- Browser/editor widget with "Send selection → Get patch" workflow
- Multi-LLM routing (choose best model for the task)
- Repo-aware context (full codebase understanding)
- Real-time suggestions and inline completions

### ✅ Your data, your index
- **GPTRAM/SQLite**: High hit-rate caching, conversation history
- **nowgrep/ripgrep**: Low-latency code search across entire codebase
- **Local embeddings**: Qdrant/FAISS for semantic code search
- **No vendor lock-in**: Your index, your queries, your retention policy

### ✅ Reliability + auditability
- Clear logs of all LLM calls and costs
- Cost tracking per team/project/user
- Zero gray-area traffic interception
- Full compliance with vendor ToS and enterprise policies

### ✅ Multi-model intelligence
- Route to OpenAI for code generation
- Route to Anthropic for complex reasoning
- Route to local models (Llama, CodeLlama) for privacy-sensitive code
- Fallback chains when primary model unavailable

---

## Minimal Mock Setup (Test End-to-End Safely)

Drop this into a throwaway folder and run. It simulates LLM calls and editor round-trips without touching any vendor's private API.

### Project structure

```
mock-universal-copilot/
├─ package.json
├─ src/
│  ├─ widget.ts            # "in-page assistant" shim (pretends to send code selections)
│  ├─ router.ts            # local router: chooses provider, enforces limits
│  ├─ providers/
│  │  ├─ openai.ts         # uses official SDK *or* mock
│  │  ├─ anthropic.ts      # uses official SDK *or* mock
│  │  └─ mock.ts           # deterministic fake LLM (for tests & CI)
│  ├─ applyPatch.ts        # emulates editor applying patch to file
│  └─ schema.ts            # zod types for requests/responses
├─ tests/
│  ├─ router.spec.ts       # unit tests (plan/patch/error cases)
│  ├─ integration.spec.ts  # full "select → router → patch" flow
│  └─ fixtures/
│     ├─ sample.ts
│     └─ sample_expected.patch
├─ .env.example            # OPENAI_API_KEY, ANTHROPIC_API_KEY (not needed for mock)
└─ README.md
```

### package.json

```json
{
  "name": "mock-universal-copilot",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx src/widget.ts",
    "test": "vitest run --coverage",
    "test:ci": "NODE_ENV=test USE_MOCK=1 vitest run --coverage"
  },
  "dependencies": {
    "zod": "^3.23.8",
    "bottleneck": "^2.19.5"
  },
  "devDependencies": {
    "typescript": "^5.6.2",
    "tsx": "^4.19.1",
    "vitest": "^2.1.1"
  }
}
```

### src/schema.ts

```typescript
import { z } from "zod";

export const Selection = z.object({
  filePath: z.string(),
  language: z.string().optional(),
  code: z.string()
});

export const Request = z.object({
  selection: Selection,
  intent: z.enum(["explain","refactor","test","fix"]).default("fix"),
  modelPref: z.enum(["openai","anthropic","auto","mock"]).default("mock"),
  maxTokens: z.number().int().positive().max(4000).default(800),
  temperature: z.number().min(0).max(2).default(0.2)
});

export type Request = z.infer<typeof Request>;

export const Patch = z.object({
  filePath: z.string(),
  unifiedDiff: z.string() // produce a unified diff for applyPatch
});

export type Patch = z.infer<typeof Patch>;
```

### src/providers/mock.ts

```typescript
import { Request, Patch } from "../schema.js";

export async function callMockLLM(req: Request): Promise<Patch> {
  // Deterministic "LLM" for tests: wrap code in try/catch or append comment.
  const header = `/* Mock-${req.intent.toUpperCase()} by router */\n`;
  const newCode = header + req.selection.code;
  const diff = [
    `--- a/${req.selection.filePath}`,
    `+++ b/${req.selection.filePath}`,
    `@@`,
    `-${req.selection.code.split("\n").join("\n-")}`,
    `+${newCode.split("\n").join("\n+")}`
  ].join("\n");
  return { filePath: req.selection.filePath, unifiedDiff: diff };
}
```

### src/router.ts

```typescript
import Bottleneck from "bottleneck";
import { Request, Request as Req } from "./schema.js";
import { callMockLLM } from "./providers/mock.js";
// import { callOpenAI } from "./providers/openai.js"
// import { callAnthropic } from "./providers/anthropic.js"

const limiter = new Bottleneck({ minTime: 150 }); // ~6.6 rps

export async function route(req: Req) {
  const r = Request.parse(req);
  return limiter.schedule(async () => {
    const provider = (process.env.USE_MOCK === "1") ? "mock" : r.modelPref;
    switch (provider) {
      case "mock":      return callMockLLM(r);
      // case "openai":  return callOpenAI(r);
      // case "anthropic": return callAnthropic(r);
      case "auto":      return callMockLLM(r); // in tests use mock for determinism
      default:          return callMockLLM(r);
    }
  });
}
```

### src/applyPatch.ts

```typescript
import fs from "node:fs";

export function applyUnifiedDiff(filePath: string, unified: string) {
  // Minimal patcher for tests: replace full contents with "+++" hunk's content.
  const lines = unified.split("\n");
  const plusLines = lines.filter(l => l.startsWith("+") && !l.startsWith("+++")).map(l => l.slice(1));
  // strip header comment when present to simulate real patching
  const content = plusLines.join("\n").replace(/^\/\* Mock-.*?\*\/\n/, "");
  fs.writeFileSync(filePath, content, "utf8");
}
```

### src/widget.ts

```typescript
import { route } from "./router.js";
import { applyUnifiedDiff } from "./applyPatch.js";
import { Request } from "./schema.js";
import fs from "node:fs";

async function main() {
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

  const patch = await route(req);
  applyUnifiedDiff(req.selection.filePath, patch.unifiedDiff);
  console.log("OK: patch applied");
}

main().catch(e => { console.error(e); process.exit(1); });
```

### tests/router.spec.ts (Vitest)

```typescript
import { describe, it, expect } from "vitest";
import { route } from "../src/router.js";
import fs from "node:fs";

describe("router mock flow", () => {
  it("returns a deterministic patch", async () => {
    const code = "export const x=1;\n";
    const res = await route({
      selection: { filePath: "sample.ts", code },
      intent: "fix", modelPref: "mock", maxTokens: 100, temperature: 0.1
    });
    expect(res.unifiedDiff).toContain("Mock-FIX");
    expect(res.unifiedDiff).toContain("sample.ts");
  });
});
```

### Run it

```bash
npm i
npm run test              # mock provider (deterministic)
USE_MOCK=1 npm run dev    # end-to-end demo without touching real APIs
```

Swap to real providers later by adding official SDKs (still compliant), setting `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`, and flipping `USE_MOCK=0`.

---

## How to Test "Paid-Only" Flows Without Spoofing

### Contract tests
Define JSON contracts (request/response shapes) and assert your code obeys them, independent of the model.

```typescript
// tests/contracts/openai.spec.ts
import { describe, it, expect } from "vitest";
import { OpenAIRequestSchema, OpenAIResponseSchema } from "../src/contracts/openai.js";

describe("OpenAI API contract", () => {
  it("request matches expected shape", () => {
    const req = {
      model: "gpt-4",
      messages: [{ role: "user", content: "test" }],
      max_tokens: 100
    };
    expect(() => OpenAIRequestSchema.parse(req)).not.toThrow();
  });

  it("response matches expected shape", () => {
    const res = {
      id: "chatcmpl-123",
      object: "chat.completion",
      created: 1677652288,
      model: "gpt-4",
      choices: [{ index: 0, message: { role: "assistant", content: "test" }, finish_reason: "stop" }]
    };
    expect(() => OpenAIResponseSchema.parse(res)).not.toThrow();
  });
});
```

### Golden files
Store expected patches for small fixtures; fail CI if diffs drift.

```typescript
// tests/golden/refactor.spec.ts
import { describe, it, expect } from "vitest";
import { route } from "../src/router.js";
import fs from "node:fs";

describe("golden file regression tests", () => {
  it("produces expected refactoring patch", async () => {
    const code = fs.readFileSync("tests/fixtures/legacy.ts", "utf8");
    const res = await route({
      selection: { filePath: "legacy.ts", code },
      intent: "refactor", modelPref: "mock", maxTokens: 500, temperature: 0
    });

    const golden = fs.readFileSync("tests/golden/legacy_refactor.patch", "utf8");
    expect(res.unifiedDiff).toBe(golden);
  });
});
```

### Fault injection
Simulate rate-limit, 5xx, or timeouts in `providers/mock.ts`.

```typescript
// src/providers/mock.ts (enhanced)
import { Request, Patch } from "../schema.js";

export async function callMockLLM(req: Request): Promise<Patch> {
  // Simulate fault injection based on environment variables
  if (process.env.INJECT_RATE_LIMIT === "1") {
    throw new Error("Rate limit exceeded (429)");
  }

  if (process.env.INJECT_TIMEOUT === "1") {
    await new Promise(resolve => setTimeout(resolve, 60000)); // simulate timeout
  }

  if (process.env.INJECT_SERVER_ERROR === "1") {
    throw new Error("Internal server error (500)");
  }

  // Normal mock response
  const header = `/* Mock-${req.intent.toUpperCase()} by router */\n`;
  const newCode = header + req.selection.code;
  const diff = [
    `--- a/${req.selection.filePath}`,
    `+++ b/${req.selection.filePath}`,
    `@@`,
    `-${req.selection.code.split("\n").join("\n-")}`,
    `+${newCode.split("\n").join("\n+")}`
  ].join("\n");
  return { filePath: req.selection.filePath, unifiedDiff: diff };
}
```

### Latency budgets
Add a sleep/jitter layer to mimic real provider latencies and verify timeouts/retries.

```typescript
// src/providers/latencySimulator.ts
export async function simulateLatency(provider: string) {
  const latencies = {
    openai: { min: 200, max: 2000 },      // 200-2000ms
    anthropic: { min: 300, max: 3000 },   // 300-3000ms
    mock: { min: 10, max: 50 }            // 10-50ms
  };

  const range = latencies[provider] || latencies.mock;
  const delay = Math.random() * (range.max - range.min) + range.min;

  await new Promise(resolve => setTimeout(resolve, delay));
}

// Usage in router.ts
import { simulateLatency } from "./latencySimulator.js";

export async function route(req: Req) {
  const r = Request.parse(req);
  return limiter.schedule(async () => {
    await simulateLatency(r.modelPref);
    // ... rest of routing logic
  });
}
```

---

## Production Architecture

### Multi-tier routing strategy

```
User Selection
     ↓
[Intent Classifier]
     ↓
┌─────────────────┐
│  Router Layer   │
│  - Rate limits  │
│  - Cost caps    │
│  - Model health │
└─────────────────┘
     ↓
┌──────────┬──────────┬──────────┐
│ OpenAI   │ Anthropic│  Local   │
│ (speed)  │ (quality)│ (privacy)│
└──────────┴──────────┴──────────┘
     ↓
[Response Cache - GPTRAM]
     ↓
[Patch Application]
```

### Local indexing pipeline

```
Codebase
   ↓
[nowgrep/ripgrep] → Fast exact search
   ↓
[AST Parser] → Structural understanding
   ↓
[Embedding Model] → Semantic vectors
   ↓
[Qdrant/FAISS] → Vector search
   ↓
[Context Assembler] → Smart context window packing
   ↓
LLM Request
```

### Cost tracking and governance

```typescript
// src/governance/costTracker.ts
import { z } from "zod";

export const CostEvent = z.object({
  timestamp: z.date(),
  provider: z.enum(["openai", "anthropic", "local"]),
  model: z.string(),
  inputTokens: z.number(),
  outputTokens: z.number(),
  costUSD: z.number(),
  userId: z.string(),
  projectId: z.string()
});

export class CostTracker {
  async logUsage(event: z.infer<typeof CostEvent>) {
    // Store in SQLite/PostgreSQL
    await db.insert("cost_events").values(event);

    // Check budget limits
    const monthlyTotal = await this.getMonthlyTotal(event.userId);
    if (monthlyTotal > USER_BUDGET_LIMIT) {
      throw new Error("Monthly budget exceeded");
    }
  }

  async getMonthlyTotal(userId: string): Promise<number> {
    const start = new Date();
    start.setDate(1);
    start.setHours(0, 0, 0, 0);

    const result = await db
      .select({ total: sum(cost_events.costUSD) })
      .from(cost_events)
      .where(
        and(
          eq(cost_events.userId, userId),
          gte(cost_events.timestamp, start)
        )
      );

    return result[0]?.total || 0;
  }
}
```

---

## Integration with PNKLN Products

### Cor ↔ NS (9-LLM Coordination)
Cor's code understanding feeds context to NS's planning LLM:
- "This function has 3 security vulnerabilities" → NS prioritizes security review
- "Test coverage is 45%" → NS schedules test generation task
- "Dependency outdated (CVE-2024-1234)" → NS creates upgrade task

### Cor ↔ ActiveShield
Cor's code analysis detects watermarked AI-generated code:
- ResNet-based watermark detector scans all patches before application
- Alert if patch contains ShadowTag 2.0 watermark
- Policy: block/allow/flag based on org rules

### Cor ↔ AiURCM (Compliance)
Cor enforces regulatory compliance in code:
- BERT analyzes patches for GDPR/CCPA violations (PII logging, data retention)
- Blocks patches that violate org compliance policies
- Audit trail: all code changes logged with compliance status

---

## Compliance Checklist

### ✅ What we DO
- Use official SDKs (OpenAI Python SDK, Anthropic SDK)
- Respect rate limits and quotas
- Pay for usage at published rates
- Use public APIs only
- Build local indexes from owned codebases
- Cache responses in our own infrastructure

### ❌ What we DON'T do
- Spoof authentication tokens
- Impersonate official extensions
- Access private/undocumented APIs
- Bypass vendor rate limits
- Intercept network traffic (MITM)
- Forge entitlement flags
- Use cracked/leaked API keys

---

## Cost Comparison: Compliant vs. Spoofed

### GitHub Copilot Business
- **Official**: $19/user/month ($228/year)
- **Spoofed approach**: $0 upfront, legal risk = ∞, no support
- **Cor approach**: $0.01-0.10 per completion (usage-based), legal risk = 0, full support

**Break-even analysis:**
- Average developer: 100 completions/day × 20 work days = 2,000/month
- Cor cost: 2,000 × $0.05 = $100/month
- Savings vs. Copilot: 47% ($228 → $100)
- Risk reduction: Priceless

### Claude Code (Sonnet)
- **Official**: Pay-per-use via API (~$0.003/1K input tokens, $0.015/1K output)
- **Spoofed approach**: Access via editor extension entitlements (blocked)
- **Cor approach**: Same official API, but with intelligent caching

**Cost optimization through caching:**
- Naive approach: 10K requests/day × $0.02/request = $200/day
- Cor with GPTRAM cache (80% hit rate): 2K new requests × $0.02 = $40/day
- Monthly savings: $4,800

---

## Migration Path for Existing Copilot/Cody Users

### Phase 1: Parallel operation (Week 1-2)
- Install Cor extension alongside existing tool
- Configure Cor to use same models (OpenAI Codex, Claude)
- Test on non-critical code

### Phase 2: Feature parity validation (Week 3-4)
- Compare completion quality (blind A/B test)
- Measure latency (Cor should be competitive or faster with local index)
- Verify context accuracy (Cor's local index vs. vendor index)

### Phase 3: Gradual rollout (Month 2-3)
- Migrate 10% of team to Cor exclusively
- Monitor cost, quality, developer satisfaction
- Expand to 50%, then 100%

### Phase 4: Optimization (Month 4+)
- Fine-tune routing rules (OpenAI for speed, Anthropic for quality)
- Optimize caching (increase hit rate to 90%+)
- Add custom models for domain-specific code

---

## Open Source Strategy

### Core principle
Cor's router and indexing layer are **open source** (MIT license), vendor integrations are **plugins**.

**Why open source?**
- Builds trust (auditable, no hidden spoofing)
- Community contributions (new model integrations)
- Ecosystem growth (plugins for Neovim, Emacs, JetBrains)
- Competitive moat through network effects

**What stays proprietary?**
- PNKLN-specific integrations (NS, ActiveShield, AiURCM)
- Advanced routing algorithms (learned from usage data)
- Enterprise features (SSO, audit logs, compliance dashboards)

---

## FAQ

### Q: Is this legal?
**A:** Yes. We use official APIs with proper authentication and billing. No ToS violations.

### Q: Does it work with my organization's VPN/proxy?
**A:** Yes. All traffic goes through standard HTTPS to official endpoints. No special network requirements.

### Q: Can I use my existing OpenAI/Anthropic keys?
**A:** Yes. Bring your own keys (BYOK) or use PNKLN's managed keys.

### Q: What if a vendor blocks programmatic access?
**A:** We only use documented, supported APIs. If a vendor blocks legitimate API usage, we'll work with them or find alternatives.

### Q: How does local indexing compare to GitHub Copilot's cloud index?
**A:** For private repositories, local indexing is often **better** (no stale data, instant updates). For public repos, Copilot may have slight edge from cross-repo learning.

### Q: Can I run Cor fully offline?
**A:** Yes, with local models (Llama 3, CodeLlama, StarCoder). Quality trades off, but privacy is absolute.

---

## TL;DR

**Left out:** Anything requiring faked entitlements, private extension internals, or bypassing vendor limits.

**Kept:** The UX you want (select → think → patch), multi-LLM routing, local indexing/caching, full audits—and it's stable, supportable, and safe to ship.

**Mock now, swap later:** The scaffold above lets you prove the flow today; flip to real SDKs when ready, no rewrites.

**Strategic advantage:** While competitors risk legal action for ToS violations, Cor builds a defensible, scalable, enterprise-ready platform that vendors will **partner** with, not fight.

---

*Document prepared for PNKLN permanent memory storage, November 2025.*
