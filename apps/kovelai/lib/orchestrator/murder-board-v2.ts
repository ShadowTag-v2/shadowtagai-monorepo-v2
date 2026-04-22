/**
 * Murder Board Orchestrator v2
 *
 * The 7-stage pipeline that transforms a raw client intake
 * into a complete legal triage output with:
 * - Entity extraction
 * - Conflict check
 * - Viability scoring
 * - Fee structure recommendation
 * - Oracle Memo generation
 * - Retainer draft
 * - Judge 6 risk gate approval
 *
 * Each stage is streamed via SSE for real-time dashboard UX.
 * Uses Cloud Tasks for async stage execution (BullMQ banned).
 */
import {
  buildMurderBoardPrompt,
  type MurderBoardStage,
} from '../prompts/war-room-prompts';
import { AntigravityMCPClient } from '../mcp/antigravity-client';

// ─── Types ────────────────────────────────────────────────────────────
export interface MurderBoardInput {
  caseDescription: string;
  firmId: string;
  matterId?: string;
  clientId: string;
  jurisdiction: string;
  practiceArea: string;
  documents?: string[];
  modelTier?: 'reasoning' | 'flash' | 'lite';
}

export interface StageResult {
  stage: MurderBoardStage;
  status: 'pending' | 'running' | 'completed' | 'failed';
  output?: unknown;
  error?: string;
  durationMs?: number;
  tokenUsage?: { input: number; output: number };
}

export interface MurderBoardResult {
  id: string;
  firmId: string;
  clientId: string;
  status: 'running' | 'completed' | 'rejected' | 'failed';
  stages: StageResult[];
  finalDecision?: 'APPROVED' | 'CONDITIONAL_APPROVAL' | 'REJECTED';
  createdAt: string;
  completedAt?: string;
}

// ─── Orchestrator ─────────────────────────────────────────────────────
const STAGES: MurderBoardStage[] = [
  'EXTRACTION',
  'CONFLICT_CHECK',
  'VIABILITY_SCORING',
  'FEE_STRUCTURE',
  'ORACLE_MEMO',
  'RETAINER_DRAFT',
  'RISK_GATE',
];

/**
 * Executes the full 7-stage Murder Board pipeline.
 *
 * @param input - The case intake data
 * @param onStageUpdate - Callback for real-time stage updates (SSE)
 * @returns Complete Murder Board result with all stage outputs
 */
export async function executeMurderBoard(
  input: MurderBoardInput,
  onStageUpdate?: (stage: StageResult) => void,
): Promise<MurderBoardResult> {
  const boardId = crypto.randomUUID();
  const modelTier = input.modelTier ?? 'flash';
  const result: MurderBoardResult = {
    id: boardId,
    firmId: input.firmId,
    clientId: input.clientId,
    status: 'running',
    stages: STAGES.map((stage) => ({
      stage,
      status: 'pending' as const,
    })),
    createdAt: new Date().toISOString(),
  };

  let previousOutput = input.caseDescription;

  for (let i = 0; i < STAGES.length; i++) {
    const stageName = STAGES[i];
    const stageResult = result.stages[i];
    stageResult.status = 'running';
    onStageUpdate?.(stageResult);

    const startTime = Date.now();

    try {
      // Build prompt with context from previous stages
      const contextualInput = buildStageInput(
        stageName,
        previousOutput,
        result.stages.slice(0, i),
        input,
      );

      const prompt = buildMurderBoardPrompt(stageName, contextualInput, modelTier);

      // Execute LLM call
      const output = await callLLM(prompt.system, prompt.user, modelTier);

      stageResult.output = output;
      stageResult.status = 'completed';
      stageResult.durationMs = Date.now() - startTime;

      // Feed output to next stage
      previousOutput = typeof output === 'string' ? output : JSON.stringify(output);

      // Check for Judge 6 rejection at final stage
      if (stageName === 'RISK_GATE') {
        const riskOutput = typeof output === 'string' ? output : JSON.stringify(output);
        if (riskOutput.includes('REJECTED')) {
          result.finalDecision = 'REJECTED';
          result.status = 'rejected';
        } else if (riskOutput.includes('CONDITIONAL_APPROVAL')) {
          result.finalDecision = 'CONDITIONAL_APPROVAL';
          result.status = 'completed';
        } else {
          result.finalDecision = 'APPROVED';
          result.status = 'completed';
        }
      }

      onStageUpdate?.(stageResult);
    } catch (error) {
      stageResult.status = 'failed';
      stageResult.error = error instanceof Error ? error.message : 'Unknown error';
      stageResult.durationMs = Date.now() - startTime;
      onStageUpdate?.(stageResult);

      // Stage failure — mark board as failed and stop
      result.status = 'failed';
      break;
    }
  }

  result.completedAt = new Date().toISOString();
  return result;
}

