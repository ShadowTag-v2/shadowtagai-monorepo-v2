/**
 * Agent configuration settings
 */

export interface AgentConfig {
  apiKey?: string;
  maxTokens?: number;
  temperature?: number;
  model?: string;
}

export const DEFAULT_AGENT_CONFIG: AgentConfig = {
  apiKey: process.env.GEMINI_API_KEY,
  maxTokens: 8192,
  temperature: 0.7,
  model: 'gemini-1.5-pro',
};

export function getAgentConfig(overrides?: Partial<AgentConfig>): AgentConfig {
  return {
    ...DEFAULT_AGENT_CONFIG,
    ...overrides,
  };
}
 * Agent Configuration
 * Global configuration for agent behavior and constraints
 */

import type { AgentConfig as IAgentConfig, AgentCategory } from '../types/agent.types';

export class AgentConfig implements IAgentConfig {
  enabledCategories: AgentCategory[] = [
    'product-strategy',
    'development',
    'design-ux',
    'quality-testing',
    'operations',
    'business-analytics',
    'ai-innovation',
  ];

  defaultConstraints = {
    maxTokens: 100000,
    timeoutMs: 300000, // 5 minutes
  };

  customPrompts: Record<string, string> = {};

  featureFlags: Record<string, boolean> = {
    enableParallelExecution: true,
    enableCaching: true,
    enableTelemetry: false,
    enableDebugMode: false,
  };

  constructor(overrides?: Partial<IAgentConfig>) {
    if (overrides) {
      Object.assign(this, overrides);
    }
  }

  /**
   * Enable specific categories
   */
  enableCategories(categories: AgentCategory[]): void {
    this.enabledCategories = categories;
  }

  /**
   * Set custom prompt for an agent
   */
  setCustomPrompt(agentId: string, prompt: string): void {
    this.customPrompts[agentId] = prompt;
  }

  /**
   * Set feature flag
   */
  setFeatureFlag(flag: string, enabled: boolean): void {
    this.featureFlags[flag] = enabled;
  }

  /**
   * Update default constraints
   */
  updateConstraints(constraints: Partial<typeof this.defaultConstraints>): void {
    Object.assign(this.defaultConstraints, constraints);
  }
}

// Export default configuration
export const defaultConfig = new AgentConfig();
