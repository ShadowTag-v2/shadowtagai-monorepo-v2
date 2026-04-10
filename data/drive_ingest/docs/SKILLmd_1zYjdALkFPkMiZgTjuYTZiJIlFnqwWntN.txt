# Universal Copilot Patterns (Compliant AI-Assisted Coding)

**Purpose:** Build AI-assisted coding features without spoofing vendor APIs or violating TOS
**Enforcement:** `"suggest"`
**Priority:** `"high"`
**Version:** 1.0.0
**Cor Reference:** Cor. Spoofing

---

## Overview

This skill defines **compliant patterns** for building AI-assisted coding features (like GitHub Copilot, Claude Code, or Cody) without:
- Spoofing vendor APIs or entitlements
- Man-in-the-middle (MITM) attacks on vendor traffic
- Bypassing organizational policies or usage caps
- Hooking private/undocumented extension internals

**The Goal:** Same UX shape (select → think → patch), full auditability, zero legal/security risk.

---

## What Gets Left Out (By Design)

### 1. Paywalled Capabilities Without Paying

❌ **Not Allowed:**
```typescript
// Pretending you have Pro-tier access
const response = await openai.chat.completions.create({
  model: "gpt-4-32k",  // Your key doesn't have access
  headers: { "X-Entitlement": "pro" }  // SPOOFING
});
```

✅ **Compliant Alternative:**
```typescript
// Use what your key actually provides
const response = await openai.chat.completions.create({
  model: "gpt-4",  // Base tier you're paying for
  max_tokens: 4096  // Within your limits
});
```

### 2. Extension-Internal/Private APIs

❌ **Not Allowed:**
```typescript
// Intercepting Copilot extension's private endpoints
fetch("https://copilot-internal.github.com/entitlements", {
  headers: { "X-GitHub-Session": stolenSessionToken }
});
```

✅ **Compliant Alternative:**
```typescript
// Use official public APIs only
import OpenAI from "openai";
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
```

### 3. Vendor-Side Codebase Indexes

❌ **Not Allowed:**
```typescript
// Fetching GitHub's prebuilt code embeddings without permission
const embeddings = await fetch("https://copilot-index.github.com/repo/user/project");
```

✅ **Compliant Alternative:**
```typescript
// Build your own local index
import { embed } from "@your-org/embeddings";
const localEmbeddings = await embed(codebaseFiles);
// Store in local vector DB (Qdrant, FAISS, etc.)
```

### 4. Undocumented UI Hooks in Editors

❌ **Not Allowed:**
```typescript
// Injecting into Copilot's DOM/IPC channels
vscode.extensions.getExtension("github.copilot")
  .__internal_api.ghostText.override(myCustomSuggestions);
```

✅ **Compliant Alternative:**
```typescript
// Use public VS Code API
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const provider: vscode.InlineCompletionItemProvider = {
    provideInlineCompletionItems: async (document, position, context) => {
      // Your implementation using official APIs
      const suggestion = await getAISuggestion(document, position);
      return [new vscode.InlineCompletionItem(suggestion)];
    }
  };

  vscode.languages.registerInlineCompletionItemProvider(
    { pattern: "**" },
    provider
  );
}
```

### 5. Bypassing Org Policy or Rate Limits

❌ **Not Allowed:**
```typescript
// Proxying around org-level blocks
const proxy = "http://bypass-corporate-firewall.com";
await fetch(blockedModel, { proxy });
```

✅ **Compliant Alternative:**
```typescript
// Respect organizational controls
if (await isModelBlocked(modelName)) {
  throw new Error(`Model ${modelName} blocked by org policy`);
}
// Use approved models only
```

---

## What You Do Get (Compliant Architecture)

