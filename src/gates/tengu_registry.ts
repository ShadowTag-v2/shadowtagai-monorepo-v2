// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Tengu Gate Registry — Single Source of Truth
 *
 * Every gate in the system MUST be registered here. Unregistered gates
 * will throw at evaluation time (fail-closed).
 *
 * Gate naming convention: `tengu_{domain}_{feature}`
 *   - domain: ccr, sessions, harbor, onyx, cobalt, ant, etc.
 *   - feature: bridge, auth_enforcement, frost, plover, etc.
 *
 * @see https://docs.growthbook.io/lib/js for GrowthBook SDK patterns
 * @see src/services/analytics/growthbook.ts for cache/blocking helpers
 */

// ─── Gate Categories ───────────────────────────────────────────────
export enum GateCategory {
  /** Security-critical gates that MUST block for fresh values. */
  SECURITY = "SECURITY",
  /** Subscription/org-level feature access. */
  ENTITLEMENT = "ENTITLEMENT",
  /** Feature rollout flags (non-critical). */
  FEATURE = "FEATURE",
  /** Analytics/observability configuration. */
  TELEMETRY = "TELEMETRY",
  /** Internal ant-only debug/test gates. */
  INTERNAL = "INTERNAL",
}

// ─── FIPS-199 Impact Levels ────────────────────────────────────────
export enum FIPSImpact {
  LOW = "LOW",
  MODERATE = "MODERATE",
  HIGH = "HIGH",
}

// ─── Gate Definition ───────────────────────────────────────────────
export interface TenguGateDefinition<T = unknown> {
  /** The GrowthBook feature key. */
  readonly key: string;
  /** Human-readable description for diagnostics. */
  readonly description: string;
  /** Gate category determines evaluation strategy. */
  readonly category: GateCategory;
  /** Default value when GrowthBook is unavailable or cache is cold. */
  readonly defaultValue: T;
  /** FIPS-199 confidentiality impact if gate is bypassed. */
  readonly confidentiality: FIPSImpact;
  /** FIPS-199 integrity impact if gate is bypassed. */
  readonly integrity: FIPSImpact;
  /** FIPS-199 availability impact if gate is bypassed. */
  readonly availability: FIPSImpact;
  /** If true, gate requires USER_TYPE=ant. */
  readonly antOnly: boolean;
  /** If true, gate value changes trigger a UI re-render via the refreshed signal. */
  readonly reactive: boolean;
}

// ─── Registry ──────────────────────────────────────────────────────

/**
 * Canonical gate registry. Add new gates here.
 *
 * SECURITY gates: checkSecurityRestrictionGate (waits for re-init)
 * ENTITLEMENT gates: checkGate_CACHED_OR_BLOCKING (fast true, blocking false)
 * FEATURE/TELEMETRY gates: getFeatureValue_CACHED_MAY_BE_STALE (non-blocking)
 * INTERNAL gates: ant-only, same as FEATURE but with antOnly=true
 */
