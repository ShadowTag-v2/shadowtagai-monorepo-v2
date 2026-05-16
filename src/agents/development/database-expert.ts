/**
 * Database Expert Agent
 * Optimizes queries and designs scalable schemas
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

export class DatabaseExpertAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "database-expert",
    name: "Database Expert",
    category: "development",
    description:
      "Fixes those queries that take 30 seconds. Designs schemas that scale to millions.",
    tagline: "Database optimization and schema design",
    capabilities: ["analysis", "optimization", "implementation"],
    tags: ["database", "sql", "nosql", "optimization", "indexing", "migrations"],
    difficulty: "advanced",
    estimatedTime: "2-4 hours",
  };

  prompt: AgentPromptTemplate = {
    system: `You are a Database Expert with deep knowledge of SQL, NoSQL, and database optimization.

Your expertise:
1. Schema design and normalization
2. Query optimization and indexing strategies
3. Migration planning and execution
4. Database scaling (replication, sharding, partitioning)
5. Performance tuning and profiling

Focus areas:
- Index optimization (B-tree, hash, composite)
- Query plan analysis and optimization
- N+1 query elimination
- Caching strategies (Redis, in-memory)
- Transaction management and isolation levels
- Data modeling for both SQL and NoSQL

Turn 30-second queries into 30-millisecond queries.`,
  };

  tools: AgentTools = {
    required: ["Glob", "Read", "Grep", "Write", "Edit"],
    optional: ["Bash"],
  };

  workflow: AgentWorkflow = {
    steps: [
      {
        name: "Schema Analysis",
        description: "Review database schema and relationships",
        action: "Analyze tables, indexes, constraints",
      },
      {
        name: "Query Profiling",
        description: "Identify slow queries",
        action: "Profile queries and analyze execution plans",
      },
      {
        name: "Optimization",
        description: "Optimize queries and add indexes",
        action: "Rewrite queries, add indexes, eliminate N+1",
      },
      {
        name: "Schema Improvements",
        description: "Improve schema design",
        action: "Normalize/denormalize, add constraints",
      },
      {
        name: "Migration",
        description: "Create database migrations",
        action: "Generate safe migration scripts",
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
