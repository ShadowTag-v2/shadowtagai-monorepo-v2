/**
 * Firestore Persistence — Headless Approval Requests
 *
 * Stores attorney review approval records with HMAC-bound tokens
 * for ABA Rule 5.3 compliance audit trail.
 *
 * Collection: `approval_requests/{firmId}/{requestId}`
 * TTL: 90 days (configurable per firm)
 */

import { FieldValue, getFirestore, Timestamp } from "firebase-admin/firestore";

const db = getFirestore();

/** Approval Request Status */
type ApprovalStatus = "pending" | "approved" | "rejected" | "expired" | "auto_approved";

/** Approval Request Firestore Document */
interface ApprovalRequestDoc {
  requestId: string;
  firmId: string;
  sessionId: string;
  memoId: string;
  requestedBy: string; // System or paralegal email
  assignedTo: string; // Attorney email
  status: ApprovalStatus;
  channel: "slack" | "google_chat" | "email" | "in_app";
  proofOfReviewHash?: string; // HMAC-SHA256 of review action
  tokenHash: string; // Hash of the one-time approval token
  expiresAt: Timestamp;
  metadata: {
    memoTitle: string;
    memoWordCount: number;
    riskTier: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    modelUsed: string;
    clientMatter?: string;
  };
  createdAt: Timestamp;
  resolvedAt?: Timestamp;
  resolvedBy?: string;
  rejectionReason?: string;
}

/**
 * Create a new approval request in Firestore.
 */
export async function createApprovalRequest(params: {
  firmId: string;
  sessionId: string;
  memoId: string;
  assignedTo: string;
  channel: ApprovalRequestDoc["channel"];
  tokenHash: string;
  ttlMinutes: number;
  metadata: ApprovalRequestDoc["metadata"];
}): Promise<{ path: string; requestId: string }> {
  const requestId = `AR-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`;
  const expiresAt = Timestamp.fromMillis(Date.now() + params.ttlMinutes * 60_000);

  const doc: ApprovalRequestDoc = {
    requestId,
    firmId: params.firmId,
    sessionId: params.sessionId,
    memoId: params.memoId,
    requestedBy: "system",
    assignedTo: params.assignedTo,
    status: "pending",
    channel: params.channel,
    tokenHash: params.tokenHash,
    expiresAt,
    metadata: params.metadata,
    createdAt: Timestamp.now(),
  };

  const ref = db
    .collection("approval_requests")
    .doc(params.firmId)
    .collection("requests")
    .doc(requestId);

  await ref.set(doc);

  // Update firm-level pending count
  await db
    .collection("approval_requests")
    .doc(params.firmId)
    .set(
      { pendingCount: FieldValue.increment(1), lastRequestAt: Timestamp.now() },
      { merge: true },
    );

  return { path: ref.path, requestId };
}

/**
 * Resolve an approval request (approve/reject).
 */
export async function resolveApproval(params: {
  firmId: string;
  requestId: string;
  status: "approved" | "rejected";
  resolvedBy: string;
  proofOfReviewHash: string;
  rejectionReason?: string;
}): Promise<void> {
  const ref = db
    .collection("approval_requests")
    .doc(params.firmId)
    .collection("requests")
    .doc(params.requestId);

  await ref.update({
    status: params.status,
    resolvedAt: Timestamp.now(),
    resolvedBy: params.resolvedBy,
    proofOfReviewHash: params.proofOfReviewHash,
    rejectionReason: params.rejectionReason || null,
  });

  // Decrement pending count
  await db
    .collection("approval_requests")
    .doc(params.firmId)
    .set({ pendingCount: FieldValue.increment(-1) }, { merge: true });
}

/**
 * Expire all stale pending approvals for a firm.
 * Designed to run as a Cloud Tasks scheduled job.
 */
export async function expireStaleApprovals(firmId: string): Promise<number> {
  const snapshot = await db
    .collection("approval_requests")
    .doc(firmId)
    .collection("requests")
    .where("status", "==", "pending")
    .where("expiresAt", "<", Timestamp.now())
    .get();

  const batch = db.batch();
  let count = 0;

  for (const doc of snapshot.docs) {
    batch.update(doc.ref, {
      status: "expired",
      resolvedAt: Timestamp.now(),
      resolvedBy: "system:ttl_expiry",
    });
    count++;
  }

  if (count > 0) {
    await batch.commit();
    await db
      .collection("approval_requests")
      .doc(firmId)
      .set({ pendingCount: FieldValue.increment(-count) }, { merge: true });
  }

  return count;
}

/**
 * Get audit trail for compliance review.
 */
export async function getApprovalAuditTrail(
  firmId: string,
  options?: { sessionId?: string; limit?: number },
): Promise<ApprovalRequestDoc[]> {
  let query = db
    .collection("approval_requests")
    .doc(firmId)
    .collection("requests")
    .orderBy("createdAt", "desc");

  if (options?.sessionId) {
    query = query.where("sessionId", "==", options.sessionId) as typeof query;
  }

  const snapshot = await query.limit(options?.limit || 100).get();
  return snapshot.docs.map((doc) => doc.data() as ApprovalRequestDoc);
}
