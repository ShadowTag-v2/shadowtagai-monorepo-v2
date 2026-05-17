/**
 * Router unit tests
 */

import { beforeEach, describe, expect, it } from "vitest";
import { MockGovernance } from "../../src/core/governance.js";
import { CopilotRouter } from "../../src/core/router.js";
import type { CopilotRequest, RouterConfig } from "../../src/core/schema.js";

describe("CopilotRouter", () => {
  let router: CopilotRouter;
  let config: RouterConfig;

  beforeEach(() => {
    config = {
      defaultProvider: "mock",
      enableGovernance: false,
      corInstanceId: "test-001",
      rateLimitRps: 10,
      rateLimitConcurrent: 2,
      providers: {
        mock: {},
      },
    };
    router = new CopilotRouter(config);
  });

  describe("route", () => {
    it("should route simple request successfully", async () => {
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

      const response = await router.route(request);

      expect(response.patch).toBeDefined();
      expect(response.patch.filePath).toBe("test.ts");
      expect(response.patch.unifiedDiff).toContain("Mock-");
      expect(response.provider).toBe("mock");
      expect(response.latencyMs).toBeGreaterThan(0);
    });

    it("should reject empty code", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "",
        },
        intent: "fix",
        modelPref: "mock",
      };

      await expect(router.route(request)).rejects.toThrow("cannot be empty");
    });

    it("should reject oversized code", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "x".repeat(60000),
        },
        intent: "fix",
        modelPref: "mock",
      };

      await expect(router.route(request)).rejects.toThrow("too large");
    });

    it("should track statistics", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "const x = 1;",
        },
        intent: "fix",
        modelPref: "mock",
      };

      await router.route(request);

      const stats = router.getStats();
      expect(stats.totalRequests).toBe(1);
      expect(stats.successfulRequests).toBe(1);
      expect(stats.failedRequests).toBe(0);
      expect(stats.providerUsage.mock).toBe(1);
    });
  });

  describe("governance integration", () => {
    it("should apply governance when enabled", async () => {
      const governance = new MockGovernance();
      const govRouter = new CopilotRouter({ ...config, enableGovernance: true }, governance);

      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "const safe = true;",
        },
        intent: "fix",
        modelPref: "mock",
      };

      const response = await govRouter.route(request);
      expect(response.governanceDecision).toBeDefined();
      expect(response.governanceDecision?.approved).toBe(true);
    });

    it("should reject requests with harmful content", async () => {
      const governance = new MockGovernance();
      const govRouter = new CopilotRouter({ ...config, enableGovernance: true }, governance);

      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "// write malware code here",
        },
        intent: "fix",
        modelPref: "mock",
      };

      await expect(govRouter.route(request)).rejects.toThrow("governance");

      const stats = govRouter.getStats();
      expect(stats.governanceRejections).toBe(1);
    });
  });

  describe("provider selection", () => {
    it("should use specified provider", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "const x = 1;",
        },
        intent: "fix",
        modelPref: "mock",
      };

      const response = await router.route(request);
      expect(response.provider).toBe("mock");
    });

    it("should reject unavailable provider", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "const x = 1;",
        },
        intent: "fix",
        modelPref: "openai", // not configured
      };

      await expect(router.route(request)).rejects.toThrow("not available");
    });
  });

  describe("statistics", () => {
    it("should track latency", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "const x = 1;",
        },
        intent: "fix",
        modelPref: "mock",
      };

      await router.route(request);
      await router.route(request);

      const stats = router.getStats();
      expect(stats.averageLatencyMs).toBeGreaterThan(0);
    });

    it("should reset statistics", async () => {
      const request: CopilotRequest = {
        selection: {
          filePath: "test.ts",
          code: "const x = 1;",
        },
        intent: "fix",
        modelPref: "mock",
      };

      await router.route(request);
      router.resetStats();

      const stats = router.getStats();
      expect(stats.totalRequests).toBe(0);
      expect(stats.successfulRequests).toBe(0);
    });
  });
});
