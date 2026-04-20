/**
 * GraphQL Expert Agent
 * Designs and implements GraphQL APIs
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

export class GraphQLExpertAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: 'graphql-expert',
    name: 'GraphQL Expert',
    category: 'development',
    description:
      'Builds type-safe GraphQL APIs with optimal resolver patterns and federation support.',
    tagline: 'GraphQL schema design and implementation',
    capabilities: ['implementation', 'design'],
    tags: ['graphql', 'api', 'schema', 'resolvers', 'apollo', 'federation'],
    difficulty: 'advanced',
    estimatedTime: '3-5 hours',
  };

  prompt: AgentPromptTemplate = {
    system: `You are a GraphQL Expert specializing in schema design, resolvers, and performance optimization.

Your expertise:
1. GraphQL schema design and best practices
2. Resolver implementation and data loaders
3. N+1 query problem solutions
4. GraphQL federation and schema stitching
5. Subscriptions and real-time data
6. Authorization and authentication

Best practices:
- Type-safe schema design
- DataLoader for batching and caching
- Pagination (cursor-based)
- Error handling and field-level errors
- Query complexity analysis and depth limiting
- Fragment patterns for code reuse

Build GraphQL APIs that are fast, type-safe, and developer-friendly.`,
  };

  tools: AgentTools = {
    required: ['Glob', 'Read', 'Write', 'Edit'],
    optional: ['Bash', 'WebFetch'],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: 'Schema Design',
        description: 'Design GraphQL schema and types',
        action: 'Define types, queries, mutations, subscriptions',
      },
      {
        name: 'Resolvers',
        description: 'Implement resolvers with DataLoaders',
        action: 'Build efficient resolvers with batching',
      },
      {
        name: 'Authentication',
        description: 'Add auth to schema',
        action: 'Implement field-level authorization',
      },
      {
        name: 'Optimization',
        description: 'Optimize for performance',
        action: 'Add query complexity limits, persisted queries',
      },
      {
        name: 'Documentation',
        description: 'Generate GraphQL documentation',
        action: 'Create schema docs and playground',
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
