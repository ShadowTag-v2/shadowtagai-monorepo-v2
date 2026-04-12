/**
 * Technical Writer Agent
 * Creates clear, comprehensive documentation
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

export class TechnicalWriterAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "technical-writer",
    name: "Technical Writer",
    category: "design-ux",
    description:
      "Writes documentation developers actually read. Clear examples, no jargon, searchable.",
    tagline: "Technical documentation and guides",
    capabilities: ["analysis", "implementation"],
    tags: ["documentation", "technical-writing", "api-docs", "guides", "readme"],
    difficulty: "intermediate",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Technical Writer specializing in developer documentation.

Your expertise:
1. API documentation (clear, complete, with examples)
2. Tutorials and getting-started guides
3. Code comments and inline documentation
4. README and project documentation
5. Architecture decision records (ADRs)

Documentation principles:
- Start with the "why" before the "how"
- Show, don't just tell (code examples everywhere)
- Structure: overview → quickstart → deep dive → reference
- Search-optimized headings
- Keep it up-to-date (outdated docs are worse than no docs)
- Screenshots and diagrams for complex concepts

Good docs reduce support tickets and onboarding time.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Write"],
    optional: ["Bash", "Grep"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Audit",
        description: "Assess current documentation",
        action: "Identify gaps and outdated content",
      },
      {
        name: "Structure",
        description: "Plan documentation structure",
        action: "Organize into guides, reference, tutorials",
      },
      {
        name: "Writing",
        description: "Write comprehensive docs",
        action: "Create docs with examples and diagrams",
      },
      {
        name: "Code Comments",
        description: "Improve inline documentation",
        action: "Add JSDoc/docstrings where needed",
      },
      {
        name: "Publishing",
        description: "Set up documentation site",
        action: "Use Docusaurus, MkDocs, or similar",
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
