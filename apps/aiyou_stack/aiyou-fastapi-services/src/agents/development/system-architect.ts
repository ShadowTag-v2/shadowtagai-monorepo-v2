/**
 * System Architect Agent
 * Transforms messy codebases into clean, scalable systems
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

export class SystemArchitectAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "system-architect",
    name: "System Architect",
    category: "development",
    description:
      "Transforms messy codebases into clean, scalable systems. Your future self will thank you.",
    tagline: "Architecture design and system optimization",
    capabilities: ["analysis", "implementation", "optimization"],
    tags: ["architecture", "design-patterns", "scalability", "refactoring", "clean-code"],
    difficulty: "expert",
    estimatedTime: "4-8 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a System Architect with expertise in software architecture, design patterns, and scalable systems.

Your expertise:
1. Architecture assessment and modernization
2. Design pattern application (SOLID, DDD, Clean Architecture)
3. Scalability and performance optimization
4. Dependency management and modularization
5. Technical debt elimination

Focus on:
- Separation of concerns and single responsibility
- Dependency injection and inversion of control
- Layered architecture (presentation, business, data)
- Microservices vs. monolith decisions
- API design and contract-first development

Provide architectural blueprints and migration paths. Show the structure, not just the code.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Write", "Edit"],
    optional: ["Bash", "WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Architecture Analysis",
        description: "Analyze current system architecture and identify issues",
        action: "Map dependencies, layers, and coupling",
      },
      {
        name: "Design Patterns",
        description: "Identify applicable design patterns",
        action: "Apply SOLID principles and patterns",
      },
      {
        name: "Refactoring Plan",
        description: "Create step-by-step refactoring roadmap",
        action: "Prioritize architectural improvements",
      },
      {
        name: "Implementation",
        description: "Execute architectural refactoring",
        action: "Implement new structure incrementally",
      },
      {
        name: "Validation",
        description: "Verify architecture improvements",
        action: "Test and validate changes",
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
