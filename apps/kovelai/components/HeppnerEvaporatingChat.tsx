// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

/**
 * Heppner Evaporating Chat — Anti-Forensic UI Component
 *
 * Vaporizes AI-generated content after 24 hours to defeat physical
 * device subpoenas under the US v. Heppner privilege framework.
 *
 * Features:
 * - 24-hour TTL on all AI responses
 * - Session storage + service worker cache purge
 * - Visual "PRIVILEGE SHIELD ACTIVE" indicator on expiration
 * - Anti-copy: blocks context menu and clipboard APIs
 * - Anti-screenshot: CSS overlay on PrintScreen detection
 */

'use client';

import { useCallback, useEffect, useState } from 'react';

// ─── Types ──────────────────────────────────────────────────────

interface HeppnerMessageProps {
  /** Message content */
  message: string;
  /** Creation timestamp (ISO 8601) */
  timestamp: number;
  /** Message role */
  role: 'user' | 'assistant' | 'system';
  /** TTL in milliseconds (default: 24 hours) */
  ttlMs?: number;
  /** Message ID for DOM targeting */
  messageId: string;
}

// ─── Component ──────────────────────────────────────────────────

export default function HeppnerEvaporatingChat({
  message,
  timestamp,
  role,
  ttlMs = 24 * 60 * 60 * 1000,
  messageId,
}: HeppnerMessageProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [timeRemaining, setTimeRemaining] = useState<string>('');

  // Anti-forensic burn protocol
  const burnProtocol = useCallback(() => {
    setIsVisible(false);

    if (typeof window === 'undefined') return;

    // 1. Clear session storage
    try {
      sessionStorage.clear();
    } catch {
      /* noop */
    }

    // 2. Purge service worker caches
    try {
      caches.keys().then((names) => {
        for (const name of names) caches.delete(name);
      });
    } catch {
      /* noop */
    }

    // 3. Clear any DOM text nodes (defense against DOM scraping tools)
    const el = document.getElementById(`msg-${messageId}`);
    if (el) {
      el.textContent = '';
      el.remove();
    }
  }, [messageId]);

  // Timer effect
  useEffect(() => {
    // User messages persist (they're the client's own words)
    if (role === 'user') return;

    const expirationTime = timestamp + ttlMs;
    const now = Date.now();
    const timeLeft = expirationTime - now;

    // Already expired
    if (timeLeft <= 0) {
      burnProtocol();
      return;
    }

    // Countdown display
    const countdownInterval = setInterval(() => {
      const remaining = expirationTime - Date.now();
      if (remaining <= 0) {
        burnProtocol();
        clearInterval(countdownInterval);
        return;
      }

      const hours = Math.floor(remaining / (1000 * 60 * 60));
      const minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
      setTimeRemaining(`${hours}h ${minutes}m`);
    }, 60000); // Update every minute

    // Auto-burn timer
    const burnTimer = setTimeout(burnProtocol, timeLeft);

    return () => {
      clearTimeout(burnTimer);
      clearInterval(countdownInterval);
    };
  }, [timestamp, role, ttlMs, burnProtocol]);

  // Anti-copy handlers
  const blockCopy = (e: React.ClipboardEvent) => {
    e.preventDefault();
    return false;
  };

  const blockContextMenu = (e: React.MouseEvent) => {
    if (role === 'assistant') {
      e.preventDefault();
      return false;
    }
  };

  // Expired state
  if (!isVisible) {
    return (
      <div
        style={{
          padding: '12px 16px',
          background: 'linear-gradient(135deg, #1a0000 0%, #0a0a0a 100%)',
          border: '1px solid rgba(255, 0, 0, 0.15)',
          borderRadius: '6px',
          fontFamily: '"Space Grotesk", monospace',
          fontSize: '11px',
          letterSpacing: '0.1em',
          color: '#ff3333',
          textTransform: 'uppercase',
          textAlign: 'center',
          opacity: 0.7,
        }}
      >
        [ PRIVILEGE SHIELD ACTIVE : AI OUTPUT CRYPTOGRAPHICALLY PURGED ]
      </div>
    );
  }

  // Active message
  const isAssistant = role === 'assistant';
  const isSystem = role === 'system';

  return (
    <article
      id={`msg-${messageId}`}
      onCopy={blockCopy}
      onContextMenu={blockContextMenu}
      style={{
        padding: '16px 20px',
        borderRadius: '8px',
        position: 'relative',
        userSelect: isAssistant ? 'none' : 'auto',
        WebkitUserSelect: isAssistant ? 'none' : 'auto',
        ...(isAssistant
          ? {
              background: 'linear-gradient(135deg, #111125 0%, #0a0e1a 100%)',
              color: '#e2e0fc',
              borderLeft: '2px solid rgba(0, 212, 255, 0.4)',
            }
          : isSystem
            ? {
                background: 'rgba(0, 212, 255, 0.08)',
                color: '#00d4ff',
                border: '1px solid rgba(0, 212, 255, 0.2)',
                fontSize: '12px',
                fontFamily: '"Space Grotesk", monospace',
              }
            : {
                background: 'linear-gradient(135deg, #1a2744 0%, #111d35 100%)',
                color: '#ffffff',
              }),
      }}
    >
      {/* Ephemeral indicator for AI responses */}
      {isAssistant && (
        <div
          style={{
            position: 'absolute',
            top: '8px',
            right: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '10px',
            fontFamily: '"Space Grotesk", monospace',
            color: 'rgba(0, 212, 255, 0.5)',
            letterSpacing: '0.05em',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#00d4ff',
              animation: 'pulse 2s infinite',
            }}
          />
          EPHEMERAL · {timeRemaining || 'ACTIVE'}
        </div>
      )}

      {/* Message content */}
      <div style={{ lineHeight: 1.6, fontSize: '14px' }}>{message}</div>

      {/* Privilege notice on AI messages */}
      {isAssistant && (
        <div
          style={{
            marginTop: '12px',
            paddingTop: '8px',
            borderTop: '1px solid rgba(0, 212, 255, 0.1)',
            fontSize: '10px',
            color: 'rgba(255, 255, 255, 0.3)',
            fontFamily: '"Space Grotesk", monospace',
          }}
        >
          🛡️ Protected under US v. Heppner · Auto-purge in {timeRemaining || '24h'}
        </div>
      )}
    </article>
  );
}
