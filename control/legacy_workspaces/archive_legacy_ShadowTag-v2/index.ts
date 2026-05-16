/**
 * MCP Filesystem-Based Tool Discovery
 *
 * Main entry point - exports all servers and skills
 */

export * as autogen from "./servers/autogen/index.js";
export {
  createAgent,
  createAgentTeam,
  debate,
  decomposeAndExecute,
  orchestrateAgents,
} from "./servers/autogen/index.js";
export * as judge from "./servers/judge/index.js";
export {
  checkCoverage,
  enforceDeploymentGate,
  reviewCode,
  validatePRB,
} from "./servers/judge/index.js";
export * as shadowtag from "./servers/shadowtag/index.js";
export {
  notarize,
  verifyNotarization,
  verifyVideo,
  watermarkVideo,
} from "./servers/shadowtag/index.js";
// Export all MCP servers
export * as vertexAI from "./servers/vertex-ai/index.js";
// Re-export commonly used functions for convenience
export {
  executeBatch,
  executeModel,
  findMostSimilar,
  generateEmbeddings,
} from "./servers/vertex-ai/index.js";
// Export all skills
export * as skills from "./skills/index.js";

// Version info
export const VERSION = "1.0.0";
export const DESCRIPTION = "MCP filesystem-based tool discovery for 98.7% token efficiency";

// Architecture info
export const ARCHITECTURE = {
  pattern: "filesystem-based-tool-discovery",
  inspiration: ["Cloudflare Code Mode", "Anthropic Skills"],
  efficiency: {
    tokenReduction: 0.987, // 98.7%
    traditional: "150K tokens",
    filesystem: "2K tokens",
  },
  features: [
    "Progressive disclosure",
    "Context efficiency",
    "Native control flow",
    "Privacy-preserving",
    "Skills persistence",
  ],
};

console.log(`
═══════════════════════════════════════════════════════════════
  MCP FILESYSTEM-BASED TOOL DISCOVERY v${VERSION}
  Token Efficiency: 98.7% reduction (150K→2K tokens)
═══════════════════════════════════════════════════════════════

Available MCP Servers:
  • vertex-ai     - Gemini model execution & embeddings
  • autogen       - Multi-agent orchestration
  • judge         - Purpose/Reasons/Brakes validation
  • shadowtag     - Digital watermarking & notarization

Available Skills:
  • protect-video           - Watermark + blockchain pipeline
  • enforce-quality-gates   - Complete QA validation
  • code-review-team        - Multi-agent code review

Usage:
  import { executeModel } from './servers/vertex-ai/index.js';
  import { protectVideo } from './skills/protect-video.js';

Documentation:
  README.md          - Complete guide
  examples/          - Usage examples
  skills/README.md   - Skills documentation

═══════════════════════════════════════════════════════════════
`);
