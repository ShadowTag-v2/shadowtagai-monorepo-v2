// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

/**
 * Integrated Ephemeral Search UI with Dead Man's Switch
 *
 * Item #8: Wire Dead Man's Switch INTO EphemeralSearchUI.
 *
 * The search UI now auto-activates the Dead Man's Switch on mount
 * and wipes all results + clears DOM on inactivity/tab blur.
 */

'use client';

import type React from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { DeadManSwitch, useDeadManSwitch } from './DeadManSwitch';

// ─── Types ──────────────────────────────────────────────────────────

interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  source: 'google_enterprise' | 'perplexity_sonar';
}

interface EphemeralSearchProps {
  sessionId: string;
  seuToken: string;
  sandboxId: string;
  firmCxId?: string;
  onSessionExpired?: () => void;
}

// ─── Component ──────────────────────────────────────────────────────

export function EphemeralSearchIntegrated({
  sessionId,
  seuToken,
  sandboxId,
  firmCxId,
  onSessionExpired,
}: EphemeralSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isWiped, setIsWiped] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ─── Dead Man's Switch Integration ────────────────────────────
  const { isActive, isPaused, heartbeatCount } = useDeadManSwitch({
    timeoutMs: 5 * 60 * 1000, // 5 min
    warningMs: 60 * 1000, // 1 min warning
    heartbeatIntervalMs: 5000,
    onTimeout: () => {
      // WIPE EVERYTHING
      wipeSession();
    },
    onWarning: () => {
      // Visual warning — UI turns red
    },
    pauseOnBlur: true,
  });

  // ─── Session Wipe ────────────────────────────────────────────
  const wipeSession = useCallback(() => {
    setResults([]);
    setQuery('');
    setIsWiped(true);

    // Clear DOM completely
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    // Clear any cached data
    try {
      sessionStorage.clear();
    } catch {
      // Ignore
    }

    onSessionExpired?.();
  }, [onSessionExpired]);

  // ─── Tab blur handler ────────────────────────────────────────
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        // Immediately blur-wipe results on tab switch
        setResults([]);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // ─── Search Handler ──────────────────────────────────────────
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isWiped) return;

    setIsSearching(true);

    try {
      const res = await fetch('/api/privileged-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-SEU-Token': seuToken,
        },
        body: JSON.stringify({
          query: query.trim(),
          ephemeralToken: seuToken,
          sandboxId,
          firmGoogleCxId: firmCxId,
          sessionId,
        }),
      });

      if (!res.ok) {
        if (res.status === 403) {
          wipeSession();
          return;
        }
        throw new Error(`Search failed: ${res.status}`);
      }

      const data = await res.json();
      setResults(data.results ?? []);
    } catch (_err) {
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // ─── Render ──────────────────────────────────────────────────
  if (isWiped) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          background: '#0D1117',
          color: '#6e7681',
          fontFamily: 'Inter, sans-serif',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔒</div>
          <h2 style={{ color: '#c9d1d9', marginBottom: '8px' }}>Session Expired</h2>
          <p>All data has been securely wiped.</p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{
        minHeight: '100vh',
        background: '#0D1117',
        color: '#c9d1d9',
        fontFamily: 'Inter, sans-serif',
        padding: '24px',
      }}
    >
      {/* Privilege Banner */}
      <div
        style={{
          textAlign: 'center',
          padding: '8px',
          background: 'rgba(0, 212, 255, 0.1)',
          borderRadius: '6px',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          marginBottom: '24px',
          fontSize: '12px',
          color: '#00D4FF',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
        }}
      >
        🛡️ PRIVILEGED SESSION — KOVEL PROTECTED — ZERO DATA RETENTION
      </div>

      {/* Dead Man's Switch Status */}
      <DeadManSwitch timeoutMs={5 * 60 * 1000} warningMs={60 * 1000} onTimeout={wipeSession} />

      {/* Search Form */}
      <form onSubmit={handleSearch} style={{ marginBottom: '24px' }}>
        <div
          style={{
            display: 'flex',
            gap: '12px',
            maxWidth: '800px',
            margin: '0 auto',
          }}
        >
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search securely under attorney-client privilege..."
            autoComplete="off"
            autoCorrect="off"
            spellCheck={false}
            style={{
              flex: 1,
              padding: '14px 20px',
              background: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '6px',
              color: '#c9d1d9',
              fontSize: '16px',
              outline: 'none',
            }}
          />
          <button
            type="submit"
            disabled={isSearching || !query.trim()}
            style={{
              padding: '14px 28px',
              background: isSearching ? '#21262d' : '#00D4FF',
              color: isSearching ? '#6e7681' : '#0D1117',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 600,
              cursor: isSearching ? 'not-allowed' : 'pointer',
              fontSize: '14px',
            }}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {/* Results — No copy, no export, no right-click */}
      <div
        style={{ maxWidth: '800px', margin: '0 auto' }}
        onCopy={(e) => e.preventDefault()}
        onContextMenu={(e) => e.preventDefault()}
      >
        {results.map((result, i) => (
          <div
            key={i}
            style={{
              padding: '16px',
              background: '#161b22',
              border: '1px solid #30363d',
              borderRadius: '6px',
              marginBottom: '12px',
            }}
          >
            <h3 style={{ color: '#58a6ff', fontSize: '16px', marginBottom: '4px' }}>
              {result.title}
            </h3>
            <p style={{ fontSize: '14px', lineHeight: '1.6', color: '#8b949e' }}>
              {result.snippet}
            </p>
            <span style={{ fontSize: '12px', color: '#484f58' }}>
              {result.source === 'google_enterprise' ? '🔒 Enterprise ZDR' : '🔒 Sonar Pro ZDR'}
            </span>
          </div>
        ))}

        {results.length === 0 && !isSearching && query && (
          <p style={{ textAlign: 'center', color: '#484f58' }}>No results found.</p>
        )}
      </div>

      {/* Footer */}
      <div
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '8px',
          background: '#0D1117',
          borderTop: '1px solid #21262d',
          textAlign: 'center',
          fontSize: '11px',
          color: '#484f58',
        }}
      >
        Session: {sessionId.slice(0, 8)}… | Heartbeats: {heartbeatCount} | Status:{' '}
        {isPaused ? '⏸ Paused' : isActive ? '🟢 Active' : '🔴 Expired'}
      </div>
    </div>
  );
}
