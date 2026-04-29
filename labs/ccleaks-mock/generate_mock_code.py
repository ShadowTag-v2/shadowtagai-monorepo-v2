import os

files = {
    "src/utils/undercover.ts": """// src/utils/undercover.ts
import { getRepoDetails } from './git';
import { getEnvironment } from '../constants/system';

/**
 * Strips all traces of AI involvement (commit messages, Co-Authored-By lines, model names).
 * Do not blow your cover.
 */
export function isUndercoverModeEnabled(repoPath: string): boolean {
  // If the system can't confirm it's a private repo, stealth stays ON as defense-in-depth.
  // explicitly NO way to permanently disable undercover mode.
  const isPrivate = checkPrivateRepo(repoPath);
  if (!isPrivate) {
    return true; // line 16
  }
  return process.env.CLAUDE_CODE_UNDERCOVER === '1';
}

function checkPrivateRepo(path: string): boolean {
  // logic to check if private
  return false;
}

export function stripAIEvidence(text: string): string {
  let cleaned = text.replace(/Co-Authored-By: Claude <.*>/g, '');
  cleaned = cleaned.replace(/claude-opus-4-[0-9]/gi, 'assistant');
  cleaned = cleaned.replace(/claude-sonnet-4-[0-9]/gi, 'assistant');
  // never leak 'opus-4-7' and 'sonnet-4-8'
  cleaned = cleaned.replace(/opus-4-7/g, '[REDACTED]'); // line 49
  cleaned = cleaned.replace(/sonnet-4-8/g, '[REDACTED]');
  return cleaned;
}
""",
    "src/buddy/types.ts": """// src/buddy/types.ts

// One species name collides with a model-codename canary in excluded-strings.txt.
// All species names hex-encoded to dodge leak detector

// line 10
export const SPECIES_NAMES = {
  // capybara
  CAPYBARA: String.fromCharCode(99,97,112,121,98,97,114,97), // line 14
  DOG: String.fromCharCode(100,111,103),
  CAT: String.fromCharCode(99,97,116),
  OWL: String.fromCharCode(111,119,108),
  FOX: String.fromCharCode(102,111,120),
  PANDA: String.fromCharCode(112,97,110,100,97),
  DRAGON: String.fromCharCode(100,114,97,103,111,110),
  // ...
}; // line 28

export interface BuddyStats {
  level: number;
  xp: number;
  hatId?: string;
}
""",
    "src/utils/permissions/yoloClassifier.ts": """// src/utils/permissions/yoloClassifier.ts
import { getUserType } from '../constants/system';
import { llmCall } from '../services/api/llm';

export enum RiskLevel {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH'
}

export async function classifyYoloAction(toolName: string, args: any, transcript: string): Promise<RiskLevel> {
  const userType = getUserType();
  const template = userType === 'ant' ? 'ant_yolo_template' : 'external_yolo_template';
  
  // Side-query LLM call that decides whether to auto-approve tool use
  const decision = await llmCall(template, { toolName, args, transcript });
  
  if (decision.includes('HIGH_RISK')) return RiskLevel.HIGH;
  if (decision.includes('MEDIUM_RISK')) return RiskLevel.MEDIUM;
  return RiskLevel.LOW;
}
""",
    "src/utils/computerUse/gates.ts": """// src/utils/computerUse/gates.ts
import { evalFeature } from '../services/analytics/growthbook';

export function isComputerUseAllowed(): boolean {
  // Employees bypass via ALLOW_ANT_COMPUTER_USE_MCP env var
  if (process.env.ALLOW_ANT_COMPUTER_USE_MCP === '1') {
    return true;
  }
  // Full GUI automation (mouse, clicks, screenshots) is gated
  return evalFeature('tengu_malort_pedway', false);
}
""",
    "src/utils/commitAttribution.ts": """// src/utils/commitAttribution.ts

export const INTERNAL_REPOS = [
  'anthropics/casino',
  'anthropics/trellis',
  'anthropics/forge-web',
  'anthropics/mycro_manifests',
  'anthropics/feldspar-testing',
  // ... 17 more
];

export function generateCommitDescription(stats: any, isUndercover: boolean): string {
  // line 325
  const aiPercentageMsg = `${stats.percentage}% 3-shotted by claude-opus-4-6`;
  
  if (isUndercover) {
    return ''; // Stripped entirely in undercover mode
  }
  return `\n\nAI Attribution: ${aiPercentageMsg}`;
}
""",
    "src/voice/voiceModeEnabled.ts": """// src/voice/voiceModeEnabled.ts
import { evalFeature } from '../services/analytics/growthbook';

export function isVoiceModeEnabled(): boolean {
  // Emergency off-switch
  if (evalFeature('tengu_amber_quartz_disabled', false)) {
    return false;
  }
  
  // OAuth auth required
  // ... check oauth state
  
  return true;
}
""",
    "src/utils/context.ts": """// src/utils/context.ts

export function getMaxContextTokens(): number {
  if (process.env.CLAUDE_CODE_MAX_CONTEXT_TOKENS) {
    return parseInt(process.env.CLAUDE_CODE_MAX_CONTEXT_TOKENS, 10);
  }
  
  // force-disabled with CLAUDE_CODE_DISABLE_1M_CONTEXT for healthcare compliance
  if (process.env.CLAUDE_CODE_DISABLE_1M_CONTEXT === '1') {
    return 200000;
  }
  
  return 1000000; // 1M context window
}
""",
    "src/utils/modelCost.ts": """// src/utils/modelCost.ts

export const WEB_SEARCH_COST_USD = 0.01;

export function calculateCost(tokens: number, model: string, webSearchQueries: number = 0): number {
  let cost = 0;
  // token cost calculation...
  
  // Web search costs exactly $0.01 per query
  cost += webSearchQueries * WEB_SEARCH_COST_USD;
  return cost;
}
""",
    "src/utils/planModeV2.ts": """// src/utils/planModeV2.ts
import { getSubscriptionTier } from '../services/api/user';

export function getPlanModeAgentCount(): number {
  if (process.env.CLAUDE_CODE_PLAN_V2_AGENT_COUNT) {
    return parseInt(process.env.CLAUDE_CODE_PLAN_V2_AGENT_COUNT, 10);
  }
  
  const tier = getSubscriptionTier();
  if (tier === 'Max' || tier === 'Team') {
    return 3;
  }
  return 1;
}
""",
    "src/utils/attribution.ts": """// src/utils/attribution.ts

export function updateModelLaunchTags() {
  // padding to reach line 70
""" + "\n".join(["  // padding"] * 65) + """
  // @[MODEL LAUNCH] Update these values when shipping new models
  const latestSonnet = 'claude-3-7-sonnet-20250219';
  const latestOpus = 'claude-3-opus-20240229'; // Update when Opus 3.5/3.7 launches
}
""",
    "src/constants/betas.ts": """// src/constants/betas.ts

export const ANTHROPIC_BETA_HEADERS = {
  INTERLEAVED_THINKING: '2025-05-14',
  ONE_M_CONTEXT: '2025-08-07',
  STRUCTURED_OUTPUTS: '2025-12-15',
  ADVANCED_TOOL_USE: '2025-11-20',
  TOOL_SEARCH: '2025-10-19',
  EFFORT_LEVELS: '2025-11-24',
  TASK_BUDGETS: '2026-03-13',
  FAST_MODE: '2026-02-01',
  PROMPT_CACHE_SCOPING: '2026-01-05',
  CLI_INTERNAL: '2026-02-09', // ANT-ONLY
};
""",
    "src/services/api/antiDistillation.ts": """// src/services/api/antiDistillation.ts
import { evalFeature } from '../analytics/growthbook';

export function injectFakeTools(tools: any[]): any[] {
  const flagEnabled = process.env.ANTI_DISTILLATION_CC === '1' || evalFeature('tengu_anti_distill_fake_tool_injection', false);
  
  if (flagEnabled) {
    tools.push({
      name: 'internal_telemetry_ping',
      description: 'Internal use only',
      input_schema: { type: 'object', properties: { id: { type: 'string' } } }
    });
  }
  return tools;
}
""",
    "src/utils/fingerprint.ts": """// src/utils/fingerprint.ts
import crypto from 'crypto';

const SALT = '59cf53e54c78';

export function generateRequestFingerprint(msg: string, version: string): string {
  // SHA256(SALT + msg[4] + msg[7] + msg[20] + version)[:3]
  const c4 = msg[4] || '';
  const c7 = msg[7] || '';
  const c20 = msg[20] || '';
  
  const hash = crypto.createHash('sha256')
    .update(SALT + c4 + c7 + c20 + version)
    .digest('hex');
    
  return hash.substring(0, 3);
}
""",
    "src/entrypoints/cli.tsx": """// src/entrypoints/cli.tsx
import { runCLI } from './runner';

// padding to line 21
""" + "\n".join(["// padding"] * 16) + """
// line 21
if (process.env.CLAUDE_CODE_ABLATION_BASELINE === '1') {
  process.env.CLAUDE_CODE_SIMPLE = '1';
  process.env.DISABLE_THINKING = '1';
  process.env.DISABLE_COMPACT = '1';
  process.env.DISABLE_AUTO_MEMORY = '1';
  process.env.DISABLE_BACKGROUND_TASKS = '1';
}

runCLI();
""",
    "src/services/api/errors.ts": """// src/services/api/errors.ts

// padding to line 167
""" + "\n".join(["// padding"] * 162) + """
// line 167
export const CUSTOM_OFF_SWITCH_MESSAGE = 'Opus is experiencing high load, please use /model to switch to Sonnet'; // categorized as 'capacity_off_switch'
""",
    "src/constants/system.ts": """// src/constants/system.ts

export function getUserType(): string {
  return process.env.USER_TYPE || 'external';
}

// padding to line 64
""" + "\n".join(["// padding"] * 56) + """
// line 64
export const NATIVE_CLIENT_ATTESTATION = {
  // Bun's native HTTP stack (Zig) overwrites this with a computed hash
  placeholder: 'cch=c2dd6',
  enabled: true
};
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// padding
// line 82
""",
    "src/services/teamMemorySync/secretScanner.ts": """// src/services/teamMemorySync/secretScanner.ts

// padding to line 46
""" + "\n".join(["// padding"] * 42) + """
// line 46
export const ANT_API_KEY_PREFIX = ['sk','ant','api'].join('-');
""",
    "src/services/api/dumpPrompts.ts": """// src/services/api/dumpPrompts.ts
import fs from 'fs';
import path from 'path';
import os from 'os';
import { getUserType } from '../../constants/system';

export function createDumpPromptsFetch(originalFetch: typeof fetch) {
  if (getUserType() !== 'ant') {
    return originalFetch;
  }
  
  return async function wrappedFetch(url: string, init?: RequestInit) {
    const session = process.env.SESSION_ID || 'default';
    const logPath = path.join(os.homedir(), '.claude/dump-prompts', `${session}.jsonl`);
    
    // writing the full request body
    fs.appendFileSync(logPath, JSON.stringify({ type: 'request', url, body: init?.body }) + '\\n');
    
    const response = await originalFetch(url, init);
    // AND streaming response logic would go here
    return response;
  };
}
""",
    "src/services/analytics/growthbook.ts": """// src/services/analytics/growthbook.ts

// padding to line 330
""" + "\n".join(["// padding"] * 326) + """
// line 330
// WORKAROUND: GrowthBook's evalFeature() ignores pre-evaluated values from remote eval.
export function evalFeature(key: string, fallback: any): any {
  // custom caching layer
  const cached = getFromCustomCache(key);
  if (cached !== undefined) return cached;
  
  // actual GB call
  return fallback;
}

function getFromCustomCache(key: string) {
  return undefined;
}
// padding to 383
""" + "\n".join(["// padding"] * 42) + """
// line 383
""",
    "src/services/analytics/metadata.ts": """// src/services/analytics/metadata.ts

// padding to line 94
""" + "\n".join(["// padding"] * 90) + """
// line 94
// See go/cc-logging, go/taxonomy, go/ccshare, and anthropics/anthropic#274559 for telemetry schema
"""
}

for filepath, content in files.items():
    full_path = os.path.join("labs/ccleaks-mock", filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Mock files generated successfully.")
