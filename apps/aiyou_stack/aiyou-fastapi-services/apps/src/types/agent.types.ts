/**
 * Agent SDK Types and Interfaces
 * Comprehensive type definitions for Claude Code Agents
 */

export type AgentCategory =
  | 'product-strategy'
  | 'development'
  | 'design-ux'
  | 'quality-testing'
  | 'operations'
  | 'business-analytics'
  | 'ai-innovation'
  | 'pnkln-stack';

export type AgentCapability =
  | 'analysis'
  | 'implementation'
  | 'optimization'
  | 'testing'
  | 'monitoring'
  | 'automation'
  | 'design'
  | 'strategy';

export interface AgentMetadata {
  id: string;
  name: string;
  category: AgentCategory;
  description: string;
  tagline: string;
  capabilities: AgentCapability[];
  tags: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  estimatedTime?: string;
  dependencies?: string[];
}

export interface AgentPromptTemplate {
  system: string;
  userPromptPrefix?: string;
  context?: string[];
  examples?: {
    input: string;
    output: string;
  }[];
}

export interface AgentTools {
  required: string[];
  optional: string[];
}

export interface AgentWorkflow {
  steps: {
    name: string;
    description: string;
    action: string;
    validation?: string;
  }[];
}

export interface Agent {
  metadata: AgentMetadata;
  prompt: AgentPromptTemplate;
  tools: AgentTools;
  workflow: AgentWorkflow;
  execute: (context: AgentExecutionContext) => Promise<AgentResult>;
}

export interface AgentExecutionContext {
  projectPath: string;
  userQuery: string;
  additionalContext?: Record<string, any>;
  constraints?: {
    maxTokens?: number;
    timeoutMs?: number;
    dryRun?: boolean;
  };
}

export interface AgentResult {
  success: boolean;
  output: string;
  artifacts?: {
    filesCreated?: string[];
    filesModified?: string[];
    filesDeleted?: string[];
  };
  metrics?: {
    executionTimeMs: number;
    tokensUsed?: number;
    stepsCompleted: number;
  };
  errors?: Array<{
    code: string;
    message: string;
    details?: unknown;
  }>;
  recommendations?: string[];
}

export interface AgentRegistry {
  agents: Map<string, Agent>;
  categories: Map<AgentCategory, Agent[]>;
  getAgent: (id: string) => Agent | undefined;
  getAgentsByCategory: (category: AgentCategory) => Agent[];
  searchAgents: (query: string) => Agent[];
  registerAgent: (agent: Agent) => void;
}

export interface AgentConfig {
  enabledCategories: AgentCategory[];
  defaultConstraints: {
    maxTokens: number;
    timeoutMs: number;
  };
  customPrompts?: Record<string, string>;
  featureFlags?: Record<string, boolean>;
}
