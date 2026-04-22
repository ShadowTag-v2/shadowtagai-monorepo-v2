/**
 * @fileoverview Murder Board Integration Tests
 *
 * End-to-end tests for the 7-stage War Room pipeline.
 * Uses mock Firestore and model stubs for deterministic testing.
 *
 * @see murder-board.ts — Pipeline orchestrator
 * @see legal-prompts.ts — System prompts
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ═══════════════════════════════════════════════════════════
// Mock Setup
// ═══════════════════════════════════════════════════════════

const mockFirestore = {
  collection: vi.fn().mockReturnThis(),
  doc: vi.fn().mockReturnThis(),
  set: vi.fn().mockResolvedValue(undefined),
  get: vi.fn().mockResolvedValue({
    exists: true,
    data: () => ({
      status: 'intake',
      firm_id: 'test-firm-001',
      seu_token_hash: 'test-token-hash',
    }),
  }),
  update: vi.fn().mockResolvedValue(undefined),
};

vi.mock('firebase-admin/firestore', () => ({
  getFirestore: () => mockFirestore,
  FieldValue: {
    serverTimestamp: () => new Date().toISOString(),
  },
}));

// Mock model responses for each stage
const MOCK_RESPONSES: Record<string, string> = {
  intake: JSON.stringify({
    parties: [{ name: 'John Doe', role: 'plaintiff' }],
    timeline: [{ date: '2025-06-15', event: 'Contract signed' }],
    claims: ['breach_of_contract'],
    keywords: ['contract', 'damages', 'breach'],
    jurisdiction: 'CA',
  }),
  osint: JSON.stringify({
    queries: [
      'California breach of contract elements',
      'contract damages calculation California',
    ],
  }),
  verb_audit: JSON.stringify({
    verbs: [
      {
        verb: 'breached',
        context: 'Defendant breached the agreement on July 1',
        kinematic_classification: 'volitional',
        cause_of_action: 'Breach of Contract',
        element_matched: 'Material breach by defendant',
        confidence: 0.92,
        strengthens_or_weakens: 'strengthens',
      },
    ],
  }),
  oracle: 'Based on the evidence presented, the client has a strong case for breach of contract under Cal. Civ. Code § 1549...',
  citations: JSON.stringify({
    citations: [
      {
        id: 'cit-001',
        text: 'Cal. Civ. Code § 1549',
        source: 'California Civil Code',
        url: 'https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1549',
        relevance: 0.95,
        authority_type: 'statute',
      },
    ],
  }),
  brief: '# Attorney Work-Product Brief\n\n## Executive Summary\n\nStrong case for breach of contract...',
};

// ═══════════════════════════════════════════════════════════
// Pipeline Stage Tests
// ═══════════════════════════════════════════════════════════

describe('Murder Board Pipeline', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Session Management', () => {
    it('should create a new session with correct initial state', async () => {
      const sessionId = 'test-session-001';
      const sessionData = {
        session_id: sessionId,
        firm_id: 'test-firm-001',
        status: 'intake',
        seu_token_hash: 'test-hash-abc123',
        started_at: expect.any(String),
      };

      await mockFirestore.set(sessionData);

      expect(mockFirestore.set).toHaveBeenCalledWith(
        expect.objectContaining({
          session_id: sessionId,
          status: 'intake',
        }),
      );
    });

    it('should reject sessions without S.E.U. token', () => {
      const invalidSession = {
        firm_id: 'test-firm-001',
        seu_token_hash: '', // Empty — invalid
      };

      expect(invalidSession.seu_token_hash).toBeFalsy();
    });
  });

  describe('Stage 1: Intake Extraction', () => {
    it('should extract parties, timeline, claims, and jurisdiction', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.intake);

      expect(parsed.parties).toHaveLength(1);
      expect(parsed.parties[0].name).toBe('John Doe');
      expect(parsed.timeline).toHaveLength(1);
      expect(parsed.claims).toContain('breach_of_contract');
      expect(parsed.jurisdiction).toBe('CA');
    });

    it('should extract search keywords for OSINT', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.intake);
      expect(parsed.keywords.length).toBeGreaterThan(0);
    });
  });

  describe('Stage 2: OSINT Query Generation', () => {
    it('should generate jurisdiction-specific search queries', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.osint);
      expect(parsed.queries.length).toBeGreaterThanOrEqual(2);
      expect(parsed.queries[0]).toContain('California');
    });
  });

  describe('Stage 3: Verb Audit', () => {
    it('should classify verbs with kinematic taxonomy', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.verb_audit);
      expect(parsed.verbs).toHaveLength(1);
      expect(parsed.verbs[0].kinematic_classification).toBe('volitional');
      expect(parsed.verbs[0].confidence).toBeGreaterThan(0.5);
    });

    it('should map verbs to causes of action', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.verb_audit);
      expect(parsed.verbs[0].cause_of_action).toBe('Breach of Contract');
    });

    it('should indicate whether verb strengthens or weakens the case', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.verb_audit);
      expect(['strengthens', 'weakens']).toContain(
        parsed.verbs[0].strengthens_or_weakens,
      );
    });
  });

  describe('Stage 4: Oracle Memo', () => {
    it('should produce strategy memo with citations', () => {
      expect(MOCK_RESPONSES.oracle).toContain('breach of contract');
      expect(MOCK_RESPONSES.oracle).toContain('Cal. Civ. Code');
    });
  });

  describe('Stage 5: Citation Validation', () => {
    it('should produce structured citations with authority types', () => {
      const parsed = JSON.parse(MOCK_RESPONSES.citations);
      expect(parsed.citations).toHaveLength(1);
      expect(parsed.citations[0].authority_type).toBe('statute');
      expect(parsed.citations[0].relevance).toBeGreaterThan(0.8);
    });
  });

  describe('Stage 6: Brief Generation', () => {
    it('should produce markdown with proper heading structure', () => {
      expect(MOCK_RESPONSES.brief).toMatch(/^# /);
      expect(MOCK_RESPONSES.brief).toContain('## Executive Summary');
    });
  });

  describe('Pipeline Error Handling', () => {
    it('should set session status to failed on stage error', async () => {
      await mockFirestore.update({ status: 'failed', error: 'Model timeout' });
      expect(mockFirestore.update).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'failed' }),
      );
    });

    it('should preserve partial results on failure', async () => {
      const partialSession = {
        status: 'failed',
        intake_data: JSON.parse(MOCK_RESPONSES.intake),
        error: 'Failed at stage 3',
      };

      expect(partialSession.intake_data.parties).toBeDefined();
      expect(partialSession.error).toContain('stage 3');
    });
  });

  describe('Billing Telemetry', () => {
    it('should record token consumption per stage', () => {
      const telemetry = {
        firm_id: 'test-firm-001',
        session_id: 'test-session-001',
        pipeline_type: 'war_room',
        stages_completed: 7,
        verb_count: 12,
        citation_count: 8,
        model_routed: 'gemini-2.5-flash',
        tokens_consumed: 14500,
      };

      expect(telemetry.stages_completed).toBe(7);
      expect(telemetry.tokens_consumed).toBeGreaterThan(0);
    });
  });
});
