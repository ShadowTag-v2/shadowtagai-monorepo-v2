/**
 * Provider registry and factory
 */

import type { Provider, ProviderConfig } from '../core/schema.js';
import { createAnthropicProvider } from './anthropic.js';
import type { BaseProvider } from './base.js';
import { createMockProvider } from './mock.js';
import { createOpenAIProvider } from './openai.js';

/**
 * Create provider instance based on type
 */
export function createProvider(provider: Provider, config: ProviderConfig): BaseProvider {
  switch (provider) {
    case 'mock':
      return createMockProvider(config);
    case 'openai':
      return createOpenAIProvider(config);
    case 'anthropic':
      return createAnthropicProvider(config);
    default:
      throw new Error(`Unknown provider: ${provider}`);
  }
}

/**
 * Get all available providers
 */
export function getAvailableProviders(configs: Record<Provider, ProviderConfig>): Provider[] {
  const providers: Provider[] = [];

  for (const [name, config] of Object.entries(configs)) {
    try {
      const provider = createProvider(name as Provider, config);
      if (provider.isAvailable()) {
        providers.push(name as Provider);
      }
    } catch {
      // Provider not available
    }
  }

  return providers;
}

export { AnthropicProvider } from './anthropic.js';
export { BaseProvider } from './base.js';
export { MockProvider } from './mock.js';
export { OpenAIProvider } from './openai.js';
