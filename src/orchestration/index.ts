/**
 * V25 Jules Ascension — Orchestration Module Barrel Export
 *
 * Central export for all V25 orchestration modules.
 * The Antigravity orchestrator imports from this single entry point.
 *
 * @module orchestration
 * Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
 */

// Claude Sourcemap Bridge — Production error deobfuscation
export {
  ClaudeSourcemapBridge,
  type DeobfuscatedFrame,
  type DeobfuscatedTrace,
  type ErrorCorrelation,
  type SourcemapEntry,
  type StackTraceFrame,
} from "./claude_sourcemap_bridge.js";

// Dart Edge Bridge — Task management integration
export {
  type DartComment,
  type DartDoc,
  DartEdgeBridge,
  type DartMcpPlan,
  type DartOperation,
  type DartPriority,
  type DartTask,
  type DartTaskStatus,
} from "./dart_edge_bridge.js";
// Fleet Orchestrator — Cloud Run fleet management via Jules SDK
export {
  type DeploymentPlan,
  type DeploymentResult,
  type FleetDeployTarget,
  type FleetHealthReport,
  type FleetService,
  type GitHubSource,
  type JulesConfig,
  JulesFleetOrchestrator,
  type JulesSessionConfig,
  type ServiceStatus,
  type SessionActivity,
  type SessionArtifact,
} from "./jules_fleet_orchestrator.js";

// NotebookLM Epistemic Hook — RAG memory corpus
export {
  type ExpirationPolicy,
  type MemoryCorpus,
  type MemoryEntry,
  type MemoryType,
  NotebookLMEpistemicHook,
  type NotebookLMIngestPlan,
} from "./notebooklm_hook.js";
