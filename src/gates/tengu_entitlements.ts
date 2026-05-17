// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Tengu Entitlement Gates — Subscription and feature access control.
 *
 * Entitlement gates use `checkGate_CACHED_OR_BLOCKING` which returns
 * cached `true` immediately (fast path) but blocks up to ~5s on a
 * cached `false` to fetch fresh server values. This prevents users
 * from being unfairly blocked by stale cache.
 *
 * Each entitlement function provides a structured reason when denied,
 * suitable for user-facing error messages.
 */

import { checkGate_CACHED_OR_BLOCKING } from "../services/analytics/growthbook.js";
import { logForDebugging } from "../utils/debug.js";
import { TENGU_GATES } from "./tengu_registry.js";

// ─── Entitlement Result ────────────────────────────────────────────

export interface EntitlementResult {
  /** Whether the entitlement is granted. */
  readonly entitled: boolean;
  /** The gate key that was evaluated. */
  readonly gate: string;
  /** User-facing reason for denial (null if entitled). */
  readonly reason: string | null;
}

// ─── Bridge Mode (Remote Control) ──────────────────────────────────

/**
 * Check if the user has the Remote Control (bridge) entitlement.
 *
 * This delegates to `checkGate_CACHED_OR_BLOCKING('tengu_ccr_bridge')`
 * which returns cached `true` fast, or blocks ~5s to fetch fresh value
 * when cache says `false`.
 *
 * Bridge mode additionally requires:
 * 1. A claude.ai subscription (checked by bridgeEnabled.ts)
 * 2. An OAuth token with user:profile scope
 * 3. A populated oauthAccount.organizationUuid
 *
 * This function checks ONLY the GrowthBook gate. Use
 * `bridgeEnabled.getBridgeDisabledReason()` for the full diagnostic.
 */
export async function checkBridgeEntitlement(): Promise<EntitlementResult> {
  const value = await checkGate_CACHED_OR_BLOCKING(TENGU_GATES.ccr_bridge.key);
  return {
    entitled: value,
    gate: TENGU_GATES.ccr_bridge.key,
    reason: value ? null : "Remote Control is not yet enabled for your account.",
  };
}

// ─── Harbor (Channel Server) ───────────────────────────────────────

/**
 * Check if the user has channel server access.
 *
 * Harbor gates control enrollment in pub/sub channels for
 * multi-session coordination and remote monitoring.
 */
export async function checkHarborEntitlement(): Promise<EntitlementResult> {
  const value = await checkGate_CACHED_OR_BLOCKING(TENGU_GATES.harbor.key);
  return {
    entitled: value,
    gate: TENGU_GATES.harbor.key,
    reason: value ? null : "Channel server access is not enabled for your account.",
  };
}

// ─── Voice Mode ────────────────────────────────────────────────────

/**
 * Check if the user has voice mode (push-to-talk) entitlement.
 */
export async function checkVoiceEntitlement(): Promise<EntitlementResult> {
  const value = await checkGate_CACHED_OR_BLOCKING(TENGU_GATES.voice_enabled.key);
  return {
    entitled: value,
    gate: TENGU_GATES.voice_enabled.key,
    reason: value ? null : "Voice mode is not yet enabled for your account.",
  };
}

// ─── Batch Entitlement Check ───────────────────────────────────────

/**
 * Check all entitlements at once. Returns a map of gate key → EntitlementResult.
 *
 * Useful for rendering a feature availability summary in the UI.
 */
export async function checkAllEntitlements(): Promise<Map<string, EntitlementResult>> {
  const results = new Map<string, EntitlementResult>();

  const [bridge, harbor, voice] = await Promise.all([
    checkBridgeEntitlement(),
    checkHarborEntitlement(),
    checkVoiceEntitlement(),
  ]);

  results.set(bridge.gate, bridge);
  results.set(harbor.gate, harbor);
  results.set(voice.gate, voice);

  logForDebugging(
    `[tengu-entitlements] ${results.size} checked: ${[...results.values()].filter((r) => r.entitled).length} granted`,
  );

  return results;
}