### Approved Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    EDITOR EXTENSION                      │
│  (VS Code / Cursor / Web Widget - Public APIs Only)     │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   ROUTING LAYER                          │
│  • Multi-LLM selection (OpenAI, Anthropic, local)       │
│  • Rate limiting (Bottleneck, Redis)                    │
│  • Cost tracking & budgets                              │
│  • Audit logging                                         │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│              OFFICIAL PROVIDER SDKS                      │
│  • OpenAI SDK (with your API key)                       │
│  • Anthropic SDK (with your API key)                    │
│  • Local models (Ollama, vLLM, etc.)                    │
└──────────────────────┬──────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│              LOCAL CODE INDEX                            │
│  • GPTRAM/SQLite (hit-rate tracking)                    │
│  • nowgrep/ripgrep (low-latency search)                 │
│  • Local embeddings (Qdrant/FAISS)                      │
│  • Your data, your control                              │
└─────────────────────────────────────────────────────────┘
```

### Features You Get

✅ **Same UX Shape**
- Browser/editor widget
- "Send selection → Get patch" workflow
- Multi-LLM routing (choose best model for task)
- Repo-aware context (local index)

✅ **Your Data, Your Index**
- GPTRAM/SQLite for hit-rate tracking
- nowgrep/ripgrep for low-latency search
- Local embeddings (Qdrant/FAISS) if needed
- No vendor lock-in

✅ **Reliability + Auditability**
- Clear logs (who requested what, when, cost)
- Cost tracking (budget alerts)
- Zero gray-area traffic interception
- Compliant with corporate security policies

---

## Minimal Mock Setup

**Purpose:** Test end-to-end flows without touching vendor APIs (safe for CI/CD)

**See:** [resources/mock-setup.md](resources/mock-setup.md) for complete implementation

### Quick Demo

```bash
# Clone the mock setup (separate repo recommended)
git clone https://github.com/shadowtagai/mock-universal-copilot
cd mock-universal-copilot

# Install dependencies
pnpm install

# Run tests (uses mock provider, deterministic)
pnpm test

# Run end-to-end demo (no real API calls)
USE_MOCK=1 pnpm dev

# Later: Swap to real providers
OPENAI_API_KEY=sk-... USE_MOCK=0 pnpm dev
```

**Key Components:**
- `widget.ts` - In-page assistant shim (simulates code selection)
- `router.ts` - Local router (chooses provider, enforces limits)
- `providers/mock.ts` - Deterministic fake LLM (for tests)
- `providers/openai.ts` - Official SDK integration
- `providers/anthropic.ts` - Official SDK integration
- `applyPatch.ts` - Emulates editor applying patch

---

## Testing "Paid-Only" Flows Without Spoofing

### 1. Contract Tests

Define JSON contracts (request/response shapes) and assert your code obeys them:

```typescript
// tests/contracts/openai.contract.ts
import { z } from "zod";

export const OpenAIRequestContract = z.object({
  model: z.string(),
  messages: z.array(z.object({
    role: z.enum(["system", "user", "assistant"]),
    content: z.string()
  })),
  max_tokens: z.number().int().positive().max(4096),
  temperature: z.number().min(0).max(2)
});

export const OpenAIResponseContract = z.object({
  id: z.string(),
  choices: z.array(z.object({
    message: z.object({
      role: z.literal("assistant"),
      content: z.string()
    }),
    finish_reason: z.enum(["stop", "length", "content_filter"])
  })),
  usage: z.object({
    prompt_tokens: z.number(),
    completion_tokens: z.number(),
    total_tokens: z.number()
  })
});

// Test that your code obeys contract
it("should match OpenAI request contract", () => {
  const request = buildOpenAIRequest(userInput);
  expect(() => OpenAIRequestContract.parse(request)).not.toThrow();
});
```

### 2. Golden Files

Store expected patches for small fixtures; fail CI if diffs drift:

```typescript
// tests/golden/refactor.test.ts
import fs from "fs";
import path from "path";

it("should produce expected refactor patch", async () => {
  const input = fs.readFileSync("tests/fixtures/sample.ts", "utf8");
  const patch = await route({
    selection: { filePath: "sample.ts", code: input },
    intent: "refactor",
    modelPref: "mock"
  });

  const expectedPatch = fs.readFileSync(
    "tests/golden/sample_refactor.patch",
    "utf8"
  );

  expect(patch.unifiedDiff).toBe(expectedPatch);
});
```

### 3. Fault Injection

Simulate rate-limit, 5xx, or timeouts in `providers/mock.ts`:

```typescript
// providers/mock.ts
export async function callMockLLM(req: Request): Promise<Patch> {
  // Inject faults based on env var
  if (process.env.INJECT_RATE_LIMIT === "1") {
    throw new Error("Rate limit exceeded (mock)");
  }

  if (process.env.INJECT_5XX === "1") {
    throw new Error("Service unavailable (mock)");
  }

  if (process.env.INJECT_TIMEOUT === "1") {
    await new Promise(resolve => setTimeout(resolve, 10000));
  }

  // Normal mock response
  return { filePath: req.selection.filePath, unifiedDiff: "..." };
}
```

### 4. Latency Budgets

Add sleep/jitter layer to mimic real provider latencies:

```typescript
// router.ts
const limiter = new Bottleneck({
  minTime: 150,  // ~6.6 rps
  reservoir: 100,  // max 100 concurrent
  reservoirRefreshAmount: 100,
  reservoirRefreshInterval: 60 * 1000  // per minute
});

