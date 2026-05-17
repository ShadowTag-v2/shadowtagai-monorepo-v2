/**
 * Headless Approval System — ABA Model Rule 5.3 Compliance
 *
 * Solves the "Unsupervised Agent Trap": If the Agent autonomously
 * drops a finished brief into Clio without lawyer review, the lawyer
 * commits Unauthorized Practice of Law (UPL).
 *
 * Because KovelAI is Agent-Native (no dashboard), we lost the physical
 * "Approve" button. This module re-introduces it as a Cryptographic
 * Proof of Review delivered via headless messaging (Slack, Google Chat,
 * Email).
 *
 * Flow:
 * 1. Agent completes work → calls requestApproval()
 * 2. Module sends structured approval request to lawyer
 * 3. Workflow PAUSES durably until lawyer responds
 * 4. Lawyer clicks [APPROVE & VAULT] → generates HMAC hash
 * 5. Hash satisfies ABA Rule 5.3 supervision mandate
 * 6. Agent resumes and delivers to CRM backend
 */

import { createHmac, randomUUID } from "node:crypto";

// ─── Types ──────────────────────────────────────────────────────

export interface ApprovalRequest {
  /** Unique approval request ID */
  id: string;
  /** Firm ID requesting approval */
  firmId: string;
  /** Type of deliverable */
  deliverableType:
    | "KINETIC_MURDER_BOARD"
    | "ORACLE_MEMO"
    | "CLIENT_BRIEF"
    | "TIME_ENTRY"
    | "CLE_CERTIFICATE";
  /** Human-readable summary for the lawyer */
  summary: string;
  /** Pre-signed URL to the full deliverable */
  deliverableUrl: string;
  /** Approval token (one-time use, HMAC-bound) */
  approvalToken: string;
  /** Expiration time for the approval request */
  expiresAt: string;
  /** Status */
  status: "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED";
  /** Timestamp of status change */
  statusChangedAt?: string;
  /** Proof of Review hash (set when approved) */
  proofOfReviewHash?: string;
  /** Channel where approval was requested */
  channel: "SLACK" | "GOOGLE_CHAT" | "EMAIL";
}

export interface ApprovalResponse {
  approved: boolean;
  proofOfReviewHash: string;
  reviewerEmail: string;
  reviewedAt: string;
  approvalRequestId: string;
}

// ─── In-Memory Registry ─────────────────────────────────────────

const approvalRequests = new Map<string, ApprovalRequest>();

// ─── Core Functions ─────────────────────────────────────────────

/**
 * Creates a headless approval request for a completed deliverable.
 *
 * In production, this sends a Slack Block Kit message (or Google Chat
 * card) with [APPROVE & VAULT] and [REJECT] buttons.
 */
export function createApprovalRequest(
  firmId: string,
  deliverableType: ApprovalRequest["deliverableType"],
  summary: string,
  deliverableUrl: string,
  channel: ApprovalRequest["channel"] = "SLACK",
  ttlMinutes: number = 60,
): ApprovalRequest {
  const id = randomUUID();
  const approvalToken = generateApprovalToken(id, firmId);
  const now = new Date();

  const request: ApprovalRequest = {
    id,
    firmId,
    deliverableType,
    summary,
    deliverableUrl,
    approvalToken,
    expiresAt: new Date(now.getTime() + ttlMinutes * 60 * 1000).toISOString(),
    status: "PENDING",
    channel,
  };

  approvalRequests.set(id, request);

  return request;
}

/**
 * Generates the Slack Block Kit payload for the approval message.
 * This is what the lawyer sees in their Slack channel.
 */
export function generateSlackBlockKit(request: ApprovalRequest): object {
  return {
    blocks: [
      {
        type: "header",
        text: {
          type: "plain_text",
          text: "🛡️ KovelAI Agent — Deliverable Ready for Review",
        },
      },
      { type: "divider" },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: [
            `*Type:* ${formatDeliverableType(request.deliverableType)}`,
            `*Summary:* ${request.summary}`,
            `*Expires:* ${new Date(request.expiresAt).toLocaleString()}`,
            "",
            "⚖️ _ABA Model Rule 5.3 requires attorney review before filing._",
          ].join("\n"),
        },
      },
      {
        type: "section",
        text: {
          type: "mrkdwn",
          text: `<${request.deliverableUrl}|📄 Review Full Deliverable>`,
        },
      },
      { type: "divider" },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: { type: "plain_text", text: "✅ APPROVE & VAULT" },
            style: "primary",
            action_id: "kovelai_approve",
            value: request.approvalToken,
          },
          {
            type: "button",
            text: { type: "plain_text", text: "❌ REJECT" },
            style: "danger",
            action_id: "kovelai_reject",
            value: request.id,
          },
        ],
      },
      {
        type: "context",
        elements: [
          {
            type: "mrkdwn",
            text: `Request ID: \`${request.id}\` | Approval generates cryptographic Proof of Review`,
          },
        ],
      },
    ],
  };
}

