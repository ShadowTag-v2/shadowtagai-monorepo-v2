/**
 * Design System Builder Agent
 * Creates comprehensive design systems
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

export class DesignSystemBuilderAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "design-system-builder",
    name: "Design System Builder",
    category: "design-ux",
    description:
      "Creates a component library you'll actually use. Consistent styles across everything.",
    tagline: "Design system and component library creation",
    capabilities: ["implementation", "design"],
    tags: ["design-system", "components", "tokens", "storybook", "consistency"],
    difficulty: "advanced",
    estimatedTime: "4-8 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Design System Builder specializing in component libraries and design tokens.

Your expertise:
1. Design token architecture (colors, spacing, typography)
2. Component library design and implementation
3. Documentation and Storybook setup
4. Theming and customization
5. Accessibility and responsive patterns

Design system layers:
- Tokens: primitives (colors, spacing, typography)
- Components: reusable UI building blocks
- Patterns: common UI patterns and layouts
- Templates: page-level structures
- Documentation: usage guidelines

Build systems that scale. Make consistency easy, not hard.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Write", "Edit"],
    optional: ["Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Audit",
        description: "Audit existing components and styles",
        action: "Identify inconsistencies and patterns",
      },
      {
        name: "Tokens",
        description: "Define design tokens",
        action: "Create color, spacing, typography scales",
      },
      {
        name: "Components",
        description: "Build component library",
        action: "Create reusable, composable components",
      },
      {
        name: "Documentation",
        description: "Document design system",
        action: "Set up Storybook and guidelines",
      },
      {
        name: "Migration",
        description: "Migrate to design system",
        action: "Replace ad-hoc styles with system",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
