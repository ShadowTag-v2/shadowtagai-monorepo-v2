/**
 * HeadFade Core Domain Types
 *
 * Canonical type definitions for the HeadFade Truth Layer platform.
 * All types are vendor-agnostic and map to Firestore document schemas.
 */

// ---------------------------------------------------------------------------
// User & Auth
// ---------------------------------------------------------------------------

export type UserRole = "CREATOR" | "PUBLISHER" | "USER" | "ADMIN";

export interface HFUser {
  uid: string;
  role: UserRole;
  displayName: string;
  email: string;
  stripeCustomerId?: string;
  createdAt: Date;
  updatedAt: Date;
}

// ---------------------------------------------------------------------------
// Video & Content
// ---------------------------------------------------------------------------

export type VideoStatus =
  | "UPLOADING"
  | "SCANNING"
  | "ANALYZING"
  | "PUBLISHED"
  | "BLOCKED"
  | "FLAGGED";

export type GroundTruth = "AI" | "REAL" | "UNKNOWN";

export interface HFVideo {
  id: string;
  creatorId: string;
  gcsUri: string;
  title: string;
  description: string;
  groundTruth: GroundTruth;
  status: VideoStatus;
  judge6Verdict?: Judge6Verdict;
  remixNodeId?: string;
  createdAt: Date;
}

// ---------------------------------------------------------------------------
// Judge6 Trust & Safety Gate
// ---------------------------------------------------------------------------

export type Judge6Decision = "PASS" | "BLOCK" | "REVIEW";

export type Judge6Category =
  | "CSAM"
  | "VIOLENCE"
  | "HATE_SPEECH"
  | "SELF_HARM"
  | "TERRORISM"
  | "EXPLICIT_CONTENT"
  | "CLEAN";

export interface Judge6Verdict {
  decision: Judge6Decision;
  categories: Judge6Category[];
  confidenceScore: number;
  /** Latency of the Judge6 scan in milliseconds */
  latencyMs: number;
  /** ISO timestamp of when the scan was performed */
  scannedAt: string;
  /** Model/API used for the scan */
  scannerModel: string;
  /** Raw annotations from Cloud Video Intelligence, if available */
  rawAnnotations?: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Forensic Analysis (Arbiter)
// ---------------------------------------------------------------------------

export interface ForensicVerdict {
  id: string;
  videoId: string;
  model: string;
  geminiVerdict: string;
  geminiThoughts: string;
  confidenceScore: number;
  latencyMs: number;
  analyzedAt: Date;
}

// ---------------------------------------------------------------------------
// Human Deception Index (HDI)
// ---------------------------------------------------------------------------

export type UserVote = "AI" | "REAL";

export interface HDITelemetry {
  id: string;
  videoId: string;
  userId?: string;
  userVote: UserVote;
  actualTruth: GroundTruth;
  isCorrect: boolean;
  latencyMs: number;
  votedAt: Date;
}

// ---------------------------------------------------------------------------
// Remix Tree — Provenance Tracking
// ---------------------------------------------------------------------------

export type RemixNodeType = "ORIGINAL" | "REMIX" | "DERIVATIVE" | "COMPILATION";

export interface RemixNode {
  id: string;
  videoId: string;
  parentNodeId?: string;
  creatorId: string;
  nodeType: RemixNodeType;
  /** Hash of the original content for tamper detection */
  contentHash: string;
  /** Depth in the remix tree (0 = original) */
  depth: number;
  /** Number of direct children */
  childCount: number;
  /** Whether this node has been cryptographically shredded */
  isOrphaned: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// ---------------------------------------------------------------------------
// Licensing
// ---------------------------------------------------------------------------

export type LicenseType = "STANDARD" | "EXCLUSIVE" | "EMBED_ONLY";

export interface License {
  id: string;
  videoId: string;
  buyerId: string;
  sellerId: string;
  licenseType: LicenseType;
  priceAmount: number;
  priceCurrency: string;
  stripePaymentIntentId: string;
  purchasedAt: Date;
}

// ---------------------------------------------------------------------------
// Embed Telemetry
// ---------------------------------------------------------------------------

export interface EmbedTelemetry {
  id: string;
  videoId: string;
  publisherId: string;
  domain: string;
  views: number;
  playDurationSec: number;
  recordedAt: Date;
}

// ---------------------------------------------------------------------------
// Ingestion Pipeline State Machine
// ---------------------------------------------------------------------------

export type IngestionStage =
  | "RECEIVED"
  | "UPLOADING_TO_GCS"
  | "JUDGE6_SCANNING"
  | "FORENSIC_ANALYSIS"
  | "REMIX_TREE_INSERTION"
  | "COMPLETE"
  | "BLOCKED"
  | "ERROR";

export interface IngestionJob {
  id: string;
  videoId: string;
  creatorId: string;
  stage: IngestionStage;
  judge6Verdict?: Judge6Verdict;
  forensicVerdict?: ForensicVerdict;
  remixNodeId?: string;
  /** Error message if stage is ERROR */
  error?: string;
  createdAt: Date;
  updatedAt: Date;
}

// ---------------------------------------------------------------------------
// API Request/Response Contracts
// ---------------------------------------------------------------------------

export interface IngestRequest {
  title: string;
  description: string;
  groundTruth: GroundTruth;
  parentRemixNodeId?: string;
}

export interface IngestResponse {
  jobId: string;
  videoId: string;
  signedUploadUrl: string;
  stage: IngestionStage;
}

export interface NukeMyDataRequest {
  userId: string;
  confirmationPhrase: string;
}

export interface NukeMyDataResponse {
  success: boolean;
  nodesOrphaned: number;
  piiFieldsPurged: number;
  completedAt: string;
}