/**
 * Processes an approval response from the lawyer.
 *
 * When the lawyer clicks [APPROVE & VAULT], this:
 * 1. Validates the one-time approval token
 * 2. Generates HMAC Proof of Review hash
 * 3. Updates the request status
 * 4. Returns the proof for CRM injection
 */
export function processApproval(
  approvalRequestId: string,
  approvalToken: string,
  reviewerEmail: string,
): ApprovalResponse | { error: string } {
  const request = approvalRequests.get(approvalRequestId);

  if (!request) {
    return { error: "Approval request not found." };
  }

  if (request.status !== "PENDING") {
    return { error: `Request already ${request.status.toLowerCase()}.` };
  }

  // Check expiration
  if (new Date() > new Date(request.expiresAt)) {
    request.status = "EXPIRED";
    return { error: "Approval request has expired." };
  }

  // Validate the one-time token
  const expectedToken = generateApprovalToken(request.id, request.firmId);
  if (approvalToken !== expectedToken) {
    return { error: "Invalid approval token." };
  }

  // Generate Proof of Review
  const reviewedAt = new Date().toISOString();
  const proofOfReviewHash = generateProofOfReview(
    request.id,
    reviewerEmail,
    reviewedAt,
    request.deliverableType,
  );

  // Update request
  request.status = "APPROVED";
  request.statusChangedAt = reviewedAt;
  request.proofOfReviewHash = proofOfReviewHash;

  return {
    approved: true,
    proofOfReviewHash,
    reviewerEmail,
    reviewedAt,
    approvalRequestId,
  };
}

/**
 * Processes a rejection from the lawyer.
 */
export function processRejection(approvalRequestId: string): { success: boolean } {
  const request = approvalRequests.get(approvalRequestId);
  if (!request || request.status !== "PENDING") {
    return { success: false };
  }

  request.status = "REJECTED";
  request.statusChangedAt = new Date().toISOString();
  return { success: true };
}

/**
 * Checks if a specific approval is complete (for durable workflow polling).
 */
export function isApprovalComplete(approvalRequestId: string): {
  complete: boolean;
  approved: boolean;
  proofHash?: string;
} {
  const request = approvalRequests.get(approvalRequestId);
  if (!request) return { complete: false, approved: false };

  if (request.status === "PENDING") {
    // Check for expiration
    if (new Date() > new Date(request.expiresAt)) {
      request.status = "EXPIRED";
      return { complete: true, approved: false };
    }
    return { complete: false, approved: false };
  }

  return {
    complete: true,
    approved: request.status === "APPROVED",
    proofHash: request.proofOfReviewHash,
  };
}

// ─── Crypto Helpers ─────────────────────────────────────────────

function generateApprovalToken(requestId: string, firmId: string): string {
  const secret = process.env.KOVELAI_APPROVAL_SECRET ?? "approval-dev-secret";
  return createHmac("sha256", secret).update(`${requestId}:${firmId}`).digest("hex").slice(0, 32); // Truncated for URL safety
}

/**
 * Proof of Review — cryptographic evidence that a licensed attorney
 * reviewed and approved the Agent's deliverable before filing.
 *
 * This hash satisfies ABA Model Rule 5.3's supervision requirement.
 */
function generateProofOfReview(
  requestId: string,
  reviewerEmail: string,
  reviewedAt: string,
  deliverableType: string,
): string {
  const secret = process.env.KOVELAI_PROOF_SECRET ?? "proof-dev-secret";
  const payload = `${requestId}:${reviewerEmail}:${reviewedAt}:${deliverableType}`;
  return createHmac("sha256", secret).update(payload).digest("hex");
}

function formatDeliverableType(type: string): string {
  const labels: Record<string, string> = {
    KINETIC_MURDER_BOARD: "⚔️ Kinetic Murder Board",
    ORACLE_MEMO: "🔮 Oracle Memo",
    CLIENT_BRIEF: "📋 Client Brief",
    TIME_ENTRY: "⏱️ Time Entry Draft",
    CLE_CERTIFICATE: "🎓 CLE Certificate",
  };
  return labels[type] ?? type;
}