export async function route(req: Request) {
  return limiter.schedule(async () => {
    // Add artificial latency to match real API
    if (process.env.MOCK_LATENCY_MS) {
      const jitter = Math.random() * 200;  // 0-200ms jitter
      await sleep(parseInt(process.env.MOCK_LATENCY_MS) + jitter);
    }

    const provider = selectProvider(req.modelPref);
    return provider(req);
  });
}
```

---

## Compliance Checklist

When building AI-assisted coding features:

- [ ] **Only use official SDKs** (OpenAI, Anthropic, etc. - no private APIs)
- [ ] **Respect API keys & entitlements** (don't fake Pro access with Basic key)
- [ ] **No MITM on vendor traffic** (don't intercept Copilot/Claude Code requests)
- [ ] **No hooking private extension internals** (use public VS Code API only)
- [ ] **Respect org policies** (if model blocked, don't bypass)
- [ ] **Build local index** (don't steal vendor's prebuilt embeddings)
- [ ] **Audit logging enabled** (track all LLM calls with user, cost, timestamp)
- [ ] **Rate limiting enforced** (don't abuse provider APIs)
- [ ] **Cost tracking** (alert when approaching budget limits)
- [ ] **Mock testing in CI** (don't hit real APIs in automated tests)

---

## Common Violations & Fixes

### Violation 1: Hardcoded API Keys

❌ **Bad:**
```typescript
const openai = new OpenAI({
  apiKey: "YOUR_API_KEY_HERE"  // Hardcoded!
});
```

✅ **Good:**
```typescript
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY  // From environment
});

if (!process.env.OPENAI_API_KEY) {
  throw new Error("OPENAI_API_KEY not set");
}
```

### Violation 2: No Rate Limiting

❌ **Bad:**
```typescript
// Unlimited requests to OpenAI
for (const file of files) {
  await openai.chat.completions.create({ ... });
}
```

✅ **Good:**
```typescript
import Bottleneck from "bottleneck";

const limiter = new Bottleneck({
  minTime: 100,  // 10 rps max
  maxConcurrent: 5
});

for (const file of files) {
  await limiter.schedule(() =>
    openai.chat.completions.create({ ... })
  );
}
```

### Violation 3: No Cost Tracking

❌ **Bad:**
```typescript
// No idea how much this costs
await openai.chat.completions.create({ ... });
```

✅ **Good:**
```typescript
const response = await openai.chat.completions.create({ ... });

const cost = calculateCost({
  model: "gpt-4",
  inputTokens: response.usage.prompt_tokens,
  outputTokens: response.usage.completion_tokens
});

await logUsage({
  user: req.user.id,
  model: "gpt-4",
  tokens: response.usage.total_tokens,
  cost,
  timestamp: new Date()
});

if (await getUserMonthlyCost(req.user.id) > BUDGET_LIMIT) {
  throw new Error("Monthly budget exceeded");
}
```

---

## Integration with ShadowTagAi Stack

### Backend Service (Express + TypeScript)

```typescript
// backend/ai-assist/routes.ts
import { Router } from "express";
import { authenticate } from "../middleware/auth.middleware";
import { route } from "./router";

const router = Router();

router.post(
  "/assist",
  authenticate,
  async (req, res, next) => {
    try {
      const { selection, intent } = req.body;

      // Route to appropriate LLM
      const patch = await route({
        selection,
        intent,
        modelPref: req.user.preferences?.aiModel || "auto",
        maxTokens: 800,
        temperature: 0.2
      });

      // Log usage for billing
      await logAIUsage({
        userId: req.user.id,
        intent,
        tokensUsed: patch.metadata.tokensUsed,
        cost: patch.metadata.cost,
        timestamp: new Date()
      });

      res.json({ success: true, data: patch });
    } catch (error) {
      next(error);
    }
  }
);

