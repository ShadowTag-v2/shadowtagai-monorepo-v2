/**
 * Kovel Attestation Receipt in Search Flow
 *
 * Item #15: Generate Kovel receipt after every privileged search session.
 *
 * This middleware wraps the privileged search to automatically generate
 * a Kovel attestation receipt at session end.
 *
 * @see lib/attestation/kovel-receipt.ts
 * @see app/api/privileged-search/route.ts
 */

import { generateKovelReceipt, type KovelReceiptInput } from '@/lib/attestation/kovel-receipt';
import { enqueueDeletionTasks, scheduleFullSessionCleanup } from '@/lib/compliance/gdpr-scheduler';

// ─── Types ──────────────────────────────────────────────────────────

export interface SessionSearchAccumulator {
  sessionId: string;
  firmId: string;
  queries: string[];
  modelUsed: string;
  jurisdictions: string[];
  sessionStart: Date;
  lastActivity: Date;
}

// ─── In-Memory Session Registry ─────────────────────────────────────
// Production: This moves to Redis/Firestore

const activeSessions = new Map<string, SessionSearchAccumulator>();

/**
 * Records a search query for a session's Kovel receipt.
 */
export function recordSearchQuery(
  sessionId: string,
  firmId: string,
  query: string,
  model: string,
  jurisdiction: string,
): void {
  const existing = activeSessions.get(sessionId);

  if (existing) {
    existing.queries.push(query);
    existing.lastActivity = new Date();
    if (!existing.jurisdictions.includes(jurisdiction)) {
      existing.jurisdictions.push(jurisdiction);
    }
  } else {
    activeSessions.set(sessionId, {
      sessionId,
      firmId,
      queries: [query],
      modelUsed: model,
      jurisdictions: [jurisdiction],
      sessionStart: new Date(),
      lastActivity: new Date(),
    });
  }
}

/**
 * Closes a session and generates the Kovel attestation receipt.
 *
 * This is called when:
 * 1. Dead Man's Switch fires (timeout)
 * 2. Client explicitly ends session
 * 3. S.E.U. token expires
 */
export async function closeSessionAndGenerateReceipt(
  sessionId: string,
  hmacSecret: string,
): Promise<{
  receipt: Awaited<ReturnType<typeof generateKovelReceipt>> | null;
  gdprScheduled: boolean;
}> {
  const session = activeSessions.get(sessionId);
  if (!session) {
    return { receipt: null, gdprScheduled: false };
  }

  // Generate Kovel receipt
  const transcriptContent = session.queries.join('\n---\n');

  const receiptInput: KovelReceiptInput = {
    sessionId: session.sessionId,
    firmId: session.firmId,
    transcriptContent,
    queryCount: session.queries.length,
    modelUsed: session.modelUsed,
    jurisdictions: session.jurisdictions,
    sessionStart: session.sessionStart,
    sessionEnd: new Date(),
  };

  const receipt = await generateKovelReceipt(receiptInput, hmacSecret);

  // Schedule GDPR cleanup (30-day TTL)
  let gdprScheduled = false;
  try {
    const deletionTasks = scheduleFullSessionCleanup(session.firmId, session.sessionId, 30);
    const result = await enqueueDeletionTasks(deletionTasks);
    gdprScheduled = result.enqueued > 0;
  } catch (_err) {}

  // Remove from active sessions
  activeSessions.delete(sessionId);

  return { receipt, gdprScheduled };
}

/**
 * Gets the active session count (for monitoring).
 */
export function getActiveSessionCount(): number {
  return activeSessions.size;
}

/**
 * Cleans up stale sessions (cron job, every 15 min).
 */
export async function cleanupStaleSessions(
  hmacSecret: string,
  maxAgeMins = 120,
): Promise<{ cleaned: number }> {
  const cutoff = Date.now() - maxAgeMins * 60 * 1000;
  let cleaned = 0;

  for (const [sessionId, session] of activeSessions.entries()) {
    if (session.lastActivity.getTime() < cutoff) {
      await closeSessionAndGenerateReceipt(sessionId, hmacSecret);
      cleaned++;
    }
  }

  return { cleaned };
}
