/**
 * Type-safe schema definitions for Universal Copilot
 * Using Zod for runtime validation and TypeScript inference
 */

import { z } from "zod";

/**
 * Code selection from editor
 */
export const Selection = z.object({
  filePath: z.string().min(1),
  language: z.string().optional(),
  code: z.string(),
  startLine: z.number().int().positive().optional(),
  endLine: z.number().int().positive().optional(),
  context: z.string().optional(), // surrounding code for context
});

export type Selection = z.infer<typeof Selection>;

/**
 * User intent for code modification
 */
export const Intent = z.enum([
  "explain", // Generate explanation
  "refactor", // Improve code structure
  "test", // Generate tests
  "fix", // Fix bugs or issues
  "optimize", // Improve performance
  "document", // Add documentation
  "security", // Fix security issues
]);

export type Intent = z.infer<typeof Intent>;

/**
 * LLM provider selection
 */
export const Provider = z.enum([
  "mock", // Deterministic mock for testing
  "openai", // OpenAI GPT models
  "anthropic", // Anthropic Claude models
  "auto", // Automatic selection based on task
]);

export type Provider = z.infer<typeof Provider>;

/**
 * Complete request to copilot
 */
export const CopilotRequest = z.object({
  selection: Selection,
  intent: Intent.default("fix"),
  modelPref: Provider.default("mock"),
  maxTokens: z.number().int().positive().max(8000).default(800),
  temperature: z.number().min(0).max(2).default(0.2),
  userId: z.string().optional(),
  sessionId: z.string().optional(),
});

export type CopilotRequest = z.infer<typeof CopilotRequest>;

/**
 * Unified diff patch format
 */
export const Patch = z.object({
  filePath: z.string(),
  unifiedDiff: z.string(),
  explanation: z.string().optional(),
  confidence: z.number().min(0).max(1).optional(),
});

export type Patch = z.infer<typeof Patch>;

/**
 * Response from copilot
 */
export const CopilotResponse = z.object({
  patch: Patch,
  provider: Provider,
  tokensUsed: z.number().int().nonnegative().optional(),
  latencyMs: z.number().nonnegative().optional(),
  governanceDecision: z
    .object({
      approved: z.boolean(),
      riskLevel: z.string(),
      reasoning: z.string().optional(),
    })
    .optional(),
});

export type CopilotResponse = z.infer<typeof CopilotResponse>;

/**
 * Error response
 */
export const CopilotError = z.object({
  code: z.string(),
  message: z.string(),
  provider: Provider.optional(),
  retryable: z.boolean().default(false),
  details: z.record(z.unknown()).optional(),
});

export type CopilotError = z.infer<typeof CopilotError>;

/**
 * Provider configuration
 */
export const ProviderConfig = z.object({
  apiKey: z.string().optional(),
  baseURL: z.string().url().optional(),
  timeout: z.number().int().positive().default(30000),
  retries: z.number().int().nonnegative().default(2),
  model: z.string().optional(),
});

export type ProviderConfig = z.infer<typeof ProviderConfig>;

/**
 * Router configuration
 */
export const RouterConfig = z.object({
  defaultProvider: Provider.default("mock"),
  enableGovernance: z.boolean().default(true),
  corInstanceId: z.string().default("copilot-001"),
  rateLimitRps: z.number().positive().default(6.6),
  rateLimitConcurrent: z.number().int().positive().default(2),
  providers: z.record(Provider, ProviderConfig).optional(),
});

export type RouterConfig = z.infer<typeof RouterConfig>;
