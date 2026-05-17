/**
 * Express API Server for Vertex AI Workbench Agents
 * Complete collection of 51 specialized AI agents
 */

import cors from "cors";
import dotenv from "dotenv";
import express, { type NextFunction, type Request, type Response } from "express";
import { z } from "zod";
import { AgentCategory } from "./agents/base";
import { AgentRegistry } from "./agents/registry";

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const port = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Request validation schemas
const AgentTaskRequestSchema = z.object({
  task: z.string().min(1, "Task description is required"),
  context: z.record(z.any()).optional(),
});

// Response types
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    error: err.message || "Internal server error",
  });
});

/**
 * Root endpoint
 */
app.get("/", (req: Request, res: Response) => {
  res.json({
    name: "Vertex AI Workbench Agents API",
    version: "1.0.0",
    description: "51 specialized AI agents for development, ML operations, and prompt engineering",
    total_agents: AgentRegistry.getAgentCount(),
    endpoints: {
      agents: "/agents",
      categories: "/categories",
      stats: "/stats",
      search: "/agents/search?q=<query>",
      execute: "/agents/:agentId/execute",
      docs: "/docs",
    },
  });
});

/**
 * Health check endpoint
 */
app.get("/health", (req: Request, res: Response) => {
  res.json({ status: "healthy", timestamp: new Date().toISOString() });
});

/**
 * Get all agents
 */
