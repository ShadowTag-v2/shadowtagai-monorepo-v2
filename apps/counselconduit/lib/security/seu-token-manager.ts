/**
 * S.E.U. JWT Guard — Secure Execution Unit Token Manager
 * 
 * Generates and validates short-lived sandboxId tokens for CounselConduit
 * sandbox environments. Implements the privilege-preserving architecture
 * under Heppner (S.D.N.Y. 2026) compliance requirements.
 * 
 * Token lifecycle:
 * - Issued on sandbox creation (15-min TTL default)
 * - Contains: sandboxId, firmId, userId, scopes, privilegeLevel
 * - Rotated automatically before expiration
 * - Revocable via Firestore blacklist
 * 
 * @module seu-token-manager
 * @version 1.0.0
 */

import * as crypto from 'crypto';

// ============================================================================
// Types
// ============================================================================

export interface SEUTokenPayload {
  /** Unique sandbox execution ID */
  sandboxId: string;
  /** Law firm identifier */
  firmId: string;
  /** Authenticated user ID */
  userId: string;
  /** Granted scopes for this sandbox session */
  scopes: SEUScope[];
  /** Attorney-client privilege level */
  privilegeLevel: PrivilegeLevel;
  /** Token issuance timestamp (Unix seconds) */
  iat: number;
  /** Token expiration timestamp (Unix seconds) */
  exp: number;
  /** Token unique identifier for revocation */
  jti: string;
}

export type SEUScope =
  | 'sandbox:execute'
  | 'sandbox:read'
  | 'model:query'
  | 'model:stream'
  | 'document:ingest'
  | 'document:summarize'
  | 'billing:meter'
  | 'audit:read';

export type PrivilegeLevel =
  | 'attorney_work_product'  // Highest protection — opinion/strategy
  | 'attorney_client'        // Standard privilege — communications
  | 'confidential'           // Business-sensitive, non-privileged
  | 'public';                // No protection

export interface SEUTokenOptions {
  /** TTL in seconds (default: 900 = 15 minutes) */
  ttlSeconds?: number;
  /** Scopes to grant (default: ['sandbox:execute', 'model:query']) */
  scopes?: SEUScope[];
  /** Privilege level (default: 'attorney_client') */
  privilegeLevel?: PrivilegeLevel;
}

export interface TokenValidationResult {
  valid: boolean;
  payload?: SEUTokenPayload;
  error?: string;
  /** Time remaining in seconds (-1 if expired) */
  remainingSeconds: number;
}

// ============================================================================
// Constants
// ============================================================================

const DEFAULT_TTL_SECONDS = 900; // 15 minutes
const MAX_TTL_SECONDS = 3600;    // 1 hour absolute max
const MIN_TTL_SECONDS = 60;      // 1 minute minimum
const ROTATION_THRESHOLD = 0.2;  // Rotate when < 20% TTL remaining
const TOKEN_VERSION = 1;

const DEFAULT_SCOPES: SEUScope[] = ['sandbox:execute', 'model:query'];
const DEFAULT_PRIVILEGE: PrivilegeLevel = 'attorney_client';

// ============================================================================
// SEU Token Manager
// ============================================================================

export class SEUTokenManager {
  private readonly signingKey: Buffer;
  private readonly algorithm = 'sha256';

  /**
   * @param secret - HMAC signing secret (from GCP Secret Manager: MAGIC_LINK_SECRET)
   */
  constructor(secret: string) {
    if (!secret || secret.length < 32) {
      throw new Error('SEU signing secret must be at least 32 characters');
    }
    this.signingKey = Buffer.from(secret, 'utf-8');
  }

  /**
   * Issue a new SEU token for a sandbox session.
   */
  issue(
    sandboxId: string,
    firmId: string,
    userId: string,
    options: SEUTokenOptions = {}
  ): string {
    const ttl = this.clampTTL(options.ttlSeconds ?? DEFAULT_TTL_SECONDS);
    const now = Math.floor(Date.now() / 1000);

    const payload: SEUTokenPayload = {
      sandboxId,
      firmId,
      userId,
      scopes: options.scopes ?? DEFAULT_SCOPES,
      privilegeLevel: options.privilegeLevel ?? DEFAULT_PRIVILEGE,
      iat: now,
      exp: now + ttl,
      jti: crypto.randomUUID(),
    };

    return this.encode(payload);
  }

