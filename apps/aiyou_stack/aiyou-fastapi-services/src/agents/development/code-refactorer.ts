/**
 * Code Refactorer Agent
 * Cleans up code for readability and maintainability
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

export class CodeRefactorerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "code-refactorer",
    name: "Code Refactorer",
    category: "development",
    description: "Cleans up that code you wrote at 3am. Makes it readable, fast, and maintainable.",
    tagline: "Code quality and maintainability improvements",
    capabilities: ["analysis", "implementation", "optimization"],
    tags: ["refactoring", "clean-code", "readability", "maintainability", "code-quality"],
    difficulty: "intermediate",
    estimatedTime: "1-3 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Code Refactoring Expert specializing in clean code principles and maintainability.

Your focus:
1. Code smell detection and elimination
2. Naming clarity and consistency
3. Function/method size and complexity reduction
4. DRY principle application
5. Code readability improvements

Refactoring priorities:
- Extract long methods into smaller, focused functions
- Improve variable and function naming
- Eliminate code duplication
- Reduce cyclomatic complexity
- Remove dead code and unused imports

Make code self-documenting. If it needs a comment to explain, refactor it to be clearer.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Edit"],
    optional: ["Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Code Smell Detection",
        description: "Identify code smells and anti-patterns",
        action: "Scan for long methods, duplication, complexity",
      },
      {
        name: "Prioritization",
        description: "Rank refactoring opportunities by impact",
        action: "Score by maintainability impact",
      },
      {
        name: "Refactoring",
        description: "Apply clean code transformations",
        action: "Extract, rename, simplify, eliminate duplication",
      },
      {
        name: "Validation",
        description: "Ensure functionality preserved",
        action: "Run tests and verify behavior",
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
