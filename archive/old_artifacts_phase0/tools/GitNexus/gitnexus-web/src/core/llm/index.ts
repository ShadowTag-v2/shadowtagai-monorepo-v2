/**
 * LLM Module Exports
 *
 * Provides Graph RAG agent capabilities for code analysis.
 */

// Agent
export {
  type AgentMessage,
  BASE_SYSTEM_PROMPT,
  createChatModel,
  createGraphRAGAgent,
  invokeAgent,
  streamAgentResponse,
} from './agent';
// Context Builder
export {
  buildCodebaseContext,
  buildDynamicSystemPrompt,
  type CodebaseContext,
  type CodebaseStats,
  formatContextForPrompt,
  type Hotspot,
} from './context-builder';
// Settings management
export {
  clearSettings,
  getActiveProviderConfig,
  getAvailableModels,
  getProviderDisplayName,
  isProviderConfigured,
  loadSettings,
  saveSettings,
  setActiveProvider,
  updateProviderSettings,
} from './settings-service';
// Tools
export { createGraphRAGTools } from './tools';
// Types
export * from './types';
