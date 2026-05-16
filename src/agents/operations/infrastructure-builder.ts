/**
 * Infrastructure Builder Agent
 * Designs and implements cloud infrastructure
 */

import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class InfrastructureBuilderAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "infrastructure-builder",
    name: "Infrastructure Builder",
    category: "operations",
    description:
      "Designs cloud architecture that scales and doesn't bankrupt you. Terraform included.",
    tagline: "Cloud infrastructure and IaC",
    capabilities: ["implementation", "design"],
    tags: ["infrastructure", "terraform", "aws", "gcp", "azure", "iac"],
    difficulty: "expert",
    estimatedTime: "4-8 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are an Infrastructure Builder Expert specializing in cloud architecture and Infrastructure as Code.

Your expertise:
1. Cloud platform architecture (AWS, GCP, Azure)
2. Infrastructure as Code (Terraform, CloudFormation, Pulumi)
3. Network design and security
4. Scalability and high availability
5. Cost optimization

Infrastructure principles:
- Immutable infrastructure
- Everything as code (version controlled)
- Security by default (least privilege, encryption)
- Scalability (horizontal > vertical)
- Fault tolerance and redundancy
- Cost optimization (right-sizing, reserved instances)

Build infrastructure that's reliable, secure, and cost-effective.`,
  };

  tools: AgentTools = {
    required: ["Read", "Write", "Glob"],
    optional: ["Bash", "WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Architecture Design",
        description: "Design cloud architecture",
        action: "Define services, networking, security",
      },
      {
        name: "Terraform Setup",
        description: "Create Terraform configuration",
        action: "Write IaC for infrastructure",
      },
      {
        name: "Security",
        description: "Implement security best practices",
        action: "Configure IAM, VPC, encryption",
      },
      {
        name: "Scalability",
        description: "Add auto-scaling and load balancing",
        action: "Configure ASG, ALB, etc.",
      },
      {
        name: "Cost Optimization",
        description: "Optimize for cost",
        action: "Right-size resources, use spot instances",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    _context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
