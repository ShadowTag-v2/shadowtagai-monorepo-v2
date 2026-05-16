import { describe, expect, it } from 'vitest';

/**
 * Tests for the pure-logic functions extracted from useForensicElo.
 * We test eloGain, deceptionTier, and priceMultiplier independently
 * since they are the core scoring engine behind the forensic economy.
 */

// --- Extracted pure functions (mirrors useForensicElo.ts internals) ---

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

// --- eloGain tests ---
describe('eloGain', () => {
  describe('correct votes (isCorrect = true)', () => {
    it('returns +1 for easy detections (foolRate <= 0.25)', () => {
      expect(eloGain(0.1, true)).toBe(1);
      expect(eloGain(0.0, true)).toBe(1);
      expect(eloGain(0.25, true)).toBe(1);
    });

    it('returns +5 for moderate detections (0.25 < foolRate <= 0.5)', () => {
      expect(eloGain(0.3, true)).toBe(5);
      expect(eloGain(0.5, true)).toBe(5);
    });

    it('returns +15 for hard detections (0.5 < foolRate <= 0.75)', () => {
      expect(eloGain(0.6, true)).toBe(15);
      expect(eloGain(0.75, true)).toBe(15);
    });

    it('returns +25 for expert detections (0.75 < foolRate <= 0.9)', () => {
      expect(eloGain(0.8, true)).toBe(25);
      expect(eloGain(0.9, true)).toBe(25);
    });

    it('returns +50 for god-tier detections (foolRate > 0.9)', () => {
      expect(eloGain(0.91, true)).toBe(50);
      expect(eloGain(0.99, true)).toBe(50);
      expect(eloGain(1.0, true)).toBe(50);
    });
  });

  describe('incorrect votes (isCorrect = false)', () => {
    it('returns -5 for missing obvious fakes (foolRate < 0.2)', () => {
      expect(eloGain(0.1, false)).toBe(-5);
      expect(eloGain(0.0, false)).toBe(-5);
      expect(eloGain(0.19, false)).toBe(-5);
    });

    it('returns -2 for missing harder content (foolRate >= 0.2)', () => {
      expect(eloGain(0.2, false)).toBe(-2);
      expect(eloGain(0.5, false)).toBe(-2);
      expect(eloGain(0.9, false)).toBe(-2);
      expect(eloGain(1.0, false)).toBe(-2);
    });
  });
});

// --- deceptionTier tests ---
describe('deceptionTier', () => {
  it('returns transparent for foolRate <= 0.25', () => {
    expect(deceptionTier(0.0)).toBe('transparent');
    expect(deceptionTier(0.1)).toBe('transparent');
    expect(deceptionTier(0.25)).toBe('transparent');
  });

  it('returns convincing for 0.25 < foolRate <= 0.5', () => {
    expect(deceptionTier(0.26)).toBe('convincing');
    expect(deceptionTier(0.5)).toBe('convincing');
  });

  it('returns expert for 0.5 < foolRate <= 0.75', () => {
    expect(deceptionTier(0.51)).toBe('expert');
    expect(deceptionTier(0.75)).toBe('expert');
  });

  it('returns god-tier for foolRate > 0.75', () => {
    expect(deceptionTier(0.76)).toBe('god-tier');
    expect(deceptionTier(0.99)).toBe('god-tier');
    expect(deceptionTier(1.0)).toBe('god-tier');
  });
});

// --- priceMultiplier tests ---
describe('priceMultiplier', () => {
  it('returns 0.5 for transparent tier (no bonus)', () => {
    expect(priceMultiplier('transparent')).toBe(0.5);
  });

  it('returns 1 for convincing tier', () => {
    expect(priceMultiplier('convincing')).toBe(1);
  });

  it('returns 2 for expert tier', () => {
    expect(priceMultiplier('expert')).toBe(2);
  });

  it('returns 6 for god-tier', () => {
    expect(priceMultiplier('god-tier')).toBe(6);
  });
});

// --- End-to-end scoring pipeline ---
describe('Pomelli → Elo Pipeline Integration', () => {
  it('maps a high-fool-rate video through the full tier + multiplier chain', () => {
    const foolRate = 0.92;
    const tier = deceptionTier(foolRate);
    const multiplier = priceMultiplier(tier);
    const voterElo = eloGain(foolRate, true);

    expect(tier).toBe('god-tier');
    expect(multiplier).toBe(6);
    expect(voterElo).toBe(50);
  });

  it('maps a low-fool-rate video through the full chain', () => {
    const foolRate = 0.1;
    const tier = deceptionTier(foolRate);
    const multiplier = priceMultiplier(tier);
    const voterElo = eloGain(foolRate, true);

    expect(tier).toBe('transparent');
    expect(multiplier).toBe(0.5);
    expect(voterElo).toBe(1);
  });

  it('penalizes a voter who missed an obvious fake', () => {
    const foolRate = 0.05; // Almost nobody was fooled
    const voterElo = eloGain(foolRate, false);
    expect(voterElo).toBe(-5); // Harsh penalty
  });

  it('gives mild penalty for missing hard content', () => {
    const foolRate = 0.8; // Most people were fooled too
    const voterElo = eloGain(foolRate, false);
    expect(voterElo).toBe(-2); // Mild — it was genuinely hard
  });
});
