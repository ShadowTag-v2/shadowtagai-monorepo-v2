/**
 * Firestore Persistence — Genesis Block Entries
 *
 * Stores cryptographic evidence hashes in Firestore for court-admissible
 * chain-of-custody records (FRE 901/902).
 *
 * Collection: `genesis_blocks/{firmId}/{blockId}`
 * TTL: Permanent (evidence records never expire)
 */

import { initializeApp, getApps, cert } from 'firebase-admin/app';
import { getFirestore, Timestamp, FieldValue } from 'firebase-admin/firestore';

// Initialize Firebase Admin (idempotent)
if (!getApps().length) {
  initializeApp({
    credential: cert(JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON || '{}')),
    projectId: process.env.GCLOUD_PROJECT || 'shadowtag-omega-v4',
  });
}

const db = getFirestore();

/** Genesis Block Firestore Document */
interface GenesisBlockDoc {
  blockId: string;
  firmId: string;
  sessionId: string;
  contentHash: string;       // SHA-256 of original content
  algorithm: 'sha256';
  c2paManifest?: string;     // C2PA manifest URI
  sourceType: 'query' | 'document' | 'transcript' | 'search_result';
  metadata: {
    fileName?: string;
    contentType?: string;
    byteLength: number;
    modelUsed?: string;
  };
  attestationRef?: string;   // Reference to Kovel attestation
  createdAt: Timestamp;
  createdBy: string;         // Attorney email
  chainPrevious?: string;    // Previous block hash for chain integrity
}

/**
 * Persist a genesis block to Firestore.
 * Returns the document path for audit reference.
 */
export async function persistGenesisBlock(params: {
  firmId: string;
  sessionId: string;
  contentHash: string;
  sourceType: GenesisBlockDoc['sourceType'];
  metadata: GenesisBlockDoc['metadata'];
  createdBy: string;
  c2paManifest?: string;
  attestationRef?: string;
  chainPrevious?: string;
}): Promise<{ path: string; blockId: string }> {
  const blockId = `GB-${Date.now()}-${params.contentHash.substring(0, 8)}`;

  const doc: GenesisBlockDoc = {
    blockId,
    firmId: params.firmId,
    sessionId: params.sessionId,
    contentHash: params.contentHash,
    algorithm: 'sha256',
    c2paManifest: params.c2paManifest,
    sourceType: params.sourceType,
    metadata: params.metadata,
    attestationRef: params.attestationRef,
    createdAt: Timestamp.now(),
    createdBy: params.createdBy,
    chainPrevious: params.chainPrevious,
  };

  const ref = db
    .collection('genesis_blocks')
    .doc(params.firmId)
    .collection('blocks')
    .doc(blockId);

  await ref.set(doc);

  // Update firm-level block count
  await db.collection('genesis_blocks').doc(params.firmId).set(
    { blockCount: FieldValue.increment(1), lastBlockAt: Timestamp.now() },
    { merge: true }
  );

  return { path: ref.path, blockId };
}

/**
 * Retrieve genesis block chain for a session (for audit/court).
 */
export async function getSessionChain(
  firmId: string,
  sessionId: string
): Promise<GenesisBlockDoc[]> {
  const snapshot = await db
    .collection('genesis_blocks')
    .doc(firmId)
    .collection('blocks')
    .where('sessionId', '==', sessionId)
    .orderBy('createdAt', 'asc')
    .get();

  return snapshot.docs.map((doc) => doc.data() as GenesisBlockDoc);
}

/**
 * Verify chain integrity by walking the hash chain.
 */
export async function verifyChainIntegrity(
  firmId: string,
  sessionId: string
): Promise<{ valid: boolean; brokenAt?: string }> {
  const chain = await getSessionChain(firmId, sessionId);

  for (let i = 1; i < chain.length; i++) {
    if (chain[i].chainPrevious !== chain[i - 1].contentHash) {
      return { valid: false, brokenAt: chain[i].blockId };
    }
  }

  return { valid: true };
}
