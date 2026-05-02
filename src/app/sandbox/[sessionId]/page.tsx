// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Sandbox Session Page — Attorney Diff Review Route (Phase 4)
 *
 * This page wires DiffView into the sandbox session route: /sandbox/[sessionId]
 *
 * Phase 4 Flow:
 *   1. Attorney navigates to /sandbox/{session-id}?matter={matter-id}
 *   2. Page FIRST hydrates session from Firestore via GET /api/sandbox/{sessionId}
 *   3. Then fetches diffs from GET /api/sandbox/{sessionId}/diffs
 *   4. DiffView renders the overlay changes
 *   5. WebSocket listens for real-time state transitions
 *   6. Attorney makes accept/reject/partial decision
 *   7. Decision POSTed to POST /api/sandbox/{sessionId}/commit
 *   8. Decision persisted to Firestore decisions sub-collection
 *   9. WebSocket broadcasts committed/rejected to all connected clients
 *
 * Security:
 *   - Server-side auth check via middleware
 *   - Attorney UID verified against session config
 *   - All decisions produce immutable audit trail (Firestore + .beads/)
 *   - WebSocket messages contain session prefix only (no PII)
 */

'use client';

import { useParams, useSearchParams } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import { DiffView } from '@/components/diff-view/DiffView';
import type {
  CommitAction,
  CommitResponse,
  DiffFile,
  DiffResponse,
} from '@/components/diff-view/types';
import { usePanopticonContext } from '@/components/telemetry/PanopticonProvider';
import { type StateChangeEvent, useSandboxWebSocket } from '@/hooks/useSandboxWebSocket';
import styles from './sandbox-session.module.css';

/** Session state machine — aligns with Python SandboxSession.lifecycle */
type SessionPhase =
  | 'hydrating'
  | 'loading'
  | 'reviewing'
  | 'committing'
  | 'committed'
  | 'rejected'
  | 'error';

interface SessionMeta {
  sessionId: string;
  state: string;
  matterId: string;
  createdAt: number;
}

interface SessionState {
  phase: SessionPhase;
  meta: SessionMeta | null;
  diffs: DiffFile[];
  matterId: string;
  error: string | null;
  commitResult: CommitResponse | null;
}

