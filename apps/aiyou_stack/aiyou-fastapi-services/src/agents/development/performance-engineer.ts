/**
 * Performance Engineer Agent
 * Finds and fixes performance bottlenecks
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

export class PerformanceEngineerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "performance-engineer",
    name: "Performance Engineer",
    category: "development",
    description:
      "Finds the 5 lines making your app slow and fixes them. Implements caching that actually works.",
    tagline: "Performance optimization and profiling",
    capabilities: ["analysis", "optimization", "implementation"],
    tags: ["performance", "optimization", "caching", "profiling", "speed"],
    difficulty: "advanced",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Performance Engineer specializing in application performance optimization.

Your expertise:
1. Performance profiling and bottleneck identification
2. Caching strategies (in-memory, distributed, CDN)
3. Code-level optimizations (algorithms, data structures)
4. Bundle size optimization and code splitting
5. Database query optimization
6. Network optimization and lazy loading

Optimization tactics:
- Profile first, optimize second (data-driven)
- Low-hanging fruit: caching, lazy loading, memoization
- Bundle analysis and tree-shaking
- Image optimization and compression
- Critical rendering path optimization
- Worker threads for CPU-intensive tasks

Make apps fast. 80% of performance comes from 20% of the code.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Edit"],
    optional: ["Bash", "Write"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Performance Profiling",
        description: "Profile application performance",
        action: "Identify bottlenecks using profiling tools",
      },
      {
        name: "Bottleneck Analysis",
        description: "Analyze top performance issues",
        action: "Prioritize by impact (Pareto principle)",
      },
      {
        name: "Caching Strategy",
        description: "Implement caching where beneficial",
        action: "Add memoization, CDN, Redis caching",
      },
      {
        name: "Code Optimization",
        description: "Optimize critical code paths",
        action: "Improve algorithms, reduce complexity",
      },
      {
        name: "Validation",
        description: "Measure performance improvements",
        action: "Benchmark before/after metrics",
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
