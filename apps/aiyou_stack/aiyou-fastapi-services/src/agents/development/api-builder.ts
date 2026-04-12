/**
 * API Builder Agent
 * Creates beautiful, well-documented APIs
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

export class APIBuilderAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "api-builder",
    name: "API Builder",
    category: "development",
    description:
      "Creates beautiful APIs that developers actually want to use. Includes auth, rate limiting, docs.",
    tagline: "RESTful and GraphQL API development",
    capabilities: ["implementation", "design"],
    tags: ["api", "rest", "graphql", "openapi", "documentation", "auth"],
    difficulty: "intermediate",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are an API Builder Expert specializing in API design, implementation, and developer experience.

Your expertise:
1. RESTful API design (resources, verbs, status codes)
2. GraphQL schema and resolver design
3. API authentication (JWT, OAuth, API keys)
4. Rate limiting and throttling
5. API documentation (OpenAPI/Swagger)
6. Versioning strategies

Best practices:
- Consistent naming and resource structures
- Proper HTTP status codes and error responses
- Pagination, filtering, and sorting
- HATEOAS and discoverability
- Comprehensive documentation
- Security (auth, validation, sanitization)

Build APIs that are intuitive, secure, and well-documented.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Write", "Edit"],
    optional: ["WebFetch", "Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "API Design",
        description: "Design API resources, endpoints, and schemas",
        action: "Create OpenAPI spec and data models",
      },
      {
        name: "Authentication",
        description: "Implement auth mechanisms",
        action: "Add JWT/OAuth, middleware, guards",
      },
      {
        name: "Endpoints",
        description: "Build CRUD endpoints with validation",
        action: "Implement controllers, services, validation",
      },
      {
        name: "Rate Limiting",
        description: "Add rate limiting and throttling",
        action: "Implement rate limiters",
      },
      {
        name: "Documentation",
        description: "Generate API documentation",
        action: "Create OpenAPI/Swagger docs",
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
