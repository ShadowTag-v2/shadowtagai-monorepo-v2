// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

/**
 * Firm Admin Dashboard
 *
 * The command center for law firm administrators to manage:
 * - Active client sessions (with privacy preservation)
 * - Billing & Stripe Connect status
 * - Team member access control
 * - Insurance compliance status
 * - AI usage metrics and cost tracking
 * - GDPR retention enforcement status
 *
 * Nag Protocol #19: Build firm admin dashboard
 */
'use client';
import { useState } from 'react';

// ─── Types ────────────────────────────────────────────────────────────
interface FirmStats {
  activeSessions: number;
  totalClients: number;
  monthlyRevenue: number;
  aiQueriesThisMonth: number;
  avgResponseTime: number;
  privilegeComplianceScore: number;
}

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'attorney' | 'paralegal' | 'intake';
  status: 'active' | 'invited' | 'suspended';
  lastActive: string;
  casesAssigned: number;
}

interface BillingStatus {
  tier: 'solo' | 'practice' | 'enterprise';
  stripeConnected: boolean;
  monthlySpend: number;
  nextBillingDate: string;
  paymentMethod: string;
  autoScaleTier: boolean;
}

interface InsuranceStatus {
  status: 'VERIFIED' | 'CONDITIONAL' | 'FAILED' | 'PENDING';
  carrier: string;
  coverage: number;
  expiryDate: string;
  daysUntilExpiry: number;
}

interface FirmAdminDashboardProps {
  firmName: string;
  firmId: string;
  stats: FirmStats;
  team: TeamMember[];
  billing: BillingStatus;
  insurance: InsuranceStatus;
}

