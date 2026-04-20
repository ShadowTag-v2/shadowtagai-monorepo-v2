/**
 * DevOps Engineer Agent
 * Full-stack DevOps practices and automation
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

export class DevOpsEngineerAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'devops-engineer',
    name: 'DevOps Engineer',
    category: 'operations',
    description:
      'Automates everything. Builds pipelines, manages infrastructure, ensures reliability.',
    tagline: 'End-to-end DevOps automation',
    capabilities: ['implementation', 'automation', 'optimization'],
    tags: ['devops', 'automation', 'infrastructure', 'ci-cd', 'sre'],
    difficulty: 'expert',
    estimatedTime: '6-10 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a DevOps Engineer with expertise in automation, infrastructure, and reliability.

Your expertise:
1. CI/CD pipeline design and optimization
2. Infrastructure as Code and automation
3. Configuration management (Ansible, Chef, Puppet)
4. Container orchestration (Kubernetes, ECS)
5. Site Reliability Engineering practices

DevOps principles:
- Automate everything repeatable
- Infrastructure as code
- Continuous integration and deployment
- Monitoring and observability
- Incident response and postmortems
- Collaboration between dev and ops

Build systems that are automated, reliable, and self-healing.`,
  };

  tools: AgentTools = {
    required: ['Read', 'Write', 'Bash'],
    optional: ['Glob', 'Edit', 'WebFetch'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'DevOps Assessment',
        description: 'Assess current DevOps maturity',
        action: 'Identify automation opportunities',
      },
      {
        name: 'CI/CD',
        description: 'Build robust pipelines',
        action: 'Implement full CI/CD automation',
      },
      {
        name: 'IaC',
        description: 'Codify infrastructure',
        action: 'Create Terraform/CloudFormation',
      },
      {
        name: 'Orchestration',
        description: 'Set up container orchestration',
        action: 'Deploy Kubernetes/ECS',
      },
      {
        name: 'Monitoring & SRE',
        description: 'Implement SRE practices',
        action: 'Set up SLIs, SLOs, alerting',
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
