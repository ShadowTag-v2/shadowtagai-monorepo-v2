/**
 * War Room Component with SSE Integration
 *
 * Item #13: Wire SSE client into War Room component.
 *
 * Real-time collaborative workspace for multi-model debate:
 * - Murder Board decisions stream in via SSE
 * - Model responses appear as they arrive
 * - Confidence scores update live
 * - Lawyer can override/veto any model response
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  createWarRoomSSEClient,
  type ResilientSSEClient,
  type SSEMessage,
} from '@/lib/streaming/sse-client';

// ─── Types ──────────────────────────────────────────────────────────

interface WarRoomMessage {
  id: string;
  model: string;
  type: 'response' | 'citation' | 'dissent' | 'confidence' | 'verdict' | 'system';
  content: string;
  confidence?: number;
  timestamp: string;
  citations?: Citation[];
}

interface Citation {
  caseTitle: string;
  citation: string;
  url?: string;
}

interface WarRoomProps {
  sessionId: string;
  seuToken: string;
  caseTitle: string;
  onVerdictReached?: (verdict: WarRoomMessage) => void;
}

// ─── Model Colors ───────────────────────────────────────────────────

const MODEL_COLORS: Record<string, string> = {
  'gemini-3.1-flash-lite': '#00D4FF',
  'claude-sonnet-4.5': '#FF6B35',
  'gpt-4o': '#10B981',
  'perplexity-sonar': '#A855F7',
  system: '#6E7681',
};

// ─── Component ──────────────────────────────────────────────────────

export function WarRoom({ sessionId, seuToken, caseTitle, onVerdictReached }: WarRoomProps) {
  const [messages, setMessages] = useState<WarRoomMessage[]>([]);
  const [connectionState, setConnectionState] = useState<string>('CLOSED');
  const [retryCount, setRetryCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sseClientRef = useRef<ResilientSSEClient | null>(null);

  // ─── SSE Message Handler ──────────────────────────────────────
  const handleSSEMessage = useCallback(
    (event: SSEMessage) => {
      try {
        const msg: WarRoomMessage = JSON.parse(event.data);

        setMessages((prev) => {
          // Deduplicate by ID
          if (prev.some((m) => m.id === msg.id)) return prev;
          return [...prev, msg];
        });

        if (msg.type === 'verdict') {
          onVerdictReached?.(msg);
        }
      } catch {
        // Non-JSON message — treat as system
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            model: 'system',
            type: 'system',
            content: event.data,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    },
    [onVerdictReached],
  );

  // ─── Connect SSE ──────────────────────────────────────────────
  useEffect(() => {
    const client = createWarRoomSSEClient(sessionId, seuToken, handleSSEMessage);

    // Override callbacks for state tracking
    const originalConfig = client as unknown as { config: Record<string, unknown> };
    const _origOnOpen = originalConfig.config.onOpen as (() => void) | undefined;
    const _origOnClose = originalConfig.config.onClose as (() => void) | undefined;

    sseClientRef.current = client;

    // Track connection state via polling
    const statePoller = setInterval(() => {
      setConnectionState(client.state);
      setRetryCount(client.currentRetryCount);
    }, 1000);

    client.connect();

    return () => {
      clearInterval(statePoller);
      client.disconnect();
    };
  }, [sessionId, seuToken, handleSSEMessage]);

  // ─── Auto-scroll ──────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // ─── Render ───────────────────────────────────────────────────
  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: '#0D1117',
        color: '#c9d1d9',
        fontFamily: 'Inter, sans-serif',
      }}
    >
      {/* Header */}
      <header
        style={{
          padding: '16px 24px',
          borderBottom: '1px solid #21262d',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h1
            style={{
              fontSize: '20px',
              fontFamily: 'Space Grotesk, sans-serif',
              color: '#f0f6fc',
              margin: 0,
            }}
          >
            ⚔️ War Room
          </h1>
          <p style={{ fontSize: '13px', color: '#8b949e', margin: '4px 0 0 0' }}>{caseTitle}</p>
        </div>

        {/* Connection Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background:
                connectionState === 'OPEN'
                  ? '#3fb950'
                  : connectionState === 'RECONNECTING'
                    ? '#d29922'
                    : '#f85149',
            }}
          />
          <span style={{ color: '#8b949e' }}>
            {connectionState === 'OPEN'
              ? 'Live'
              : connectionState === 'RECONNECTING'
                ? `Reconnecting (${retryCount})`
                : connectionState === 'CONNECTING'
                  ? 'Connecting...'
                  : 'Disconnected'}
          </span>
        </div>
      </header>

      {/* Messages Stream */}
      <div
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px 24px',
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              marginBottom: '16px',
              padding: '16px',
              background: msg.type === 'verdict' ? 'rgba(0, 212, 255, 0.08)' : '#161b22',
              border: `1px solid ${msg.type === 'verdict' ? '#00D4FF' : '#30363d'}`,
              borderLeft: `3px solid ${MODEL_COLORS[msg.model] ?? '#6e7681'}`,
              borderRadius: '6px',
            }}
          >
            {/* Message Header */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: MODEL_COLORS[msg.model] ?? '#8b949e',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  {msg.model}
                </span>
                <span
                  style={{
                    fontSize: '10px',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background:
                      msg.type === 'dissent'
                        ? 'rgba(248, 81, 73, 0.15)'
                        : msg.type === 'verdict'
                          ? 'rgba(0, 212, 255, 0.15)'
                          : 'rgba(110, 118, 129, 0.15)',
                    color:
                      msg.type === 'dissent'
                        ? '#f85149'
                        : msg.type === 'verdict'
                          ? '#00D4FF'
                          : '#8b949e',
                  }}
                >
                  {msg.type}
                </span>
              </div>

              {msg.confidence !== undefined && (
                <span
                  style={{
                    fontSize: '12px',
                    color:
                      msg.confidence >= 0.8
                        ? '#3fb950'
                        : msg.confidence >= 0.5
                          ? '#d29922'
                          : '#f85149',
                  }}
                >
                  {Math.round(msg.confidence * 100)}% confidence
                </span>
              )}
            </div>

            {/* Content */}
            <p style={{ fontSize: '14px', lineHeight: '1.6', margin: 0 }}>{msg.content}</p>

            {/* Citations */}
            {msg.citations && msg.citations.length > 0 && (
              <div
                style={{
                  marginTop: '12px',
                  paddingTop: '8px',
                  borderTop: '1px solid #21262d',
                }}
              >
                {msg.citations.map((c) => (
                  <div
                    key={`${c.caseTitle}-${c.citation}`}
                    style={{ fontSize: '12px', color: '#8b949e', marginBottom: '4px' }}
                  >
                    📑 <em>{c.caseTitle}</em>, {c.citation}
                  </div>
                ))}
              </div>
            )}

            {/* Timestamp */}
            <div style={{ fontSize: '11px', color: '#484f58', marginTop: '8px' }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer */}
      <footer
        style={{
          padding: '12px 24px',
          borderTop: '1px solid #21262d',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: '#484f58',
        }}
      >
        <span>{messages.length} messages</span>
        <span>Session: {sessionId.slice(0, 8)}…</span>
      </footer>
    </div>
  );
}
