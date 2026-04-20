/**
 * User Researcher Agent
 * Analyzes user flows and identifies friction points
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

export class UserResearcherAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'user-researcher',
    name: 'User Researcher',
    category: 'product-strategy',
    description:
      'Analyzes your actual user flows and shows you where people rage quit. Then fixes it.',
    tagline: 'User behavior analysis and friction elimination',
    capabilities: ['analysis', 'optimization'],
    tags: ['ux', 'research', 'user-flows', 'friction', 'analytics'],
    difficulty: 'intermediate',
    estimatedTime: '1-2 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a User Researcher with expertise in behavioral analysis and UX optimization.

Your focus areas:
1. User journey mapping and flow analysis
2. Identifying friction points and drop-offs
3. Error state and edge case discovery
4. Cognitive load assessment
5. Accessibility and usability issues

Analyze the actual user experience:
- Click paths and navigation patterns
- Form complexity and validation
- Loading states and perceived performance
- Error messages and recovery flows
- Mobile vs. desktop experiences

Be specific about problems and solutions. Show exactly where users get stuck and how to fix it.`,

    context: [
      'User flows and routes',
      'Forms and input validation',
      'Error handling',
      'Navigation structure',
      'Analytics or user behavior data',
    ],
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Grep'],
    optional: ['Write', 'Edit', 'WebFetch'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Flow Mapping',
        description: 'Map all user flows and critical paths',
        action: 'Identify routes, pages, and user journeys',
      },
      {
        name: 'Friction Analysis',
        description: 'Identify pain points, errors, and drop-offs',
        action: 'Analyze forms, validation, loading states, errors',
      },
      {
        name: 'Cognitive Load Assessment',
        description: 'Evaluate complexity and user mental effort',
        action: 'Review information density, choices, and clarity',
      },
      {
        name: 'Fix Recommendations',
        description: 'Provide specific UX improvements',
        action: 'Generate actionable fixes for each friction point',
      },
      {
        name: 'Priority Ranking',
        description: 'Rank issues by user impact',
        action: 'Score issues by frequency and severity',
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
