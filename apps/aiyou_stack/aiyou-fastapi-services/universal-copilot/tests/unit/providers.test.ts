/**
 * Provider unit tests
 */

import { describe, expect, it } from "vitest";
import type { CopilotRequest } from "../../src/core/schema.js";
import { MockProvider } from "../../src/providers/mock.js";

describe("MockProvider", () => {
  it("should generate deterministic patches", async () => {
    const provider = new MockProvider();

    const request: CopilotRequest = {
      selection: {
        filePath: "test.ts",
        language: "typescript",
        code: "const x = 1;",
      },
      intent: "fix",
      modelPref: "mock",
      maxTokens: 100,
      temperature: 0.1,
    };

    const patch1 = await provider.generatePatch(request);
    const patch2 = await provider.generatePatch(request);

    // Structure should be consistent
    expect(patch1.filePath).toBe(patch2.filePath);
    expect(patch1.unifiedDiff).toContain("---");
    expect(patch1.unifiedDiff).toContain("+++");
    expect(patch1.unifiedDiff).toContain("@@");
  });

  it("should generate different patches for different intents", async () => {
    const provider = new MockProvider();

    const baseRequest: CopilotRequest = {
      selection: {
        filePath: "test.ts",
        code: "const x = 1;",
      },
      intent: "fix",
      modelPref: "mock",
    };

    const fixPatch = await provider.generatePatch(baseRequest);
    const refactorPatch = await provider.generatePatch({
      ...baseRequest,
      intent: "refactor",
    });

    expect(fixPatch.unifiedDiff).toContain("Bug fix");
    expect(refactorPatch.unifiedDiff).toContain("Refactored");
  });

  it("should provide explanations", async () => {
    const provider = new MockProvider();

    const request: CopilotRequest = {
      selection: {
        filePath: "test.ts",
        code: "const x = 1;",
      },
      intent: "explain",
      modelPref: "mock",
    };

    const patch = await provider.generatePatch(request);
    expect(patch.explanation).toBeDefined();
    expect(patch.explanation).toContain("explanation");
  });

  it("should be always available", () => {
    const provider = new MockProvider();
    expect(provider.isAvailable()).toBe(true);
  });

  it("should have zero cost", () => {
    const provider = new MockProvider();

    const request: CopilotRequest = {
      selection: {
        filePath: "test.ts",
        code: "const x = 1;",
      },
      intent: "fix",
      modelPref: "mock",
    };

    expect(provider.estimateCost(request)).toBe(0);
  });

  it("should return correct model name", () => {
    const provider = new MockProvider();
    expect(provider.getName()).toBe("mock");
    expect(provider.getModel()).toContain("mock");
  });
});
