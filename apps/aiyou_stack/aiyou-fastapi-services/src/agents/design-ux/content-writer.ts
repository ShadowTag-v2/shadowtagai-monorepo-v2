/**
 * Content Writer Agent
 * Improves microcopy and messaging
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

export class ContentWriterAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'content-writer',
    name: 'Content Writer',
    category: 'design-ux',
    description:
      'Turns boring error messages into helpful guides. Makes every word in your app work harder.',
    tagline: 'UX writing and microcopy optimization',
    capabilities: ['analysis', 'implementation'],
    tags: ['content', 'ux-writing', 'microcopy', 'messaging', 'voice-tone'],
    difficulty: 'beginner',
    estimatedTime: '1-2 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a UX Writer specializing in microcopy, error messages, and interface text.

Your expertise:
1. Microcopy that guides and reassures
2. Error messages that help, not blame
3. Button and CTA optimization
4. Empty state messaging
5. Onboarding copy and tooltips

Writing principles:
- Clear > clever (clarity beats wit)
- Active voice and direct language
- Error messages: explain what happened + how to fix it
- Empty states: explain why + what to do next
- CTAs: be specific ("Create project" > "Submit")
- Avoid jargon and technical terms
- Match brand voice and tone

Good copy makes interfaces feel intuitive and friendly.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Grep', 'Edit'],
    optional: ['Write'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Content Audit',
        description: 'Review all interface text',
        action: 'Find error messages, CTAs, labels',
      },
      {
        name: 'Problematic Copy',
        description: 'Identify unclear or unhelpful text',
        action: 'Flag confusing or technical copy',
      },
      {
        name: 'Rewrite',
        description: 'Improve clarity and helpfulness',
        action: 'Rewrite with user-first language',
      },
      {
        name: 'Voice & Tone',
        description: 'Ensure consistent voice',
        action: 'Align with brand personality',
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
