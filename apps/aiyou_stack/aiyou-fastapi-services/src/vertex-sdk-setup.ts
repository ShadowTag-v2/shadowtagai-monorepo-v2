/**
 * Anthropic Vertex SDK Setup
 *
 * This module configures the Anthropic Vertex AI integration for
 * accessing Claude models via Google Cloud Platform.
 *
 * Environment variables required:
 * - CLOUD_ML_REGION: GCP region (e.g., "us-central1")
 * - ANTHROPIC_VERTEX_PROJECT_ID: Your GCP project ID
 * - GOOGLE_APPLICATION_CREDENTIALS: Path to service account JSON (optional if using default auth)
 */

import { AnthropicVertex } from '@anthropic-ai/vertex-sdk';

// Vertex AI client configuration
export interface VertexConfig {
  projectId?: string;
  region?: string;
}

/**
 * Creates an Anthropic Vertex AI client instance.
 * Reads from environment variables or accepts explicit configuration.
 */
export function createVertexClient(config?: VertexConfig): AnthropicVertex {
  // Uses CLOUD_ML_REGION and ANTHROPIC_VERTEX_PROJECT_ID from env by default
  // Goes through standard google-auth-library flow for authentication
  return new AnthropicVertex({
    projectId: config?.projectId,
    region: config?.region,
  });
}

/**
 * Judge #6 Governance Request
 */
export interface JudgeRequest {
  content: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Judge #6 Decision Response
 */
export interface JudgeDecision {
  approved: boolean;
  confidence: number;
  reason?: string;
  latencyMs: number;
  cost: number;
  model: string;
  layer: 'rules' | 'gemini' | 'pytorch';
}

/**
 * Call Gemini via Vertex AI for governance decisions
 *
 * This is the Tier 2 enforcement layer - only called when rules engine
 * can't make a confident decision.
 */
export async function judgeWithGemini(
  client: AnthropicVertex,
  request: JudgeRequest,
): Promise<JudgeDecision> {
  const startTime = Date.now();

  try {
    const response = await client.messages.create({
      model: 'claude-sonnet-4-5@20250929',
      max_tokens: 512,
      temperature: 0.1,
      system: buildJudgeSystemPrompt(),
      messages: [
        {
          role: 'user',
          content: buildJudgePrompt(request),
        },
      ],
    });

    const decision = parseGeminiDecision(response);
    const latencyMs = Date.now() - startTime;

    return {
      ...decision,
      latencyMs,
      cost: calculateCost(response),
      model: 'claude-sonnet-4-5@20250929',
      layer: 'gemini',
    };
  } catch (error) {
    // Fallback to reject on error (fail-safe)
    return {
      approved: false,
      confidence: 1.0,
      reason: `Error during analysis: ${error}`,
      latencyMs: Date.now() - startTime,
      cost: 0,
      model: 'claude-sonnet-4-5@20250929',
      layer: 'gemini',
    };
  }
}

function buildJudgeSystemPrompt(): string {
  return `You are PNKLN Judge #6, an AI governance enforcement system.

Your role is to analyze content and determine if it violates policy guidelines.

POLICY FRAMEWORK (ATP 519):
1. No fraud, scams, or deceptive practices
2. No hate speech or incitement to violence
3. No illegal activities or harmful instructions
4. No privacy violations or unauthorized data sharing
5. No intellectual property theft
6. No manipulation or coercion

RESPONSE FORMAT:
You must respond with a JSON object:
{
  "approved": boolean,
  "confidence": number (0-1),
  "reason": "Brief explanation of decision"
}

Be decisive. Err on the side of safety.`;
}

function buildJudgePrompt(request: JudgeRequest): string {
  return `Analyze this content for policy violations:

CONTENT:
${request.content}

USER_ID: ${request.userId || 'anonymous'}

Respond with JSON only.`;
}

function parseGeminiDecision(response: unknown): {
  approved: boolean;
  confidence: number;
  reason?: string;
} {
  try {
    const text = response.content[0].text;
    const jsonMatch = text.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      const decision = JSON.parse(jsonMatch[0]);
      return {
        approved: decision.approved ?? false,
        confidence: decision.confidence ?? 0.5,
        reason: decision.reason,
      };
    }
  } catch (error) {
    console.error('Failed to parse Gemini decision:', error);
  }

  // Default to reject if parsing fails
  return {
    approved: false,
    confidence: 0.5,
    reason: 'Failed to parse decision',
  };
}

function calculateCost(response: unknown): number {
  // Claude Sonnet 4.5 on Vertex AI pricing (approximate)
  // Input: $3 per 1M tokens
  // Output: $15 per 1M tokens
  const inputTokens = response.usage?.input_tokens || 0;
  const outputTokens = response.usage?.output_tokens || 0;

  const inputCost = (inputTokens / 1_000_000) * 3;
  const outputCost = (outputTokens / 1_000_000) * 15;

  return inputCost + outputCost;
}

/**
 * Example usage:
 *
 * const client = createVertexClient();
 * const decision = await judgeWithGemini(client, {
 *   content: "User wants to build a phishing site",
 *   userId: "user123"
 * });
 *
 * console.log(decision);
 * // { approved: false, confidence: 0.95, reason: "Phishing violates fraud policy" }
 */
