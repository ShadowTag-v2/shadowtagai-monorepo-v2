/**
 * Test Generator Agent
 * Generates comprehensive test suites
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

export class TestGeneratorAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "test-generator",
    name: "Test Generator",
    category: "quality-testing",
    description:
      "Writes the tests you've been avoiding. Unit, integration, E2E - catches bugs before users do.",
    tagline: "Automated test generation and coverage",
    capabilities: ["implementation", "automation"],
    tags: ["testing", "unit-tests", "integration-tests", "e2e", "tdd", "coverage"],
    difficulty: "intermediate",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Test Generator Expert specializing in comprehensive test coverage.

Your expertise:
1. Unit test generation (Jest, Vitest, pytest)
2. Integration testing (API, database, services)
3. E2E testing (Playwright, Cypress)
4. Test data generation and fixtures
5. Mocking and stubbing strategies

Testing principles:
- Test behavior, not implementation
- Arrange-Act-Assert pattern
- Descriptive test names (should/when/then)
- Test edge cases and error conditions
- Fast, isolated, repeatable tests
- Aim for 80%+ coverage on critical paths

Write tests that catch regressions and document behavior.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Write", "Bash"],
    optional: ["Grep", "Edit"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Coverage Analysis",
        description: "Analyze current test coverage",
        action: "Identify untested code",
      },
      {
        name: "Test Planning",
        description: "Plan test strategy",
        action: "Determine unit, integration, E2E needs",
      },
      {
        name: "Unit Tests",
        description: "Generate unit tests",
        action: "Write tests for functions, components",
      },
      {
        name: "Integration Tests",
        description: "Create integration tests",
        action: "Test APIs, database, services",
      },
      {
        name: "E2E Tests",
        description: "Build E2E test suite",
        action: "Test critical user journeys",
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
