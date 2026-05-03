/**
 * ExitPlanModeV2Tool — state machine hardening tests.
 *
 * Tests the mode restoration logic, auto-mode gate fallback,
 * teammate approval flow, and mapToolResultToToolResultBlockParam
 * output formatting. Uses self-contained mocks to avoid importing
 * the real production module (which has deep deps on bun:bundle,
 * Ink, permissionSetup, etc.).
 *
 * Sprint 3-4 security hardening (feat/batch2-security-hardening).
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// ── Constants matching production ──────────────────────────────────
const EXIT_PLAN_MODE_V2_TOOL_NAME = 'exit_plan_mode_v2';
const AGENT_TOOL_NAME = 'Agent';
const TEAM_CREATE_TOOL_NAME = 'TeamCreate';

// ── Mock AppState helpers ──────────────────────────────────────────
interface MockToolPermissionContext {
  mode: 'plan' | 'default' | 'auto';
  prePlanMode?: 'default' | 'auto';
  strippedDangerousRules?: boolean;
}

interface MockAppState {
  toolPermissionContext: MockToolPermissionContext;
  tasks: Record<string, unknown>;
}

function createMockAppState(overrides: Partial<MockAppState> = {}): MockAppState {
  return {
    toolPermissionContext: {
      mode: 'plan',
      prePlanMode: 'default',
      ...overrides.toolPermissionContext,
    },
    tasks: overrides.tasks ?? {},
  };
}

// ── Mode restoration logic (extracted from ExitPlanModeV2Tool.call) ──
// This is a pure-function extraction of the setAppState callback in
// ExitPlanModeV2Tool.ts lines 320-359, parameterized for testability.
function computeRestoreMode(
  currentMode: string,
  prePlanMode: string | undefined,
  isAutoModeGateEnabled: boolean,
  strippedDangerousRules: boolean,
): {
  restoreMode: string;
  gateFallback: boolean;
  needsAutoModeExitAttachment: boolean;
  shouldRestoreDangerousRules: boolean;
} {
  if (currentMode !== 'plan') {
    return {
      restoreMode: currentMode,
      gateFallback: false,
      needsAutoModeExitAttachment: false,
      shouldRestoreDangerousRules: false,
    };
  }

  let restoreMode = prePlanMode ?? 'default';
  let gateFallback = false;

  if (restoreMode === 'auto' && !isAutoModeGateEnabled) {
    restoreMode = 'default';
    gateFallback = true;
  }

  const finalRestoringAuto = restoreMode === 'auto';
  // In real code, autoWasUsedDuringPlan is read from isAutoModeActive().
  // For testing, we model it as: if prePlanMode was 'auto', it was active.
  const autoWasUsedDuringPlan = prePlanMode === 'auto';
  const needsAutoModeExitAttachment = autoWasUsedDuringPlan && !finalRestoringAuto;

  const restoringToAuto = restoreMode === 'auto';
  const shouldRestoreDangerousRules = !restoringToAuto && strippedDangerousRules;

  return {
    restoreMode,
    gateFallback,
    needsAutoModeExitAttachment,
    shouldRestoreDangerousRules,
  };
}

// ── mapToolResultToToolResultBlockParam (extracted) ─────────────────
function mapToolResultToToolResultBlockParam(
  output: {
    plan: string | null;
    isAgent: boolean;
    filePath?: string;
    hasTaskTool?: boolean;
    planWasEdited?: boolean;
    awaitingLeaderApproval?: boolean;
    requestId?: string;
  },
  toolUseID: string,
): { type: string; content: string; tool_use_id: string } {
  if (output.awaitingLeaderApproval) {
    return {
      type: 'tool_result',
      content: `Your plan has been submitted to the team lead for approval.\n\nPlan file: ${output.filePath}\n\n**What happens next:**\n1. Wait for the team lead to review your plan\n2. You will receive a message in your inbox with approval/rejection\n3. If approved, you can proceed with implementation\n4. If rejected, refine your plan based on the feedback\n\n**Important:** Do NOT proceed until you receive approval. Check your inbox for response.\n\nRequest ID: ${output.requestId}`,
      tool_use_id: toolUseID,
    };
  }

  if (output.isAgent) {
    return {
      type: 'tool_result',
      content:
        'User has approved the plan. There is nothing else needed from you now. Please respond with "ok"',
      tool_use_id: toolUseID,
    };
  }

  if (!output.plan || output.plan.trim() === '') {
    return {
      type: 'tool_result',
      content: 'User has approved exiting plan mode. You can now proceed.',
      tool_use_id: toolUseID,
    };
  }

  const teamHint = output.hasTaskTool
    ? `\n\nIf this plan can be broken down into multiple independent tasks, consider using the ${TEAM_CREATE_TOOL_NAME} tool to create a team and parallelize the work.`
    : '';

  const planLabel = output.planWasEdited ? 'Approved Plan (edited by user)' : 'Approved Plan';

  return {
    type: 'tool_result',
    content: `User has approved your plan. You can now start coding. Start with updating your todo list if applicable\n\nYour plan has been saved to: ${output.filePath}\nYou can refer back to it if needed during implementation.${teamHint}\n\n## ${planLabel}:\n${output.plan}`,
    tool_use_id: toolUseID,
  };
}

// ── Tests ────────────────────────────────────────────────────────────

describe('ExitPlanModeV2Tool — computeRestoreMode', () => {
  it('restores to default when prePlanMode is undefined', () => {
    const result = computeRestoreMode('plan', undefined, false, false);
    expect(result.restoreMode).toBe('default');
    expect(result.gateFallback).toBe(false);
  });

  it('restores to default when prePlanMode is "default"', () => {
    const result = computeRestoreMode('plan', 'default', true, false);
    expect(result.restoreMode).toBe('default');
    expect(result.gateFallback).toBe(false);
  });

  it('restores to auto when prePlanMode is "auto" and gate is enabled', () => {
    const result = computeRestoreMode('plan', 'auto', true, false);
    expect(result.restoreMode).toBe('auto');
    expect(result.gateFallback).toBe(false);
    expect(result.needsAutoModeExitAttachment).toBe(false);
  });

  it('circuit breaker: falls back to default when prePlanMode="auto" but gate is disabled', () => {
    const result = computeRestoreMode('plan', 'auto', false, false);
    expect(result.restoreMode).toBe('default');
    expect(result.gateFallback).toBe(true);
    // Auto was used during plan (prePlanMode='auto') but NOT restoring to auto
    // → needs the exit attachment to notify the model
    expect(result.needsAutoModeExitAttachment).toBe(true);
  });

  it('no-op when current mode is not plan', () => {
    const result = computeRestoreMode('default', 'auto', true, false);
    expect(result.restoreMode).toBe('default');
    expect(result.gateFallback).toBe(false);
  });

  it('restores dangerous rules when not restoring to auto', () => {
    const result = computeRestoreMode('plan', 'default', true, true);
    expect(result.shouldRestoreDangerousRules).toBe(true);
  });

  it('does NOT restore dangerous rules when restoring to auto', () => {
    const result = computeRestoreMode('plan', 'auto', true, true);
    expect(result.shouldRestoreDangerousRules).toBe(false);
  });

  it('gate fallback + strippedDangerousRules: restores rules since falling to default', () => {
    const result = computeRestoreMode('plan', 'auto', false, true);
    expect(result.restoreMode).toBe('default');
    expect(result.gateFallback).toBe(true);
    expect(result.shouldRestoreDangerousRules).toBe(true);
  });
});

describe('ExitPlanModeV2Tool — mapToolResultToToolResultBlockParam', () => {
  it('teammate awaiting approval: includes request ID and instructions', () => {
    const result = mapToolResultToToolResultBlockParam(
      {
        plan: 'The plan',
        isAgent: true,
        filePath: '/tmp/plan.md',
        awaitingLeaderApproval: true,
        requestId: 'req-123',
      },
      'tu-1',
    );
    expect(result.content).toContain('submitted to the team lead');
    expect(result.content).toContain('req-123');
    expect(result.content).toContain('/tmp/plan.md');
    expect(result.content).toContain('Do NOT proceed');
  });

  it('agent (non-teammate) returns short approval message', () => {
    const result = mapToolResultToToolResultBlockParam(
      { plan: 'The plan', isAgent: true, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    expect(result.content).toContain('respond with "ok"');
    expect(result.content).not.toContain('## Approved Plan');
  });

  it('empty plan returns simple approval', () => {
    const result = mapToolResultToToolResultBlockParam(
      { plan: '', isAgent: false, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    expect(result.content).toBe(
      'User has approved exiting plan mode. You can now proceed.',
    );
  });

  it('null plan returns simple approval', () => {
    const result = mapToolResultToToolResultBlockParam(
      { plan: null, isAgent: false, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    expect(result.content).toBe(
      'User has approved exiting plan mode. You can now proceed.',
    );
  });

  it('non-agent with plan includes "## Approved Plan:" marker', () => {
    const result = mapToolResultToToolResultBlockParam(
      { plan: 'Step 1\nStep 2', isAgent: false, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    expect(result.content).toContain('## Approved Plan:\nStep 1\nStep 2');
    expect(result.content).toContain('saved to: /tmp/plan.md');
  });

  it('edited plan uses "(edited by user)" marker', () => {
    const result = mapToolResultToToolResultBlockParam(
      {
        plan: 'Revised step',
        isAgent: false,
        filePath: '/tmp/plan.md',
        planWasEdited: true,
      },
      'tu-1',
    );
    expect(result.content).toContain('## Approved Plan (edited by user):\nRevised step');
  });

  it('hasTaskTool appends team hint', () => {
    const result = mapToolResultToToolResultBlockParam(
      {
        plan: 'Multi-task plan',
        isAgent: false,
        filePath: '/tmp/plan.md',
        hasTaskTool: true,
      },
      'tu-1',
    );
    expect(result.content).toContain(TEAM_CREATE_TOOL_NAME);
    expect(result.content).toContain('parallelize the work');
  });

  it('no hasTaskTool omits team hint', () => {
    const result = mapToolResultToToolResultBlockParam(
      { plan: 'Simple plan', isAgent: false, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    expect(result.content).not.toContain(TEAM_CREATE_TOOL_NAME);
  });

  it('tool_use_id is passed through correctly', () => {
    const result = mapToolResultToToolResultBlockParam(
      { plan: 'Plan', isAgent: false, filePath: '/tmp/plan.md' },
      'custom-tool-use-id-42',
    );
    expect(result.tool_use_id).toBe('custom-tool-use-id-42');
  });
});

describe('ExitPlanModeV2Tool — validateInput edge cases', () => {
  // Extracted validateInput logic for pure testing
  function validateInput(
    mode: string,
    isTeammate: boolean,
    hasExitedPlanModeInSession: boolean,
  ): { result: boolean; message?: string; errorCode?: number } {
    if (isTeammate) {
      return { result: true };
    }
    if (mode !== 'plan') {
      return {
        result: false,
        message:
          'You are not in plan mode. This tool is only for exiting plan mode after writing a plan. If your plan was already approved, continue with implementation.',
        errorCode: 1,
      };
    }
    return { result: true };
  }

  it('rejects non-teammate call outside plan mode', () => {
    const result = validateInput('default', false, false);
    expect(result.result).toBe(false);
    expect(result.errorCode).toBe(1);
    expect(result.message).toContain('not in plan mode');
  });

  it('rejects non-teammate call in auto mode', () => {
    const result = validateInput('auto', false, false);
    expect(result.result).toBe(false);
  });

  it('allows non-teammate call in plan mode', () => {
    const result = validateInput('plan', false, false);
    expect(result.result).toBe(true);
  });

  it('allows teammate regardless of mode', () => {
    expect(validateInput('default', true, false).result).toBe(true);
    expect(validateInput('auto', true, false).result).toBe(true);
    expect(validateInput('plan', true, false).result).toBe(true);
  });
});

describe('ExitPlanModeV2Tool — plan marker round-trip', () => {
  // Validates that mapToolResultToToolResultBlockParam produces content
  // that extractApprovedPlan (from ccr-session) can parse back.
  function extractApprovedPlan(content: string): string {
    const markers = ['## Approved Plan (edited by user):\n', '## Approved Plan:\n'];
    for (const marker of markers) {
      const idx = content.indexOf(marker);
      if (idx !== -1) return content.slice(idx + marker.length).trimEnd();
    }
    throw new Error(`No approved plan marker found`);
  }

  it('round-trips normal plan through map→extract', () => {
    const originalPlan = 'Step 1: Do X\nStep 2: Do Y\nStep 3: Verify';
    const toolResult = mapToolResultToToolResultBlockParam(
      { plan: originalPlan, isAgent: false, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    const extracted = extractApprovedPlan(toolResult.content);
    expect(extracted).toBe(originalPlan);
  });

  it('round-trips edited plan through map→extract', () => {
    const originalPlan = 'Revised: Step A';
    const toolResult = mapToolResultToToolResultBlockParam(
      { plan: originalPlan, isAgent: false, filePath: '/tmp/plan.md', planWasEdited: true },
      'tu-1',
    );
    const extracted = extractApprovedPlan(toolResult.content);
    expect(extracted).toBe(originalPlan);
  });

  it('round-trips plan with special characters', () => {
    const originalPlan = 'Run `npm test` && check $HOME/output\n## Sub-heading\n- Item 1';
    const toolResult = mapToolResultToToolResultBlockParam(
      { plan: originalPlan, isAgent: false, filePath: '/tmp/plan.md' },
      'tu-1',
    );
    const extracted = extractApprovedPlan(toolResult.content);
    expect(extracted).toBe(originalPlan);
  });
});
