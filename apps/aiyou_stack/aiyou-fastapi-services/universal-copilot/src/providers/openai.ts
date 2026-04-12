/**
 * OpenAI provider using official SDK
 * Compliant implementation using public APIs only
 */

import OpenAI from "openai";
import type { CopilotRequest, Patch, ProviderConfig } from "../core/schema.js";
import { BaseProvider } from "./base.js";
import { ProviderError } from "../core/errors.js";

/**
 * OpenAI provider for GPT models
 */
export class OpenAIProvider extends BaseProvider {
  private client: OpenAI | null = null;
  private model: string;

  constructor(config: ProviderConfig) {
    super(config);
    this.model = config.model || "gpt-4o-2024-08-06";

    if (config.apiKey) {
      this.client = new OpenAI({
        apiKey: config.apiKey,
        baseURL: config.baseURL,
        timeout: config.timeout,
        maxRetries: config.retries,
      });
    }
  }

  async generatePatch(request: CopilotRequest): Promise<Patch> {
    if (!this.client) {
      throw new ProviderError("OpenAI API key not configured", "openai", false);
    }

    const prompt = this.buildPrompt(request);

    try {
      const completion = await this.client.chat.completions.create({
        model: this.model,
        messages: [
          {
            role: "system",
            content: this.getSystemPrompt(request.intent),
          },
          {
            role: "user",
            content: prompt,
          },
        ],
        max_tokens: request.maxTokens,
        temperature: request.temperature,
      });

      const response = completion.choices[0]?.message?.content;
      if (!response) {
        throw new ProviderError("Empty response from OpenAI", "openai", true);
      }

      return this.parsePatchResponse(response, request.selection.filePath);
    } catch (error: unknown) {
      if (error.status === 429) {
        const retryAfter = error.headers?.["retry-after"];
        throw new ProviderError("Rate limit exceeded", "openai", true, { retryAfter });
      }

      throw new ProviderError(error.message || "Unknown OpenAI error", "openai", false, {
        originalError: error,
      });
    }
  }

  private getSystemPrompt(intent: string): string {
    const prompts: Record<string, string> = {
      explain: "You are a code explanation assistant. Provide clear, concise explanations.",
      refactor:
        "You are a code refactoring expert. Improve structure while preserving functionality.",
      test: "You are a test generation expert. Create comprehensive unit tests.",
      fix: "You are a debugging expert. Fix bugs while maintaining code clarity.",
      optimize:
        "You are a performance optimization expert. Improve efficiency without breaking functionality.",
      document: "You are a documentation expert. Add clear, helpful documentation.",
      security: "You are a security expert. Fix vulnerabilities following OWASP best practices.",
    };

    return (
      prompts[intent] ||
      "You are a helpful coding assistant. Provide clear, correct code improvements."
    );
  }

  private buildPrompt(request: CopilotRequest): string {
    const { selection, intent } = request;

    let prompt = `File: ${selection.filePath}\n`;
    if (selection.language) {
      prompt += `Language: ${selection.language}\n`;
    }
    prompt += `\nIntent: ${intent}\n\n`;
    prompt += `Code:\n\`\`\`\n${selection.code}\n\`\`\`\n\n`;

    if (selection.context) {
      prompt += `Context:\n${selection.context}\n\n`;
    }

    prompt += `Provide the improved code as a unified diff patch. Format:\n`;
    prompt += `--- a/filename\n+++ b/filename\n@@ line info @@\n-removed\n+added\n`;

    return prompt;
  }

  private parsePatchResponse(response: string, filePath: string): Patch {
    // Extract patch from response (may be wrapped in markdown)
    let patch = response;

    // Remove markdown code blocks if present
    const codeBlockMatch = response.match(/```diff?\n([\s\S]*?)\n```/);
    if (codeBlockMatch) {
      patch = codeBlockMatch[1];
    }

    // Extract explanation if present
    let explanation: string | undefined;
    const explanationMatch = response.match(/explanation:?\s*(.+?)(?:\n\n|$)/i);
    if (explanationMatch) {
      explanation = explanationMatch[1].trim();
    }

    return {
      filePath,
      unifiedDiff: patch,
      explanation,
      confidence: 0.85,
    };
  }

  estimateCost(request: CopilotRequest): number {
    // Rough estimate: $0.002 per 1K input tokens, $0.006 per 1K output tokens
    const inputTokens = Math.ceil(request.selection.code.length / 4);
    const outputTokens = Math.min(request.maxTokens, 1000);

    return (inputTokens / 1000) * 0.002 + (outputTokens / 1000) * 0.006;
  }

  isAvailable(): boolean {
    return this.client !== null;
  }

  getName(): string {
    return "openai";
  }

  getModel(): string {
    return this.model;
  }
}

/**
 * Create OpenAI provider instance
 */
export function createOpenAIProvider(config: ProviderConfig): OpenAIProvider {
  return new OpenAIProvider(config);
}
