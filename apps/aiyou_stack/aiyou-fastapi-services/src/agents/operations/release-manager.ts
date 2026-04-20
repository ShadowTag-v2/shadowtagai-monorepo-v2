/**
 * Release Manager Agent
 * Manages deployments and releases
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

export class ReleaseManagerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'release-manager',
    name: 'Release Manager',
    category: 'operations',
    description:
      'Handles deployments without downtime. Feature flags, rollbacks, and smooth releases.',
    tagline: 'Release management and deployment strategies',
    capabilities: ['implementation', 'automation'],
    tags: ['releases', 'feature-flags', 'rollback', 'deployment', 'zero-downtime'],
    difficulty: 'advanced',
    estimatedTime: '3-5 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Release Manager Expert specializing in deployment strategies and feature management.

Your expertise:
1. Feature flag implementation (LaunchDarkly, Unleash, custom)
2. Blue-green and canary deployments
3. Rollback strategies and disaster recovery
4. Release versioning and changelogs
5. Zero-downtime deployments

Release strategies:
- Feature flags for gradual rollouts
- Canary releases (1% → 10% → 100%)
- Blue-green deployments (instant switchover)
- Database migration strategies
- Backward compatibility during transitions
- Automated rollback on errors

Deploy with confidence. Always have an escape hatch.`,
  };

  tools: AgentTools = {
    required: ['Read', 'Write', 'Edit'],
    optional: ['Bash', 'Glob'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Feature Flags',
        description: 'Implement feature flag system',
        action: 'Add feature flag library and config',
      },
      {
        name: 'Deployment Strategy',
        description: 'Choose deployment approach',
        action: 'Design blue-green or canary',
      },
      {
        name: 'Rollback Plan',
        description: 'Create rollback procedures',
        action: 'Implement automated rollback',
      },
      {
        name: 'Release Process',
        description: 'Document release workflow',
        action: 'Create release checklist',
      },
      {
        name: 'Changelog',
        description: 'Generate release notes',
        action: 'Automate changelog generation',
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