app.get("/agents", (req: Request, res: Response) => {
  try {
    const agentsWithIds = AgentRegistry.getAllAgentsWithIds();
    const response = agentsWithIds.map(({ id, agent }) => ({
      id,
      ...agent.toDict(),
    }));

    res.json({ success: true, data: response });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Get specific agent
 */
app.get("/agents/:agentId", (req: Request, res: Response) => {
  try {
    const { agentId } = req.params;
    const result = AgentRegistry.getAgentWithId(agentId);

    if (!result) {
      return res.status(404).json({
        success: false,
        error: `Agent '${agentId}' not found`,
      });
    }

    res.json({
      success: true,
      data: {
        id: result.id,
        ...result.agent.toDict(),
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Execute agent task
 */
app.post("/agents/:agentId/execute", async (req: Request, res: Response) => {
  try {
    const { agentId } = req.params;
    const agent = AgentRegistry.getAgent(agentId);

    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `Agent '${agentId}' not found`,
      });
    }

    // Validate request body
    const validation = AgentTaskRequestSchema.safeParse(req.body);
    if (!validation.success) {
      return res.status(400).json({
        success: false,
        error: validation.error.errors[0].message,
      });
    }

    const { task, context } = validation.data;
    const result = await agent.execute(task, context);

    res.json({
      success: true,
      data: result,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Get agent system prompt
 */
app.get("/agents/:agentId/prompt", (req: Request, res: Response) => {
  try {
    const { agentId } = req.params;
    const agent = AgentRegistry.getAgent(agentId);

    if (!agent) {
      return res.status(404).json({
        success: false,
        error: `Agent '${agentId}' not found`,
      });
    }

    res.json({
      success: true,
      data: {
        agent: agent.metadata.name,
        prompt: agent.getSystemPrompt(),
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Get agents by category
 */
app.get("/agents/category/:category", (req: Request, res: Response) => {
  try {
    const { category } = req.params;

    // Find matching category
    const categoryKey = Object.keys(AgentCategory).find(
      (key) =>
        AgentCategory[key as keyof typeof AgentCategory].toLowerCase().replace(/\s+/g, "-") ===
        category.toLowerCase().replace(/\s+/g, "-"),
    );

    if (!categoryKey) {
      return res.status(404).json({
        success: false,
        error: `Category '${category}' not found. Available: ${AgentRegistry.getCategories().join(
          ", ",
        )}`,
      });
    }

    const agentCategory = AgentCategory[categoryKey as keyof typeof AgentCategory];
    const agents = AgentRegistry.getAgentsByCategory(agentCategory);

    // Get IDs for these agents
    const response = agents.map((agent) => {
      const entry = AgentRegistry.getAllAgentsWithIds().find(
        ({ agent: a }) => a.metadata.name === agent.metadata.name,
      );
      return {
        id: entry?.id,
        ...agent.toDict(),
      };
    });

    res.json({ success: true, data: response });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Get all categories
 */
app.get("/categories", (req: Request, res: Response) => {
  try {
    const categories = AgentRegistry.getCategories();
    res.json({
      success: true,
      data: {
        categories,
        count: categories.length,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Search agents
 */
app.get("/agents/search", (req: Request, res: Response) => {
  try {
    const query = req.query.q as string;

    if (!query) {
      return res.status(400).json({
        success: false,
        error: "Search query parameter 'q' is required",
      });
    }

    const agents = AgentRegistry.searchAgents(query);

    // Get IDs for matching agents
    const response = agents.map((agent) => {
      const entry = AgentRegistry.getAllAgentsWithIds().find(
        ({ agent: a }) => a.metadata.name === agent.metadata.name,
      );
      return {
        id: entry?.id,
        ...agent.toDict(),
      };
    });

    res.json({ success: true, data: response });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Get statistics
 */
app.get("/stats", (req: Request, res: Response) => {
  try {
    const stats = AgentRegistry.getStats();
    res.json({ success: true, data: stats });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * Get agents grouped by category
 */
app.get("/agents/grouped", (req: Request, res: Response) => {
  try {
    const grouped: Record<string, any[]> = {};

    for (const category of Object.values(AgentCategory)) {
      const agents = AgentRegistry.getAgentsByCategory(category);

      if (agents.length > 0) {
        grouped[category] = agents.map((agent) => {
          const entry = AgentRegistry.getAllAgentsWithIds().find(
            ({ agent: a }) => a.metadata.name === agent.metadata.name,
          );
          return {
            id: entry?.id,
            ...agent.toDict(),
          };
        });
      }
    }

    res.json({
      success: true,
      data: {
        total: AgentRegistry.getAgentCount(),
        categories: Object.keys(grouped).length,
        agents: grouped,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    });
  }
});

/**
 * API documentation endpoint
 */
app.get("/docs", (req: Request, res: Response) => {
  res.json({
    title: "Vertex AI Workbench Agents API",
    version: "1.0.0",
    description:
      "Complete collection of 46 specialized AI agents for software development and ML operations",
    endpoints: {
      GET: {
        "/": "API information",
        "/health": "Health check",
        "/agents": "List all agents",
        "/agents/:agentId": "Get specific agent",
        "/agents/:agentId/prompt": "Get agent system prompt",
        "/agents/category/:category": "Get agents by category",
        "/agents/grouped": "Get agents grouped by category",
        "/categories": "List all categories",
        "/agents/search?q=query": "Search agents",
        "/stats": "Get agent statistics",
      },
      POST: {
        "/agents/:agentId/execute": "Execute agent task",
      },
    },
  });
});

// Start server
app.listen(port, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║   Vertex AI Workbench Agents API                          ║
║                                                            ║
║   🚀 Server running on http://localhost:${port}           ║
║   📊 Total Agents: ${AgentRegistry.getAgentCount()}                                      ║
║   📚 Docs: http://localhost:${port}/docs                  ║
║                                                            ║
║   Categories:                                              ║
║   - Product Strategy (5)                                   ║
║   - Development (8)                                        ║
║   - Design & UX (4)                                        ║
║   - Quality & Testing (4)                                  ║
║   - Operations (5)                                         ║
║   - Business & Analytics (7)                               ║
║   - AI & Innovation (3)                                    ║
║   - Vertex AI (10)                                         ║
╚════════════════════════════════════════════════════════════╝
  `);
});

export default app;
