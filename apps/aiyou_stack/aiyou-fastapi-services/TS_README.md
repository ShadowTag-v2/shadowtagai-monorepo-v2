# TypeScript Implementation

This directory contains the TypeScript/Node.js implementation of the Vertex AI Workbench Agents.

## Structure

```
ts-src/
├── agents/
│   ├── base.ts                    # Base agent class
│   ├── productStrategy.ts         # 5 Product Strategy agents
│   ├── development.ts             # 8 Development agents
│   ├── designUX.ts                # 4 Design & UX agents
│   ├── qualityTesting.ts          # 4 Quality & Testing agents
│   ├── operations.ts              # 5 Operations agents
│   ├── businessAnalytics.ts       # 7 Business & Analytics agents
│   ├── aiInnovation.ts            # 3 AI & Innovation agents
│   ├── vertexAI.ts                # 10 Vertex AI agents
│   ├── registry.ts                # Agent registry
│   └── index.ts                   # Exports
├── server.ts                      # Express API server
└── index.ts                       # Main entry point
```

## Quick Start

### Install Dependencies

```bash
npm install
```

### Development

```bash
npm run dev
```

The server will start at <http://localhost:8000>

### Build

```bash
npm run build
```

### Production

```bash
npm start
```

## API Endpoints

All endpoints match the Python FastAPI implementation:

- `GET /` - API information
- `GET /health` - Health check
- `GET /agents` - List all 46 agents
- `GET /agents/:agentId` - Get specific agent
- `POST /agents/:agentId/execute` - Execute agent task
- `GET /agents/:agentId/prompt` - Get agent system prompt
- `GET /agents/category/:category` - Get agents by category
- `GET /agents/grouped` - Get agents grouped by category
- `GET /categories` - List all categories
- `GET /agents/search?q=query` - Search agents
- `GET /stats` - Get agent statistics

## Usage Example

```typescript
import { AgentRegistry } from "./ts-src/agents/registry";

// Get an agent
const agent = AgentRegistry.getAgent("performance_engineer");

// Execute a task
const result = await agent.execute("Optimize my database queries", {
  database: "PostgreSQL",
  queries: [...],
});

console.log(result.prompt);
```

## API Client Example

```typescript
import axios from "axios";

// Execute a task via API
const response = await axios.post(
  "http://localhost:8000/agents/database_expert/execute",
  {
    task: "Optimize slow queries",
    context: {
      database: "PostgreSQL",
      issue: "Slow user table queries",
    },
  }
);

console.log(response.data);
```

## Integration with Claude Agent SDK

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { AgentRegistry } from "./ts-src/agents/registry";

const agent = AgentRegistry.getAgent("system_architect");

const result = await query({
  prompt: "Design a microservices architecture for my app",
  options: {
    systemPrompt: agent.getSystemPrompt(),
  },
});
```

## All 46 Agents

The TypeScript implementation includes all 46 agents:

**Product Strategy (5)**

- product_strategist, growth_engineer, user_researcher, revenue_optimizer, market_analyst

**Development (8)**

- system_architect, code_refactorer, api_builder, database_expert, integration_master, mobile_optimizer, performance_engineer, accessibility_pro

**Design & UX (4)**

- ux_optimizer, ui_polisher, content_writer, design_system_builder

**Quality & Testing (4)**

- test_generator, security_scanner, code_reviewer, load_tester

**Operations (5)**

- deployment_wizard, infrastructure_builder, monitoring_expert, release_manager, cost_optimizer

**Business & Analytics (7)**

- analytics_engineer, email_automator, support_builder, compliance_expert, seo_master, community_features, landing_page_optimizer

**AI & Innovation (3)**

- ai_integration_expert, automation_builder, innovation_lab

**Vertex AI (10)**

- vertex_model_deployer, notebook_optimizer, bigquery_integration, automl_builder, feature_store_manager, ml_pipeline_engineer, model_monitoring, vertex_endpoints_manager, training_job_optimizer, hyperparameter_tuner

## Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Start production server
- `npm test` - Run tests
- `npm run lint` - Lint code
- `npm run format` - Format code with Prettier

## Environment Variables

Create a `.env` file:

```env
PORT=8000
NODE_ENV=development
ANTHROPIC_API_KEY=your-api-key
```

## Type Safety

All agents are fully typed with TypeScript interfaces:

```typescript
interface AgentMetadata {
  name: string;
  description: string;
  category: AgentCategory;
  icon: string;
  version: string;
  tags: string[];
}

interface AgentExecutionResult {
  agent: string;
  task: string;
  context: AgentContext;
  prompt: string;
  status: string;
}
```

## Deployment

### Docker

```bash
docker build -t vertex-ai-agents-ts .
docker run -p 8000:8000 vertex-ai-agents-ts
```

### Node.js

```bash
npm run build
npm start
```

## Testing

```bash
# Run tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

## Contributing

The TypeScript implementation mirrors the Python implementation exactly. When adding new agents:

1. Add the agent class to the appropriate category file
2. Export it from that file
3. Register it in `registry.ts`
4. Update this README

## License

MIT
