# Compliance & Design Decisions

## Overview

This document explains what Universal Copilot **deliberately leaves out** and why, ensuring we stay fully compliant with vendor terms of service, maintain ethical AI development practices, and provide a supportable, auditable system.

---

## What Gets Left Out (By Design)

### 1. Paywalled Capabilities Without Paying

**Left Out:**


- Vendor-only features (e.g., "Pro-only" context windows, enterprise rate limits)


- Proprietary features from first-party extensions


- Features that require specific subscription tiers

**Why:**


- **Legal**: Bypassing paywalls violates terms of service


- **Ethical**: Creators deserve compensation for their work


- **Sustainable**: Undermining business models hurts the ecosystem

**Alternative:**

```typescript
// We use what YOU pay for
const config = {
  providers: {
    openai: {
      apiKey: process.env.OPENAI_API_KEY, // YOUR key
      model: "gpt-4o", // model YOU have access to
    },
  },
};

```

---

### 2. Extension-Internal/Private APIs

**Left Out:**


- Private endpoints used by GitHub Copilot


- Claude Code extension's internal APIs


- Cody's proprietary communication channels


- Entitlement flags and license checks


- Telemetry channels

**Why:**


- **Security**: Private APIs can change without notice


- **Stability**: No guarantee of continued access


- **Legal**: Reverse engineering may violate TOS


- **Supportable**: Can't debug what we don't control

**Alternative:**

```typescript
// We use PUBLIC SDKs only
import OpenAI from "openai"; // Official public SDK
import Anthropic from "@anthropic-ai/sdk"; // Official public SDK

// NOT: Hooking into extension internals
// NOT: Intercepting extension <-> server traffic
// NOT: Spoofing extension user agents

```

---

### 3. Vendor-Side Codebase Indexes

**Left Out:**


- GitHub Copilot's prebuilt code embeddings


- Claude Code's hosted codebase indexes


- Vendor-maintained code intelligence pipelines


- Cross-repository semantic search (vendor-hosted)

**Why:**


- **Access Control**: These require authenticated extension access


- **Data Privacy**: Your code on vendor servers


- **Dependency**: Creates vendor lock-in

**Alternative:**

```typescript
// Build YOUR OWN index (you control the data)
import { ripgrep } from "your-search-tool";
import { Qdrant } from "vector-db";

// Local code intelligence
const results = await ripgrep.search(pattern, {
  cwd: workspaceRoot,
  glob: "**/*.ts",
});

// Your embeddings, your control
const embeddings = await localEmbedder.embed(codeChunk);
await vectorDb.insert(embeddings);

```

---

### 4. Undocumented UI Hooks in Editors

**Left Out:**


- Invasive DOM manipulation in VS Code webviews


- IPC hooks into editor internals


- Modification of other extensions' behavior


- Undocumented editor APIs

**Why:**


- **Fragility**: Breaks with editor updates


- **Conflicts**: Interferes with other extensions


- **Unsupported**: No help when it breaks


- **Security**: Potential injection vulnerabilities

**Alternative:**

```typescript
// Use DOCUMENTED VS Code APIs
import * as vscode from "vscode";

// Official extension API
const editor = vscode.window.activeTextEditor;
const selection = editor.selection;
const text = editor.document.getText(selection);

// Apply patch using documented APIs
await editor.edit((editBuilder) => {
  editBuilder.replace(selection, patchedCode);
});

```

---

### 5. Bypassing Org Policy, Network Controls, or Usage Caps

**Left Out:**


- Proxy around corporate network restrictions


- Circumvent org-level model blocks


- Evade usage quotas or rate limits


- Hide usage from org administrators

**Why:**


- **Security**: Org policies exist for good reasons


- **Compliance**: Regulatory requirements matter


- **Trust**: Transparency with org admins


- **Liability**: You're responsible for misuse

**Alternative:**

```typescript
// Respect rate limits
const limiter = new Bottleneck({
  minTime: 150, // ~6.6 rps (within OpenAI free tier)
  maxConcurrent: 2,
});

// Respect org policies
if (isModelBlocked(model)) {
  throw new Error("Model blocked by org policy");
}

// Track usage transparently
logger.info("LLM request", {
  user: userId,
  model: model,
  tokensUsed: response.usage.total_tokens,
  cost: estimateCost(response),
});

```

---

## What You DO Get Instead

### Same UX Shape

✅ **Editor widget** - Select code → Get suggestions
✅ **Patch format** - Unified diffs you can review
✅ **Multi-LLM routing** - Choose best provider for task
✅ **Repo-aware context** - Use YOUR local index

```typescript
// End-to-end flow (all compliant)
const response = await router.route({
  selection: { code, filePath, language },
  intent: "refactor",
  modelPref: "auto", // Picks best available
});

await patcher.applyPatch(
  response.patch.filePath,
  response.patch.unifiedDiff,
  { createBackup: true }
);

```

### Your Data, Your Index

