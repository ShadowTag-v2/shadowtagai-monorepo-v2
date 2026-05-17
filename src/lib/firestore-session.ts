// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Firestore Session Client Library — Phase 4
 *
 * Client-side utilities for interacting with the Firestore-backed
 * sandbox session API. Provides typed fetch wrappers and a React hook
 * for session lifecycle management.
 *
 * All API calls go through the Next.js API routes which proxy to the
 * FastAPI backend — no direct Firestore access from the client.
 *
 * Security:
 *   - Auth cookies are sent automatically via fetch credentials
 *   - No PII in client-side state (session_id prefix only in logs)
 *   - Attorney UID verified server-side on every request
 */

// ── Types ──────────────────────────────────────────────────────────────

export interface SessionCreateRequest {
  matterId: string;
  ttlSeconds?: number;
  maxOverlayFiles?: number;
}

export interface SessionCreateResponse {
  session_id: string;
  state: string;
  matter_id: string;
  created_at: number;
}

export interface SessionSummary {
  session_id: string;
  state: string;
  matter_id: string;
  attorney_uid: string;
  created_at: number;
}

export interface SessionCommitRequest {
  action: "accept" | "reject" | "partial_accept";
  matterId: string;
  selectedFiles?: string[];
  rejectionReason?: string;
}

export interface SessionCommitResponse {
  success: boolean;
  committed_files: string[];
  rejected_files: string[];
  audit_id: string;
  error: string;
  duration_ms: number;
}

export interface DiffResponse {
  session_id: string;
  matter_id: string;
  diffs: Array<Record<string, unknown>>;
  file_count: number;
}

// ── API Client ─────────────────────────────────────────────────────────

const API_BASE = "/api/sandbox";

/**
 * Create a new sandbox session.
 */
export async function createSession(req: SessionCreateRequest): Promise<SessionCreateResponse> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      matter_id: req.matterId,
      ttl_seconds: req.ttlSeconds ?? 1800,
      max_overlay_files: req.maxOverlayFiles ?? 50,
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Session creation failed" }));
    throw new SessionApiError(res.status, body.detail ?? "Session creation failed");
  }

  return res.json();
}

/**
 * Resume / hydrate an existing session.
 */
export async function resumeSession(sessionId: string): Promise<SessionCreateResponse> {
  const res = await fetch(`${API_BASE}/${sessionId}`, {
    credentials: "include",
  });

  if (!res.ok) {
    if (res.status === 404) {
      throw new SessionNotFoundError(sessionId);
    }
    if (res.status === 403) {
      throw new SessionAccessDeniedError(sessionId);
    }
    const body = await res.json().catch(() => ({ detail: "Resume failed" }));
    throw new SessionApiError(res.status, body.detail ?? "Resume failed");
  }

  return res.json();
}

/**
 * List active sessions for the current attorney.
 */
export async function listSessions(matterId?: string): Promise<SessionSummary[]> {
  const params = new URLSearchParams();
  if (matterId) params.set("matter", matterId);

  const res = await fetch(`${API_BASE}/sessions?${params.toString()}`, {
    credentials: "include",
  });

  if (!res.ok) {
    throw new SessionApiError(res.status, "Failed to list sessions");
  }

  return res.json();
}

/**
 * Fetch diffs for a session.
 */
export async function fetchDiffs(sessionId: string, matterId: string): Promise<DiffResponse> {
  const res = await fetch(`${API_BASE}/${sessionId}/diffs?matter=${encodeURIComponent(matterId)}`, {
    credentials: "include",
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Diff fetch failed" }));
    throw new SessionApiError(res.status, body.detail ?? "Diff fetch failed");
  }

  return res.json();
}

/**
 * Submit attorney decision on a session.
 */
export async function commitSession(
  sessionId: string,
  req: SessionCommitRequest,
): Promise<SessionCommitResponse> {
  const res = await fetch(`${API_BASE}/${sessionId}/commit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      action: req.action,
      matter_id: req.matterId,
      selected_files: req.selectedFiles,
      rejection_reason: req.rejectionReason ?? "",
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: "Commit failed" }));
    throw new SessionApiError(res.status, body.detail ?? "Commit failed");
  }

  return res.json();
}

// ── Error Classes ──────────────────────────────────────────────────────

export class SessionApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "SessionApiError";
  }
}

export class SessionNotFoundError extends SessionApiError {
  constructor(sessionId: string) {
    super(404, `Session ${sessionId.slice(0, 8)}… not found`);
    this.name = "SessionNotFoundError";
  }
}

export class SessionAccessDeniedError extends SessionApiError {
  constructor(sessionId: string) {
    super(403, `Access denied to session ${sessionId.slice(0, 8)}…`);
    this.name = "SessionAccessDeniedError";
  }
}
