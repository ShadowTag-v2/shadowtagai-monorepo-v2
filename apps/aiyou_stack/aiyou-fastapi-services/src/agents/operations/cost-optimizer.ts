/**
 * Cost Optimizer Agent
 * Reduces cloud costs and optimizes spending
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

export class CostOptimizerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'cost-optimizer',
    name: 'Cost Optimizer',
    category: 'operations',
    description:
      'Cuts your AWS bill by 50%. Finds waste, right-sizes everything, implements auto-scaling.',
    tagline: 'Cloud cost optimization and FinOps',
    capabilities: ['analysis', 'optimization'],
    tags: ['cost-optimization', 'finops', 'aws', 'cloud-costs', 'savings'],
    difficulty: 'intermediate',
    estimatedTime: '2-3 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Cost Optimizer specializing in cloud cost reduction and FinOps.

Your expertise:
1. Cloud cost analysis and waste identification
2. Right-sizing resources (compute, storage, databases)
3. Reserved instances and savings plans
4. Auto-scaling and cost-aware architectures
5. Cost allocation and tagging strategies

Cost optimization tactics:
- Identify unused resources (orphaned volumes, old snapshots)
- Right-size over-provisioned instances
- Use spot instances for non-critical workloads
- Implement auto-scaling (scale down during off-hours)
- Reserved instances for predictable workloads
- S3 lifecycle policies and intelligent tiering
- CDN and caching to reduce data transfer

Every dollar saved is profit. Optimize ruthlessly.`,
  };

  tools: AgentTools = {
    required: ['Read', 'Bash'],
    optional: ['Write', 'WebFetch'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Cost Analysis',
        description: 'Analyze current spending',
        action: 'Identify top cost drivers',
      },
      {
        name: 'Waste Detection',
        description: 'Find unused resources',
        action: 'Identify idle resources to terminate',
      },
      {
        name: 'Right-Sizing',
        description: 'Optimize resource sizing',
        action: 'Recommend instance downsizing',
      },
      {
        name: 'Auto-Scaling',
        description: 'Implement cost-aware scaling',
        action: 'Add auto-scaling policies',
      },
      {
        name: 'Savings Plans',
        description: 'Recommend commitments',
        action: 'Analyze RI and savings plan opportunities',
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
