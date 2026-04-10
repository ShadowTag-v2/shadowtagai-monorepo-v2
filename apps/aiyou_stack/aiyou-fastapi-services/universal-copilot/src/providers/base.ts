/**
 * Base provider interface for LLM providers
 */

import type { CopilotRequest, Patch, ProviderConfig } from "../core/schema.js";

/**
 * Abstract base class for all LLM providers
 */
export abstract class BaseProvider {
  constructor(protected config: ProviderConfig) {}

  /**
   * Generate a code patch based on the request
   */
  abstract generatePatch(request: CopilotRequest): Promise<Patch>;

  /**
   * Estimate cost for a request (in USD)
   */
  abstract estimateCost(request: CopilotRequest): number;

  /**
   * Check if provider is available and configured
   */
  abstract isAvailable(): boolean;

  /**
   * Get provider name
   */
  abstract getName(): string;

  /**
   * Get model name being used
   */
  abstract getModel(): string;
}

/**
 * Provider factory interface
 */
export interface ProviderFactory {
  createProvider(config: ProviderConfig): BaseProvider;
}
