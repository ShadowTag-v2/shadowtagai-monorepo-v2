/**
 * S.E.U. Token System — Sandbox-bound, Ephemeral, User-billed
 *
 * Sprint Item #6: Core privilege token architecture.
 *
 * Each S.E.U. token:
 * 1. Is cryptographically bound to a client IP + firm_id
 * 2. Expires in 24 hours (configurable per tier)
 * 3. Tracks usage for per-user billing attribution
 * 4. Can be revoked instantly (one API call)
 *
 * @see CLE seminar deck — Slide 7
 * @see Cor.30 Pillar 1 — Identity & Session
 */

import { z } from 'zod';

// ─── Types ──────────────────────────────────────────────────────────

export const SEUTokenSchema = z.object({
  tokenId: z.string().uuid(),
  firmId: z.string().uuid(),
  clientId: z.string().uuid(),
  ipHash: z.string(), // SHA-256 hash of client IP — never store raw IP
  issuedAt: z.string().datetime(),
  expiresAt: z.string().datetime(),
  tier: z.enum(['solo', 'practice', 'enterprise']),
  scope: z.array(
    z.enum([
      'privileged_search',
      'murder_board',
      'anxiety_radar',
      'oracle_memo',
      'byok_management',
    ]),
  ),
  usageTokens: z.number().int().default(0),
  revoked: z.boolean().default(false),
});

export type SEUToken = z.infer<typeof SEUTokenSchema>;

// ─── TTL Configuration ──────────────────────────────────────────────

const TTL_BY_TIER: Record<SEUToken['tier'], number> = {
  solo: 24 * 60 * 60 * 1000, // 24 hours
  practice: 12 * 60 * 60 * 1000, // 12 hours
  enterprise: 8 * 60 * 60 * 1000, // 8 hours (tighter for compliance)
};

const DEFAULT_SCOPES: Record<SEUToken['tier'], SEUToken['scope']> = {
  solo: ['privileged_search', 'anxiety_radar'],
  practice: ['privileged_search', 'murder_board', 'anxiety_radar', 'oracle_memo'],
  enterprise: [
    'privileged_search',
    'murder_board',
    'anxiety_radar',
    'oracle_memo',
    'byok_management',
  ],
};

// ─── Token Minting ──────────────────────────────────────────────────

export interface MintTokenRequest {
  firmId: string;
  clientId: string;
  clientIp: string;
  tier: SEUToken['tier'];
  customScopes?: SEUToken['scope'];
  customTtlMs?: number;
}

/**
 * Mints a new S.E.U. token.
 *
 * The token is NOT a JWT — it's a server-side reference token
 * stored in Firestore. This prevents client-side tampering and
 * allows instant revocation.
 */
export async function mintSEUToken(request: MintTokenRequest): Promise<SEUToken> {
  const now = new Date();
  const ttl = request.customTtlMs ?? TTL_BY_TIER[request.tier];
  const expiresAt = new Date(now.getTime() + ttl);

  // Hash the IP — never store raw
  const ipHash = await hashIP(request.clientIp);

  const token: SEUToken = {
    tokenId: crypto.randomUUID(),
    firmId: request.firmId,
    clientId: request.clientId,
    ipHash,
    issuedAt: now.toISOString(),
    expiresAt: expiresAt.toISOString(),
    tier: request.tier,
    scope: request.customScopes ?? DEFAULT_SCOPES[request.tier],
    usageTokens: 0,
    revoked: false,
  };

  console.log(
    `[S.E.U.] Minted token ${token.tokenId} for firm ${token.firmId} | TTL: ${ttl / 1000}s`,
  );

  return token;
}

// ─── Token Validation ───────────────────────────────────────────────

export interface ValidationResult {
  valid: boolean;
  reason?: string;
  token?: SEUToken;
}

/**
 * Validates an S.E.U. token against:
 * 1. Existence
 * 2. Expiry
 * 3. Revocation status
 * 4. IP binding
 * 5. Scope authorization
 */
export async function validateSEUToken(
  tokenId: string,
  clientIp: string,
  requiredScope: SEUToken['scope'][number],
  lookupFn: (tokenId: string) => Promise<SEUToken | null>,
): Promise<ValidationResult> {
  // 1. Existence
  const token = await lookupFn(tokenId);
  if (!token) {
    return { valid: false, reason: 'TOKEN_NOT_FOUND' };
  }

  // 2. Revocation
  if (token.revoked) {
    return { valid: false, reason: 'TOKEN_REVOKED' };
  }

  // 3. Expiry
  if (new Date(token.expiresAt) < new Date()) {
    return { valid: false, reason: 'TOKEN_EXPIRED' };
  }

  // 4. IP binding
  const currentIpHash = await hashIP(clientIp);
  if (token.ipHash !== currentIpHash) {
    return { valid: false, reason: 'IP_MISMATCH' };
  }

  // 5. Scope
  if (!token.scope.includes(requiredScope)) {
    return { valid: false, reason: 'SCOPE_UNAUTHORIZED' };
  }

  return { valid: true, token };
}

// ─── Token Revocation ───────────────────────────────────────────────

/**
 * Revokes all tokens for a firm. One API call.
 *
 * @returns Number of tokens revoked
 */
export async function revokeFirmTokens(
  firmId: string,
  lookupAllFn: (firmId: string) => Promise<SEUToken[]>,
  updateFn: (tokenId: string, patch: Partial<SEUToken>) => Promise<void>,
): Promise<number> {
  const tokens = await lookupAllFn(firmId);
  let revoked = 0;

  for (const token of tokens) {
    if (!token.revoked) {
      await updateFn(token.tokenId, { revoked: true });
      revoked++;
    }
  }

  console.log(`[S.E.U.] Revoked ${revoked} tokens for firm ${firmId}`);
  return revoked;
}

// ─── Usage Tracking ─────────────────────────────────────────────────

/**
 * Increments the usage counter on a token.
 * Used for per-user billing attribution.
 */
export async function trackTokenUsage(
  tokenId: string,
  tokensUsed: number,
  updateFn: (tokenId: string, patch: Partial<SEUToken>) => Promise<void>,
  lookupFn: (tokenId: string) => Promise<SEUToken | null>,
): Promise<void> {
  const token = await lookupFn(tokenId);
  if (!token) return;

  await updateFn(tokenId, {
    usageTokens: token.usageTokens + tokensUsed,
  });
}

// ─── Helpers ────────────────────────────────────────────────────────

async function hashIP(ip: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(ip);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}
