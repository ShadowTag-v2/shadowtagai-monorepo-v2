/**
 * Deployment Wizard Agent
 * Sets up CI/CD pipelines and deployment automation
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

export class DeploymentWizardAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "deployment-wizard",
    name: "Deployment Wizard",
    category: "operations",
    description:
      "Sets up CI/CD that actually works. Push to main, deploy to production. No more manual steps.",
    tagline: "CI/CD and deployment automation",
    capabilities: ["implementation", "automation"],
    tags: ["ci-cd", "deployment", "github-actions", "docker", "automation"],
    difficulty: "intermediate",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Deployment Wizard specializing in CI/CD pipelines and deployment automation.

Your expertise:
1. CI/CD pipeline design (GitHub Actions, GitLab CI, CircleCI)
2. Docker and containerization
3. Deployment strategies (blue-green, canary, rolling)
4. Environment management (dev, staging, production)
5. Secrets and configuration management

Pipeline best practices:
- Automated testing before deployment
- Build once, deploy many
- Immutable deployments
- Rollback capability
- Deployment notifications
- Environment parity

Make deployments boring and reliable.`,
  };

  tools: AgentTools = {
    required: ["Read", "Write", "Bash"],
    optional: ["Glob", "WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Pipeline Design",
        description: "Design CI/CD pipeline",
        action: "Define stages: test, build, deploy",
      },
      {
        name: "CI Setup",
        description: "Configure continuous integration",
        action: "Set up GitHub Actions/GitLab CI",
      },
      {
        name: "Containerization",
        description: "Create Docker configuration",
        action: "Write Dockerfile and docker-compose",
      },
      {
        name: "CD Setup",
        description: "Configure deployment",
        action: "Set up automated deployments",
      },
      {
        name: "Validation",
        description: "Test pipeline end-to-end",
        action: "Verify deployment automation",
      },
    ],
  };

  protected async executeStep(
    step: AgentWorkflow["steps"][0],
    context: AgentExecutionContext,
    result: AgentResult,
  ): Promise<void> {
    result.recommendations?.push(`Execute: ${step.description}`);
  }
}
