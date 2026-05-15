/**
 * V25 Jules Ascension — Orchestration Module Barrel Export
 *
 * Central export for all V25 orchestration modules.
 * The Antigravity orchestrator imports from this single entry point.
 *
 * @module orchestration
 * Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
 */

// Fleet Orchestrator — Cloud Run fleet management via Jules SDK
export {
  JulesFleetOrchestrator,
  type JulesConfig,
  type GitHubSource,
  type FleetService,
  type ServiceStatus,
  type DeploymentPlan,
  type FleetDeployTarget,
  type JulesSessionConfig,
  type FleetHealthReport,
  type SessionActivity,
  type SessionArtifact,
  type DeploymentResult,
} from './jules_fleet_orchestrator.js';

// Dart Edge Bridge — Task management integration
export {
  DartEdgeBridge,
  type DartTask,
  type DartTaskStatus,
  type DartPriority,
  type DartDoc,
  type DartComment,
  type DartMcpPlan,
  type DartOperation,
} from './dart_edge_bridge.js';

// Claude Sourcemap Bridge — Production error deobfuscation
export {
  ClaudeSourcemapBridge,
  type SourcemapEntry,
  type StackTraceFrame,
  type DeobfuscatedTrace,
  type DeobfuscatedFrame,
  type ErrorCorrelation,
} from './claude_sourcemap_bridge.js';

// NotebookLM Epistemic Hook — RAG memory corpus
export {
  NotebookLMEpistemicHook,
  type MemoryEntry,
  type MemoryType,
  type MemoryCorpus,
  type ExpirationPolicy,
  type NotebookLMIngestPlan,
} from './notebooklm_hook.js';
