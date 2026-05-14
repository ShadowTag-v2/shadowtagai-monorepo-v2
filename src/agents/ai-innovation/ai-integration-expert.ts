import type {
  AgentExecutionContext,
  AgentMetadata,
  AgentPromptTemplate,
  AgentResult,
  AgentTools,
  AgentWorkflow,
} from "../../types/agent.types";
import { BaseAgent } from "../../utils/base-agent";

export class AIIntegrationExpertAgent extends BaseAgent {
  metadata: AgentMetadata = {
    id: "ai-integration-expert",
    name: "AI Integration Expert",
    category: "ai-innovation",
    description:
      "Adds ChatGPT-like features to your app. Handles prompts, streaming, embeddings, the works.",
    tagline: "AI and LLM integration",
    capabilities: ["implementation"],
    tags: ["ai", "llm", "openai", "embeddings", "chatgpt", "anthropic"],
    difficulty: "advanced",
    estimatedTime: "3-6 hours",
  };
  prompt: AgentPromptTemplate = {
    system: `You are an AI Integration Expert specializing in LLM integration. Implement OpenAI, Anthropic Claude, streaming responses, embeddings, RAG patterns, prompt engineering.`,
  };
  tools: AgentTools = { required: ["Read", "Write", "Edit"], optional: ["Bash", "WebFetch"] };
  workflow: AgentWorkflow = {
    steps: [
      {
        name: "AI Setup",
        description: "Set up AI API integration",
        action: "Integrate OpenAI or Anthropic",
      },
      {
        name: "Prompt Engineering",
        description: "Design effective prompts",
        action: "Create prompt templates",
      },
      {
        name: "Streaming",
        description: "Implement streaming responses",
        action: "Add real-time streaming UI",
      },
      {
        name: "Embeddings",
        description: "Add embeddings and RAG",
        action: "Implement vector search",
      },
      { name: "Safety", description: "Add content moderation", action: "Implement safety filters" },
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
