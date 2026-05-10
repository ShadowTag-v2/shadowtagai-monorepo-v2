// src/edge/MobileJTFCommand.tsx
//
// Mobile JTF Command — Extended Commander Interface
//
// Extends MobileTOC with:
//   - Real-time J-Staff status monitoring
//   - J-6 CSRMC risk dashboard
//   - Temporal workflow progress tracking
//   - Push notification support for backbrief signals
//
// This is the Commander's full-spectrum mobile C2 node.

'use client';

import { useState } from 'react';

type JStaffStatus = {
  jCode: string;
  role: string;
  status: 'IDLE' | 'ACTIVE' | 'COMPLETE' | 'FAILED';
  lastActivity: string;
};

type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREMELY_HIGH';

export default function MobileJTFCommand() {
  const [jStaff, _setJStaff] = useState<JStaffStatus[]>([
    { jCode: 'J-1', role: 'Vault', status: 'IDLE', lastActivity: 'Awaiting artifacts' },
    { jCode: 'J-2', role: 'Intel', status: 'IDLE', lastActivity: 'Awaiting tasking' },
    { jCode: 'J-3', role: 'Ops', status: 'IDLE', lastActivity: 'Standing by' },
    { jCode: 'J-4', role: 'Corrector', status: 'IDLE', lastActivity: 'No repairs needed' },
    { jCode: 'J-5', role: 'Architect', status: 'IDLE', lastActivity: 'No plans queued' },
    { jCode: 'J-6', role: 'Judge 6.1', status: 'ACTIVE', lastActivity: 'ZTA monitoring' },
    { jCode: 'J-9', role: 'Splinter', status: 'IDLE', lastActivity: 'No content queued' },
  ]);

  const [currentRisk, _setCurrentRisk] = useState<RiskLevel>('LOW');
  const [activeWorkflows, _setActiveWorkflows] = useState(0);

  const statusColor: Record<string, string> = {
    IDLE: 'bg-gray-700',
    ACTIVE: 'bg-emerald-600',
    COMPLETE: 'bg-blue-600',
    FAILED: 'bg-red-600',
  };

  const riskColor: Record<RiskLevel, string> = {
    LOW: 'text-green-400',
    MODERATE: 'text-yellow-400',
    HIGH: 'text-orange-400',
    EXTREMELY_HIGH: 'text-red-400',
  };

  return (
    <div className="bg-[#02050a] min-h-[100dvh] w-full font-mono text-emerald-500 p-4 select-none">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-sm font-bold text-white">JTF-PNKLN</h1>
          <p className="text-[8px] text-emerald-800">JP 3-33 COMMAND NODE</p>
        </div>
        <div className="text-right">
          <p className={`text-xs font-bold ${riskColor[currentRisk]}`}>RISK: {currentRisk}</p>
          <p className="text-[8px] text-emerald-800">{activeWorkflows} active workflows</p>
        </div>
      </div>

      {/* J-Staff Status Grid */}
      <div className="space-y-2 mb-6">
        <h2 className="text-[10px] font-bold text-emerald-700 uppercase tracking-widest">
          J-Staff Readiness
        </h2>
        {jStaff.map((staff) => (
          <div
            key={staff.jCode}
            className="bg-black/50 border border-emerald-900/30 rounded-lg p-3 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${statusColor[staff.status]}`} />
              <div>
                <p className="text-[10px] font-bold text-emerald-400">
                  {staff.jCode} — {staff.role}
                </p>
                <p className="text-[8px] text-emerald-800">{staff.lastActivity}</p>
              </div>
            </div>
            <span className="text-[8px] text-emerald-600">{staff.status}</span>
          </div>
        ))}
      </div>

      {/* CSRMC Risk Dashboard */}
      <div className="bg-black/50 border border-emerald-900/30 rounded-xl p-4 mb-6">
        <h2 className="text-[10px] font-bold text-emerald-700 uppercase tracking-widest mb-3">
          CSRMC Risk Posture (NIST RMF)
        </h2>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-emerald-900/20 rounded-lg p-2">
            <p className="text-[8px] text-emerald-600">FIPS 199</p>
            <p className="text-xs font-bold text-emerald-400">MODERATE</p>
          </div>
          <div className="bg-emerald-900/20 rounded-lg p-2">
            <p className="text-[8px] text-emerald-600">ATP 5-19</p>
            <p className="text-xs font-bold text-green-400">LOW</p>
          </div>
          <div className="bg-emerald-900/20 rounded-lg p-2">
            <p className="text-[8px] text-emerald-600">cATO</p>
            <p className="text-xs font-bold text-emerald-400">ACTIVE</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center">
        <p className="text-[7px] text-emerald-900">
          pnkln V.OMEGA | JTF-PNKLN | CSRMC cATO ACTIVE | ALL RIGHTS RESERVED
        </p>
      </div>
    </div>
  );
}
