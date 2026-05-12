/**
 * Boundary tests for the Forensic Elo scoring functions.
 *
 * Tests exact threshold values (0.2, 0.25, 0.5, 0.75, 0.9)
 * to ensure deterministic tier/gain classification at edges.
 */
import { describe, expect, it } from 'vitest';

// Re-implement the pure functions from useForensicElo for isolated testing.
// These mirror the hook's internal functions exactly.

type DeceptionTier = 'transparent' | 'convincing' | 'expert' | 'god-tier';

function eloGain(foolRate: number, isCorrect: boolean): number {
  if (!isCorrect) return foolRate < 0.2 ? -5 : -2;
  if (foolRate > 0.9) return 50;
  if (foolRate > 0.75) return 25;
  if (foolRate > 0.5) return 15;
  if (foolRate > 0.25) return 5;
  return 1;
}

function deceptionTier(foolRate: number): DeceptionTier {
  if (foolRate > 0.75) return 'god-tier';
  if (foolRate > 0.5) return 'expert';
  if (foolRate > 0.25) return 'convincing';
  return 'transparent';
}

function priceMultiplier(tier: DeceptionTier): number {
  switch (tier) {
    case 'god-tier':
      return 6;
    case 'expert':
      return 2;
    case 'convincing':
      return 1;
    default:
      return 0.5;
  }
}

describe('eloGain — boundary values', () => {
  // ---- Correct votes at exact thresholds ----
  it('foolRate=0.0 correct → +1 (transparent floor)', () => {
    expect(eloGain(0.0, true)).toBe(1);
  });

  it('foolRate=0.2 correct → +1 (≤0.25 band)', () => {
    expect(eloGain(0.2, true)).toBe(1);
  });

  it('foolRate=0.25 correct → +1 (boundary: NOT >0.25)', () => {
    expect(eloGain(0.25, true)).toBe(1);
  });

  it('foolRate=0.251 correct → +5 (just over 0.25)', () => {
    expect(eloGain(0.251, true)).toBe(5);
  });

  it('foolRate=0.5 correct → +5 (boundary: NOT >0.5)', () => {
    expect(eloGain(0.5, true)).toBe(5);
  });

  it('foolRate=0.501 correct → +15 (just over 0.5)', () => {
    expect(eloGain(0.501, true)).toBe(15);
  });

  it('foolRate=0.75 correct → +15 (boundary: NOT >0.75)', () => {
    expect(eloGain(0.75, true)).toBe(15);
  });

  it('foolRate=0.751 correct → +25 (just over 0.75)', () => {
    expect(eloGain(0.751, true)).toBe(25);
  });

  it('foolRate=0.9 correct → +25 (boundary: NOT >0.9)', () => {
    expect(eloGain(0.9, true)).toBe(25);
  });

  it('foolRate=0.901 correct → +50 (god-tier detection)', () => {
    expect(eloGain(0.901, true)).toBe(50);
  });

  it('foolRate=1.0 correct → +50 (max fool rate)', () => {
    expect(eloGain(1.0, true)).toBe(50);
  });

  // ---- Incorrect votes at boundary ----
  it('foolRate=0.19 incorrect → -5 (obvious miss penalty)', () => {
    expect(eloGain(0.19, false)).toBe(-5);
  });

  it('foolRate=0.2 incorrect → -2 (boundary: ≥0.2 = not obvious)', () => {
    expect(eloGain(0.2, false)).toBe(-2);
  });

  it('foolRate=0.0 incorrect → -5 (max obvious miss)', () => {
    expect(eloGain(0.0, false)).toBe(-5);
  });

  it('foolRate=0.5 incorrect → -2 (standard miss)', () => {
    expect(eloGain(0.5, false)).toBe(-2);
  });

  it('foolRate=1.0 incorrect → -2 (missed god-tier)', () => {
    expect(eloGain(1.0, false)).toBe(-2);
  });
});

describe('deceptionTier — boundary values', () => {
  it('foolRate=0.0 → transparent', () => {
    expect(deceptionTier(0.0)).toBe('transparent');
  });

  it('foolRate=0.25 → transparent (NOT >0.25)', () => {
    expect(deceptionTier(0.25)).toBe('transparent');
  });

  it('foolRate=0.251 → convincing', () => {
    expect(deceptionTier(0.251)).toBe('convincing');
  });

  it('foolRate=0.5 → convincing (NOT >0.5)', () => {
    expect(deceptionTier(0.5)).toBe('convincing');
  });

  it('foolRate=0.501 → expert', () => {
    expect(deceptionTier(0.501)).toBe('expert');
  });

  it('foolRate=0.75 → expert (NOT >0.75)', () => {
    expect(deceptionTier(0.75)).toBe('expert');
  });

  it('foolRate=0.751 → god-tier', () => {
    expect(deceptionTier(0.751)).toBe('god-tier');
  });

  it('foolRate=1.0 → god-tier', () => {
    expect(deceptionTier(1.0)).toBe('god-tier');
  });
});

describe('priceMultiplier — all tiers', () => {
  it('transparent → 0.5×', () => {
    expect(priceMultiplier('transparent')).toBe(0.5);
  });

  it('convincing → 1×', () => {
    expect(priceMultiplier('convincing')).toBe(1);
  });

  it('expert → 2×', () => {
    expect(priceMultiplier('expert')).toBe(2);
  });

  it('god-tier → 6×', () => {
    expect(priceMultiplier('god-tier')).toBe(6);
  });
});
