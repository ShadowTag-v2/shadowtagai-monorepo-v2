import { describe, it, expect } from 'vitest';
import { generatePlanScaffold, renderPlanMarkdown } from '../../../src/commands/ultraplan.js';
import type { PlanPhase } from '../../../src/commands/ultraplan.js';

describe('Ultraplan: generatePlanScaffold', () => {
  it('generates 5 phases', () => {
    const phases = generatePlanScaffold();
    expect(phases).toHaveLength(5);
  });

  it('all phases start as pending', () => {
    const phases = generatePlanScaffold();
    expect(phases.every(p => p.status === 'pending')).toBe(true);
  });

  it('includes topic in content when provided', () => {
    const phases = generatePlanScaffold('Migrate to Firestore v2');
    expect(phases[0].content).toContain('Migrate to Firestore v2');
  });

  it('omits topic line when not provided', () => {
    const phases = generatePlanScaffold();
    expect(phases[0].content).not.toContain('**Topic:**');
  });

  it('phases have correct names', () => {
    const phases = generatePlanScaffold();
    expect(phases[0].name).toBe('Problem Decomposition');
    expect(phases[1].name).toBe('Solution Architecture');
    expect(phases[2].name).toBe('Risk Assessment');
    expect(phases[3].name).toBe('Implementation Plan');
    expect(phases[4].name).toBe('Validation Criteria');
  });

  it('each phase has a description', () => {
    const phases = generatePlanScaffold();
    expect(phases.every(p => p.description.length > 10)).toBe(true);
  });
});

describe('Ultraplan: renderPlanMarkdown', () => {
  it('renders header with title', () => {
    const phases = generatePlanScaffold();
    const md = renderPlanMarkdown(phases);
    expect(md).toContain('# Ultraplan');
    expect(md).toContain('STATE B Speculation');
  });

  it('renders all phase headers', () => {
    const phases = generatePlanScaffold();
    const md = renderPlanMarkdown(phases);
    expect(md).toContain('Phase 1: Problem Decomposition');
    expect(md).toContain('Phase 5: Validation Criteria');
  });

  it('includes topic when provided', () => {
    const phases = generatePlanScaffold('Auth refactor');
    const md = renderPlanMarkdown(phases, 'Auth refactor');
    expect(md).toContain('**Topic:** Auth refactor');
  });

  it('renders status icons for complete phases', () => {
    const phases: PlanPhase[] = [
      { name: 'Test', description: 'Testing', status: 'complete', content: 'Done' },
    ];
    const md = renderPlanMarkdown(phases);
    expect(md).toContain('✅');
  });

  it('renders pending icon for incomplete phases', () => {
    const phases: PlanPhase[] = [
      { name: 'Test', description: 'Testing', status: 'pending', content: '' },
    ];
    const md = renderPlanMarkdown(phases);
    expect(md).toContain('⏳');
  });

  it('includes duration when present', () => {
    const phases: PlanPhase[] = [
      { name: 'Test', description: 'Testing', status: 'complete', content: 'Done', durationMs: 150 },
    ];
    const md = renderPlanMarkdown(phases);
    expect(md).toContain('Duration: 150ms');
  });

  it('includes phase count in header', () => {
    const phases = generatePlanScaffold();
    const md = renderPlanMarkdown(phases);
    expect(md).toContain('**Phases:** 5');
  });
});
