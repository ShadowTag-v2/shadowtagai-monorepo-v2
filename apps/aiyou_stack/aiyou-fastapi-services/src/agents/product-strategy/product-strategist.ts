/**
 * Product Strategist Agent
 * Analyzes features and provides strategic product direction
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

export class ProductStrategistAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "product-strategist",
    name: "Product Strategist",
    category: "product-strategy",
    description:
      "Looks at your features and asks the hard questions. Tells you what to build next and what to kill.",
    tagline: "Strategic product direction and feature prioritization",
    capabilities: ["analysis", "strategy"],
    tags: ["product", "strategy", "roadmap", "features", "prioritization"],
    difficulty: "intermediate",
    estimatedTime: "30-60 minutes",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Product Strategist with deep expertise in product management, market analysis, and strategic planning.

Your role is to:
1. Analyze existing features and product direction
2. Ask critical questions about product-market fit
3. Identify features that should be prioritized, deprioritized, or killed
4. Provide strategic recommendations for product evolution
5. Challenge assumptions and identify blind spots

Be direct and honest. If a feature doesn't serve the core value proposition, say so. If the product is trying to do too much, call it out.

Focus on:
- User value and business impact
- Technical feasibility vs. strategic value
- Competitive positioning
- Resource allocation
- Market timing`,

    userPromptPrefix: "Analyze the following product and provide strategic recommendations:",

    context: [
      "Current features and functionality",
      "Product roadmap or backlog",
      "User feedback and analytics",
      "Competitive landscape",
      "Business goals and constraints",
    ],

    examples: [
      {
        input: "We have 15 features planned for next quarter",
        output: `Let me analyze your roadmap systematically:

STRATEGIC ASSESSMENT:
1. Core Value Proposition: What are the 2-3 features that define your unique value?
2. Feature Bloat Risk: 15 features suggest potential lack of focus
3. Resource Reality: Can you actually deliver 15 high-quality features?

HARD QUESTIONS:
- Which features directly solve your users' top pain point?
- Which features are "nice to have" vs. "must have"?
- Are you building features because competitors have them?
- What happens if you only ship 3 features instead?

RECOMMENDATIONS:
1. KILL: Features that don't tie to core value prop or key metrics
2. BUILD NOW: The 3 features with highest user value + business impact
3. BUILD LATER: Good ideas that can wait
4. NEVER BUILD: Complexity that doesn't justify the maintenance burden

Next Steps:
- Run a feature scoring exercise (Impact vs. Effort)
- Talk to 10 users about their actual needs
- Define your product's "job to be done"`,
      },
    ],
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep"],
    optional: ["WebFetch", "WebSearch", "Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Discovery",
        description: "Scan codebase for features, components, and product structure",
        action: "Use Glob and Grep to identify features, routes, components, and documentation",
        validation: "Ensure comprehensive understanding of current product scope",
      },
      {
        name: "Feature Analysis",
        description: "Analyze each feature for complexity, usage, and strategic value",
        action: "Review code complexity, dependencies, and potential user impact",
        validation: "Create feature inventory with strategic assessment",
      },
      {
        name: "Strategic Assessment",
        description: "Evaluate product direction and identify strategic gaps",
        action: "Assess product-market fit, competitive positioning, and focus areas",
        validation: "Generate strategic insights and recommendations",
      },
      {
        name: "Prioritization Framework",
        description: "Create actionable prioritization of features",
        action: "Score features on impact, effort, strategic value, and user value",
        validation: "Provide clear BUILD/KILL/DEFER recommendations",
      },
      {
        name: "Recommendations",
        description: "Generate strategic recommendations and action items",
        action: "Create specific, actionable next steps for product evolution",
        validation: "Ensure recommendations are practical and measurable",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    // Implementation would use Claude Agent SDK to execute the step
    // This is a placeholder for the actual implementation
    switch (step.name) {
      case "Discovery":
        result.recommendations?.push("Scan codebase for feature inventory");
        break;
      case "Feature Analysis":
        result.recommendations?.push("Analyze feature complexity and usage patterns");
        break;
      case "Strategic Assessment":
        result.recommendations?.push("Evaluate product-market fit and positioning");
        break;
      case "Prioritization Framework":
        result.recommendations?.push("Score and prioritize features");
        break;
      case "Recommendations":
        result.recommendations?.push("Generate actionable strategic recommendations");
        break;
    }
  }
}