✅ **Local storage** - GPTRAM, SQLite, or your choice
✅ **Local search** - ripgrep, nowgrep, or custom
✅ **Local embeddings** - Qdrant, FAISS, or hosted
✅ **No vendor lock-in** - Export/migrate anytime

### Reliability + Auditability

✅ **Clear logs** - Every decision traceable
✅ **Cost tracking** - Know exactly what you spend
✅ **Error handling** - Graceful degradation
✅ **Governance** - Judge #6 safety enforcement

---

## Testing Without Spoofing

### Contract Tests

Validate request/response shapes independent of provider:

```typescript
describe("Provider contract", () => {
  it("should return valid patch structure", async () => {
    const patch = await provider.generatePatch(request);

    expect(patch).toMatchObject({
      filePath: expect.any(String),
      unifiedDiff: expect.stringMatching(/^---.*\n\+\+\+.*\n@@/),
      explanation: expect.any(String),
      confidence: expect.any(Number),
    });
  });
});

```

### Golden Files

Store expected outputs for regression testing:

```typescript
// tests/fixtures/refactor-example-expected.patch
--- a/example.ts
+++ b/example.ts
@@ -1,3 +1,5 @@
+// Refactored for clarity
+const items = [1, 2, 3];
-const x = [1,2,3];
-console.log(x);
+console.log(items);

```

### Fault Injection

Simulate provider failures without touching real APIs:

```typescript
class FaultyProvider extends MockProvider {
  async generatePatch(request: CopilotRequest): Promise<Patch> {
    if (Math.random() < 0.3) {
      throw new ProviderError("Rate limit", "test", true);
    }
    return super.generatePatch(request);
  }
}

// Test retry logic
const response = await router.route(request);
expect(response.patch).toBeDefined(); // Eventually succeeds

```

### Latency Budgets

Verify timeouts and performance:

```typescript
class SlowProvider extends MockProvider {
  async generatePatch(request: CopilotRequest): Promise<Patch> {
    await sleep(2000); // Simulate slow API
    return super.generatePatch(request);
  }
}

// Test timeout handling
await expect(
  router.route(request, { timeout: 1000 })
).rejects.toThrow("Timeout");

```

---

## Vendor Comparison

| Feature | Universal Copilot | GitHub Copilot | Claude Code | Cody |
|---------|-------------------|----------------|-------------|------|
| **API Access** | Public SDKs only | Private extension APIs | Private extension APIs | Private extension APIs |
| **Governance** | Judge #6 (cryptographic) | Undocumented | Undocumented | Undocumented |
| **Cost Tracking** | ✅ Transparent | ❌ Opaque | ❌ Opaque | ❌ Opaque |
| **Audit Trail** | ✅ Complete | ❌ None | ❌ None | ❌ None |
| **Multi-Provider** | ✅ Yes (3+) | ❌ No | ❌ No | ❌ No |
| **Local Index** | ✅ Your choice | ❌ GitHub-only | ❌ Vendor-hosted | ❌ Vendor-hosted |
| **Offline Mode** | ✅ Mock provider | ❌ No | ❌ No | ❌ No |
| **Vendor Lock-In** | ❌ None | ✅ GitHub | ✅ Anthropic | ✅ Sourcegraph |

---

## Compliance Checklist

Before deployment, verify:



- [ ] All API keys are YOUR own (no sharing/spoofing)


- [ ] Using public SDKs only (no private APIs)


- [ ] Governance enabled in production


- [ ] Rate limiting configured appropriately


- [ ] Audit logging enabled


- [ ] Cost tracking active


- [ ] Backup/rollback tested


- [ ] Error handling validated


- [ ] Org policies respected


- [ ] Terms of Service reviewed

---

## Legal Disclaimer

Universal Copilot is designed to comply with vendor terms of service, copyright law, and ethical AI development practices. Users are responsible for:



1. **API Usage**: Ensure your API keys are used in accordance with provider terms


2. **Code Ownership**: Respect copyright and licensing of code you process


3. **Data Privacy**: Handle sensitive code appropriately


4. **Org Policies**: Follow your organization's AI usage policies


5. **Liability**: You are responsible for outputs and their use

**We do not:**


- Provide legal advice


- Guarantee compliance with all jurisdictions


- Warrant fitness for any particular purpose


- Accept liability for misuse

---

## Questions?

**Q: Can I use this commercially?**
A: Yes, if you have appropriate licenses for the LLM providers you use.

**Q: What if a vendor changes their TOS?**
A: We adapt to use compliant alternatives or document limitations.

**Q: Can I contribute compliance improvements?**
A: Absolutely! Open a PR with your proposed changes.

**Q: What about regulatory compliance (HIPAA, SOX, etc.)?**
A: Judge #6 provides audit trails; consult your legal team for full compliance.

---

## Summary

Universal Copilot trades **grey-area features** for:


- ✅ **Legal safety**


- ✅ **Long-term supportability**


- ✅ **Full auditability**


- ✅ **Vendor independence**


- ✅ **Ethical AI development**

You get **90% of the functionality** with **100% of the peace of mind**.
