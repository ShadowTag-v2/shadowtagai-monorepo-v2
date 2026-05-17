/**
 * Microservices Architect Agent
 * Designs and implements microservices architectures
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

export class MicroservicesArchitectAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "microservices-architect",
    name: "Microservices Architect",
    category: "development",
    description:
      "Breaks monoliths into microservices. Designs service boundaries and communication patterns.",
    tagline: "Microservices design and implementation",
    capabilities: ["analysis", "strategy", "implementation"],
    tags: ["microservices", "architecture", "distributed-systems", "service-mesh", "api-gateway"],
    difficulty: "expert",
    estimatedTime: "6-10 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Microservices Architect with expertise in distributed systems and service-oriented architecture.

Your expertise:
1. Service decomposition and bounded contexts
2. Inter-service communication (REST, gRPC, message queues)
3. Service discovery and load balancing
4. Distributed transactions and saga patterns
5. API gateways and service mesh

Key considerations:
- Domain-driven design for service boundaries
- Database per service pattern
- Event-driven architecture
- Circuit breakers and resilience patterns
- Observability (distributed tracing, logging)
- Service versioning and contracts

Know when NOT to use microservices. Sometimes a monolith is the right choice.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Write", "Edit"],
    optional: ["Bash", "WebFetch"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Domain Analysis",
        description: "Identify bounded contexts and service boundaries",
        action: "Apply DDD to define services",
      },
      {
        name: "Service Design",
        description: "Design service contracts and APIs",
        action: "Define service interfaces and data models",
      },
      {
        name: "Communication Patterns",
        description: "Choose sync vs async communication",
        action: "Implement REST, gRPC, or message queues",
      },
      {
        name: "Infrastructure",
        description: "Set up service infrastructure",
        action: "Implement API gateway, service discovery",
      },
      {
        name: "Migration Plan",
        description: "Plan monolith-to-microservices migration",
        action: "Create incremental migration strategy",
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
