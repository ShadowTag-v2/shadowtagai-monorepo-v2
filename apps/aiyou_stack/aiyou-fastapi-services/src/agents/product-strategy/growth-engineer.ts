/**
 * Growth Engineer Agent
 * Identifies growth opportunities and builds viral loops
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

export class GrowthEngineerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "growth-engineer",
    name: "Growth Engineer",
    category: "product-strategy",
    description:
      "Finds where users get hooked in your app and builds viral loops that actually work.",
    tagline: "Data-driven growth hacking and viral mechanics",
    capabilities: ["analysis", "implementation", "optimization"],
    tags: ["growth", "viral", "hooks", "retention", "activation"],
    difficulty: "advanced",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Growth Engineer specializing in user acquisition, activation, and viral growth.

Your expertise includes:
1. Identifying "aha moments" in user journeys
2. Building viral loops and referral systems
3. Optimizing onboarding flows for activation
4. Implementing growth hooks (invites, sharing, social proof)
5. A/B testing and growth experimentation

Focus on actionable growth mechanics:
- Viral coefficient optimization
- Time-to-value reduction
- Network effects and social features
- Gamification and engagement loops
- Frictionless sharing mechanisms

Be data-driven and practical. Build features that measurably increase growth metrics.`,

    context: [
      "User activation flows",
      "Social/sharing features",
      "Referral systems",
      "Onboarding sequences",
      "Analytics and user behavior data",
    ],
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Write", "Edit"],
    optional: ["WebFetch", "Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "User Flow Analysis",
        description: "Map user activation journey and identify drop-off points",
        action: "Analyze routes, components, and user flows",
      },
      {
        name: "Hook Identification",
        description: 'Find the "aha moment" where users get value',
        action: "Identify core value delivery points",
      },
      {
        name: "Viral Loop Design",
        description: "Design viral mechanics and sharing features",
        action: "Create referral systems, social sharing, invites",
      },
      {
        name: "Implementation",
        description: "Build growth features and tracking",
        action: "Implement viral loops, analytics, and A/B tests",
      },
      {
        name: "Optimization Plan",
        description: "Create growth experimentation roadmap",
        action: "Define metrics, experiments, and success criteria",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    // Placeholder implementation
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
