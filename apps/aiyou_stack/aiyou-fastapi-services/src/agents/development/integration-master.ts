/**
 * Integration Master Agent
 * Connects applications to external services
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

export class IntegrationMasterAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "integration-master",
    name: "Integration Master",
    category: "development",
    description:
      "Connects your app to any service. Handles auth flows, webhooks, and retries like magic.",
    tagline: "Third-party integrations and API connections",
    capabilities: ["implementation", "automation"],
    tags: ["integrations", "apis", "webhooks", "oauth", "sdks"],
    difficulty: "intermediate",
    estimatedTime: "2-3 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are an Integration Master specializing in connecting applications to external services.

Your expertise:
1. Third-party API integration (Stripe, Twilio, SendGrid, etc.)
2. OAuth flows and authentication
3. Webhook handling and verification
4. Retry logic and error handling
5. SDK wrapper creation

Best practices:
- Robust error handling and retries (exponential backoff)
- Webhook signature verification
- Rate limit handling
- Idempotency for critical operations
- Secure credential management (env vars, secrets)
- Type-safe API clients

Make integrations reliable and maintainable.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Write", "Edit"],
    optional: ["WebFetch", "Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Integration Planning",
        description: "Define integration requirements",
        action: "Identify APIs, auth, webhooks needed",
      },
      {
        name: "Authentication",
        description: "Implement OAuth or API key auth",
        action: "Set up auth flows and credential storage",
      },
      {
        name: "API Client",
        description: "Build type-safe API client",
        action: "Create SDK wrapper with error handling",
      },
      {
        name: "Webhooks",
        description: "Implement webhook handlers",
        action: "Add webhook endpoints with verification",
      },
      {
        name: "Testing",
        description: "Test integration with mocks",
        action: "Create integration tests",
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
