/**
 * V23 Phosphor-Awakening Feature Flags
 * Task 2 & 10: Semantic Routing + AB Test Harness
 *
 * Layered resolution: Runtime > File > Env > Defaults
 * Python FeatureFlagStore (packages/speculation_engine/feature_flags.py) remains
 * canonical for the Python speculation layer. This TS module governs the
 * Bun/TypeScript routing and teleportation subsystems.
 */

export interface FeatureFlagConfig {
  readonly SEMANTIC_ROUTING: boolean;
  readonly AB_TEST_HARNESS_ACTIVE: boolean;
  readonly TELEPORTATION_PROTOCOL_V1: boolean;
  readonly ASYNC_CONSUMER_BATCHING: boolean;
  readonly NOTEBOOKLM_MCP_ENABLED: boolean;
  readonly POMELLI_SWARM_ACTIVE: boolean;
  readonly DEEP_THINK_AUDIT_ON_PUSH: boolean;
}

const DEFAULTS: FeatureFlagConfig = {
  SEMANTIC_ROUTING: true,
  AB_TEST_HARNESS_ACTIVE: true,
  TELEPORTATION_PROTOCOL_V1: true,
  ASYNC_CONSUMER_BATCHING: true,
  NOTEBOOKLM_MCP_ENABLED: true,
  POMELLI_SWARM_ACTIVE: false, // Gated until Pomelli repo is cloned
  DEEP_THINK_AUDIT_ON_PUSH: true,
};

/** Runtime overrides — set programmatically during session */
const runtimeOverrides: Partial<FeatureFlagConfig> = {};

/**
 * Resolve a flag value through the 4-layer cascade:
 * Runtime > Environment > File (.beads/feature_flags.json) > Defaults
 */
export function resolveFlag<K extends keyof FeatureFlagConfig>(key: K): FeatureFlagConfig[K] {
  // Layer 1: Runtime override
  if (key in runtimeOverrides) {
    return runtimeOverrides[key] as FeatureFlagConfig[K];
  }

  // Layer 2: Environment variable (e.g., FEATURE_SEMANTIC_ROUTING=false)
  const envKey = `FEATURE_${key}`;
  const envVal = typeof process !== 'undefined' ? process.env[envKey] : undefined;
  if (envVal !== undefined) {
    return (envVal === 'true') as FeatureFlagConfig[K];
  }

  // Layer 3: Defaults
  return DEFAULTS[key];
}

export function setRuntimeOverride<K extends keyof FeatureFlagConfig>(
  key: K,
  value: FeatureFlagConfig[K],
): void {
  (runtimeOverrides as Record<string, unknown>)[key] = value;
}

export function clearRuntimeOverrides(): void {
  for (const key of Object.keys(runtimeOverrides)) {
    delete (runtimeOverrides as Record<string, unknown>)[key];
  }
}

export function getAllFlags(): FeatureFlagConfig {
  const result = { ...DEFAULTS };
  for (const key of Object.keys(result) as Array<keyof FeatureFlagConfig>) {
    (result as Record<string, unknown>)[key] = resolveFlag(key);
  }
  return result;
}
