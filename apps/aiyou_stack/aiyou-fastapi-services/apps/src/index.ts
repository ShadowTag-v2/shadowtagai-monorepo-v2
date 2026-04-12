/**
 * AI Agent SDK for FastAPI Services
 *
 * Main exports for the agent system
 */

// Agents
export { SystemArchitect, systemArchitect } from './agents/system-architect';

// Tools
export { architectureMcpServer } from './tools/architecture-tools';

// Configuration
export { SYSTEM_PROMPTS } from './config/system-prompts';
export { getAgentConfig, DEFAULT_AGENT_CONFIG } from './config/agent-config';
export type { AgentConfig } from './config/agent-config';
 * Claude Code Agents - Main Entry Point
 * Comprehensive agent system for development workflows
 */

// Export types
export * from './types/agent.types';
export * from './types/pnkln.types';

// Export base agent
export { BaseAgent } from './utils/base-agent';

// Export all agent categories
export * as ProductStrategy from './agents/product-strategy';
export * as Development from './agents/development';
export * as DesignUX from './agents/design-ux';
export * as QualityTesting from './agents/quality-testing';
export * as Operations from './agents/operations';
export * as BusinessAnalytics from './agents/business-analytics';
export * as AIInnovation from './agents/ai-innovation';
export * as PNKLNStack from './agents/pnkln-stack';

// Export registry
export { AgentRegistry, agentRegistry } from './agents/registry';

// Export configuration
export { AgentConfig } from './config/agent-config';

// Export PNKLN frameworks
export { masterPromptFramework } from './prompts/frameworks/master-prompt-framework';

/**
 * Get an agent by ID
 * @example
 * const agent = getAgent('product-strategist');
 * const result = await agent.execute({ projectPath: '/path/to/project', userQuery: 'Analyze my features' });
 */
export function getAgent(id: string) {
  return agentRegistry.getAgent(id);
}

/**
 * Search for agents by query
 * @example
 * const agents = searchAgents('performance');
 */
export function searchAgents(query: string) {
  return agentRegistry.searchAgents(query);
}

/**
 * Get all agents in a category
 * @example
 * const agents = getAgentsByCategory('development');
 */
export function getAgentsByCategory(category: string) {
  return agentRegistry.getAgentsByCategory(category as any);
}

/**
 * Get all available agents
 */
export function getAllAgents() {
  return agentRegistry.getAllAgents();
}

/**
 * Get agent statistics
 */
export function getAgentStats() {
  return {
    totalAgents: agentRegistry.getAgentCount(),
    totalCategories: agentRegistry.getCategoryCount(),
    categories: agentRegistry.listCategories(),
  };
}
