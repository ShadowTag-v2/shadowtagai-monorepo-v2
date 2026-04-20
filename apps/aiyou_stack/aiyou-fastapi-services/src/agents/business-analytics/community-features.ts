import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from '../../types/agent.types';
import { BaseAgent } from '../../utils/base-agent';

export class CommunityFeaturesAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'community-features',
    name: 'Community Features',
    category: 'business-analytics',
    description:
      'Adds forums, comments, user profiles. Builds the features that keep users coming back.',
    tagline: 'Community and social features',
    capabilities: ['implementation'],
    tags: ['community', 'social', 'forums', 'comments', 'profiles'],
    difficulty: 'intermediate',
    estimatedTime: '3-5 hours',
  };
  prompt: AgentPromptTemplate = {
    system: `You are a Community Features Expert specializing in social and engagement features. Build comments, forums, user profiles, followers, notifications. Create sticky community features.`,
  };
  tools: AgentTools = { required: ['Read', 'Write', 'Edit'], optional: ['Bash'] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'User Profiles',
        description: 'Create user profile system',
        action: 'Build profiles, avatars, bios',
      },
      {
        name: 'Comments',
        description: 'Add commenting system',
        action: 'Implement threaded comments',
      },
      {
        name: 'Social Features',
        description: 'Add social mechanics',
        action: 'Implement follow, like, share',
      },
      {
        name: 'Notifications',
        description: 'Build notification system',
        action: 'Add real-time notifications',
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