export default function SandboxSessionPage() {
  const params = useParams<{ sessionId: string }>();
  const searchParams = useSearchParams();
  const sessionId = params.sessionId;
  const matterId = searchParams.get('matter') ?? 'unknown';

  const { track, trackAsync } = usePanopticonContext();

  const [state, setState] = useState<SessionState>({
    phase: 'hydrating',
    meta: null,
    diffs: [],
    matterId,
    error: null,
    commitResult: null,
  });

  // ── WebSocket: real-time state transitions ────────────────
  const handleWsStateChange = useCallback(
    (event: StateChangeEvent) => {
      track('sandbox.ws_state_received', {
        from: event.from,
        to: event.to,
      });

      // Map backend state transitions to frontend phases
      if (event.to === 'committed') {
        setState((prev) => ({
          ...prev,
          phase: 'committed',
          commitResult: prev.commitResult ?? {
            success: true,
            committed_files: [],
            rejected_files: [],
            audit_id: (event.metadata?.audit_id as string) ?? '',
            error: '',
            duration_ms: 0,
          },
        }));
      } else if (event.to === 'rejected') {
        setState((prev) => ({ ...prev, phase: 'rejected' }));
      } else if (event.to === 'reviewing') {
        setState((prev) => ({ ...prev, phase: 'reviewing' }));
      }
    },
    [track],
  );

  const { connectionState, reconnectCount } = useSandboxWebSocket({
    sessionId,
    onStateChange: handleWsStateChange,
    enabled: state.phase !== 'error',
  });

  // ── Phase 4: Hydrate session from Firestore, then fetch diffs ──
  useEffect(() => {
    if (!sessionId) return;

    track('sandbox.session_opened', {
      session_id_prefix: sessionId.slice(0, 8),
    });

    const hydrateAndFetch = async () => {
      // Step 1: Hydrate session metadata from Firestore
      try {
        const sessionRes = await fetch(`/api/sandbox/${sessionId}`);
        if (sessionRes.ok) {
          const sessionData = await sessionRes.json();
          const meta: SessionMeta = {
            sessionId: sessionData.session_id,
            state: sessionData.state,
            matterId: sessionData.matter_id ?? matterId,
            createdAt: sessionData.created_at,
          };
          setState((prev) => ({
            ...prev,
            meta,
            matterId: meta.matterId,
          }));

          track('sandbox.session_hydrated', {
            persisted_state: meta.state,
            session_age_s: Math.floor(Date.now() / 1000 - meta.createdAt),
          });

          // If session is already in a terminal state, short-circuit
          if (meta.state === 'committed') {
            setState((prev) => ({
              ...prev,
              phase: 'committed',
              commitResult: {
                success: true,
                committed_files: [],
                rejected_files: [],
                audit_id: '',
                error: '',
                duration_ms: 0,
              },
            }));
            return;
          }
          if (meta.state === 'rejected') {
            setState((prev) => ({ ...prev, phase: 'rejected' }));
            return;
          }
        }
      } catch {
        // Hydration failure is non-fatal — fall through to diff fetch
        track('sandbox.hydration_failed', { error_type: 'fetch_failed' }, 'warn');
      }

      // Step 2: Fetch diffs (works regardless of hydration success)
      setState((prev) => ({ ...prev, phase: 'loading' }));
      try {
        const effectiveMatter = state.matterId !== 'unknown' ? state.matterId : matterId;
        const res = await fetch(`/api/sandbox/${sessionId}/diffs?matter=${effectiveMatter}`);
        if (!res.ok) {
          const body = await res.json().catch(() => ({ error: 'Unknown error' }));
          throw new Error(body.error ?? `HTTP ${res.status}`);
        }

        const data: DiffResponse = await res.json();
        setState((prev) => ({
          ...prev,
          phase: 'reviewing',
          diffs: data.diffs as DiffFile[],
          matterId: data.matter_id ?? effectiveMatter,
        }));

        track('sandbox.diffs_loaded', {
          file_count: data.diffs.length,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load diffs';
        setState((prev) => ({ ...prev, phase: 'error', error: message }));
        track('sandbox.load_error', { error_type: 'fetch_failed' }, 'error');
      }
    };

    void hydrateAndFetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, matterId, track]);

  // ── Handle attorney decision ──────────────────────────────
  const handleDecision = useCallback(
    async (action: CommitAction, selectedFiles?: string[]) => {
      setState((prev) => ({ ...prev, phase: 'committing' }));

      try {
        await trackAsync('sandbox.decision_submitted', {
          action,
          file_count: selectedFiles?.length ?? state.diffs.length,
        });

        const res = await fetch(`/api/sandbox/${sessionId}/commit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action,
            selected_files: selectedFiles ?? null,
            matter_id: state.matterId,
            rejection_reason: '',
          }),
        });

        if (!res.ok) {
          const body = await res.json().catch(() => ({ error: 'Commit failed' }));
          throw new Error(body.error ?? `HTTP ${res.status}`);
        }

        const result: CommitResponse = await res.json();
        setState((prev) => ({
          ...prev,
          phase: 'committed',
          commitResult: result,
        }));

        track('sandbox.decision_completed', {
          action,
          success: 1,
          duration_ms: result.duration_ms,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Commit failed';
        setState((prev) => ({ ...prev, phase: 'error', error: message }));
        track('sandbox.decision_error', { error_type: 'commit_failed' }, 'error');
      }
    },
    [sessionId, state.diffs.length, state.matterId, track, trackAsync],
  );

  // ── Render: Hydrating spinner ─────────────────────────────
  if (state.phase === 'hydrating') {
    return (
      <div className={styles.container}>
        <div className={styles.loadingCard}>
          <div className={styles.spinner} />
          <p className={styles.loadingText}>Restoring session…</p>
        </div>
      </div>
    );
  }

  // ── Render: Error state ───────────────────────────────────
  if (state.phase === 'error') {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <div className={styles.errorIcon}>⚠</div>
          <h2 className={styles.errorTitle}>Session Error</h2>
          <p className={styles.errorMessage}>{state.error}</p>
          <button className={styles.retryButton} onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (state.phase === 'rejected') {
    return (
      <div className={styles.container}>
        <div className={styles.rejectedCard}>
          <div className={styles.rejectedIcon}>✕</div>
          <h2 className={styles.rejectedTitle}>Session Rejected</h2>
          <p className={styles.rejectedMessage}>
            This sandbox session has been rejected. Speculative changes were discarded and will not
            be applied to the matter.
          </p>
          <p className={styles.auditNote}>
            Session: <code>{sessionId.slice(0, 8)}…</code>
          </p>
        </div>
      </div>
    );
  }

  if (state.phase === 'committed' && state.commitResult) {
    return (
      <div className={styles.container}>
        <div className={styles.successCard}>
          <div className={styles.successIcon}>✓</div>
          <h2 className={styles.successTitle}>Decision Recorded</h2>
          <div className={styles.commitSummary}>
            {state.commitResult.committed_files.length > 0 && (
              <p>
                <strong>{state.commitResult.committed_files.length}</strong> file(s) committed
              </p>
            )}
            {state.commitResult.rejected_files.length > 0 && (
              <p>
                <strong>{state.commitResult.rejected_files.length}</strong> file(s) rejected
              </p>
            )}
            <p className={styles.auditNote}>
              Audit ID: <code>{state.commitResult.audit_id}</code>
            </p>
            <p className={styles.durationNote}>
              Completed in {state.commitResult.duration_ms.toFixed(0)}ms
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Session metadata badge (Phase 4) */}
      {state.meta && (
        <div className={styles.sessionBadge}>
          <span className={styles.badgeLabel}>Session</span>
          <code className={styles.badgeId}>{state.meta.sessionId.slice(0, 8)}…</code>
          <span className={styles.badgeSeparator}>|</span>
          <span className={styles.badgeState}>{state.meta.state}</span>
        </div>
      )}

      {/* WebSocket connection status indicator */}
      <div
        className={styles.wsStatus}
        data-state={connectionState}
        title={
          connectionState === 'connected'
            ? 'Real-time updates active'
            : connectionState === 'connecting'
              ? `Connecting${reconnectCount > 0 ? ` (attempt ${reconnectCount})` : ''}…`
              : 'Real-time updates disconnected'
        }
      >
        <span className={styles.wsStatusDot} />
        <span className={styles.wsStatusText}>
          {connectionState === 'connected'
            ? 'Live'
            : connectionState === 'connecting'
              ? 'Connecting…'
              : 'Offline'}
        </span>
      </div>

      <DiffView
        sessionId={sessionId}
        matterId={state.matterId}
        diffs={state.diffs}
        onDecision={handleDecision}
        isLoading={state.phase === 'loading' || state.phase === 'committing'}
      />
    </div>
  );
}
