import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class LandingPageOptimizerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "landing-page-optimizer",
    name: "Landing Page Optimizer",
    category: "business-analytics",
    description:
      "Writes copy that converts visitors to users. Headlines, CTAs, social proof that works.",
    tagline: "Landing page optimization and conversion",
    capabilities: ["implementation", "optimization"],
    tags: ["landing-page", "conversion", "cta", "copywriting", "cro"],
    difficulty: "beginner",
    estimatedTime: "1-2 hours",
  };
  prompt: AgentPromptTemplate = {
    system: `You are a Landing Page Optimizer specializing in conversion rate optimization. Write compelling headlines, CTAs, value propositions. Add social proof, testimonials, urgency.`,
  };
  tools: AgentTools = { required: ["Read", "Edit"], optional: ["Write"] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Audit",
        description: "Audit current landing page",
        action: "Analyze conversion elements",
      },
      {
        name: "Headlines",
        description: "Optimize headlines",
        action: "Write compelling value prop",
      },
      {
        name: "CTAs",
        description: "Improve calls-to-action",
        action: "Make CTAs specific and prominent",
      },
      {
        name: "Social Proof",
        description: "Add credibility elements",
        action: "Add testimonials, logos, stats",
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
