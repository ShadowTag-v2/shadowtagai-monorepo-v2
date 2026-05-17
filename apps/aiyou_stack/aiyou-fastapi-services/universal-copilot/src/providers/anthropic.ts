/**
 * Anthropic provider using official SDK
 * Compliant implementation using public APIs only
 */

import Anthropic from "@anthropic-ai/sdk";
import { ProviderError } from "../core/errors.js";
import type { CopilotRequest, Patch, ProviderConfig } from "../core/schema.js";
import { BaseProvider } from "./base.js";

/**
 * Anthropic provider for Claude models
 */
export class AnthropicProvider extends BaseProvider {
  private client: Anthropic | null = null;
  private model: string;

  constructor(config: ProviderConfig) {
    super(config);
    this.model = config.model || "claude-sonnet-4-20250514";

    if (config.apiKey) {
      this.client = new Anthropic({
        apiKey: config.apiKey,
        baseURL: config.baseURL,
        timeout: config.timeout,
        maxRetries: config.retries,
      });
    }
  }

  async generatePatch(request: CopilotRequest): Promise<Patch> {
    if (!this.client) {
      throw new ProviderError("Anthropic API key not configured", "anthropic", false);
    }

    const prompt = this.buildPrompt(request);

    try {
      const message = await this.client.messages.create({
        model: this.model,
        max_tokens: request.maxTokens,
        temperature: request.temperature,
        messages: [
          {
            role: "user",
            content: prompt,
          },
        ],
        system: this.getSystemPrompt(request.intent),
      });

      const response = message.content[0];
      if (response.type !== "text") {
        throw new ProviderError("Unexpected response type from Anthropic", "anthropic", false);
      }

      return this.parsePatchResponse(response.text, request.selection.filePath);
    } catch (error: unknown) {
      if (error.status === 429) {
        const retryAfter = error.headers?.["retry-after"];
        throw new ProviderError("Rate limit exceeded", "anthropic", true, { retryAfter });
      }

      throw new ProviderError(error.message || "Unknown Anthropic error", "anthropic", false, {
        originalError: error,
      });
    }
  }

  private getSystemPrompt(intent: string): string {
    const basePrompt = `You are a professional coding assistant providing ${intent} for code.

CRITICAL RULES:
1. Output ONLY a unified diff patch - no explanations before or after
2. Format: --- a/file.ext\\n+++ b/file.ext\\n@@ -X,Y +A,B @@\\n-old\\n+new
3. Be precise and minimal - only change what's necessary
4. Preserve indentation and formatting
5. Ensure the patch can be applied cleanly`;

    const intentSpecific: Record<string, string> = {
      explain: "\nAdd clear comments explaining the code's purpose and logic.",
      refactor: "\nImprove structure, naming, and organization while preserving behavior.",
      test: "\nGenerate comprehensive unit tests covering edge cases.",
      fix: "\nFix bugs and add error handling where needed.",
      optimize: "\nImprove performance using efficient algorithms and data structures.",
      document: "\nAdd JSDoc/docstrings and inline comments for clarity.",
      security: "\nFix security vulnerabilities following OWASP best practices.",
    };

    return basePrompt + (intentSpecific[intent] || "");
  }

  private buildPrompt(request: CopilotRequest): string {
    const { selection, intent } = request;

    let prompt = `File: ${selection.filePath}\n`;
    if (selection.language) {
      prompt += `Language: ${selection.language}\n`;
    }
    prompt += `\nTask: ${intent}\n\n`;
    prompt += `Current code:\n\`\`\`${selection.language || ""}\n${selection.code}\n\`\`\`\n\n`;

    if (selection.context) {
      prompt += `Surrounding context:\n${selection.context}\n\n`;
    }

    prompt += `Generate a unified diff patch to ${intent} this code.`;

    return prompt;
  }

  private parsePatchResponse(response: string, filePath: string): Patch {
    // Extract patch from response (may be wrapped in markdown or explanation)
    let patch = response;

    // Remove markdown code blocks if present
    const codeBlockMatch = response.match(/```diff?\n([\s\S]*?)\n```/);
    if (codeBlockMatch) {
      patch = codeBlockMatch[1];
    } else {
      // Try to find diff markers
      const diffStart = response.indexOf("---");
      if (diffStart !== -1) {
        patch = response.substring(diffStart);
      }
    }

    // Extract explanation if present (text before the patch)
    let explanation: string | undefined;
    const diffStart = response.indexOf("---");
    if (diffStart > 0) {
      const preText = response.substring(0, diffStart).trim();
      if (preText.length > 0 && preText.length < 500) {
        explanation = preText;
      }
    }

    return {
      filePath,
      unifiedDiff: patch.trim(),
      explanation,
      confidence: 0.9,
    };
  }

  estimateCost(request: CopilotRequest): number {
    // Claude pricing: $3 per 1M input tokens, $15 per 1M output tokens
    const inputTokens = Math.ceil(request.selection.code.length / 3.5);
    const outputTokens = Math.min(request.maxTokens, 1000);

    return (inputTokens / 1_000_000) * 3.0 + (outputTokens / 1_000_000) * 15.0;
  }

  isAvailable(): boolean {
    return this.client !== null;
  }

  getName(): string {
    return "anthropic";
  }

  getModel(): string {
    return this.model;
  }
}

/**
 * Create Anthropic provider instance
 */
export function createAnthropicProvider(config: ProviderConfig): AnthropicProvider {
  return new AnthropicProvider(config);
}
