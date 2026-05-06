'use client';
import { useEffect, useState } from 'react';
import { JulesSessionControl } from '../../../../../../packages/ui/JulesSessionControl';
import '../../../../../../packages/ui/jules-session.css';
import '../../../../../../packages/ui/index.css';

export default function DarkFactoryDashboard() {
  const [sessionState, setSessionState] = useState({
    status: 'UNINITIALIZED',
    sessionName: 'Initializing...',
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setSessionState((prev) => {
        if (prev.status === 'UNINITIALIZED') return { status: 'CONNECTING', sessionName: 'Connecting to Jules...' };
        if (prev.status === 'CONNECTING') return { status: 'PENDING_APPROVAL', sessionName: 'jules-session-8f3a2c' };
        return prev;
      });
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  const handleApprove = (msg: string) => {
    console.log('Plan Approved:', msg);
    setSessionState({ status: 'ACTIVE', sessionName: 'jules-session-8f3a2c (Executing)' });
  };

  const handleInteract = (msg: string) => {
    console.log('Interact:', msg);
  };

  return (
    <div className="sovereign-bg min-h-screen" style={{ backgroundColor: '#0a0a0c', padding: '2rem' }}>
      <header style={{ marginBottom: '3rem', borderBottom: '1px solid #333', paddingBottom: '1rem' }}>
        <h1 style={{ color: '#fff', fontSize: '2rem', fontFamily: 'monospace', letterSpacing: '0.05em' }}>
          Sovereign Command Center
        </h1>
        <p style={{ color: '#888', marginTop: '0.5rem' }}>Monitoring autonomous orchestration swarm.</p>
      </header>

      <main style={{ maxWidth: '800px' }}>
        <JulesSessionControl
          sourceName="ShadowTag Omega v4 Monorepo"
          sessionName={sessionState.sessionName}
          status={sessionState.status}
          onApprovePlan={handleApprove}
          onInteract={handleInteract}
        />
      </main>
    </div>
  );
}
