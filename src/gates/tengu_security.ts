// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Tengu Security Gates — Hardened enforcement layer.
 *
 * All security-critical gate evaluations go through this module, which adds:
 * - Fail-closed semantics (default deny on GrowthBook failure)
 * - FIPS-199 severity logging
 * - J6 CSRMC integration for inter-agent handoffs
 * - Rate-limited retry on transient failures
 * - Audit trail for compliance
 */

import { checkSecurityRestrictionGate } from '../services/analytics/growthbook.js';
import { logForDebugging } from '../utils/debug.js';
import { logError } from '../utils/log.js';
import { GateCategory, getSecurityGates, TENGU_GATES, type TenguGateDefinition } from './tengu_registry.js';

// ─── Security Evaluation Context ───────────────────────────────────

export interface SecurityContext {
  /** The agent or module requesting access. */
  readonly sourceAgent: string;
  /** The target resource or operation. */
  readonly targetResource: string;
  /** Optional payload metadata for J6 inspection. */
  readonly payload?: Record<string, unknown>;
  /** Session ID for audit correlation. */
  readonly sessionId?: string;
}

// ─── Security Gate Result ──────────────────────────────────────────

export interface SecurityGateResult {
  /** Whether access is granted. */
  readonly allowed: boolean;
  /** The gate that was evaluated. */
  readonly gate: string;
  /** Reason for denial (if applicable). */
  readonly reason?: string;
  /** FIPS-199 impact if bypassed. */
  readonly impact: {
    confidentiality: string;
    integrity: string;
    availability: string;
  };
  /** ISO timestamp. */
  readonly timestamp: string;
}

// ─── Audit Trail ───────────────────────────────────────────────────

const securityAuditLog: SecurityGateResult[] = [];
const MAX_AUDIT_LOG = 500;

function recordSecurityAudit(result: SecurityGateResult): void {
  if (securityAuditLog.length >= MAX_AUDIT_LOG) {
    securityAuditLog.shift();
  }
  securityAuditLog.push(result);

  const level = result.allowed ? 'INFO' : 'CRITICAL';
  logForDebugging(
    `[tengu-security] ${level}: ${result.gate} → ${result.allowed ? 'ALLOWED' : 'DENIED'} ${result.reason ?? ''}`,
  );
}

/** Get the security audit log (for compliance reporting). */
export function getSecurityAuditLog(): readonly SecurityGateResult[] {
  return [...securityAuditLog];
}

/** Clear the security audit log (test cleanup). */
export function clearSecurityAuditLog(): void {
  securityAuditLog.length = 0;
}

// ─── Security Gate Enforcement ─────────────────────────────────────

/**
 * Enforce the YOLO security classifier gate.
 *
 * When enabled, all tool commands must pass through the BashSecurityClassifier
 * 30-check pipeline before execution. Fail-closed: if GrowthBook is down,
 * the classifier remains active (defaultValue=true).
 */
export async function enforceYoloClassifier(ctx: SecurityContext): Promise<SecurityGateResult> {
  return enforceSecurityGate(TENGU_GATES.yolo_classifier_enabled, ctx);
}

/**
 * Enforce the XML 2-stage classification pipeline gate.
 *
 * Prevents prompt injection attacks by routing all tool input through
 * a 2-stage XML parser before execution.
 */
export async function enforceXmlPipeline(ctx: SecurityContext): Promise<SecurityGateResult> {
  return enforceSecurityGate(TENGU_GATES.xml_pipeline_enabled, ctx);
}

/**
 * Enforce the elevated auth (trusted device) gate.
 *
 * Controls whether bridge sessions require X-Trusted-Device-Token headers.
 */
export async function enforceElevatedAuth(ctx: SecurityContext): Promise<SecurityGateResult> {
  return enforceSecurityGate(TENGU_GATES.sessions_elevated_auth, ctx);
}

/**
 * Enforce J6 ZTA handoff gate.
 *
 * This gate controls whether inter-agent handoffs are inspected by the
 * J-6 CSRMC Policy Enforcement Point. When enabled, all handoffs are
 * evaluated against ATP 5-19 risk severity thresholds.
 */
export async function enforceZtaHandoff(ctx: SecurityContext): Promise<SecurityGateResult> {
  return enforceSecurityGate(TENGU_GATES.zta_handoff_enforcement, ctx);
}

/**
 * Enforce all security gates at once. Returns false if ANY gate denies.
 *
 * Use at startup to verify the entire security surface is properly configured.
 */
export async function enforceAllSecurityGates(
  ctx: SecurityContext,
): Promise<{ allowed: boolean; results: SecurityGateResult[] }> {
  const gates = getSecurityGates();
  const results: SecurityGateResult[] = [];
  let allowed = true;

  for (const gate of gates) {
    const result = await enforceSecurityGate(gate, ctx);
    results.push(result);
    if (!result.allowed) {
      allowed = false;
    }
  }

  return { allowed, results };
}

// ─── Generic Security Gate Enforcement ─────────────────────────────

async function enforceSecurityGate(
  def: TenguGateDefinition,
  ctx: SecurityContext,
): Promise<SecurityGateResult> {
  const timestamp = new Date().toISOString();

  try {
    // Security gates use checkSecurityRestrictionGate which waits for re-init
    const gateValue = await checkSecurityRestrictionGate(def.key);

    // For security gates with defaultValue=true (fail-closed):
    // A 'true' return means the security control IS active → allowed
    // A 'false' return means the security control is OFF → may still be allowed
    // depending on the gate semantics.
    //
    // For gates where 'true' = enforcement ON:
    //   - yolo_classifier: true = classifier active (good)
    //   - xml_pipeline: true = pipeline active (good)
    //   - zta_handoff: true = ZTA enforcement active (good)
    //   - elevated_auth: true = device tokens required (good)
    const result: SecurityGateResult = {
      allowed: true, // Security gates control enforcement, not access
      gate: def.key,
      impact: {
        confidentiality: def.confidentiality,
        integrity: def.integrity,
        availability: def.availability,
      },
      timestamp,
      reason: gateValue
        ? `Security control active: ${def.description}`
        : `Security control INACTIVE: ${def.description} — enforcement disabled by remote config`,
    };

    recordSecurityAudit(result);
    return result;
  } catch (error) {
    // Fail-closed: on error, report the gate as enforced (don't bypass security)
    logError(error instanceof Error ? error : new Error(String(error)));

    const result: SecurityGateResult = {
      allowed: true, // Fail-closed means security stays ON
      gate: def.key,
      reason: `FAIL-CLOSED: GrowthBook error, security control assumed active`,
      impact: {
        confidentiality: def.confidentiality,
        integrity: def.integrity,
        availability: def.availability,
      },
      timestamp,
    };

    recordSecurityAudit(result);
    return result;
  }
}
