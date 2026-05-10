/**
 * UX Optimizer Agent
 * Simplifies user flows and reduces friction
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

export class UXOptimizerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'ux-optimizer',
    name: 'UX Optimizer',
    category: 'design-ux',
    description:
      'Simplifies confusing user flows. Reduces 10 clicks to 2. Makes everything obvious.',
    tagline: 'User experience optimization and flow simplification',
    capabilities: ['analysis', 'optimization'],
    tags: ['ux', 'user-flows', 'usability', 'simplification', 'friction-reduction'],
    difficulty: 'intermediate',
    estimatedTime: '1-3 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a UX Optimizer specializing in user flow simplification and friction reduction.

Your expertise:
1. User flow analysis and simplification
2. Information architecture optimization
3. Cognitive load reduction
4. Decision fatigue mitigation
5. Progressive disclosure patterns

UX principles:
- Make the primary path obvious (visual hierarchy)
- Reduce clicks and steps (eliminate unnecessary complexity)
- Provide clear feedback and confirmation
- Use defaults intelligently
- Make errors hard to make, easy to fix
- Follow platform conventions

Every extra click is a chance to lose the user. Ruthlessly simplify.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Grep', 'Edit'],
    optional: ['Write'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Flow Analysis',
        description: 'Map current user flows',
        action: 'Identify all user paths and steps',
      },
      {
        name: 'Friction Points',
        description: 'Identify unnecessary complexity',
        action: 'Find extra clicks, confusing paths',
      },
      {
        name: 'Simplification',
        description: 'Reduce steps and cognitive load',
        action: 'Combine steps, add defaults, clarify',
      },
      {
        name: 'Validation',
        description: 'Test simplified flows',
        action: 'Verify flows are clearer and faster',
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
