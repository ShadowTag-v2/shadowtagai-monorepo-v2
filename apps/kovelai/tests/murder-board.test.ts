/**
 * @fileoverview Murder Board Orchestrator v2 Test Suite — Vitest
 *
 * Tests the 7-stage pipeline including SSE streaming,
 * stage progression, error handling, and Judge 6 decisions.
 *
 * Sprint Item #21: Enhanced test suite.
 *
 * @see lib/orchestrator/murder-board-v2.ts
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock crypto.randomUUID
vi.stubGlobal('crypto', {
  randomUUID: () => '550e8400-e29b-41d4-a716-446655440000',
});

describe('Murder Board Orchestrator v2', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.GOOGLE_AI_API_KEY = 'test-api-key';
  });

  afterEach(() => {
    delete process.env.GOOGLE_AI_API_KEY;
    vi.restoreAllMocks();
  });

  describe('executeMurderBoard', () => {
    it('should execute all 7 stages in sequence', async () => {
      // Mock LLM responses for each stage
      mockFetch.mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            candidates: [
              {
                content: {
                  parts: [{ text: '{"status": "stage complete", "decision": "APPROVED"}' }],
                },
              },
            ],
          }),
      });

      const { executeMurderBoard } = await import('../lib/orchestrator/murder-board-v2');

      const stages: string[] = [];
      const result = await executeMurderBoard(
        {
          caseDescription: 'Client was wrongfully terminated after reporting OSHA violations',
          firmId: '550e8400-e29b-41d4-a716-446655440000',
          clientId: '660e8400-e29b-41d4-a716-446655440001',
          jurisdiction: 'California',
          practiceArea: 'Employment',
        },
        (stageResult) => {
          stages.push(`${stageResult.stage}:${stageResult.status}`);
        },
      );

      // All 7 stages should complete
      expect(result.stages).toHaveLength(7);
      expect(result.status).toBe('completed');
      expect(result.id).toBeDefined();

      // Verify stage order
      const expectedStages = [
        'EXTRACTION',
        'CONFLICT_CHECK',
        'VIABILITY_SCORING',
        'FEE_STRUCTURE',
        'ORACLE_MEMO',
        'RETAINER_DRAFT',
        'RISK_GATE',
      ];

      for (let i = 0; i < expectedStages.length; i++) {
        expect(result.stages[i].stage).toBe(expectedStages[i]);
        expect(result.stages[i].status).toBe('completed');
      }
    });

    it('should detect REJECTED decision from Judge 6', async () => {
      let callCount = 0;
      mockFetch.mockImplementation(() => {
        callCount++;
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              candidates: [
                {
                  content: {
                    parts: [
                      {
                        text:
                          callCount >= 7
                            ? 'REJECTED: Conflict of interest not resolved at Stage 2.'
                            : '{"status": "ok"}',
                      },
                    ],
                  },
                },
              ],
            }),
        });
      });

      const { executeMurderBoard } = await import('../lib/orchestrator/murder-board-v2');

      const result = await executeMurderBoard({
        caseDescription: 'Test case for rejection',
        firmId: '550e8400-e29b-41d4-a716-446655440000',
        clientId: '660e8400-e29b-41d4-a716-446655440001',
        jurisdiction: 'New York',
        practiceArea: 'Litigation',
      });

      expect(result.finalDecision).toBe('REJECTED');
      expect(result.status).toBe('rejected');
    });

    it('should detect CONDITIONAL_APPROVAL from Judge 6', async () => {
      let callCount = 0;
      mockFetch.mockImplementation(() => {
        callCount++;
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              candidates: [
                {
                  content: {
                    parts: [
                      {
                        text:
                          callCount >= 7
                            ? 'CONDITIONAL_APPROVAL: Require client waiver before proceeding.'
                            : '{"status": "ok"}',
                      },
                    ],
                  },
                },
              ],
            }),
        });
      });

      const { executeMurderBoard } = await import('../lib/orchestrator/murder-board-v2');

      const result = await executeMurderBoard({
        caseDescription: 'Test case for conditional',
        firmId: '550e8400-e29b-41d4-a716-446655440000',
        clientId: '660e8400-e29b-41d4-a716-446655440001',
        jurisdiction: 'Texas',
        practiceArea: 'Family',
      });

      expect(result.finalDecision).toBe('CONDITIONAL_APPROVAL');
      expect(result.status).toBe('completed');
    });

    it('should handle stage failure and stop pipeline', async () => {
      let callCount = 0;
      mockFetch.mockImplementation(() => {
        callCount++;
        if (callCount === 3) {
          return Promise.resolve({
            ok: false,
            status: 500,
          });
        }
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              candidates: [{ content: { parts: [{ text: '{"ok": true}' }] } }],
            }),
        });
      });

      const { executeMurderBoard } = await import('../lib/orchestrator/murder-board-v2');

      const result = await executeMurderBoard({
        caseDescription: 'Test case for failure',
        firmId: '550e8400-e29b-41d4-a716-446655440000',
        clientId: '660e8400-e29b-41d4-a716-446655440001',
        jurisdiction: 'Florida',
        practiceArea: 'Criminal',
      });

      expect(result.status).toBe('failed');
      // At least one stage should have failed
      const failedStages = result.stages.filter((s) => s.status === 'failed');
      expect(failedStages.length).toBeGreaterThan(0);
    });

    it('should throw when API key is missing', async () => {
      delete process.env.GOOGLE_AI_API_KEY;

      const { executeMurderBoard } = await import('../lib/orchestrator/murder-board-v2');

      const result = await executeMurderBoard({
        caseDescription: 'Test case without API key',
        firmId: '550e8400-e29b-41d4-a716-446655440000',
        clientId: '660e8400-e29b-41d4-a716-446655440001',
        jurisdiction: 'California',
        practiceArea: 'Employment',
      });

      expect(result.status).toBe('failed');
      const failedStage = result.stages.find((s) => s.status === 'failed');
      expect(failedStage?.error).toContain('GOOGLE_AI_API_KEY');
    });

    it('should record duration for each stage', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            candidates: [
              { content: { parts: [{ text: '{"ok": true, "decision": "APPROVED"}' }] } },
            ],
          }),
      });

      const { executeMurderBoard } = await import('../lib/orchestrator/murder-board-v2');

      const result = await executeMurderBoard({
        caseDescription: 'Duration test',
        firmId: '550e8400-e29b-41d4-a716-446655440000',
        clientId: '660e8400-e29b-41d4-a716-446655440001',
        jurisdiction: 'California',
        practiceArea: 'Employment',
      });

      for (const stage of result.stages) {
        if (stage.status === 'completed') {
          expect(stage.durationMs).toBeDefined();
          expect(stage.durationMs).toBeGreaterThanOrEqual(0);
        }
      }
    });
  });

  describe('createMurderBoardSSEStream', () => {
    it('should create a readable stream', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            candidates: [
              { content: { parts: [{ text: '{"ok": true, "decision": "APPROVED"}' }] } },
            ],
          }),
      });

      const { createMurderBoardSSEStream } = await import('../lib/orchestrator/murder-board-v2');

      const stream = createMurderBoardSSEStream({
        caseDescription: 'SSE stream test',
        firmId: '550e8400-e29b-41d4-a716-446655440000',
        clientId: '660e8400-e29b-41d4-a716-446655440001',
        jurisdiction: 'California',
        practiceArea: 'Employment',
      });

      expect(stream).toBeInstanceOf(ReadableStream);
    });
  });
});

// ─── War Room Prompts Tests ──────────────────────────────────────────

describe('War Room Prompts', () => {
  it('should build prompts for all 7 stages', async () => {
    const { generateFullPipelinePrompts } = await import('../lib/prompts/war-room-prompts');

    const prompts = generateFullPipelinePrompts('Test case', 'flash');
    expect(prompts).toHaveLength(7);

    const stageNames = prompts.map((p) => p.stage);
    expect(stageNames).toEqual([
      'EXTRACTION',
      'CONFLICT_CHECK',
      'VIABILITY_SCORING',
      'FEE_STRUCTURE',
      'ORACLE_MEMO',
      'RETAINER_DRAFT',
      'RISK_GATE',
    ]);
  });

  it('should apply prompt repetition for non-reasoning tiers', async () => {
    const { buildMurderBoardPrompt } = await import('../lib/prompts/war-room-prompts');

    const flashPrompt = buildMurderBoardPrompt('EXTRACTION', 'Test input', 'flash');
    expect(flashPrompt.system).toContain('INSTRUCTION EMPHASIS');

    const litePrompt = buildMurderBoardPrompt('EXTRACTION', 'Test input', 'lite');
    expect(litePrompt.system).toContain('INSTRUCTION EMPHASIS');
  });

  it('should NOT apply prompt repetition for reasoning tier', async () => {
    const { buildMurderBoardPrompt } = await import('../lib/prompts/war-room-prompts');

    const reasoningPrompt = buildMurderBoardPrompt('EXTRACTION', 'Test input', 'reasoning');
    // The system prompt already contains INSTRUCTION EMPHASIS inline, but
    // the wrapper should NOT add an additional block with the user input
    const additionalRepetitions = (reasoningPrompt.system.match(/Test input/g) || []).length;
    expect(additionalRepetitions).toBe(0);
  });

  it('should include all critical elements in RISK_GATE prompt', async () => {
    const { MURDER_BOARD_PROMPTS } = await import('../lib/prompts/war-room-prompts');

    const riskPrompt = MURDER_BOARD_PROMPTS.RISK_GATE.system;
    expect(riskPrompt).toContain('APPROVED');
    expect(riskPrompt).toContain('CONDITIONAL_APPROVAL');
    expect(riskPrompt).toContain('REJECTED');
    expect(riskPrompt).toContain('Judge 6');
    expect(riskPrompt).toContain('malpractice');
  });
});
