import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from '../../types/agent.types';
import { BaseAgent } from '../../utils/base-agent';

export class SupportBuilderAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'support-builder',
    name: 'Support Builder',
    category: 'business-analytics',
    description:
      'Creates help systems that reduce support tickets by 80%. FAQs, chat widgets, documentation.',
    tagline: 'Customer support and help systems',
    capabilities: ['implementation'],
    tags: ['support', 'help', 'faq', 'chat', 'intercom'],
    difficulty: 'beginner',
    estimatedTime: '1-2 hours',
  };
  prompt: AgentPromptTemplate = {
    system: `You are a Support Builder specializing in self-service help systems. Build FAQs, knowledge bases, chat widgets (Intercom, Zendesk). Reduce support load with better UX.`,
  };
  tools: AgentTools = { required: ['Read', 'Write'], optional: ['Edit'] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'FAQ',
        description: 'Create FAQ and help center',
        action: 'Build searchable FAQ system',
      },
      {
        name: 'Chat Widget',
        description: 'Add chat support',
        action: 'Integrate Intercom or custom chat',
      },
      {
        name: 'Documentation',
        description: 'Write help documentation',
        action: 'Create user guides',
      },
      { name: 'Search', description: 'Add help search', action: 'Implement searchable help' },
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
