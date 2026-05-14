/**
 * Market Analyst Agent
 * Competitive analysis and market positioning
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class MarketAnalystAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "market-analyst",
    name: "Market Analyst",
    category: "product-strategy",
    description:
      "Compares your features to competitors and finds your unfair advantages. Shows what to build to win.",
    tagline: "Competitive analysis and strategic positioning",
    capabilities: ["analysis", "strategy"],
    tags: ["competitive-analysis", "market", "positioning", "differentiation"],
    difficulty: "intermediate",
    estimatedTime: "1-3 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Market Analyst with expertise in competitive intelligence and strategic positioning.

Your capabilities:
1. Competitive feature comparison and gap analysis
2. Market positioning and differentiation strategy
3. Unfair advantage identification
4. Market opportunity assessment
5. Strategic feature recommendations

Analyze with depth:
- Feature parity vs. differentiation
- Market positioning and messaging
- Unique value propositions
- Competitive moats and barriers
- Blue ocean opportunities

Provide actionable intelligence. Show exactly what to build to win market share.`,

    context: [
      "Product features and capabilities",
      "Competitive landscape",
      "Market positioning",
      "Target customers",
      "Business model",
    ],
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "WebSearch"],
    optional: ["WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Feature Inventory",
        description: "Catalog current product capabilities",
        action: "Map all features and functionality",
      },
      {
        name: "Competitive Research",
        description: "Research competitor features and positioning",
        action: "Gather competitive intelligence",
      },
      {
        name: "Gap Analysis",
        description: "Identify feature gaps and opportunities",
        action: "Compare features and find white space",
      },
      {
        name: "Differentiation Strategy",
        description: "Define unique value and unfair advantages",
        action: "Identify moats and competitive positioning",
      },
      {
        name: "Strategic Roadmap",
        description: "Recommend features to build competitive advantage",
        action: "Prioritize features for market leadership",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    _context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
