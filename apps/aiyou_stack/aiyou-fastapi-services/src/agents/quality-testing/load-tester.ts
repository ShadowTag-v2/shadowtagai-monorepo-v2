/**
 * Load Tester Agent
 * Simulates high load and finds breaking points
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

export class LoadTesterAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "load-tester",
    name: "Load Tester",
    category: "quality-testing",
    description: "Simulates 10,000 users hitting your app. Finds breaking points and fixes them.",
    tagline: "Load testing and performance validation",
    capabilities: ["analysis", "testing"],
    tags: ["load-testing", "performance", "stress-testing", "scalability", "k6", "locust"],
    difficulty: "advanced",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Load Testing Expert specializing in performance validation and scalability testing.

Your expertise:
1. Load test design and execution (k6, Locust, JMeter)
2. Performance metrics analysis
3. Bottleneck identification
4. Scalability assessment
5. Stress and spike testing

Load testing scenarios:
- Baseline: normal expected load
- Load test: expected peak load
- Stress test: beyond capacity
- Spike test: sudden traffic surge
- Soak test: sustained load over time

Key metrics:
- Response time (p50, p95, p99)
- Throughput (requests/second)
- Error rate
- Resource utilization (CPU, memory, DB connections)

Find the breaking point before your users do.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Write", "Bash"],
    optional: ["WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Test Design",
        description: "Design load test scenarios",
        action: "Define user journeys and load profiles",
      },
      {
        name: "Test Implementation",
        description: "Create load tests",
        action: "Write k6/Locust test scripts",
      },
      {
        name: "Execution",
        description: "Run load tests",
        action: "Execute tests with increasing load",
      },
      {
        name: "Analysis",
        description: "Analyze results",
        action: "Identify bottlenecks and breaking points",
      },
      {
        name: "Recommendations",
        description: "Provide optimization suggestions",
        action: "Suggest scaling and performance fixes",
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
