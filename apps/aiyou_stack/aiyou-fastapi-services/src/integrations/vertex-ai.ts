/**
 * Vertex AI Integration Module
 *
 * Provides unified interface for Claude (via Vertex) and Gemini models
 * with automatic fallback, retry logic, and cost tracking.
 */

import { AnthropicVertex } from '@anthropic-ai/vertex-sdk';

export interface VertexConfig {
  projectId?: string;
  location?: string;
  // Model routing weights (must sum to 1.0)
  modelWeights?: {
    gemini: number;
    claude: number;
  };
}

export interface CompletionRequest {
  prompt: string;
  systemPrompt?: string;
  maxTokens?: number;
  temperature?: number;
  model?: 'gemini' | 'claude' | 'auto';
}

export interface CompletionResponse {
  content: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  latencyMs: number;
  costUsd: number;
}

// Cost per 1K tokens (approximate, varies by model version)
const COST_PER_1K_TOKENS = {
  'claude-sonnet-4-5@20250929': { input: 0.003, output: 0.015 },
  'gemini-1.5-flash-002': { input: 0.000075, output: 0.0003 },
  'gemini-1.5-pro-002': { input: 0.00125, output: 0.005 },
};

export class VertexAIClient {
  private claudeClient: AnthropicVertex;
  private projectId: string;
  private location: string;
  private modelWeights: { gemini: number; claude: number };

  constructor(config: VertexConfig = {}) {
    this.projectId = config.projectId || process.env.GOOGLE_CLOUD_PROJECT || 'pnkln-core-stack';
    this.location = config.location || process.env.GOOGLE_CLOUD_LOCATION || 'us-central1';
    this.modelWeights = config.modelWeights || { gemini: 0.6, claude: 0.4 };

    // Initialize Claude via Vertex SDK
    this.claudeClient = new AnthropicVertex({
      projectId: this.projectId,
      region: this.location,
    });
  }

  /**
   * Select model based on weights or explicit selection
   */
  private selectModel(preference?: 'gemini' | 'claude' | 'auto'): 'gemini' | 'claude' {
    if (preference && preference !== 'auto') {
      return preference;
    }

    // Weighted random selection
    const random = Math.random();
    return random < this.modelWeights.gemini ? 'gemini' : 'claude';
  }

  /**
   * Calculate cost for a completion
   */
  private calculateCost(model: string, inputTokens: number, outputTokens: number): number {
    const costs = COST_PER_1K_TOKENS[model as keyof typeof COST_PER_1K_TOKENS];
    if (!costs) return 0;

    return (inputTokens / 1000) * costs.input + (outputTokens / 1000) * costs.output;
  }

  /**
   * Call Claude via Vertex AI
   */
  async callClaude(request: CompletionRequest): Promise<CompletionResponse> {
    const startTime = performance.now();
    const model = 'claude-sonnet-4-5@20250929';

    const response = await this.claudeClient.messages.create({
      model,
      max_tokens: request.maxTokens || 4096,
      temperature: request.temperature || 0.7,
      system: request.systemPrompt,
      messages: [
        {
          role: 'user',
          content: request.prompt,
        },
      ],
    });

    const content = response.content[0].type === 'text' ? response.content[0].text : '';
    const inputTokens = response.usage.input_tokens;
    const outputTokens = response.usage.output_tokens;

    return {
      content,
      model,
      inputTokens,
      outputTokens,
      latencyMs: performance.now() - startTime,
      costUsd: this.calculateCost(model, inputTokens, outputTokens),
    };
  }

  /**
   * Call Gemini via Vertex AI REST API
   */
  async callGemini(request: CompletionRequest, flash = true): Promise<CompletionResponse> {
    const startTime = performance.now();
    const model = flash ? 'gemini-1.5-flash-002' : 'gemini-1.5-pro-002';

    const endpoint = `https://${this.location}-aiplatform.googleapis.com/v1/projects/${this.projectId}/locations/${this.location}/publishers/google/models/${model}:generateContent`;

    // Get access token from environment or default credentials
    const accessToken = process.env.GOOGLE_CLOUD_TOKEN || (await this.getAccessToken());

    const body: Record<string, unknown> = {
      contents: [
        {
          role: 'user',
          parts: [{ text: request.prompt }],
        },
      ],
      generationConfig: {
        temperature: request.temperature || 0.7,
        maxOutputTokens: request.maxTokens || 4096,
      },
    };

    if (request.systemPrompt) {
      body.systemInstruction = {
        parts: [{ text: request.systemPrompt }],
      };
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Gemini API error: ${response.status} - ${error}`);
    }

    const result = (await response.json()) as {
      candidates: Array<{
        content: {
          parts: Array<{ text: string }>;
        };
      }>;
      usageMetadata?: {
        promptTokenCount: number;
        candidatesTokenCount: number;
      };
    };

    const content = result.candidates[0]?.content?.parts[0]?.text || '';
    const inputTokens = result.usageMetadata?.promptTokenCount || 0;
    const outputTokens = result.usageMetadata?.candidatesTokenCount || 0;

    return {
      content,
      model,
      inputTokens,
      outputTokens,
      latencyMs: performance.now() - startTime,
      costUsd: this.calculateCost(model, inputTokens, outputTokens),
    };
  }

  /**
   * Get access token from Google Cloud default credentials
   */
  private async getAccessToken(): Promise<string> {
    // In production, use google-auth-library
    // This is a simplified version for environments with GOOGLE_APPLICATION_CREDENTIALS
    const { execSync } = await import('child_process');
    return execSync('gcloud auth print-access-token').toString().trim();
  }

  /**
   * Unified completion with automatic model selection and fallback
   */
  async complete(request: CompletionRequest): Promise<CompletionResponse> {
    const selectedModel = this.selectModel(request.model);

    try {
      if (selectedModel === 'claude') {
        return await this.callClaude(request);
      } else {
        return await this.callGemini(request);
      }
    } catch (error) {
      // Fallback to the other model on failure
      console.warn(`${selectedModel} failed, falling back...`, error);

      if (selectedModel === 'claude') {
        return await this.callGemini(request);
      } else {
        return await this.callClaude(request);
      }
    }
  }

  /**
   * Stream completion (Claude only for now)
   */
  async *streamClaude(request: CompletionRequest): AsyncGenerator<string> {
    const stream = this.claudeClient.messages.stream({
      model: 'claude-sonnet-4-5@20250929',
      max_tokens: request.maxTokens || 4096,
      temperature: request.temperature || 0.7,
      system: request.systemPrompt,
      messages: [
        {
          role: 'user',
          content: request.prompt,
        },
      ],
    });

    for await (const event of stream) {
      if (event.type === 'content_block_delta' && event.delta.type === 'text_delta') {
        yield event.delta.text;
      }
    }
  }
}

// Default export for convenience
export default VertexAIClient;
