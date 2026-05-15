'use client';

import { useState } from 'react';

interface PipelineRun {
  id: string;
  project: string;
  timestamp: string;
  status: 'success' | 'running' | 'failed';
  framesExtracted: number;
  creditsUsed: number;
  duration: string;
}

export default function PipelineDashboard() {
  const [runs, _setRuns] = useState<PipelineRun[]>([
    {
      id: 'run_001',
      project: 'headfade',
      timestamp: '2026-05-06 00:45:12',
      status: 'success',
      framesExtracted: 87,
      creditsUsed: 2450,
      duration: '4m 32s',
    },
    {
      id: 'run_002',
      project: 'kovelai',
      timestamp: '2026-05-05 23:18:45',
      status: 'success',
      framesExtracted: 64,
      creditsUsed: 1890,
      duration: '3m 51s',
    },
  ]);

  const [totalCreditsUsed, _setTotalCreditsUsed] = useState(4340);
  const [remainingCredits, _setRemainingCredits] = useState(9650);

  return (
    <div className="max-w-6xl mx-auto p-8 bg-zinc-950 text-white">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold">Generative Pipeline Dashboard</h1>
          <p className="text-zinc-400">HeadFade + KovelAI • Google Ultra AI Credits</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-zinc-500">REMAINING CREDITS</div>
          <div className="text-3xl font-bold text-emerald-400">
            {remainingCredits.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
          <div className="text-sm text-zinc-400">Total Runs</div>
          <div className="text-4xl font-bold mt-2">{runs.length}</div>
        </div>
        <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
          <div className="text-sm text-zinc-400">Total Frames Generated</div>
          <div className="text-4xl font-bold mt-2">
            {runs.reduce((sum, r) => sum + r.framesExtracted, 0)}
          </div>
        </div>
        <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
          <div className="text-sm text-zinc-400">Credits Consumed</div>
          <div className="text-4xl font-bold mt-2 text-rose-400">
            {totalCreditsUsed.toLocaleString()}
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
        <div className="px-6 py-4 border-b border-zinc-800 flex justify-between items-center">
          <h2 className="font-semibold">Recent Pipeline Runs</h2>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="px-4 py-1.5 text-sm bg-white text-black rounded-lg hover:bg-zinc-200"
          >
            Refresh
          </button>
        </div>

        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800 text-left text-sm text-zinc-400">
              <th className="px-6 py-3">Run ID</th>
              <th className="px-6 py-3">Project</th>
              <th className="px-6 py-3">Timestamp</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Frames</th>
              <th className="px-6 py-3">Credits Used</th>
              <th className="px-6 py-3">Duration</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id} className="border-b border-zinc-800 hover:bg-zinc-800/50">
                <td className="px-6 py-4 font-mono text-sm">{run.id}</td>
                <td className="px-6 py-4">
                  <span
                    className={`px-2 py-0.5 rounded text-xs ${run.project === 'headfade' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}
                  >
                    {run.project}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-zinc-400">{run.timestamp}</td>
                <td className="px-6 py-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${run.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}
                  >
                    {run.status}
                  </span>
                </td>
                <td className="px-6 py-4 font-mono">{run.framesExtracted}</td>
                <td className="px-6 py-4 font-mono text-rose-400">{run.creditsUsed}</td>
                <td className="px-6 py-4 text-sm text-zinc-400">{run.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-8 text-xs text-zinc-500 text-center">
        Powered by Google Ultra AI • Jules + Stitch MCP • Nano Banana 2 / Whisk / Flow • Pomelli
      </div>
    </div>
  );
}
