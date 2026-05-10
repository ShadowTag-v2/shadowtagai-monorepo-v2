import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from '../../types/agent.types';
import { BaseAgent } from '../../utils/base-agent';

export class EmailAutomatorAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'email-automator',
    name: 'Email Automator',
    category: 'business-analytics',
    description:
      'Builds email flows that users actually open. Welcome series, re-engagement, transactional.',
    tagline: 'Email automation and campaigns',
    capabilities: ['implementation', 'automation'],
    tags: ['email', 'automation', 'campaigns', 'sendgrid', 'mailchimp'],
    difficulty: 'beginner',
    estimatedTime: '2-3 hours',
  };
  prompt: AgentPromptTemplate = {
    system: `You are an Email Automator specializing in email marketing and transactional emails. Build welcome series, drip campaigns, re-engagement flows. Use SendGrid, Mailchimp, or similar.`,
  };
  tools: AgentTools = { required: ['Read', 'Write'], optional: ['Bash', 'WebFetch'] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Email Service',
        description: 'Integrate email provider',
        action: 'Set up SendGrid/Mailchimp',
      },
      {
        name: 'Templates',
        description: 'Create email templates',
        action: 'Design responsive email templates',
      },
      {
        name: 'Automation',
        description: 'Build email flows',
        action: 'Implement welcome, drip, transactional',
      },
      {
        name: 'Testing',
        description: 'Test email delivery',
        action: 'Verify sending and deliverability',
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
