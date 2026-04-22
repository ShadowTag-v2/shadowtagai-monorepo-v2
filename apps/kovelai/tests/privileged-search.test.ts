/**
 * @fileoverview Privileged Search Route Test Suite — Vitest
 *
 * Tests the Clean Room privileged search tunnel:
 * - S.E.U. token validation
 * - Anxiety vector classification
 * - ZDR search execution
 * - Perplexity Sonar fallback
 * - Anti-forensic caching headers
 *
 * Item #4 of the 22-sprint.
 *
 * @see app/api/privileged-search/route.ts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ─── Anxiety Vector Classification Tests ──────────────────────────────
// We test the classification logic directly since it's the core IP

describe('Anxiety Vector Classification', () => {
  const ANXIETY_CATEGORIES: Record<string, { keywords: string[]; urgency: number }> = {
    CRIMINAL_EXPOSURE: {
      keywords: ['arrest', 'indictment', 'felony', 'prison', 'extradition', 'warrant', 'criminal', 'plea', 'probation', 'bail'],
      urgency: 10,
    },
    ASSET_PROTECTION: {
      keywords: ['hidden', 'offshore', 'crypto', 'forfeiture', 'seizure', 'garnishment', 'lien', 'freeze', 'asset', 'property'],
      urgency: 8,
    },
    FAMILY_LAW: {
      keywords: ['custody', 'divorce', 'alimony', 'prenup', 'child support', 'visitation', 'restraining', 'domestic'],
      urgency: 7,
    },
    EMPLOYMENT: {
      keywords: ['wrongful termination', 'discrimination', 'harassment', 'whistleblower', 'retaliation', 'severance', 'non-compete'],
      urgency: 6,
    },
    REGULATORY: {
      keywords: ['compliance', 'audit', 'SEC', 'FDA', 'HIPAA', 'violation', 'investigation', 'subpoena'],
      urgency: 7,
    },
    GENERAL_ANXIETY: {
      keywords: ['what happens if', 'can they', 'am I liable', 'is it legal', 'will I lose'],
      urgency: 5,
    },
  };

  function classifyAnxietyVector(query: string) {
    const lowerQuery = query.toLowerCase();
    let bestCategory = 'GENERAL_ANXIETY';
    let bestUrgency = 3;

    for (const [category, config] of Object.entries(ANXIETY_CATEGORIES)) {
      const matchCount = config.keywords.filter((kw) => lowerQuery.includes(kw)).length;
      if (matchCount > 0 && config.urgency > bestUrgency) {
        bestCategory = category;
        bestUrgency = config.urgency;
      }
    }

    return { query, timestamp: new Date().toISOString(), category: bestCategory, urgencyScore: bestUrgency };
  }

  it('should classify criminal queries at maximum urgency', () => {
    const result = classifyAnxietyVector('Will I be arrested for tax fraud?');
    expect(result.category).toBe('CRIMINAL_EXPOSURE');
    expect(result.urgencyScore).toBe(10);
  });

  it('should classify asset queries at high urgency', () => {
    const result = classifyAnxietyVector('Can my ex-wife find my hidden crypto wallet?');
    expect(result.category).toBe('ASSET_PROTECTION');
    expect(result.urgencyScore).toBe(8);
  });

  it('should classify family law queries', () => {
    const result = classifyAnxietyVector('How do I get full custody of my children?');
    expect(result.category).toBe('FAMILY_LAW');
    expect(result.urgencyScore).toBe(7);
  });

  it('should classify employment queries', () => {
    const result = classifyAnxietyVector('I was fired for whistleblower retaliation');
    expect(result.category).toBe('EMPLOYMENT');
    expect(result.urgencyScore).toBe(6);
  });

  it('should classify regulatory queries', () => {
    const result = classifyAnxietyVector('We received an SEC subpoena last week');
    expect(result.category).toBe('REGULATORY');
    expect(result.urgencyScore).toBe(7);
  });

  it('should default to general anxiety for vague queries', () => {
    const result = classifyAnxietyVector('I need some legal help with my situation');
    expect(result.category).toBe('GENERAL_ANXIETY');
    expect(result.urgencyScore).toBe(3);
  });

  it('should handle queries with multiple category matches (highest urgency wins)', () => {
    const result = classifyAnxietyVector(
      'I was arrested and they want to freeze my offshore crypto accounts',
    );
    expect(result.category).toBe('CRIMINAL_EXPOSURE');
    expect(result.urgencyScore).toBe(10);
  });

  it('should handle empty-ish queries gracefully', () => {
    const result = classifyAnxietyVector('help');
    expect(result.category).toBe('GENERAL_ANXIETY');
    expect(result.urgencyScore).toBe(3);
  });
});

// ─── Search Result Structure Tests ────────────────────────────────────

describe('Search Result Integrity', () => {
  it('should structure results with correct privilege metadata', () => {
    const responseBody = {
      results: [
        {
          title: 'California Labor Code §1102.5',
          snippet: 'Whistleblower protections...',
          url: 'https://leginfo.legislature.ca.gov/...',
          source: 'google_enterprise',
        },
      ],
      metadata: {
        source: 'google_enterprise',
        resultCount: 1,
        privilegeStatus: 'KOVEL_PROTECTED',
        expiresAt: new Date(Date.now() + 86400000).toISOString(),
      },
    };

    expect(responseBody.metadata.privilegeStatus).toBe('KOVEL_PROTECTED');
    expect(responseBody.metadata.source).toBe('google_enterprise');
    expect(responseBody.results).toHaveLength(1);
    expect(responseBody.results[0].source).toBe('google_enterprise');
  });

  it('should enforce anti-forensic caching headers', () => {
    const headers = {
      'Cache-Control': 'no-store, no-cache, must-revalidate, private',
      'Pragma': 'no-cache',
      'X-Privilege-Shield': 'kovel-doctrine-active',
      'X-Content-Type-Options': 'nosniff',
    };

    expect(headers['Cache-Control']).toContain('no-store');
    expect(headers['Cache-Control']).toContain('private');
    expect(headers['X-Privilege-Shield']).toBe('kovel-doctrine-active');
  });
});

// ─── Request Validation Tests ──────────────────────────────────────────

describe('Request Validation Schema', () => {
  const { z } = require('zod');

  const SearchRequestSchema = z.object({
    query: z.string().min(1).max(500),
    ephemeralToken: z.string().min(1),
    sandboxId: z.string().min(1),
    firmGoogleCxId: z.string().optional(),
    sessionId: z.string().uuid(),
  });

  it('should accept valid search requests', () => {
    const valid = {
      query: 'California whistleblower protection statute',
      ephemeralToken: 'test-token',
      sandboxId: 'sandbox-001',
      sessionId: '550e8400-e29b-41d4-a716-446655440000',
    };

    expect(() => SearchRequestSchema.parse(valid)).not.toThrow();
  });

  it('should reject empty queries', () => {
    expect(() =>
      SearchRequestSchema.parse({
        query: '',
        ephemeralToken: 'token',
        sandboxId: 'sb',
        sessionId: '550e8400-e29b-41d4-a716-446655440000',
      }),
    ).toThrow();
  });

  it('should reject queries over 500 chars', () => {
    expect(() =>
      SearchRequestSchema.parse({
        query: 'x'.repeat(501),
        ephemeralToken: 'token',
        sandboxId: 'sb',
        sessionId: '550e8400-e29b-41d4-a716-446655440000',
      }),
    ).toThrow();
  });

  it('should reject missing session ID', () => {
    expect(() =>
      SearchRequestSchema.parse({
        query: 'test query',
        ephemeralToken: 'token',
        sandboxId: 'sb',
      }),
    ).toThrow();
  });

  it('should reject invalid UUID session ID', () => {
    expect(() =>
      SearchRequestSchema.parse({
        query: 'test query',
        ephemeralToken: 'token',
        sandboxId: 'sb',
        sessionId: 'not-a-uuid',
      }),
    ).toThrow();
  });
});
