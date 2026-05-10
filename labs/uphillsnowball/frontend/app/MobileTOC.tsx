// frontend/app/MobileTOC.tsx
//
// Mobile Theater of Operations Command — The Untethered Architect PWA
//
// This is the Commander's mobile glass. From here, the Theater Commander:
//   1. Issues OPORDs with SHA-256 mission hash locking
//   2. Authorizes or rejects backbriefs
//   3. Monitors real-time campaign status
//
// The SHA-256 hash is computed client-side using Web Crypto API for
// zero-latency edge hashing. The mission is immutable once locked.

'use client';

import { useCallback, useState } from 'react';

// Status type for campaign tracking
type CampaignStatus =
  | 'IDLE'
  | 'DISPATCHED'
  | 'BACKBRIEF_PENDING'
  | 'EXECUTING'
  | 'COMPLETE'
  | 'FAILED';

export default function MobileTheaterCommand() {
  const [mission, setMission] = useState('');
  const [opordHash, setOpordHash] = useState('');
  const [status, setStatus] = useState<CampaignStatus>('IDLE');
  const [error, setError] = useState('');

  const lockOpordAndDispatch = useCallback(async () => {
    if (!mission.trim()) return;
    setError('');

    try {
      // Web Crypto API: Zero-Latency Client-Side Edge Hashing
      const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(mission));
      const hashHex = Array.from(new Uint8Array(hashBuffer))
        .map((b) => b.toString(16).padStart(2, '0'))
        .join('')
        .substring(0, 16)
        .toUpperCase();

      setOpordHash(hashHex);
      setStatus('DISPATCHED');

      const response = await fetch('/api/v5/zta/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-Id': 'T-001',
        },
        body: JSON.stringify({
          payload: mission,
          hash: hashHex,
          agent_id: 'Architect',
          tenant_id: 'T-001',
        }),
      });

      if (response.status === 402) {
        setError('WET FLEECE: Payment required. Invoice past due.');
        setStatus('FAILED');
      } else if (response.status === 423) {
        setError('RKILL: Payload blocked by Judge 6.1.');
        setStatus('FAILED');
      } else if (response.status === 406) {
        setError('KICKBACK: Unauthorized practice detected.');
        setStatus('FAILED');
      } else if (response.ok) {
        setStatus('BACKBRIEF_PENDING');
      }
    } catch (err) {
      setError(`Dispatch failed: ${err}`);
      setStatus('FAILED');
    }
  }, [mission]);

  const authorizeBackbrief = useCallback(async (approved: boolean) => {
    try {
      await fetch('/api/v5/temporal/signal_backbrief', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ authorized: approved }),
      });
      setStatus(approved ? 'EXECUTING' : 'FAILED');
    } catch (err) {
      setError(`Signal failed: ${err}`);
    }
  }, []);

  const resetMission = useCallback(() => {
    setMission('');
    setOpordHash('');
    setStatus('IDLE');
    setError('');
  }, []);

  const statusColor: Record<CampaignStatus, string> = {
    IDLE: 'text-gray-400',
    DISPATCHED: 'text-yellow-400',
    BACKBRIEF_PENDING: 'text-amber-400',
    EXECUTING: 'text-emerald-400',
    COMPLETE: 'text-green-400',
    FAILED: 'text-red-400',
  };

  return (
    <div className="bg-[#02050a] h-[100dvh] w-full font-mono text-emerald-500 flex flex-col shadow-2xl p-5 select-none">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-bold text-white border-b border-emerald-900 pb-2">
          JTF COMMAND NODE
        </h1>
        <span className={`text-[10px] font-bold ${statusColor[status]}`}>● {status}</span>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-3 mb-4">
          <p className="text-[10px] text-red-400 font-bold">{error}</p>
        </div>
      )}

      {/* OPORD Input */}
      <div className="bg-black border border-emerald-900/50 rounded-xl p-4 shadow-lg flex-1">
        <h2 className="text-xs font-bold text-emerald-500 mb-2 flex items-center gap-2">
          ◆ ISSUE OPORD (AIM)
        </h2>
        <textarea
          className="w-full bg-transparent text-emerald-400 text-xs min-h-[150px] outline-none resize-none placeholder:text-emerald-900"
          value={mission}
          onChange={(e) => setMission(e.target.value)}
          disabled={!!opordHash}
          placeholder="State the Commander's Intent..."
        />
        {opordHash ? (
          <div className="mt-2 flex items-center justify-between">
            <p className="text-[10px] text-emerald-400">🔒 LOCKED: {opordHash}</p>
            <button onClick={resetMission} className="text-[10px] text-red-400 underline">
              RESET
            </button>
          </div>
        ) : (
          <button
            onClick={lockOpordAndDispatch}
            disabled={!mission.trim()}
            className="mt-4 bg-emerald-800 text-white p-3 rounded-lg text-xs font-bold w-full disabled:opacity-30 active:bg-emerald-700 transition-colors"
          >
            LOCK HASH & DISPATCH
          </button>
        )}
      </div>

      {/* Backbrief Authorization */}
      {status === 'BACKBRIEF_PENDING' && (
        <div className="mt-4 bg-amber-900/20 border border-amber-500/30 rounded-xl p-4">
          <h3 className="text-xs font-bold text-amber-400 mb-3">
            ⚠ BACKBRIEF AWAITING AUTHORIZATION
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => authorizeBackbrief(true)}
              className="flex-1 bg-emerald-800 text-white py-3 rounded-lg text-xs font-bold active:bg-emerald-700"
            >
              ✓ AUTHORIZE
            </button>
            <button
              onClick={() => authorizeBackbrief(false)}
              className="flex-1 bg-red-900 text-white py-3 rounded-lg text-xs font-bold active:bg-red-800"
            >
              ✗ REJECT
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 text-center">
        <p className="text-[8px] text-emerald-900">
          pnkln v.OMEGA | gemini-3.1-flash-lite-preview-thinking | SHA-256 IMMUTABLE
        </p>
      </div>
    </div>
  );
}
