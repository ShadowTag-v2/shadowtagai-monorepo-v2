/**
 * @shadowtag/jules-apex — Jules V25 Ascendancy Bridge
 *
 * Wraps the @google/jules-sdk to provide ShadowTag-specific orchestration
 * primitives: session creation, artifact extraction, and Cloud Run deployment
 * mapping via Judge 6 verdicts.
 *
 * Copyright 2026 ShadowTag AI. Apache-2.0.
 */

export type { ApexClientOptions, ApexSession } from './client.js';

// ShadowTag orchestration layer
export { createApexClient, JulesApexClient } from './client.js';
export type {
  DeploymentConfig,
  DeploymentResult,
  Judge6Verdict,
} from './orchestrator.js';

// Cloud Run orchestrator
export { JulesCloudRunOrchestrator } from './orchestrator.js';
// Re-export core Jules SDK types for consumers
export type {
  Activity,
  ActivitySummary,
  Artifact,
  ChangeSet,
  Plan,
  PlanStep,
  PullRequest,
  SessionConfig,
  SessionOutput,
  SessionState,
} from './types.js';
