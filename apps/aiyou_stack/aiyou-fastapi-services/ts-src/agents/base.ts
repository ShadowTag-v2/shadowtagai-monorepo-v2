/**
 * Base Agent Class for Vertex AI Workbench Agents
 */

export enum AgentCategory {
  PRODUCT_STRATEGY = "Product Strategy",
  DEVELOPMENT = "Development",
  DESIGN_UX = "Design & UX",
  QUALITY_TESTING = "Quality & Testing",
  OPERATIONS = "Operations",
  BUSINESS_ANALYTICS = "Business & Analytics",
  AI_INNOVATION = "AI & Innovation",
  VERTEX_AI = "Vertex AI",
}

export interface AgentMetadata {
  name: string;
  description: string;
  category: AgentCategory;
  icon: string;
  version: string;
  tags: string[];
}

export interface AgentContext {
  [key: string]: unknown;
}

export interface AgentExecutionResult {
  agent: string;
  task: string;
  context: AgentContext;
  prompt: string;
  status: string;
}

export interface AgentTool {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

/**
 * Base class for all Vertex AI agents
 */
export abstract class BaseAgent {
  protected context: AgentContext = {};
  public readonly metadata: AgentMetadata;

  constructor() {
    this.metadata = this.getMetadata();
  }

  /**
   * Get agent metadata
   */
  abstract getMetadata(): AgentMetadata;

  /**
   * Execute the agent's task
   */
  abstract execute(task: string, context?: AgentContext): Promise<AgentExecutionResult>;

  /**
   * Get the system prompt for this agent
   */
  abstract getSystemPrompt(): string;

  /**
   * Get tools available to this agent
   */
  getTools(): AgentTool[] {
    return [];
  }

  /**
   * Set execution context
   */
  setContext(context: AgentContext): void {
    this.context = context;
  }

  /**
   * Convert agent to dictionary representation
   */
  toDict(): Record<string, any> {
    return {
      name: this.metadata.name,
      description: this.metadata.description,
      category: this.metadata.category,
      icon: this.metadata.icon,
      version: this.metadata.version,
      tags: this.metadata.tags,
    };
  }

  /**
   * Helper method for executing agent tasks
   */
  protected async executeTask(task: string, context?: AgentContext): Promise<AgentExecutionResult> {
    return {
      agent: this.metadata.name,
      task,
      context: context || {},
      prompt: this.getSystemPrompt(),
      status: "success",
    };
  }
}
