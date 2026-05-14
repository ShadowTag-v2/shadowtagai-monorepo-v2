import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class AnalyticsEngineerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "analytics-engineer",
    name: "Analytics Engineer",
    category: "business-analytics",
    description:
      "Tracks what actually matters. Shows you user behavior, conversion funnels, and real insights.",
    tagline: "Analytics implementation and insights",
    capabilities: ["implementation", "analysis"],
    tags: ["analytics", "tracking", "metrics", "insights", "conversion"],
    difficulty: "intermediate",
    estimatedTime: "2-3 hours",
  };
  prompt: AgentPromptTemplate = {
    system: `You are an Analytics Engineer specializing in event tracking and data analysis. Implement Google Analytics, Mixpanel, Amplitude. Track user behavior, conversion funnels, and key metrics.`,
  };
  tools: AgentTools = { required: ["Read", "Write", "Edit"], optional: ["Bash"] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Analytics Setup",
        description: "Implement analytics tracking",
        action: "Add GA4, Mixpanel, or Amplitude",
      },
      {
        name: "Event Tracking",
        description: "Track key user events",
        action: "Implement event tracking code",
      },
      {
        name: "Funnels",
        description: "Create conversion funnels",
        action: "Define and track funnels",
      },
      {
        name: "Dashboards",
        description: "Build analytics dashboards",
        action: "Create data visualization",
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
