// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Tengu Gate Evaluator — Unified evaluation engine.
 *
 * Routes gate checks to the correct GrowthBook helper based on the gate's
 * category from the registry. This ensures:
 * - SECURITY gates always wait for fresh values (checkSecurityRestrictionGate)
 * - ENTITLEMENT gates use fast-path cache with blocking fallback
 * - FEATURE/TELEMETRY gates return immediately from cache (non-blocking)
 * - INTERNAL gates enforce ant-only access
 *
 * All evaluations are audit-logged when USER_TYPE=ant for diagnostics.
 */

import {
  checkGate_CACHED_OR_BLOCKING,
  checkSecurityRestrictionGate,
  getFeatureValue_CACHED_MAY_BE_STALE,
} from "../services/analytics/growthbook.js";
import { logForDebugging } from "../utils/debug.js";
import {
  GateCategory,
  getGateDefinition,
  TENGU_GATES,
  type TenguGateDefinition,
  type TenguGateName,
} from "./tengu_registry.js";

// ─── Evaluation Result ─────────────────────────────────────────────

export interface GateEvalResult<T = unknown> {
  /** The gate key evaluated. */
  readonly gate: string;
  /** The resolved value. */
  readonly value: T;
  /** Whether the value came from cache vs blocking fetch. */
  readonly source: "cache" | "blocking" | "default" | "override";
  /** Timestamp of evaluation. */
  readonly evaluatedAt: number;
  /** Category of the gate. */
  readonly category: GateCategory;
}

// ─── Audit Log ─────────────────────────────────────────────────────

const isAnt = process.env.USER_TYPE === "ant";
const evaluationLog: GateEvalResult[] = [];
const MAX_EVAL_LOG = 1000;

function recordEval(result: GateEvalResult): void {
  if (!isAnt) return;
  if (evaluationLog.length >= MAX_EVAL_LOG) {
    evaluationLog.shift();
  }
  evaluationLog.push(result);
  logForDebugging(
    `[tengu] ${result.gate} → ${JSON.stringify(result.value)} (${result.source}, ${result.category})`,
  );
}

/** Get the last N evaluations (diagnostics only). */
export function getRecentEvaluations(count = 50): readonly GateEvalResult[] {
  return evaluationLog.slice(-count);
}

// ─── Evaluator Core ────────────────────────────────────────────────

/**
 * Evaluate a boolean gate (non-blocking, cached).
 *
 * For SECURITY gates, prefer `evaluateSecurityGate()` which awaits fresh values.
 * For ENTITLEMENT gates, prefer `evaluateEntitlementGate()` which blocks on
 * false cache.
 *
 * This function is the fast-path for FEATURE/TELEMETRY/INTERNAL gates.
 */
export function evaluateGate(name: TenguGateName): boolean {
  const def = getGateDefinition(name);
  enforceAntOnly(def);

  const value = getFeatureValue_CACHED_MAY_BE_STALE(def.key, def.defaultValue as boolean);
  const result: GateEvalResult<boolean> = {
    gate: def.key,
    value,
    source: "cache",
    evaluatedAt: Date.now(),
    category: def.category,
  };
  recordEval(result);
  return value;
}

/**
 * Evaluate a typed feature value (non-blocking, cached).
 *
 * Use for gates that return non-boolean values (e.g., config objects,
 * strings, numbers).
 */
export function evaluateFeatureValue<T>(name: TenguGateName): T {
  const def = getGateDefinition(name);
  enforceAntOnly(def);

  const value = getFeatureValue_CACHED_MAY_BE_STALE(def.key, def.defaultValue as T);
  const result: GateEvalResult<T> = {
    gate: def.key,
    value,
    source: "cache",
    evaluatedAt: Date.now(),
    category: def.category,
  };
  recordEval(result);
  return value;
}

/**
 * Evaluate a security gate (blocking, waits for re-init).
 *
 * MUST be used for all SECURITY-category gates. Returns false if
 * GrowthBook is unavailable (fail-closed for security, fail-open for
 * availability per FIPS-199 LOW availability impact).
 */
export async function evaluateSecurityGate(name: TenguGateName): Promise<boolean> {
  const def = getGateDefinition(name);
  enforceAntOnly(def);

  if (def.category !== GateCategory.SECURITY) {
    logForDebugging(
      `[tengu] WARNING: evaluateSecurityGate called on non-SECURITY gate: ${def.key}`,
    );
  }

  const value = await checkSecurityRestrictionGate(def.key);
  const result: GateEvalResult<boolean> = {
    gate: def.key,
    value,
    source: "blocking",
    evaluatedAt: Date.now(),
    category: def.category,
  };
  recordEval(result);
  return value;
}

/**
 * Evaluate an entitlement gate (fast-path cache, blocking on false).
 *
 * MUST be used for all ENTITLEMENT-category gates. Returns cached true
 * immediately. If cache says false or is missing, blocks up to ~5s to
 * fetch fresh value from GrowthBook server.
 */
export async function evaluateEntitlementGate(name: TenguGateName): Promise<boolean> {
  const def = getGateDefinition(name);
  enforceAntOnly(def);

  if (def.category !== GateCategory.ENTITLEMENT) {
    logForDebugging(
      `[tengu] WARNING: evaluateEntitlementGate called on non-ENTITLEMENT gate: ${def.key}`,
    );
  }

  const value = await checkGate_CACHED_OR_BLOCKING(def.key);
  const result: GateEvalResult<boolean> = {
    gate: def.key,
    value,
    source: value ? "cache" : "blocking",
    evaluatedAt: Date.now(),
    category: def.category,
  };
  recordEval(result);
  return value;
}

// ─── Batch Evaluation ──────────────────────────────────────────────

/**
 * Evaluate all gates in a category. Returns a map of gate key → value.
 *
 * For SECURITY/ENTITLEMENT gates, this awaits all results.
 * For FEATURE/TELEMETRY/INTERNAL gates, this is non-blocking.
 */
export async function evaluateCategory(category: GateCategory): Promise<Map<string, unknown>> {
  const results = new Map<string, unknown>();

  for (const [name, def] of Object.entries(TENGU_GATES)) {
    if (def.category !== category) continue;
    const gateName = name as TenguGateName;

    switch (category) {
      case GateCategory.SECURITY:
        results.set(def.key, await evaluateSecurityGate(gateName));
        break;
      case GateCategory.ENTITLEMENT:
        results.set(def.key, await evaluateEntitlementGate(gateName));
        break;
      default:
        results.set(def.key, evaluateGate(gateName));
    }
  }

  return results;
}

/**
 * Snapshot of all gates — for diagnostics and compliance reporting.
 *
 * Returns a serializable object with all gate values grouped by category.
 */
export async function snapshotAllGates(): Promise<Record<string, Record<string, unknown>>> {
  const snapshot: Record<string, Record<string, unknown>> = {};

  for (const category of Object.values(GateCategory)) {
    if (typeof category !== "string") continue;
    const categoryGates = await evaluateCategory(category as GateCategory);
    const obj: Record<string, unknown> = {};
    for (const [k, v] of categoryGates) {
      obj[k] = v;
    }
    snapshot[category] = obj;
  }

  return snapshot;
}

// ─── Internal Helpers ──────────────────────────────────────────────

function enforceAntOnly(def: TenguGateDefinition): void {
  if (def.antOnly && !isAnt) {
    logForDebugging(`[tengu] Gate ${def.key} is ant-only but USER_TYPE=${process.env.USER_TYPE}`);
  }
}
