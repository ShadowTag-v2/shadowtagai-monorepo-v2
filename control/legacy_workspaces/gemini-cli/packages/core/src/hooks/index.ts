/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

export type { AggregatedHookResult } from "./hookAggregator.js";
export { HookAggregator } from "./hookAggregator.js";
export { HookEventHandler } from "./hookEventHandler.js";
export type { HookEventContext } from "./hookPlanner.js";
export { HookPlanner } from "./hookPlanner.js";
// Export interfaces
export type { ConfigSource, HookRegistryEntry } from "./hookRegistry.js";
export { HookRegistry } from "./hookRegistry.js";
export { HookRunner } from "./hookRunner.js";
// Export core components
export { HookSystem } from "./hookSystem.js";
// Export types
export * from "./types.js";