export default router;
```

### Frontend (React + TanStack Query)

```typescript
// frontend/hooks/useAIAssist.ts
import { useMutation } from "@tanstack/react-query";
import api from "../services/api";

export const useAIAssist = () => {
  return useMutation({
    mutationFn: async ({ selection, intent }: { selection: Selection; intent: string }) => {
      const { data } = await api.post("/ai-assist/assist", {
        selection,
        intent
      });
      return data;
    },
    onError: (error) => {
      console.error("AI assist failed:", error);
      // Show user-friendly error
    }
  });
};

// Usage in component
const { mutateAsync: assist, isPending } = useAIAssist();

const handleAssist = async () => {
  const patch = await assist({
    selection: { filePath: "app.ts", code: selectedCode },
    intent: "refactor"
  });
  applyPatchToEditor(patch);
};
```

---

## Security Considerations

### 1. User Data Privacy

```typescript
// Never send sensitive data to LLM without user consent
const sanitizedCode = removeSensitivePatterns(code);

// Log what's being sent
await audit.log({
  action: "ai_assist_request",
  user: req.user.id,
  codeHash: hash(sanitizedCode),  // Hash, not full code
  intent,
  timestamp: new Date()
});
```

### 2. Output Sanitization

```typescript
// Don't blindly apply LLM-generated code
const patch = await route(request);

// Validate patch before applying
if (!isValidPatch(patch)) {
  throw new Error("Generated patch failed validation");
}

// Check for security issues in generated code
const securityIssues = await scanForVulnerabilities(patch);
if (securityIssues.length > 0) {
  throw new Error(`Security issues detected: ${securityIssues.join(", ")}`);
}
```

### 3. Cost Controls

```typescript
// Per-user monthly budgets
const BUDGET_LIMITS = {
  free: 10,      // $10/month
  pro: 100,      // $100/month
  enterprise: 1000  // $1000/month
};

// Check before allowing request
const userCost = await getUserMonthlyCost(req.user.id);
const userTier = req.user.tier || "free";

if (userCost >= BUDGET_LIMITS[userTier]) {
  throw new Error("Monthly budget exceeded. Upgrade to continue.");
}
```

---

## Best Practices

- [ ] Use official SDKs only (no custom HTTP clients for providers)
- [ ] Always authenticate requests (don't allow anonymous AI assist)
- [ ] Rate limit aggressively (protect your API budget)
- [ ] Log all LLM calls (audit trail for debugging + billing)
- [ ] Sanitize inputs (remove secrets, PII before sending to LLM)
- [ ] Validate outputs (don't blindly apply generated code)
- [ ] Build local index (don't rely on vendor's code intelligence)
- [ ] Test with mocks (don't hit real APIs in CI/CD)
- [ ] Monitor costs (alert when approaching budget limits)
- [ ] Respect org policies (if model blocked, fail gracefully)

---

## Resources

**Skill Resources:**
- [resources/mock-setup.md](resources/mock-setup.md) - Complete mock implementation with TypeScript examples
- [resources/practical-agent-building.md](resources/practical-agent-building.md) - MVP-focused agent patterns (God of Prompt framework)
- [resources/kernel-prompt-engineering.md](resources/kernel-prompt-engineering.md) - **KERNEL framework for writing effective AI prompts** (94% first-try success rate)

**Key Highlights:**
- **Mock Setup:** Production-ready TypeScript implementation for compliant universal copilot
- **Agent Building:** Memory, tools, autonomy patterns for AI agents (LangChain, CrewAI)
- **KERNEL Prompts:** Keep simple, Easy to verify, Reproducible, Narrow scope, Explicit constraints, Logical structure

**External:**
- OpenAI Official SDK: https://github.com/openai/openai-node
- Anthropic Official SDK: https://github.com/anthropics/anthropic-sdk-typescript
- VS Code Extension API: https://code.visualstudio.com/api

---

**Last Updated:** 2025-11-15
**Maintained By:** ShadowTagAi AI Team (Erik)
**Compliance:** TOS-compliant, no spoofing, no MITM
**Cor Reference:** Cor. Spoofing (Architecture patterns for compliant AI assistance)
