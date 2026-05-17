/**
 * Component Comparison Analyzer Agent
 * Compares different PNKLN stack components and generates migration/adaptation guidance
 */

import { masterPromptFramework } from "../../prompts/frameworks/master-prompt-framework";
import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import type { PNKLNComponent } from "../../types/pnkln.types";
import { BaseAgent } from "../../utils/base-agent";

export class ComponentComparisonAnalyzerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "component-comparison-analyzer",
    name: "Component Comparison Analyzer",
    category: "ai-innovation",
    description: "Compares PNKLN components and provides migration/adaptation guidance.",
    tagline: "Component comparison and migration planning",
    capabilities: ["analysis", "strategy"],
    tags: ["pnkln", "comparison", "migration", "adaptation", "analysis"],
    difficulty: "expert",
    estimatedTime: "2-3 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are analyzing and comparing components of the PNKLN Core Stack™.
Your role is to identify key differences, provide adaptation guidance, and create migration paths.

Focus on:
1. Architectural differences and their implications
2. Metric adaptations (e.g., latency vs runtime, FP/FN vs quality scores)
3. Integration pattern shifts (caller vs callee)
4. Feature transformations (validation rules vs ethical compliance)
5. Cost model differences
6. Migration strategies and risks`,

    context: [
      "Component specifications for comparison",
      "Architecture diagrams",
      "Performance metrics",
      "Integration patterns",
      "Feature sets and unique capabilities",
    ],

    examples: [
      {
        input: "Compare Judge 6 and Gemini Ingestion Layer",
        output: masterPromptFramework.compareComponents("judge-6", "gemini-ingestion"),
      },
    ],
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep"],
    optional: ["WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Component Identification",
        description: "Identify components to compare",
        action: "Parse user request for component names",
        validation: "Verify components exist in PNKLN stack",
      },
      {
        name: "Architecture Comparison",
        description: "Compare architectural patterns",
        action: "Analyze deployment, integration, tech stack differences",
        validation: "Identify architectural implications",
      },
      {
        name: "Metrics Mapping",
        description: "Map metrics between components",
        action: "Identify equivalent metrics and necessary adaptations",
        validation: "Create metrics translation guide",
      },
      {
        name: "Feature Analysis",
        description: "Compare unique features",
        action: "Identify feature transformations and new requirements",
        validation: "Document feature gaps and opportunities",
      },
      {
        name: "Migration Path Design",
        description: "Create migration strategy",
        action: "Design step-by-step adaptation path",
        validation: "Assess risks and provide mitigation strategies",
      },
      {
        name: "Report Generation",
        description: "Generate comparison report",
        action: "Compile findings into structured comparison",
        validation: "Ensure actionable migration guidance",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    switch (step.name) {
      case "Component Identification":
        result.recommendations?.push("Identify PNKLN components for comparison");
        break;
      case "Architecture Comparison":
        result.recommendations?.push("Compare architectural patterns and tech stacks");
        break;
      case "Metrics Mapping":
        result.recommendations?.push("Map performance metrics between components");
        break;
      case "Feature Analysis":
        result.recommendations?.push("Analyze unique features and transformations");
        break;
      case "Migration Path Design":
        result.recommendations?.push("Design migration strategy with risk mitigation");
        break;
      case "Report Generation":
        result.recommendations?.push("Generate comprehensive comparison report");
        break;
    }
  }

  /**
   * Helper method to generate comparison between specific components
   */
  async compareComponents(
    componentA: PNKLNComponent,
    componentB: PNKLNComponent,
    context: AgentExecutionContext,
  ): Promise<AgentResult> {
    const comparisonPrompt = masterPromptFramework.compareComponents(componentA, componentB);

    return this.execute({
      ...context,
      userQuery: comparisonPrompt,
      additionalContext: {
        ...context.additionalContext,
        componentA,
        componentB,
        comparisonType: "detailed",
      },
    });
  }
}
