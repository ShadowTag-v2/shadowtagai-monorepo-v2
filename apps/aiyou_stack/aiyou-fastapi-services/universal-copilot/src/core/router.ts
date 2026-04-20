/**
 * Intelligent router with rate limiting and governance
 * Routes requests to appropriate providers with Judge #6 enforcement
 */

import Bottleneck from 'bottleneck';
import { type BaseProvider, createProvider } from '../providers/index.js';
import { GovernanceError, RateLimitError, ValidationError } from './errors.js';
import type { CopilotRequest, CopilotResponse, Provider, RouterConfig } from './schema.js';

/**
 * Judge #6 governance integration interface
 * Allows optional governance without hard dependency
 */
export interface GovernanceEngine {
  evaluateRequest(
    input: string,
    purpose?: string,
  ): Promise<{
    approved: boolean;
    risk_level: string;
    reasoning: string;
    violated_axioms: Array<{ axiom_id: string; name: string }>;
  }>;
}

/**
 * Router statistics
 */
export interface RouterStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  governanceRejections: number;
  rateLimitHits: number;
  providerUsage: Record<Provider, number>;
  averageLatencyMs: number;
}

/**
 * Universal Copilot Router
 */
export class CopilotRouter {
  private config: RouterConfig;
  private providers: Map<Provider, BaseProvider>;
  private limiter: Bottleneck;
  private governance: GovernanceEngine | null = null;
  private stats: RouterStats;

  constructor(config: RouterConfig, governance?: GovernanceEngine) {
    this.config = config;
    this.governance = governance || null;
    this.providers = new Map();
    this.stats = this.initializeStats();

    // Initialize rate limiter
    this.limiter = new Bottleneck({
      minTime: Math.floor(1000 / config.rateLimitRps),
      maxConcurrent: config.rateLimitConcurrent,
      reservoir: Math.floor(config.rateLimitRps * 60), // per minute
      reservoirRefreshAmount: Math.floor(config.rateLimitRps * 60),
      reservoirRefreshInterval: 60 * 1000, // 1 minute
    });

    // Setup rate limit event handlers
    this.limiter.on('failed', async (error, jobInfo) => {
      if (jobInfo.retryCount < 2) {
        this.stats.rateLimitHits++;
        return 1000; // Retry after 1 second
      }
      return undefined; // Give up
    });

    // Initialize providers
    this.initializeProviders();
  }

  private initializeStats(): RouterStats {
    return {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      governanceRejections: 0,
      rateLimitHits: 0,
      providerUsage: {
        mock: 0,
        openai: 0,
        anthropic: 0,
        auto: 0,
      },
      averageLatencyMs: 0,
    };
  }

  private initializeProviders(): void {
    const providerConfigs = this.config.providers || {};

    // Always initialize mock provider
    this.providers.set('mock', createProvider('mock', {}));

    // Initialize configured providers
    for (const [name, config] of Object.entries(providerConfigs)) {
      try {
        const provider = createProvider(name as Provider, config);
        if (provider.isAvailable()) {
          this.providers.set(name as Provider, provider);
        }
      } catch (error) {
        console.warn(`Failed to initialize provider ${name}:`, error);
      }
    }
  }

  /**
   * Route a request through governance and to appropriate provider
   */
  async route(request: CopilotRequest): Promise<CopilotResponse> {
    const startTime = Date.now();
    this.stats.totalRequests++;

    try {
      // Validate request
      this.validateRequest(request);

      // Apply governance if enabled
      let governanceDecision;
      if (this.config.enableGovernance && this.governance) {
        governanceDecision = await this.applyGovernance(request);
      }

      // Select provider
      const provider = this.selectProvider(request.modelPref);

      // Generate patch with rate limiting
      const patch = await this.limiter.schedule(() => provider.generatePatch(request));

      this.stats.successfulRequests++;
      this.stats.providerUsage[provider.getName() as Provider]++;

      const latency = Date.now() - startTime;
      this.updateLatency(latency);

      return {
        patch,
        provider: provider.getName() as Provider,
        tokensUsed: this.estimateTokens(request, patch.unifiedDiff),
        latencyMs: latency,
        governanceDecision,
      };
    } catch (error) {
      this.stats.failedRequests++;
      throw error;
    }
  }

  private validateRequest(request: CopilotRequest): void {
    if (!request.selection.code || request.selection.code.trim().length === 0) {
      throw new ValidationError('Code selection cannot be empty');
    }

    if (request.selection.code.length > 50000) {
      throw new ValidationError('Code selection too large (max 50KB)', {
        size: request.selection.code.length,
      });
    }

    if (!request.selection.filePath) {
      throw new ValidationError('File path is required');
    }
  }

  private async applyGovernance(request: CopilotRequest): Promise<{
    approved: boolean;
    riskLevel: string;
    reasoning?: string;
  }> {
    if (!this.governance) {
      return { approved: true, riskLevel: 'RA_1' };
    }

    const purpose = `Code ${request.intent} for ${request.selection.filePath}`;
    const input = `${purpose}\n\nCode:\n${request.selection.code}`;

    try {
      const decision = await this.governance.evaluateRequest(input, purpose);

      if (!decision.approved) {
        this.stats.governanceRejections++;
        const axiomNames = decision.violated_axioms.map((a) => a.name);
        throw new GovernanceError(
          `Request rejected by governance: ${decision.reasoning}`,
          decision.risk_level,
          axiomNames,
          { decision },
        );
      }

      return {
        approved: decision.approved,
        riskLevel: decision.risk_level,
        reasoning: decision.reasoning,
      };
    } catch (error) {
      if (error instanceof GovernanceError) {
        throw error;
      }
      // Fail closed on governance errors
      throw new GovernanceError('Governance check failed', 'RA_4', [], { originalError: error });
    }
  }

  private selectProvider(preference: Provider): BaseProvider {
    // If specific provider requested, use it
    if (preference !== 'auto') {
      const provider = this.providers.get(preference);
      if (!provider) {
        throw new ValidationError(`Provider ${preference} not available`);
      }
      return provider;
    }

    // Auto-selection logic
    // Priority: anthropic > openai > mock
    const priorities: Provider[] = ['anthropic', 'openai', 'mock'];

    for (const name of priorities) {
      const provider = this.providers.get(name);
      if (provider && provider.isAvailable()) {
        return provider;
      }
    }

    // Fallback to mock
    return this.providers.get('mock')!;
  }

  private estimateTokens(request: CopilotRequest, response: string): number {
    // Rough estimation: ~4 chars per token
    const inputTokens = Math.ceil(request.selection.code.length / 4);
    const outputTokens = Math.ceil(response.length / 4);
    return inputTokens + outputTokens;
  }

  private updateLatency(latencyMs: number): void {
    const total = this.stats.totalRequests;
    const current = this.stats.averageLatencyMs;
    this.stats.averageLatencyMs = (current * (total - 1) + latencyMs) / total;
  }

  /**
   * Get router statistics
   */
  getStats(): RouterStats {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = this.initializeStats();
  }

  /**
   * Get available providers
   */
  getAvailableProviders(): Provider[] {
    return Array.from(this.providers.keys());
  }

  /**
   * Estimate cost for a request
   */
  async estimateCost(request: CopilotRequest): Promise<number> {
    const provider = this.selectProvider(request.modelPref);
    return provider.estimateCost(request);
  }
}