export const TENGU_GATES = {
  // ── Security ─────────────────────────────────────────────────────
  sessions_elevated_auth: {
    key: "tengu_sessions_elevated_auth_enforcement",
    description: "Enforces elevated auth (trusted device tokens) for bridge sessions",
    category: GateCategory.SECURITY,
    defaultValue: false,
    confidentiality: FIPSImpact.HIGH,
    integrity: FIPSImpact.HIGH,
    availability: FIPSImpact.MODERATE,
    antOnly: false,
    reactive: false,
  },

  yolo_classifier_enabled: {
    key: "tengu_yolo_security_classifier",
    description: "Enables the BashSecurityClassifier for tool command validation",
    category: GateCategory.SECURITY,
    defaultValue: true, // Fail-closed: classifier ON by default
    confidentiality: FIPSImpact.HIGH,
    integrity: FIPSImpact.HIGH,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: false,
  },

  xml_pipeline_enabled: {
    key: "tengu_xml_2stage_pipeline",
    description: "Enables 2-stage XML classification pipeline for prompt injection defense",
    category: GateCategory.SECURITY,
    defaultValue: true,
    confidentiality: FIPSImpact.HIGH,
    integrity: FIPSImpact.HIGH,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: false,
  },

  zta_handoff_enforcement: {
    key: "tengu_j6_zta_handoff",
    description: "Zero Trust Architecture enforcement for inter-agent handoffs (J6 CSRMC)",
    category: GateCategory.SECURITY,
    defaultValue: true,
    confidentiality: FIPSImpact.HIGH,
    integrity: FIPSImpact.HIGH,
    availability: FIPSImpact.HIGH,
    antOnly: false,
    reactive: false,
  },

  // ── Entitlements ─────────────────────────────────────────────────
  ccr_bridge: {
    key: "tengu_ccr_bridge",
    description: "Remote Control (bridge mode) entitlement — requires claude.ai subscription",
    category: GateCategory.ENTITLEMENT,
    defaultValue: false,
    confidentiality: FIPSImpact.MODERATE,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },

  harbor: {
    key: "tengu_harbor",
    description: "Channel server access gate — controls pub/sub channel enrollment",
    category: GateCategory.ENTITLEMENT,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },

  voice_enabled: {
    key: "tengu_voice_mode",
    description: "Voice mode (push-to-talk) entitlement gate",
    category: GateCategory.ENTITLEMENT,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },

  // ── Features ─────────────────────────────────────────────────────
  streaming_tool_execution: {
    key: "tengu_streaming_tool_execution2",
    description: "Enables streaming tool execution (concurrent tool output)",
    category: GateCategory.FEATURE,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: false,
  },

  auto_dream: {
    key: "tengu_onyx_plover",
    description: "AutoDream memory consolidation — automatic memory extraction",
    category: GateCategory.FEATURE,
    defaultValue: false as unknown,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },

  cobalt_frost: {
    key: "tengu_cobalt_frost",
    description: "Deepgram Nova 3 STT model gate for voice streaming",
    category: GateCategory.FEATURE,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: false,
  },

  context_compaction: {
    key: "tengu_context_compaction_v2",
    description: "4-layer context compaction pipeline (compact/prune/summarize/trim)",
    category: GateCategory.FEATURE,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.MODERATE,
    antOnly: false,
    reactive: false,
  },

  speculation_engine: {
    key: "tengu_speculation_engine",
    description: "Speculative prompt pre-execution via forked agents",
    category: GateCategory.FEATURE,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: false,
  },

  magic_docs: {
    key: "tengu_magic_docs",
    description: "Auto-maintained markdown via subagents (MagicDocs)",
    category: GateCategory.FEATURE,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: false,
  },

  // ── Telemetry ────────────────────────────────────────────────────
  event_batch_config: {
    key: "tengu_1p_event_batch_config",
    description: "First-party event batch configuration (batch size, flush interval)",
    category: GateCategory.TELEMETRY,
    defaultValue: {} as Record<string, unknown>,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },

  event_sampling: {
    key: "tengu_event_sampling_config",
    description: "Per-event sampling rates for telemetry",
    category: GateCategory.TELEMETRY,
    defaultValue: {} as Record<string, number>,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },

  sink_killswitch: {
    key: "tengu_sink_killswitch",
    description: "Emergency killswitch for analytics sinks",
    category: GateCategory.TELEMETRY,
    defaultValue: false,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.LOW,
    availability: FIPSImpact.MODERATE,
    antOnly: false,
    reactive: true,
  },

  // ── Internal (ant-only) ──────────────────────────────────────────
  ant_model_override: {
    key: "tengu_ant_model_override",
    description: "Internal model override for ant users (testing/dogfood)",
    category: GateCategory.INTERNAL,
    defaultValue: "" as string,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.LOW,
    antOnly: true,
    reactive: false,
  },

  max_version_config: {
    key: "tengu_max_version_config",
    description: "Maximum version enforcement — gates CLI upgrade prompts",
    category: GateCategory.INTERNAL,
    defaultValue: {} as Record<string, unknown>,
    confidentiality: FIPSImpact.LOW,
    integrity: FIPSImpact.MODERATE,
    availability: FIPSImpact.LOW,
    antOnly: false,
    reactive: true,
  },
} as const satisfies Record<string, TenguGateDefinition>;

// ─── Type Helpers ──────────────────────────────────────────────────

/** All registered gate names. */
export type TenguGateName = keyof typeof TENGU_GATES;

/** Lookup a gate definition by name (compile-time checked). */
export function getGateDefinition(name: TenguGateName): TenguGateDefinition {
  return TENGU_GATES[name];
}

/** Get all gates in a specific category. */
export function getGatesByCategory(category: GateCategory): TenguGateDefinition[] {
  return Object.values(TENGU_GATES).filter((g) => g.category === category);
}

/** Get all security gates (convenience). */
export function getSecurityGates(): TenguGateDefinition[] {
  return getGatesByCategory(GateCategory.SECURITY);
}

/** Total gate count for diagnostics. */
export function getGateCount(): number {
  return Object.keys(TENGU_GATES).length;
}
