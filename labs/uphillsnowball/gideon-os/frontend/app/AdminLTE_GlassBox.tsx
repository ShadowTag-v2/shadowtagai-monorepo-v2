// frontend/app/AdminLTE_GlassBox.tsx
// ============================================================================
// AdminLTE Command Nexus — React + AdminLTE + WebSocket
// ============================================================================
// Block 11 of the Ex Toto Omni-Compile (Gideon OS Architecture)
// Declarative React UI. AdminLTE styling. Secure BLAST Auth.
// ============================================================================
'use client';
import { useEffect, useRef, useState } from 'react';

interface Message {
  type: string;
  payload: {
    text?: string;
    component?: string;
    data?: { requires_deployment?: boolean; [key: string]: unknown };
    [key: string]: unknown;
  };
}

export function GlassBoxDashboard() {
  const [systemState] = useState('FEDERAL_COMPLIANCE_ACTIVE');
  const endRef = useRef<HTMLDivElement>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host || 'ide.sovereign-gideon.com';
    const socket = new WebSocket(`${protocol}//${host}/relay`);

    socket.onopen = () => {
      setWs(socket);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  return (
    <div
      style={{
        display: 'flex',
        height: '100vh',
        backgroundColor: '#1a1a2e',
        color: '#e0e0e0',
        fontFamily: 'monospace',
      }}
    >
      {/* Sidebar */}
      <aside
        style={{
          width: '25%',
          padding: '1rem',
          borderRight: '1px solid #333',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        <h3 style={{ color: '#00ff88', fontWeight: 'bold' }}>GIDEON OS COCKPIT</h3>
        <div
          style={{
            padding: '0.5rem',
            border: '1px solid #00ff88',
            borderRadius: '4px',
            fontSize: '0.75rem',
            color: '#00ff88',
          }}
        >
          SYS_STATE: {systemState}
        </div>

        <button
          type="button"
          onClick={() => ws?.send(JSON.stringify({ type: 'ACTIVATE_WARRANT_PROTOCOL' }))}
          style={{
            padding: '0.75rem',
            border: '1px solid #ff4444',
            borderRadius: '4px',
            backgroundColor: 'transparent',
            color: '#ff4444',
            cursor: 'pointer',
            fontFamily: 'monospace',
          }}
        >
          The Blue Button (LE-1)
        </button>

        {/* Telepathy Stream */}
        <div
          style={{
            flexGrow: 1,
            overflow: 'auto',
            backgroundColor: 'rgba(0,0,0,0.5)',
            padding: '0.5rem',
            borderRadius: '4px',
            border: '1px solid #333',
            fontSize: '0.75rem',
            color: '#888',
          }}
        >
          <div
            style={{
              color: '#00bfff',
              fontWeight: 'bold',
              marginBottom: '0.5rem',
            }}
          >
            TELEPATHY STREAM
          </div>
          {messages
            .filter((m) => m.type === 'THOUGHT_STREAM')
            .map((m, i) => (
              <div key={i}>&gt; {m.payload.text}</div>
            ))}
          <div ref={endRef} />
        </div>
      </aside>

      {/* Main Content */}
      <div style={{ width: '75%', padding: '2rem', overflow: 'auto' }}>
        <h4
          style={{
            color: '#ff4444',
            fontWeight: 'bold',
            marginBottom: '1.5rem',
          }}
        >
          KINETIC OUTPUT
        </h4>
        {messages
          .filter((m) => m.type === 'UI_RENDER_COMPONENT')
          .map((m, idx) => (
            <div
              key={idx}
              style={{
                border: '1px solid #ff4444',
                borderRadius: '8px',
                backgroundColor: 'rgba(0,0,0,0.5)',
                padding: '1.5rem',
                marginBottom: '1.5rem',
                boxShadow: '0 4px 16px rgba(255,68,68,0.1)',
              }}
            >
              <pre>{JSON.stringify(m.payload, null, 2)}</pre>
              {m.payload.data?.requires_deployment && (
                <button
                  type="button"
                  disabled
                  style={{
                    padding: '0.5rem 1rem',
                    marginTop: '1rem',
                    backgroundColor: '#333',
                    color: '#888',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'not-allowed',
                  }}
                >
                  Awaiting Hammock Protocol (Check Obsidian)
                </button>
              )}
            </div>
          ))}
      </div>
    </div>
  );
}
