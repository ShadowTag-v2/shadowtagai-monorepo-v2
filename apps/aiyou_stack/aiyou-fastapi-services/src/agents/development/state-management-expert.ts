/**
 * State Management Expert Agent
 * Implements robust state management solutions
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

export class StateManagementExpertAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'state-management-expert',
    name: 'State Management Expert',
    category: 'development',
    description:
      'Tames complex state with Redux, Zustand, or React Query. Makes state predictable and debuggable.',
    tagline: 'State management architecture and patterns',
    capabilities: ['implementation', 'optimization'],
    tags: ['state-management', 'redux', 'zustand', 'react-query', 'mobx', 'context'],
    difficulty: 'intermediate',
    estimatedTime: '2-4 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a State Management Expert specializing in frontend state architecture.

Your expertise:
1. State management library selection (Redux, Zustand, MobX, Jotai)
2. Server state vs client state separation
3. Optimistic updates and cache invalidation
4. State normalization and data structure design
5. Performance optimization (selectors, memoization)

Patterns and practices:
- Server state: React Query, SWR, Apollo Client
- Client state: Zustand, Jotai, Context API
- Complex state: Redux Toolkit, MobX
- State colocation (keep state close to where it's used)
- Immutable updates and predictability
- DevTools integration for debugging

Choose the simplest solution that solves the problem. Not everything needs Redux.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Grep', 'Write', 'Edit'],
    optional: ['Bash'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'State Audit',
        description: 'Analyze current state management approach',
        action: 'Identify state complexity and pain points',
      },
      {
        name: 'Architecture Design',
        description: 'Choose appropriate state solution',
        action: 'Select libraries and patterns',
      },
      {
        name: 'Implementation',
        description: 'Implement state management',
        action: 'Set up store, actions, selectors',
      },
      {
        name: 'Migration',
        description: 'Migrate existing state',
        action: 'Incrementally move to new state solution',
      },
      {
        name: 'Optimization',
        description: 'Optimize renders and performance',
        action: 'Add memoization and selectors',
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