  /**
   * Validate and decode an SEU token.
   */
  validate(token: string): TokenValidationResult {
    try {
      const payload = this.decode(token);
      if (!payload) {
        return { valid: false, error: 'Invalid token format', remainingSeconds: -1 };
      }

      const now = Math.floor(Date.now() / 1000);

      if (payload.exp <= now) {
        return {
          valid: false,
          payload,
          error: `Token expired ${now - payload.exp}s ago`,
          remainingSeconds: -1,
        };
      }

      const remaining = payload.exp - now;
      return { valid: true, payload, remainingSeconds: remaining };
    } catch (err) {
      return {
        valid: false,
        error: `Token validation failed: ${(err as Error).message}`,
        remainingSeconds: -1,
      };
    }
  }

  /**
   * Check if a token should be rotated (< 20% TTL remaining).
   */
  shouldRotate(token: string): boolean {
    const result = this.validate(token);
    if (!result.valid || !result.payload) return true;

    const totalTTL = result.payload.exp - result.payload.iat;
    return result.remainingSeconds < totalTTL * ROTATION_THRESHOLD;
  }

  /**
   * Rotate a token — issue a new one with the same claims but fresh timestamps.
   */
  rotate(token: string, newTTL?: number): string | null {
    const result = this.validate(token);
    if (!result.payload) return null;

    return this.issue(
      result.payload.sandboxId,
      result.payload.firmId,
      result.payload.userId,
      {
        ttlSeconds: newTTL ?? (result.payload.exp - result.payload.iat),
        scopes: result.payload.scopes,
        privilegeLevel: result.payload.privilegeLevel,
      }
    );
  }

  /**
   * Extract sandboxId from token without full validation (for logging).
   */
  extractSandboxId(token: string): string | null {
    try {
      const payload = this.decode(token);
      return payload?.sandboxId ?? null;
    } catch {
      return null;
    }
  }

  // --------------------------------------------------------------------------
  // Private: Encoding / Decoding
  // --------------------------------------------------------------------------

  private encode(payload: SEUTokenPayload): string {
    const header = Buffer.from(JSON.stringify({ v: TOKEN_VERSION, alg: this.algorithm }))
      .toString('base64url');
    const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
    const signature = this.sign(`${header}.${body}`);

    return `${header}.${body}.${signature}`;
  }

  private decode(token: string): SEUTokenPayload | null {
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const [header, body, signature] = parts;

    // Verify signature
    const expectedSig = this.sign(`${header}.${body}`);
    if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSig))) {
      throw new Error('Invalid token signature');
    }

    // Decode header and verify version
    const headerObj = JSON.parse(Buffer.from(header, 'base64url').toString());
    if (headerObj.v !== TOKEN_VERSION) {
      throw new Error(`Unsupported token version: ${headerObj.v}`);
    }

    return JSON.parse(Buffer.from(body, 'base64url').toString());
  }

  private sign(data: string): string {
    return crypto
      .createHmac(this.algorithm, this.signingKey)
      .update(data)
      .digest('base64url');
  }

  private clampTTL(ttl: number): number {
    return Math.max(MIN_TTL_SECONDS, Math.min(MAX_TTL_SECONDS, ttl));
  }
}

// ============================================================================
// Factory — Singleton with lazy initialization
// ============================================================================

let _instance: SEUTokenManager | null = null;

/**
 * Get or create the SEU Token Manager singleton.
 * Secret is loaded from environment (MAGIC_LINK_SECRET via GCP Secret Manager).
 */
export function getSEUTokenManager(): SEUTokenManager {
  if (!_instance) {
    const secret = process.env.MAGIC_LINK_SECRET;
    if (!secret) {
      throw new Error(
        'MAGIC_LINK_SECRET not set. Load via: source scripts/load_mcp_secrets.sh'
      );
    }
    _instance = new SEUTokenManager(secret);
  }
  return _instance;
}
