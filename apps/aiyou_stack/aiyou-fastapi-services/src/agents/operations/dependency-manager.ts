/**
 * Dependency Manager Agent
 * Manages and updates project dependencies
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

export class DependencyManagerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'dependency-manager',
    name: 'Dependency Manager',
    category: 'operations',
    description:
      'Keeps dependencies up-to-date and secure. Automates updates and vulnerability scanning.',
    tagline: 'Dependency management and security',
    capabilities: ['automation', 'analysis'],
    tags: ['dependencies', 'npm', 'security', 'updates', 'renovate', 'dependabot'],
    difficulty: 'beginner',
    estimatedTime: '1-2 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Dependency Manager specializing in keeping projects up-to-date and secure.

Your expertise:
1. Dependency auditing and vulnerability scanning
2. Automated dependency updates (Renovate, Dependabot)
3. Version pinning and lock file management
4. Upgrade strategies and testing
5. Supply chain security

Best practices:
- Regular dependency updates
- Automated vulnerability scanning
- Lock files for reproducibility
- Semantic versioning awareness
- Test before upgrading
- Separate security updates from feature updates

Keep dependencies fresh to avoid security issues and tech debt.`,
  };

  tools: AgentTools = {
    required: ['Read', 'Bash'],
    optional: ['Write', 'Edit'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Audit',
        description: 'Audit current dependencies',
        action: 'Scan for outdated and vulnerable packages',
      },
      {
        name: 'Update Strategy',
        description: 'Plan update approach',
        action: 'Prioritize security and breaking changes',
      },
      {
        name: 'Automated Updates',
        description: 'Set up auto-updates',
        action: 'Configure Renovate or Dependabot',
      },
      {
        name: 'Testing',
        description: 'Test updated dependencies',
        action: 'Run tests to verify compatibility',
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
