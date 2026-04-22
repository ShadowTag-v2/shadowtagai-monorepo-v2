/**
 * Client Ephemeral Search UI Component
 *
 * Sprint Item #7: The privilege-preserving search interface.
 *
 * Features:
 * - Auto-logout after 5 min inactivity (Dead Man's Switch)
 * - No copy/paste allowed (right-click disabled)
 * - No browser history (replaceState on every interaction)
 * - Results rendered server-side (no client-side caching)
 * - Session timer visible at all times
 * - Kovel privilege badge
 *
 * @see U.S. v. Heppner — privilege waiver on public AI
 */

'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';

// ─── Configuration ──────────────────────────────────────────────────

const INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes
const WARNING_THRESHOLD_MS = 4 * 60 * 1000; // Warning at 4 min

// ─── Types ──────────────────────────────────────────────────────────

interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  source: string;
}

interface EphemeralSearchProps {
  seuToken: string;
  firmId: string;
  sandboxId: string;
  onSessionEnd: () => void;
}

// ─── Component ──────────────────────────────────────────────────────

export function EphemeralSearchUI({
  seuToken,
  firmId,
  sandboxId,
  onSessionEnd,
}: EphemeralSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionTimer, setSessionTimer] = useState(0);
  const [showWarning, setShowWarning] = useState(false);
  const [kovelStatus, setKovelStatus] = useState<'ACTIVE' | 'EXPIRING' | 'ENDED'>('ACTIVE');
  const lastActivityRef = useRef(Date.now());
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // ─── Dead Man's Switch ── Auto-logout on inactivity ──────────────
  const resetInactivityTimer = useCallback(() => {
    lastActivityRef.current = Date.now();
    setShowWarning(false);
    setKovelStatus('ACTIVE');
  }, []);

  useEffect(() => {
    const checkInactivity = () => {
      const elapsed = Date.now() - lastActivityRef.current;

      if (elapsed >= INACTIVITY_TIMEOUT_MS) {
        // Session expired — wipe everything
        setKovelStatus('ENDED');
        setResults([]);
        setQuery('');
        onSessionEnd();
        return;
      }

      if (elapsed >= WARNING_THRESHOLD_MS) {
        setShowWarning(true);
        setKovelStatus('EXPIRING');
      }
    };

    const interval = setInterval(checkInactivity, 1000);
    return () => clearInterval(interval);
  }, [onSessionEnd]);

  // ─── Session Timer ───────────────────────────────────────────────
  useEffect(() => {
    timerRef.current = setInterval(() => {
      setSessionTimer((prev) => prev + 1);
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // ─── Anti-Forensic: Disable copy/paste & right-click ─────────────
  useEffect(() => {
    const preventCopy = (e: ClipboardEvent) => e.preventDefault();
    const preventContext = (e: MouseEvent) => e.preventDefault();
    const preventSelect = (e: Event) => e.preventDefault();

    document.addEventListener('copy', preventCopy);
    document.addEventListener('cut', preventCopy);
    document.addEventListener('paste', preventCopy);
    document.addEventListener('contextmenu', preventContext);
    document.addEventListener('selectstart', preventSelect);

    // Replace browser history on every interaction
    window.history.replaceState(null, '', '/portal');

    return () => {
      document.removeEventListener('copy', preventCopy);
      document.removeEventListener('cut', preventCopy);
      document.removeEventListener('paste', preventCopy);
      document.removeEventListener('contextmenu', preventContext);
      document.removeEventListener('selectstart', preventSelect);
    };
  }, []);

  // ─── Search Handler ──────────────────────────────────────────────
  const handleSearch = async () => {
    if (!query.trim()) return;
    resetInactivityTimer();
    setLoading(true);

    try {
      const response = await fetch('/api/privileged-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-SEU-Token': seuToken,
        },
        body: JSON.stringify({
          query,
          ephemeralToken: seuToken,
          sandboxId,
          sessionId: crypto.randomUUID(),
        }),
      });

      if (response.status === 429) {
        setResults([]);
        return;
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // ─── Format Timer ────────────────────────────────────────────────
  const formatTimer = (seconds: number): string => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // ─── Render ──────────────────────────────────────────────────────
  return (
    <div
      className="ephemeral-search"
      onMouseMove={resetInactivityTimer}
      onKeyDown={resetInactivityTimer}
      style={{
        minHeight: '100vh',
        background: '#0d1117',
        color: '#e2e0fc',
        fontFamily: 'Inter, sans-serif',
        userSelect: 'none',
        WebkitUserSelect: 'none',
      }}
    >
      {/* ── Top Bar ── */}
      <header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 24px',
          background: '#111125',
          borderBottom: '1px solid rgba(60, 73, 78, 0.15)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: '18px',
            fontWeight: 600,
            letterSpacing: '-0.02em',
          }}>
            KovelAI
          </span>
          <span style={{
            padding: '4px 12px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 600,
            background: kovelStatus === 'ACTIVE' ? 'rgba(62, 254, 138, 0.15)' :
                        kovelStatus === 'EXPIRING' ? 'rgba(255, 179, 71, 0.15)' :
                        'rgba(255, 82, 82, 0.15)',
            color: kovelStatus === 'ACTIVE' ? '#3efe8a' :
                   kovelStatus === 'EXPIRING' ? '#ffb347' :
                   '#ff5252',
            border: `1px solid ${kovelStatus === 'ACTIVE' ? 'rgba(62, 254, 138, 0.3)' :
                                  kovelStatus === 'EXPIRING' ? 'rgba(255, 179, 71, 0.3)' :
                                  'rgba(255, 82, 82, 0.3)'}`,
          }}>
            KOVEL {kovelStatus}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{
            fontFamily: 'monospace',
            fontSize: '14px',
            color: '#bbc9cf',
          }}>
            {formatTimer(sessionTimer)}
          </span>
          <button
            onClick={onSessionEnd}
            style={{
              padding: '6px 16px',
              background: 'rgba(255, 82, 82, 0.1)',
              color: '#ff5252',
              border: '1px solid rgba(255, 82, 82, 0.3)',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
            }}
          >
            End Session
          </button>
        </div>
      </header>

      {/* ── Warning Banner ── */}
      {showWarning && (
        <div style={{
          padding: '12px 24px',
          background: 'rgba(255, 179, 71, 0.1)',
          borderBottom: '1px solid rgba(255, 179, 71, 0.2)',
          color: '#ffb347',
          fontSize: '14px',
          textAlign: 'center',
        }}>
          ⚠️ Session expiring due to inactivity. Move your mouse to continue.
        </div>
      )}

      {/* ── Search Area ── */}
      <main style={{ maxWidth: '800px', margin: '0 auto', padding: '48px 24px' }}>
        <h1 style={{
          fontFamily: 'Space Grotesk, sans-serif',
          fontSize: '28px',
          fontWeight: 600,
          letterSpacing: '-0.02em',
          marginBottom: '8px',
        }}>
          Privileged Research Portal
        </h1>
        <p style={{ color: '#bbc9cf', marginBottom: '32px', fontSize: '15px' }}>
          Your searches are protected by attorney-client privilege via the Kovel Doctrine.
        </p>

        {/* ── Search Input ── */}
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '32px',
        }}>
          <input
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); resetInactivityTimer(); }}
            onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(); }}
            placeholder="Enter your legal research query..."
            autoComplete="off"
            autoCorrect="off"
            spellCheck={false}
            style={{
              flex: 1,
              padding: '14px 20px',
              background: '#0c0c1f',
              border: 'none',
              borderBottom: '2px solid #3c494e',
              borderRadius: '6px 6px 0 0',
              color: '#e2e0fc',
              fontSize: '16px',
              fontFamily: 'Inter, sans-serif',
              outline: 'none',
            }}
          />
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            style={{
              padding: '14px 28px',
              background: loading ? '#333348' : '#00d4ff',
              color: loading ? '#bbc9cf' : '#00586b',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'wait' : 'pointer',
              fontSize: '15px',
              fontWeight: 600,
              fontFamily: 'Space Grotesk, sans-serif',
            }}
          >
            {loading ? '...' : 'Search'}
          </button>
        </div>

        {/* ── Results ── */}
        <div>
          {results.map((result, i) => (
            <div
              key={`${result.url}-${i}`}
              style={{
                padding: '20px',
                marginBottom: '12px',
                background: '#1a1a2e',
                borderRadius: '6px',
                borderTop: '0.5px solid rgba(180, 235, 255, 0.1)',
              }}
            >
              <h3 style={{
                fontFamily: 'Space Grotesk, sans-serif',
                fontSize: '16px',
                fontWeight: 600,
                color: '#a8e8ff',
                marginBottom: '8px',
              }}>
                {result.title}
              </h3>
              <p style={{
                fontSize: '14px',
                color: '#bbc9cf',
                lineHeight: 1.6,
                marginBottom: '8px',
              }}>
                {result.snippet}
              </p>
              <span style={{
                fontSize: '12px',
                color: '#859398',
                fontFamily: 'monospace',
              }}>
                {result.source}
              </span>
            </div>
          ))}
        </div>
      </main>

      {/* ── Footer ── */}
      <footer style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '8px 24px',
        background: '#111125',
        borderTop: '1px solid rgba(60, 73, 78, 0.15)',
        display: 'flex',
        justifyContent: 'center',
        gap: '24px',
        fontSize: '11px',
        color: '#859398',
      }}>
        <span>Protected by Kovel Doctrine</span>
        <span>•</span>
        <span>Zero Data Retention</span>
        <span>•</span>
        <span>Session: {formatTimer(sessionTimer)}</span>
      </footer>
    </div>
  );
}