// ─── Component ────────────────────────────────────────────────────────
export default function FirmAdminDashboard({
  firmName,
  firmId,
  stats,
  team,
  billing,
  insurance,
}: FirmAdminDashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'team' | 'billing' | 'compliance'>(
    'overview',
  );

  const tabs = [
    { key: 'overview' as const, label: 'Overview', icon: '📊' },
    { key: 'team' as const, label: 'Team', icon: '👥' },
    { key: 'billing' as const, label: 'Billing', icon: '💳' },
    { key: 'compliance' as const, label: 'Compliance', icon: '🛡️' },
  ];

  return (
    <div className="min-h-screen bg-black text-white font-sans">
      {/* Header */}
      <header className="border-b border-slate-800 px-8 py-5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black tracking-tight">{firmName}</h1>
            <p className="text-slate-500 text-xs font-mono mt-0.5">
              Firm ID: {firmId.slice(0, 8)}… • Admin Console
            </p>
          </div>
          <div className="flex gap-2">
            {tabs.map((tab) => (
              <button
                type="button"
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.key
                    ? 'bg-white text-black'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8">
        {/* ─── Overview Tab ──────────────────────────────────────── */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div className="grid grid-cols-3 lg:grid-cols-6 gap-4">
              <StatCard label="Active Sessions" value={stats.activeSessions} />
              <StatCard label="Total Clients" value={stats.totalClients} />
              <StatCard
                label="Monthly Revenue"
                value={`$${stats.monthlyRevenue.toLocaleString()}`}
              />
              <StatCard label="AI Queries" value={stats.aiQueriesThisMonth} />
              <StatCard label="Avg Response" value={`${stats.avgResponseTime}s`} />
              <StatCard
                label="Compliance"
                value={`${stats.privilegeComplianceScore}%`}
                isHighlight={stats.privilegeComplianceScore >= 95}
                isWarning={stats.privilegeComplianceScore < 90}
              />
            </div>

            {/* Quick Status */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">
                  Billing Status
                </h3>
                <div className="flex items-center gap-3 mb-3">
                  <span
                    className={`w-3 h-3 rounded-full ${
                      billing.stripeConnected ? 'bg-green-500' : 'bg-red-500 animate-pulse'
                    }`}
                  />
                  <span className="text-white font-medium">
                    {billing.stripeConnected ? 'Stripe Connected' : 'Stripe Not Connected'}
                  </span>
                </div>
                <div className="text-slate-500 text-sm space-y-1">
                  <div>
                    Tier: <span className="text-white uppercase">{billing.tier}</span>
                  </div>
                  <div>
                    Monthly:{' '}
                    <span className="text-white">${billing.monthlySpend.toLocaleString()}</span>
                  </div>
                  <div>
                    Next billing: <span className="text-white">{billing.nextBillingDate}</span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">
                  Insurance
                </h3>
                <div className="flex items-center gap-3 mb-3">
                  <span
                    className={`w-3 h-3 rounded-full ${
                      insurance.status === 'VERIFIED'
                        ? 'bg-green-500'
                        : insurance.status === 'CONDITIONAL'
                          ? 'bg-yellow-500 animate-pulse'
                          : 'bg-red-500 animate-pulse'
                    }`}
                  />
                  <span className="text-white font-medium">{insurance.status}</span>
                </div>
                <div className="text-slate-500 text-sm space-y-1">
                  <div>
                    Carrier: <span className="text-white">{insurance.carrier}</span>
                  </div>
                  <div>
                    Coverage:{' '}
                    <span className="text-white">${insurance.coverage.toLocaleString()}</span>
                  </div>
                  <div>
                    Expires in:{' '}
                    <span
                      className={insurance.daysUntilExpiry < 30 ? 'text-red-400' : 'text-white'}
                    >
                      {insurance.daysUntilExpiry} days
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─── Team Tab ──────────────────────────────────────────── */}
        {activeTab === 'team' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-bold">Team Members</h2>
              <button
                type="button"
                className="bg-white text-black px-4 py-2 rounded-lg text-sm font-bold hover:bg-slate-200 transition-colors"
              >
                + Invite Member
              </button>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 text-left text-xs uppercase tracking-widest">
                    <th className="px-4 py-3">Name</th>
                    <th className="px-4 py-3">Role</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Cases</th>
                    <th className="px-4 py-3">Last Active</th>
                    <th className="px-4 py-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {team.map((member) => (
                    <tr
                      key={member.id}
                      className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                    >
                      <td className="px-4 py-3">
                        <div className="font-medium text-white">{member.name}</div>
                        <div className="text-slate-500 text-xs">{member.email}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-xs uppercase">
                          {member.role}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-0.5 rounded text-xs ${
                            member.status === 'active'
                              ? 'bg-green-900 text-green-300'
                              : member.status === 'invited'
                                ? 'bg-blue-900 text-blue-300'
                                : 'bg-red-900 text-red-300'
                          }`}
                        >
                          {member.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400">{member.casesAssigned}</td>
                      <td className="px-4 py-3 text-slate-500 text-xs">
                        {new Date(member.lastActive).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <button type="button" className="text-slate-500 hover:text-white text-xs">
                          Manage
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ─── Billing Tab placeholder ───────────────────────────── */}
        {activeTab === 'billing' && (
          <div className="text-center text-slate-500 py-20 font-mono">
            Billing management panel — Stripe Connect integration active
          </div>
        )}

        {/* ─── Compliance Tab placeholder ────────────────────────── */}
        {activeTab === 'compliance' && (
          <div className="text-center text-slate-500 py-20 font-mono">
            Compliance dashboard — GDPR TTL enforcement, Insurance, Bar compliance
          </div>
        )}
      </main>
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────
function StatCard({
  label,
  value,
  isHighlight = false,
  isWarning = false,
}: {
  label: string;
  value: string | number;
  isHighlight?: boolean;
  isWarning?: boolean;
}) {
  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
      <div className="text-[9px] font-bold uppercase tracking-widest text-slate-500 mb-1">
        {label}
      </div>
      <div
        className={`text-xl font-black ${
          isWarning ? 'text-red-400' : isHighlight ? 'text-green-400' : 'text-white'
        }`}
      >
        {value}
      </div>
    </div>
  );
}
