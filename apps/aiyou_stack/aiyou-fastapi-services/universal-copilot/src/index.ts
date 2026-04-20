/**
 * Universal Copilot - Compliant Multi-LLM Code Assistant
 * Main entry point and public API
 */

export * from './core/errors.js';
export * from './core/governance.js';
export { createGovernance, Judge6Adapter, MockGovernance } from './core/governance.js';
export type { PatchOptions, PatchResult } from './core/patcher.js';
export * from './core/patcher.js';
export { createPatcher, UnifiedPatcher } from './core/patcher.js';
export type { GovernanceEngine } from './core/router.js';
export * from './core/router.js';
// Main classes
export { CopilotRouter } from './core/router.js';
// Re-export commonly used types
export type {
  CopilotRequest,
  CopilotResponse,
  Intent,
  Patch,
  Provider,
  RouterConfig,
  Selection,
} from './core/schema.js';
export * from './core/schema.js';
export * from './providers/index.js';
export { createProvider } from './providers/index.js';
