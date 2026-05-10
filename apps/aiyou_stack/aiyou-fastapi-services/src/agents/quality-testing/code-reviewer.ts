/**
 * Code Reviewer Agent
 * Performs thorough code reviews
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from '../../types/agent.types';
import { BaseAgent } from '../../utils/base-agent';

export class CodeReviewerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'code-reviewer',
    name: 'Code Reviewer',
    category: 'quality-testing',
    description:
      'Reviews your code like a senior engineer. Catches bugs, suggests improvements, ensures quality.',
    tagline: 'Automated code review and quality assurance',
    capabilities: ['analysis'],
    tags: ['code-review', 'quality', 'best-practices', 'bugs', 'maintainability'],
    difficulty: 'intermediate',
    estimatedTime: '1-2 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Code Reviewer with senior engineering experience across multiple languages and frameworks.

Your review criteria:
1. Correctness and potential bugs
2. Code quality and maintainability
3. Performance implications
4. Security vulnerabilities
5. Best practices and idioms
6. Test coverage and edge cases

Review checklist:
- Logic errors and edge cases
- Null/undefined handling
- Error handling and recovery
- Resource leaks (connections, memory)
- Race conditions and concurrency issues
- Code duplication (DRY)
- Naming clarity
- Function/class size and complexity
- Comments (when needed for why, not what)

Be constructive. Explain the "why" behind suggestions.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Grep'],
    optional: ['Bash'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Code Analysis',
        description: 'Analyze code changes',
        action: 'Review logic, structure, patterns',
      },
      {
        name: 'Bug Detection',
        description: 'Identify potential bugs',
        action: 'Find logic errors, edge cases',
      },
      {
        name: 'Quality Assessment',
        description: 'Evaluate code quality',
        action: 'Check maintainability, readability',
      },
      {
        name: 'Security Review',
        description: 'Check for security issues',
        action: 'Identify vulnerabilities',
      },
      {
        name: 'Recommendations',
        description: 'Provide actionable feedback',
        action: 'Suggest specific improvements',
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow['steps'][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
