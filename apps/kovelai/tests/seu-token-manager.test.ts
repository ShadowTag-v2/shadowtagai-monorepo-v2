/**
 * @fileoverview S.E.U. Proxy Token Manager — Vitest Test Suite
 *
 * Tests the Sandbox-Bound, Ephemeral, User-Billed token system.
 * Item #2 of the 22-sprint.
 *
 * @see lib/security/seu-token-manager.ts
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

// Mock jsonwebtoken
const mockSign = vi.fn().mockReturnValue('mock.jwt.token');
const mockVerify = vi.fn();

vi.mock('jsonwebtoken', () => ({
  default: {
    sign: (...args: unknown[]) => mockSign(...args),
    verify: (...args: unknown[]) => mockVerify(...args),
    TokenExpiredError: class TokenExpiredError extends Error {
      constructor() {
        super('jwt expired');
        this.name = 'TokenExpiredError';
      }
    },
  },
  sign: (...args: unknown[]) => mockSign(...args),
  verify: (...args: unknown[]) => mockVerify(...args),
  TokenExpiredError: class TokenExpiredError extends Error {
    constructor() {
      super('jwt expired');
      this.name = 'TokenExpiredError';
    }
  },
}));

// Mock crypto
vi.mock('crypto', () => ({
  randomUUID: () => '550e8400-e29b-41d4-a716-446655440000',
}));

describe('S.E.U. Token Manager', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.KOVELAI_PROXY_SECRET = 'a'.repeat(64);
  });

  afterEach(() => {
    delete process.env.KOVELAI_PROXY_SECRET;
    vi.restoreAllMocks();
  });

  describe('mintSEUProxyToken', () => {
    it('should mint a token with correct payload structure', async () => {
      const { mintSEUProxyToken } = await import('../lib/security/seu-token-manager');

      const token = mintSEUProxyToken(
        'sandbox-001',
        '192.168.1.100',
        '550e8400-e29b-41d4-a716-446655440000',
        'oracle_partner',
        'PROSPECTIVE',
      );

      expect(token).toBe('mock.jwt.token');
      expect(mockSign).toHaveBeenCalledWith(
        expect.objectContaining({
          sandbox_id: 'sandbox-001',
          allowed_ip: '192.168.1.100',
          firm_id: '550e8400-e29b-41d4-a716-446655440000',
          billing_tier_id: 'oracle_partner',
          client_state: 'PROSPECTIVE',
          iss: 'kovelai-seu',
        }),
        expect.any(String),
        expect.objectContaining({
          expiresIn: '24h',
          algorithm: 'HS512',
        }),
      );
    });

    it('should use default tier when not specified', async () => {
      const { mintSEUProxyToken } = await import('../lib/security/seu-token-manager');

      mintSEUProxyToken('sandbox-002', '10.0.0.1', '550e8400-e29b-41d4-a716-446655440000');

      expect(mockSign).toHaveBeenCalledWith(
        expect.objectContaining({
          billing_tier_id: 'oracle_partner',
          client_state: 'PROSPECTIVE',
        }),
        expect.any(String),
        expect.any(Object),
      );
    });

    it('should throw when KOVELAI_PROXY_SECRET is too short', async () => {
      process.env.KOVELAI_PROXY_SECRET = 'short';

      // Re-import to pick up new env
      vi.resetModules();
      const { mintSEUProxyToken } = await import('../lib/security/seu-token-manager');

      expect(() =>
        mintSEUProxyToken('sandbox-003', '10.0.0.1', '550e8400-e29b-41d4-a716-446655440000'),
      ).toThrow('KOVELAI_PROXY_SECRET');
    });

    it('should throw when KOVELAI_PROXY_SECRET is missing', async () => {
      delete process.env.KOVELAI_PROXY_SECRET;

      vi.resetModules();
      const { mintSEUProxyToken } = await import('../lib/security/seu-token-manager');

      expect(() =>
        mintSEUProxyToken('sandbox-004', '10.0.0.1', '550e8400-e29b-41d4-a716-446655440000'),
      ).toThrow('KOVELAI_PROXY_SECRET');
    });

    it('should include EVAPORATING state for Heppner sessions', async () => {
      const { mintSEUProxyToken } = await import('../lib/security/seu-token-manager');

      mintSEUProxyToken(
        'sandbox-005',
        '10.0.0.1',
        '550e8400-e29b-41d4-a716-446655440000',
        'oracle_partner',
        'EVAPORATING',
      );

      expect(mockSign).toHaveBeenCalledWith(
        expect.objectContaining({
          client_state: 'EVAPORATING',
        }),
        expect.any(String),
        expect.any(Object),
      );
    });
  });

  describe('verifySEUToken', () => {
    it('should verify a valid token with matching IP and sandbox', async () => {
      const validPayload = {
        jti: '550e8400-e29b-41d4-a716-446655440000',
        allowed_ip: '192.168.1.100',
        sandbox_id: 'sandbox-001',
        firm_id: '550e8400-e29b-41d4-a716-446655440000',
        billing_tier_id: 'oracle_partner',
        client_state: 'PROSPECTIVE',
        iss: 'kovelai-seu',
      };

      mockVerify.mockReturnValue(validPayload);

      const { verifySEUToken } = await import('../lib/security/seu-token-manager');

      const result = await verifySEUToken('valid.jwt.token', '192.168.1.100', 'sandbox-001');

      expect(result.firm_id).toBe('550e8400-e29b-41d4-a716-446655440000');
      expect(result.allowed_ip).toBe('192.168.1.100');
    });

    it('should reject token with IP mismatch', async () => {
      mockVerify.mockReturnValue({
        allowed_ip: '192.168.1.100',
        sandbox_id: 'sandbox-001',
      });

      const { verifySEUToken, SEUViolationError: _SEUViolationError } = await import(
        '../lib/security/seu-token-manager'
      );

      await expect(verifySEUToken('valid.jwt.token', '10.0.0.99', 'sandbox-001')).rejects.toThrow(
        'IP_MISMATCH',
      );
    });

    it('should reject token with sandbox mismatch', async () => {
      mockVerify.mockReturnValue({
        allowed_ip: '192.168.1.100',
        sandbox_id: 'sandbox-001',
      });

      const { verifySEUToken } = await import('../lib/security/seu-token-manager');

      await expect(
        verifySEUToken('valid.jwt.token', '192.168.1.100', 'wrong-sandbox'),
      ).rejects.toThrow('SANDBOX_MISMATCH');
    });

    it('should reject expired tokens', async () => {
      const TokenExpiredError = class extends Error {
        constructor() {
          super('jwt expired');
          this.name = 'TokenExpiredError';
        }
      };
      Object.defineProperty(TokenExpiredError, 'name', { value: 'TokenExpiredError' });
      mockVerify.mockImplementation(() => {
        throw new TokenExpiredError();
      });

      const { verifySEUToken } = await import('../lib/security/seu-token-manager');

      await expect(
        verifySEUToken('expired.jwt.token', '192.168.1.100', 'sandbox-001'),
      ).rejects.toThrow(/EXPIRED|expired/i);
    });
  });

  describe('Token Revocation', () => {
    it('should mark tokens as revoked', async () => {
      const { revokeSEUToken, isRevoked } = await import('../lib/security/seu-token-manager');

      const jti = '550e8400-e29b-41d4-a716-446655440000';

      expect(isRevoked(jti)).toBe(false);
      revokeSEUToken(jti);
      expect(isRevoked(jti)).toBe(true);
    });

    it('should not affect unrevoked tokens', async () => {
      const { isRevoked } = await import('../lib/security/seu-token-manager');

      expect(isRevoked('never-revoked-jti')).toBe(false);
    });
  });

  describe('SEUViolationError', () => {
    it('should include violation type in message', async () => {
      const { SEUViolationError } = await import('../lib/security/seu-token-manager');

      const error = new SEUViolationError('IP_MISMATCH', 'Test mismatch');
      expect(error.message).toContain('IP_MISMATCH');
      expect(error.violationType).toBe('IP_MISMATCH');
      expect(error.name).toBe('SEUViolationError');
    });
  });
});
