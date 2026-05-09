/**
 * V19 Agent State — Firestore Checkpoint Manager
 *
 * Provides edge-native agent state persistence using Firestore
 * as the hippocampus layer. Enables crash-recovery, session
 * replay, and autonomous loop continuation.
 *
 * Runtime: Bun
 * Project: shadowtag-omega-v4
 */
import { Firestore, FieldValue, Timestamp } from '@google-cloud/firestore';

const PROJECT_ID = 'shadowtag-omega-v4';

const db = new Firestore({ projectId: PROJECT_ID });
const COLLECTION = 'agent_checkpoints';

// ─── Types ────────────────────────────────────────────────────────
interface AgentCheckpoint {
  agentId: string;
  sessionId: string;
  stepIndex: number;
  state: Record<string, unknown>;
  status: 'running' | 'paused' | 'completed' | 'failed';
  createdAt: Timestamp;
  updatedAt: Timestamp;
  metadata: {
    model: string;
    version: string;
    taskHash: string;
  };
}

// ─── Checkpoint Operations ────────────────────────────────────────

/**
 * Save a checkpoint for the current agent execution step.
 * Enables crash-recovery and session replay.
 */
export async function saveCheckpoint(
  agentId: string,
  sessionId: string,
  stepIndex: number,
  state: Record<string, unknown>,
  metadata: AgentCheckpoint['metadata']
): Promise<string> {
  const docId = `${agentId}_${sessionId}_${stepIndex}`;
  const checkpoint: Omit<AgentCheckpoint, 'createdAt' | 'updatedAt'> & {
    createdAt: FieldValue;
    updatedAt: FieldValue;
  } = {
    agentId,
    sessionId,
    stepIndex,
    state,
    status: 'running',
    createdAt: FieldValue.serverTimestamp(),
    updatedAt: FieldValue.serverTimestamp(),
    metadata,
  };

  await db.collection(COLLECTION).doc(docId).set(checkpoint, { merge: true });
  console.log(`⚡ [Checkpoint] Saved: ${docId} (step ${stepIndex})`);
  return docId;
}

/**
 * Retrieve the latest checkpoint for a given agent session.
 * Used for crash-recovery on agent restart.
 */
export async function getLatestCheckpoint(
  agentId: string,
  sessionId: string
): Promise<AgentCheckpoint | null> {
  const snapshot = await db
    .collection(COLLECTION)
    .where('agentId', '==', agentId)
    .where('sessionId', '==', sessionId)
    .orderBy('stepIndex', 'desc')
    .limit(1)
    .get();

  if (snapshot.empty) return null;

  const doc = snapshot.docs[0];
  return doc.data() as AgentCheckpoint;
}

/**
 * Mark a checkpoint as completed or failed.
 * Updates the status field for the specified checkpoint document.
 */
export async function finalizeCheckpoint(
  docId: string,
  status: 'completed' | 'failed'
): Promise<void> {
  await db.collection(COLLECTION).doc(docId).update({
    status,
    updatedAt: FieldValue.serverTimestamp(),
  });
  console.log(`⚡ [Checkpoint] Finalized: ${docId} → ${status}`);
}

/**
 * List all checkpoints for a session, ordered by step index.
 * Useful for session replay and debugging.
 */
export async function listSessionCheckpoints(
  agentId: string,
  sessionId: string
): Promise<AgentCheckpoint[]> {
  const snapshot = await db
    .collection(COLLECTION)
    .where('agentId', '==', agentId)
    .where('sessionId', '==', sessionId)
    .orderBy('stepIndex', 'asc')
    .get();

  return snapshot.docs.map((doc) => doc.data() as AgentCheckpoint);
}

/**
 * Prune old checkpoints beyond a retention window.
 * Keeps the system lean by removing stale state.
 */
export async function pruneOldCheckpoints(
  agentId: string,
  retentionDays: number = 7
): Promise<number> {
  const cutoff = Timestamp.fromDate(
    new Date(Date.now() - retentionDays * 86400000)
  );

  const snapshot = await db
    .collection(COLLECTION)
    .where('agentId', '==', agentId)
    .where('createdAt', '<', cutoff)
    .get();

  const batch = db.batch();
  for (const doc of snapshot.docs) {
    batch.delete(doc.ref);
  }
  await batch.commit();

  console.log(
    `⚡ [Checkpoint] Pruned ${snapshot.size} stale checkpoints for ${agentId}`
  );
  return snapshot.size;
}
