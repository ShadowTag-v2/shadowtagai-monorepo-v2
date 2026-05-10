'use client';

/**
 * Uphill Snowball — Mobile Theater of Command (C2 PWA)
 *
 * The Apex Architect Glass. A single pane of glass for the
 * Enterprise Commander to issue intent, lock OPORD hashes,
 * and dispatch Uphill Snowball campaigns.
 *
 * SHA-256 locks the Commander's Intent at the client layer.
 * Once locked, the mission is immutable — no prompt drift possible.
 */

import { useCallback, useState } from 'react';

async function sha256Hex(text: string): Promise<string> {
  const buffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .substring(0, 16)
    .toUpperCase();
}

type CampaignStatus = 'idle' | 'dispatching' | 'locked' | 'error';

export default function UphillSnowballTheaterCommand() {
  const [mission, setMission] = useState('');
  const [opordHash, setOpordHash] = useState('');
  const [status, setStatus] = useState<CampaignStatus>('idle');
  const [workflowId, setWorkflowId] = useState('');

  const lockOpordAndDispatch = useCallback(async () => {
    if (!mission.trim()) return;
    setStatus('dispatching');

    try {
      const hashHex = await sha256Hex(mission);
      setOpordHash(hashHex);

      const response = await fetch('/api/v5/zta/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-Id': 'U-001',
        },
        body: JSON.stringify({ payload: mission, hash: hashHex }),
      });

      if (response.status === 423) {
        setStatus('error');
        return;
      }

      const data = await response.json();
      setWorkflowId(data.workflow_id || '');
      setStatus('locked');
    } catch {
      setStatus('error');
    }
  }, [mission]);

  return (
    <div className="bg-black h-[100dvh] w-full font-mono text-emerald-500 p-5 flex flex-col shadow-2xl">
      {/* ── Header ── */}
      <h1 className="text-lg font-bold text-white mb-2 border-b border-emerald-900 pb-2 tracking-widest">
        UPHILL SNOWBALL C2
      </h1>
      <p className="text-[10px] text-emerald-700 mb-6 uppercase tracking-wider">
        Sovereign Enterprise AI Infrastructure — Theater Command
      </p>

      {/* ── Mission Input ── */}
      <textarea
        className="w-full bg-transparent border border-emerald-900 rounded p-4 text-xs min-h-[150px] outline-none focus:border-emerald-500 transition-colors resize-none"
        value={mission}
        onChange={(e) => setMission(e.target.value)}
        disabled={status === 'locked'}
        placeholder="Issue Enterprise Commander's Intent..."
      />

      {/* ── Status Bar ── */}
      {status === 'locked' && opordHash && (
        <div className="mt-3 space-y-1">
          <p className="text-emerald-400 text-xs">
            🔒 OPORD LOCKED: <span className="font-bold text-white">{opordHash}</span>
          </p>
          {workflowId && <p className="text-emerald-600 text-[10px]">WORKFLOW: {workflowId}</p>}
        </div>
      )}

      {status === 'error' && (
        <p className="text-red-500 text-xs mt-3">
          ⛔ RKILL — Injection pattern detected or dispatch failed.
        </p>
      )}

      {/* ── Dispatch Button ── */}
      {status !== 'locked' && (
        <button
          onClick={lockOpordAndDispatch}
          disabled={!mission.trim() || status === 'dispatching'}
          className="mt-4 bg-emerald-800 text-white p-3 rounded font-bold w-full
                     hover:bg-emerald-700 active:bg-emerald-900
                     disabled:opacity-40 disabled:cursor-not-allowed
                     transition-all duration-150"
        >
          {status === 'dispatching' ? 'DISPATCHING...' : 'DISPATCH UPHILL SNOWBALL'}
        </button>
      )}

      {/* ── Footer ── */}
      <div className="mt-auto pt-4 border-t border-emerald-900/50">
        <p className="text-[9px] text-emerald-900 text-center uppercase">
          Judge 6.1 · ScholarEval · Temporal.io · Stripe Metered · PACER Verified
        </p>
      </div>
    </div>
  );
}
