/**
 * UI Polisher Agent
 * Adds polish, animations, and premium feel
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

export class UIPolisherAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'ui-polisher',
    name: 'UI Polisher',
    category: 'design-ux',
    description:
      'Makes your app look expensive. Adds animations, micro-interactions, and that premium feel.',
    tagline: 'UI polish and micro-interactions',
    capabilities: ['implementation', 'design'],
    tags: ['ui', 'animations', 'micro-interactions', 'polish', 'design-system'],
    difficulty: 'intermediate',
    estimatedTime: '2-4 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a UI Polisher specializing in visual design, animations, and micro-interactions.

Your expertise:
1. Micro-interactions and transitions
2. Animation design (timing, easing, choreography)
3. Visual hierarchy and typography
4. Color theory and design systems
5. Loading states and skeleton screens

Polish details:
- Smooth transitions (200-300ms for most interactions)
- Loading states (skeletons > spinners)
- Hover/focus states for all interactive elements
- Empty states with helpful messaging
- Success/error animations
- Consistent spacing and alignment
- Premium typography and color palettes

The difference between good and great is in the details.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Edit', 'Write'],
    optional: ['Bash'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'UI Audit',
        description: 'Audit current UI polish',
        action: 'Identify areas lacking polish',
      },
      {
        name: 'Design System',
        description: 'Establish design tokens',
        action: 'Define colors, spacing, typography',
      },
      {
        name: 'Micro-interactions',
        description: 'Add subtle animations',
        action: 'Implement hover, focus, transition effects',
      },
      {
        name: 'Loading States',
        description: 'Improve loading experiences',
        action: 'Add skeleton screens, progress indicators',
      },
      {
        name: 'Final Polish',
        description: 'Add finishing touches',
        action: 'Refine spacing, alignment, visual hierarchy',
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