// ─── Stage Input Builder ──────────────────────────────────────────────
function buildStageInput(
  stage: MurderBoardStage,
  previousOutput: string,
  previousStages: StageResult[],
  input: MurderBoardInput,
): string {
  const parts: string[] = [];

  // Always include the original case description
  parts.push(`[ORIGINAL CASE DESCRIPTION]\n${input.caseDescription}`);

  // Include jurisdiction context
  parts.push(`[JURISDICTION] ${input.jurisdiction}`);
  parts.push(`[PRACTICE AREA] ${input.practiceArea}`);

  // Include relevant previous stage outputs
  for (const prev of previousStages) {
    if (prev.status === 'completed' && prev.output) {
      parts.push(
        `[STAGE ${prev.stage} OUTPUT]\n${
          typeof prev.output === 'string'
            ? prev.output
            : JSON.stringify(prev.output, null, 2)
        }`,
      );
    }
  }

  // Stage-specific context
  switch (stage) {
    case 'CONFLICT_CHECK':
      parts.push(
        `[FIRM ID] ${input.firmId}\n[MATTER ID] ${input.matterId ?? 'NEW MATTER'}`,
      );
      break;
    case 'FEE_STRUCTURE':
      parts.push(`[JURISDICTION FOR FEE RULES] ${input.jurisdiction}`);
      break;
    default:
      break;
  }

  return parts.join('\n\n');
}

// ─── SSE Stream Generator ─────────────────────────────────────────────
/**
 * Creates an SSE stream for real-time Murder Board progress.
 * Each stage completion sends an event to the client.
 */
export function createMurderBoardSSEStream(
  input: MurderBoardInput,
): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();

  return new ReadableStream({
    async start(controller) {
      try {
        await executeMurderBoard(input, (stageResult) => {
          const event = `data: ${JSON.stringify(stageResult)}\n\n`;
          controller.enqueue(encoder.encode(event));
        });

        // Send completion event
        controller.enqueue(encoder.encode('data: {"type":"complete"}\n\n'));
        controller.close();
      } catch (error) {
        const errorEvent = `data: ${JSON.stringify({
          type: 'error',
          message: error instanceof Error ? error.message : 'Pipeline failed',
        })}\n\n`;
        controller.enqueue(encoder.encode(errorEvent));
        controller.close();
      }
    },
  });
}

// ─── LLM Call (Abstracted) ────────────────────────────────────────────
/**
 * Calls the LLM via the configured tier.
 * In production, routes through LiteLLM proxy.
 */
async function callLLM(
  systemPrompt: string,
  userPrompt: string,
  tier: 'reasoning' | 'flash' | 'lite',
): Promise<string> {
  const modelMap: Record<string, string> = {
    reasoning: 'gemini-2.5-pro',
    flash: 'gemini-2.5-flash',
    lite: 'gemini-3.1-flash-lite-preview-thinking',
  };

  const model = modelMap[tier] ?? modelMap.flash;
  const apiKey = process.env.GOOGLE_AI_API_KEY;

  if (!apiKey) {
    throw new Error('[MURDER BOARD] GOOGLE_AI_API_KEY not configured');
  }

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents: [{ parts: [{ text: userPrompt }] }],
        generationConfig: {
          maxOutputTokens: 4096,
          temperature: 0.3,
        },
      }),
      signal: AbortSignal.timeout(60000),
    },
  );

  if (!response.ok) {
    throw new Error(`LLM call failed: ${response.status}`);
  }

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text ?? '';
}
