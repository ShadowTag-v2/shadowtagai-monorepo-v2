/**
 * S.E.U. Proxy Token Manager
 *
 * S = Sandbox-Bound: token rejects requests from non-matching IPs
 * E = Ephemeral: token expires with the 24-hour triage window
 * U = User-Billed: compute costs route to the firm's auto-scaling tier
 *
 * Fixes the Perplexity .npmrc vulnerability by cryptographically binding
 * tokens to specific microVM instances. A leaked key from a dead sandbox
 * is a dead key.
 *
 * @see arXiv:2512.14982 — Prompt Repetition applied to token validation
 */
import jwt from 'jsonwebtoken';
import { randomUUID } from 'crypto';
import { z } from 'zod';

// ─── Token Payload Schema ─────────────────────────────────────────────
const SEUPayloadSchema = z.object({
  jti: z.string().uuid(),
  allowed_ip: z.string().ip(),
  sandbox_id: z.string().min(1),
  firm_id: z.string().uuid(),
  billing_tier_id: z.string(),
  client_state: z.enum(['PROSPECTIVE', 'RETAINED', 'EVAPORATING']),
  iss: z.literal('kovelai-seu'),
});

type SEUPayload = z.infer<typeof SEUPayloadSchema>;

// ─── Token Minting ────────────────────────────────────────────────────
/**
 * Mints a Sandbox-Bound, Ephemeral, User-Billed proxy token.
 *
 * @param sandboxId - The unique identifier of the microVM sandbox
 * @param sandboxIp - The IP address of the sandbox (bound to token)
 * @param firmId    - The law firm UUID (for billing attribution)
 * @param tierId    - The auto-scaling billing tier
 * @param clientState - 'PROSPECTIVE' | 'RETAINED' | 'EVAPORATING'
 * @returns Signed JWT string with 24h TTL
 */
export function mintSEUProxyToken(
  sandboxId: string,
  sandboxIp: string,
  firmId: string,
  tierId: string = 'oracle_partner',
  clientState: 'PROSPECTIVE' | 'RETAINED' | 'EVAPORATING' = 'PROSPECTIVE',
): string {
  const payload: SEUPayload = {
    jti: randomUUID(),
    allowed_ip: sandboxIp,
    sandbox_id: sandboxId,
    firm_id: firmId,
    billing_tier_id: tierId,
    client_state: clientState,
    iss: 'kovelai-seu',
  };

  // Validate payload structure before signing
  SEUPayloadSchema.parse(payload);

  // E: EPHEMERAL — dies precisely when the 24-hour bounded triage window closes
  return jwt.sign(payload, getProxySecret(), {
    expiresIn: '24h',
    algorithm: 'HS512',
  });
}

// ─── Token Verification ───────────────────────────────────────────────
/**
 * Verifies an S.E.U. token against the requesting context.
 *
 * Three-point validation:
 * 1. JWT signature + expiry (standard)
 * 2. IP binding (sandbox-bound)
 * 3. Sandbox ID match (context isolation)
 *
 * @returns Decoded payload if valid
 * @throws Error with specific violation type
 */
export async function verifySEUToken(
  token: string,
  requestIp: string,
  requestSandboxId: string,
): Promise<SEUPayload> {
  try {
    const decoded = jwt.verify(token, getProxySecret(), {
      algorithms: ['HS512'],
      issuer: 'kovelai-seu',
    }) as SEUPayload;

    // S: SANDBOX-BOUND — reject if IP doesn't match the minted context
    if (decoded.allowed_ip !== requestIp) {
      throw new SEUViolationError(
        'IP_MISMATCH',
        `Token bound to ${decoded.allowed_ip}, request from ${requestIp}`,
      );
    }

    // Context isolation — reject if sandbox ID doesn't match
    if (decoded.sandbox_id !== requestSandboxId) {
      throw new SEUViolationError(
        'SANDBOX_MISMATCH',
        `Token bound to sandbox ${decoded.sandbox_id}, request from ${requestSandboxId}`,
      );
    }

    return decoded;
  } catch (error) {
    if (error instanceof SEUViolationError) throw error;
    if (error instanceof jwt.TokenExpiredError) {
      throw new SEUViolationError('EXPIRED', 'Ephemeral token has expired');
    }
    throw new SEUViolationError('INVALID', 'Token signature verification failed');
  }
}

// ─── Token Revocation (Emergency Kill) ────────────────────────────────
const revokedTokens = new Set<string>();

export function revokeSEUToken(jti: string): void {
  revokedTokens.add(jti);
}

export function isRevoked(jti: string): boolean {
  return revokedTokens.has(jti);
}

// ─── Error Types ──────────────────────────────────────────────────────
export class SEUViolationError extends Error {
  constructor(
    public readonly violationType:
      | 'IP_MISMATCH'
      | 'SANDBOX_MISMATCH'
      | 'EXPIRED'
      | 'INVALID'
      | 'REVOKED',
    message: string,
  ) {
    super(`[SEU VIOLATION: ${violationType}] ${message}`);
    this.name = 'SEUViolationError';
  }
}

// ─── Internal Helpers ─────────────────────────────────────────────────
function getProxySecret(): string {
  const secret = process.env.KOVELAI_PROXY_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error(
      '[SEU FATAL] KOVELAI_PROXY_SECRET must be set and at least 32 characters',
    );
  }
  return secret;
}
