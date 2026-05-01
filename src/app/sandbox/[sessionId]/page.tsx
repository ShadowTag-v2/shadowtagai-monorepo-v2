// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Sandbox Session Page — Attorney Diff Review Route
 *
 * This is the Phase 3 Milestone 3 page that wires DiffView into
 * the sandbox session route: /sandbox/[sessionId]
 *
 * Flow:
 *   1. Attorney navigates to /sandbox/{session-id}?matter={matter-id}
 *   2. Page fetches diffs from /api/sandbox/[sessionId]/diffs
 *   3. DiffView renders the overlay changes
 *   4. Attorney makes accept/reject/partial decision
 *   5. Decision POSTed to /api/sandbox/[sessionId]/commit
 *
 * Security:
 *   - Server-side auth check via middleware
 *   - Attorney UID verified against session config
 *   - All decisions produce immutable audit trail
 */

'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { DiffView } from '@/components/diff-view/DiffView';
import { usePanopticonContext } from '@/components/telemetry/PanopticonProvider';
import type { CommitAction, DiffFile } from '@/components/diff-view/types';
import styles from './sandbox-session.module.css';

/** Session state machine — aligns with Python SandboxSession.lifecycle */
type SessionPhase = 'loading' | 'reviewing' | 'committing' | 'committed' | 'error';

interface SessionState {
  phase: SessionPhase;
  diffs: DiffFile[];
  matterId: string;
  error: string | null;
  commitResult: CommitResult | null;
}

interface CommitResult {
  success: boolean;
  committedFiles: string[];
  rejectedFiles: string[];
  auditId: string;
  durationMs: number;
}

export default function SandboxSessionPage() {
  const params = useParams<{ sessionId: string }>();
  const searchParams = useSearchParams();
  const sessionId = params.sessionId;
  const matterId = searchParams.get('matter') ?? 'unknown';

  const { track, trackAsync } = usePanopticonContext();

  const [state, setState] = useState<SessionState>({
    phase: 'loading',
    diffs: [],
    matterId,
    error: null,
    commitResult: null,
  });

  // ── Fetch diffs on mount ──────────────────────────────────
  useEffect(() => {
    if (!sessionId) return;

    track('sandbox.session_opened', {
      session_id_prefix: sessionId.slice(0, 8),
    });

    const fetchDiffs = async () => {
      try {
        const res = await fetch(`/api/sandbox/${sessionId}/diffs?matter=${matterId}`);
        if (!res.ok) {
          const body = await res.json().catch(() => ({ error: 'Unknown error' }));
          throw new Error(body.error ?? `HTTP ${res.status}`);
        }

        const data = await res.json();
        setState((prev) => ({
          ...prev,
          phase: 'reviewing',
          diffs: data.diffs,
          matterId: data.matterId ?? matterId,
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

    void fetchDiffs();
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
            selectedFiles,
            matterId: state.matterId,
          }),
        });

        if (!res.ok) {
          const body = await res.json().catch(() => ({ error: 'Commit failed' }));
          throw new Error(body.error ?? `HTTP ${res.status}`);
        }

        const result: CommitResult = await res.json();
        setState((prev) => ({
          ...prev,
          phase: 'committed',
          commitResult: result,
        }));

        track('sandbox.decision_completed', {
          action,
          success: 1,
          duration_ms: result.durationMs,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Commit failed';
        setState((prev) => ({ ...prev, phase: 'error', error: message }));
        track('sandbox.decision_error', { error_type: 'commit_failed' }, 'error');
      }
    },
    [sessionId, state.diffs.length, state.matterId, track, trackAsync],
  );

  // ── Render by phase ───────────────────────────────────────
  if (state.phase === 'error') {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <div className={styles.errorIcon}>⚠</div>
          <h2 className={styles.errorTitle}>Session Error</h2>
          <p className={styles.errorMessage}>{state.error}</p>
          <button
            className={styles.retryButton}
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
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
            {state.commitResult.committedFiles.length > 0 && (
              <p>
                <strong>{state.commitResult.committedFiles.length}</strong> file(s) committed
              </p>
            )}
            {state.commitResult.rejectedFiles.length > 0 && (
              <p>
                <strong>{state.commitResult.rejectedFiles.length}</strong> file(s) rejected
              </p>
            )}
            <p className={styles.auditNote}>
              Audit ID: <code>{state.commitResult.auditId}</code>
            </p>
            <p className={styles.durationNote}>
              Completed in {state.commitResult.durationMs.toFixed(0)}ms
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
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
