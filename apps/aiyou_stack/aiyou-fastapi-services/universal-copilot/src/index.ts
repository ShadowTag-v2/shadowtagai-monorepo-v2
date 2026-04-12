/**
 * Universal Copilot - Compliant Multi-LLM Code Assistant
 * Main entry point and public API
 */

export * from "./core/schema.js";
export * from "./core/errors.js";
export * from "./core/router.js";
export * from "./core/patcher.js";
export * from "./core/governance.js";
export * from "./providers/index.js";

// Re-export commonly used types
export type {
  CopilotRequest,
  CopilotResponse,
  Patch,
  Selection,
  Intent,
  Provider,
  RouterConfig,
} from "./core/schema.js";

export type { GovernanceEngine } from "./core/router.js";
export type { PatchResult, PatchOptions } from "./core/patcher.js";

// Main classes
export { CopilotRouter } from "./core/router.js";
export { UnifiedPatcher, createPatcher } from "./core/patcher.js";
export { Judge6Adapter, MockGovernance, createGovernance } from "./core/governance.js";
export { createProvider } from "./providers/index.js";
