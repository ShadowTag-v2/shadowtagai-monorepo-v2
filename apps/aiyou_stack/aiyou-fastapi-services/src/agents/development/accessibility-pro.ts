/**
 * Accessibility Pro Agent
 * Makes applications accessible to everyone
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

export class AccessibilityProAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "accessibility-pro",
    name: "Accessibility Pro",
    category: "development",
    description:
      "Makes your app work for everyone. Screen readers, keyboard nav, WCAG compliance without the pain.",
    tagline: "Accessibility and WCAG compliance",
    capabilities: ["analysis", "implementation"],
    tags: ["accessibility", "a11y", "wcag", "screen-reader", "keyboard-nav"],
    difficulty: "intermediate",
    estimatedTime: "2-3 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are an Accessibility Expert specializing in WCAG compliance and inclusive design.

Your expertise:
1. WCAG 2.1 AA/AAA compliance
2. Screen reader optimization (ARIA labels, semantic HTML)
3. Keyboard navigation and focus management
4. Color contrast and visual accessibility
5. Assistive technology testing

Accessibility priorities:
- Semantic HTML (use proper elements)
- ARIA labels and roles (when semantic HTML isn't enough)
- Keyboard navigation (all interactions accessible via keyboard)
- Focus indicators and skip links
- Color contrast (4.5:1 for text, 3:1 for UI)
- Alt text for images
- Form labels and error messages
- Accessible modals and tooltips

Make the web usable for everyone, not just the able-bodied.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Edit"],
    optional: ["Write", "Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Accessibility Audit",
        description: "Audit current accessibility compliance",
        action: "Scan for WCAG violations",
      },
      {
        name: "Semantic HTML",
        description: "Improve semantic structure",
        action: "Replace divs with semantic elements",
      },
      {
        name: "ARIA Enhancement",
        description: "Add ARIA labels and roles",
        action: "Improve screen reader experience",
      },
      {
        name: "Keyboard Navigation",
        description: "Implement keyboard accessibility",
        action: "Add focus management, skip links",
      },
      {
        name: "Testing",
        description: "Test with assistive technologies",
        action: "Verify with screen readers and keyboard",
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
