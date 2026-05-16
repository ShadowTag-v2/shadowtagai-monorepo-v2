/**
 * Vertex AI orchestrator
 * Handles all Claude API calls via Vertex AI
 */

import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";
import { BUILD_PROMPT, SCALE_PROMPT, THINK_PROMPT } from "../prompts/system-prompts";
import { Mode } from "../types";
import { logger } from "../utils/logger";
import { metrics } from "../utils/metrics";

export class VertexOrchestrator {
  private client: AnthropicVertex;
  private model: string = "claude-opus-4-1@20250805";
  private maxTokens: number = 20000;

  constructor() {
    // Reads from environment:
    // - CLOUD_ML_REGION (GKE ConfigMap)
    // - ANTHROPIC_VERTEX_PROJECT_ID (GKE Secret)
    // Uses Workload Identity for authentication
    this.client = new AnthropicVertex({
      region: process.env.CLOUD_ML_REGION || "us-central1",
      projectId: process.env.ANTHROPIC_VERTEX_PROJECT_ID,
    });

    logger.info("VertexOrchestrator initialized", {
      region: process.env.CLOUD_ML_REGION,
      model: this.model,
    });
  }

  /**
   * Execute a prompt with the appropriate mode
   */
  async execute(prompt: string, mode: Mode, context?: Record<string, unknown>): Promise<string> {
    const startTime = Date.now();
    const systemPrompt = this.getSystemPrompt(mode);

    try {
      logger.info("Executing Vertex AI request", { mode, promptLength: prompt.length });

      const message = await this.client.messages.create({
        model: this.model,
        max_tokens: this.maxTokens,
        temperature: mode === Mode.THINK ? 1 : 0.7, // Higher temp for strategic thinking
        system: systemPrompt,
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: this.buildPromptWithContext(prompt, context),
              },
            ],
          },
        ],
      });

      const duration = Date.now() - startTime;
      const response = message.content[0].text;

      // Record metrics
      metrics.recordVertexCall(
        mode,
        duration,
        message.usage?.input_tokens || 0,
        message.usage?.output_tokens || 0,
      );

      logger.info("Vertex AI request completed", {
        mode,
        duration,
        inputTokens: message.usage?.input_tokens,
        outputTokens: message.usage?.output_tokens,
        responseLength: response.length,
      });

      return response;
    } catch (error) {
      const duration = Date.now() - startTime;
      metrics.recordVertexError(mode);

      logger.error("Vertex AI request failed", {
        mode,
        duration,
        error: error instanceof Error ? error.message : String(error),
      });

      throw error;
    }
  }

  /**
   * Get the appropriate system prompt for the mode
   */
  private getSystemPrompt(mode: Mode): string {
    const prompts = {
      [Mode.THINK]: THINK_PROMPT,
      [Mode.BUILD]: BUILD_PROMPT,
      [Mode.SCALE]: SCALE_PROMPT,
    };

    return prompts[mode] || THINK_PROMPT;
  }

  /**
   * Build the full prompt with context
   */
  private buildPromptWithContext(prompt: string, context?: Record<string, unknown>): string {
    if (!context || Object.keys(context).length === 0) {
      return prompt;
    }

    const contextStr = Object.entries(context)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
      .join("\n");

    return `CONTEXT:\n${contextStr}\n\nUSER REQUEST:\n${prompt}`;
  }

  /**
   * Health check - verify Vertex AI connectivity
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 10,
        messages: [
          {
            role: "user",
            content: [{ type: "text", text: "ping" }],
          },
        ],
      });

      return response.content.length > 0;
    } catch (error) {
      logger.error("Vertex AI health check failed", {
        error: error instanceof Error ? error.message : String(error),
      });
      return false;
    }
  }
}
