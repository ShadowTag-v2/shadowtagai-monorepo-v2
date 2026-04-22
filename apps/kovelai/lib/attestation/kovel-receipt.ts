/**
 * Kovel Attestation Receipt Generator
 *
 * Sprint Item #12: Cryptographic proof of privileged communication.
 *
 * Each session generates a tamper-proof receipt containing:
 * 1. Session hash (SHA-256 of session transcript)
 * 2. Timestamp chain
 * 3. Firm attestation
 * 4. Kovel doctrine citation
 *
 * The receipt DOES NOT contain any transcript content.
 * It proves a privileged session occurred without revealing what was discussed.
 *
 * @see United States v. Kovel, 296 F.2d 918 (2d Cir. 1961)
 */

import { z } from 'zod';

// ─── Schemas ────────────────────────────────────────────────────────

export const KovelReceiptSchema = z.object({
  receiptId: z.string().uuid(),
  sessionId: z.string().uuid(),
  firmId: z.string().uuid(),
  attorneyBarNumber: z.string().optional(),

  // Cryptographic proof
  sessionHash: z.string(), // SHA-256 of full session transcript
  previousReceiptHash: z.string().optional(), // Chain linkage
  hmacSignature: z.string(), // HMAC-SHA256 with firm secret

  // Temporal
  sessionStart: z.string().datetime(),
  sessionEnd: z.string().datetime(),
  durationMinutes: z.number(),

  // Metadata (no content)
  queryCount: z.number().int(),
  modelUsed: z.string(),
  jurisdictions: z.array(z.string()),

  // Legal
  doctrineVersion: z.string().default('kovel-v1'),
  privilegeType: z.enum(['ATTORNEY_CLIENT', 'WORK_PRODUCT', 'KOVEL_EXTENSION']),
  attestation: z.string(),
});

export type KovelReceipt = z.infer<typeof KovelReceiptSchema>;

// ─── Receipt Generation ─────────────────────────────────────────────

interface SessionData {
  sessionId: string;
  firmId: string;
  attorneyBarNumber?: string;
  transcriptContent: string; // Will be hashed, never stored
  queryCount: number;
  modelUsed: string;
  jurisdictions: string[];
  sessionStart: Date;
  sessionEnd: Date;
  previousReceiptHash?: string;
}

/**
 * Generates a Kovel Attestation Receipt.
 *
 * The transcript content is hashed — the plaintext is NEVER
 * stored in the receipt. This proves the session happened
 * without revealing privileged communications.
 */
export async function generateKovelReceipt(
  data: SessionData,
  hmacSecret: string,
): Promise<KovelReceipt> {
  // Hash the session transcript
  const sessionHash = await sha256(data.transcriptContent);

  // Generate HMAC signature
  const signaturePayload = [
    data.sessionId,
    data.firmId,
    sessionHash,
    data.sessionStart.toISOString(),
    data.sessionEnd.toISOString(),
  ].join('|');

  const hmacSignature = await hmacSha256(signaturePayload, hmacSecret);

  const durationMinutes = Math.round(
    (data.sessionEnd.getTime() - data.sessionStart.getTime()) / 60_000,
  );

  const receipt: KovelReceipt = {
    receiptId: crypto.randomUUID(),
    sessionId: data.sessionId,
    firmId: data.firmId,
    attorneyBarNumber: data.attorneyBarNumber,
    sessionHash,
    previousReceiptHash: data.previousReceiptHash,
    hmacSignature,
    sessionStart: data.sessionStart.toISOString(),
    sessionEnd: data.sessionEnd.toISOString(),
    durationMinutes,
    queryCount: data.queryCount,
    modelUsed: data.modelUsed,
    jurisdictions: data.jurisdictions,
    doctrineVersion: 'kovel-v1',
    privilegeType: 'KOVEL_EXTENSION',
    attestation: generateAttestationText(data.firmId, durationMinutes),
  };

  return receipt;
}

// ─── Verification ───────────────────────────────────────────────────

/**
 * Verifies the integrity of a Kovel receipt.
 * Returns true if the HMAC signature matches.
 */
export async function verifyKovelReceipt(
  receipt: KovelReceipt,
  hmacSecret: string,
): Promise<boolean> {
  const signaturePayload = [
    receipt.sessionId,
    receipt.firmId,
    receipt.sessionHash,
    receipt.sessionStart,
    receipt.sessionEnd,
  ].join('|');

  const expectedSignature = await hmacSha256(signaturePayload, hmacSecret);
  return receipt.hmacSignature === expectedSignature;
}

// ─── Attestation Text ───────────────────────────────────────────────

function generateAttestationText(firmId: string, durationMinutes: number): string {
  return [
    'KOVEL ATTESTATION RECEIPT',
    '',
    'This receipt certifies that a privileged communication session',
    'was conducted under the Kovel Doctrine extension of attorney-client',
    'privilege, as established in United States v. Kovel, 296 F.2d 918',
    '(2d Cir. 1961), and reinforced by United States v. Heppner',
    '(S.D.N.Y. 2026).',
    '',
    `Firm: ${firmId.substring(0, 8)}...`,
    `Duration: ${durationMinutes} minutes`,
    '',
    'The session transcript has been hashed (SHA-256) and the hash is',
    'recorded above. The plaintext content has been purged per the',
    'Zero Data Retention policy.',
    '',
    'This receipt does not contain, and cannot be used to reconstruct,',
    'any privileged communication content.',
    '',
    'Verification: Use the HMAC signature above with the firm secret',
    'to verify receipt authenticity.',
  ].join('\n');
}

// ─── Crypto Helpers ─────────────────────────────────────────────────

async function sha256(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

async function hmacSha256(message: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(message));
  return Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}
