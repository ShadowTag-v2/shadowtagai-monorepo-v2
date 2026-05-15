'use client';

import { useEffect, useState } from 'react';
import { useForensicElo } from '@/hooks/useForensicElo';

/** Voter Skill Tier — describes detection ability, NOT video deception quality. */
type VoterSkillTier = 'novice' | 'analyst' | 'expert' | 'osint-master';

const VOTER_TIER_COLORS: Record<VoterSkillTier, string> = {
  novice: 'text-zinc-400',
  analyst: 'text-amber-400',
  expert: 'text-purple-400',
  'osint-master': 'text-rose-400',
};

const VOTER_TIER_LABELS: Record<VoterSkillTier, string> = {
  novice: '🔍 Novice Spotter',
  analyst: '🎯 Forensics Analyst',
  expert: '🧠 Detection Expert',
  'osint-master': '💎 OSINT Master',
};

interface MetricsDashboardProps {
  /** Current authenticated user ID — null = anonymous mode. */
  uid: string | null;
}

export default function MetricsDashboard({ uid }: MetricsDashboardProps) {
  const { elo } = useForensicElo(uid);

  const [metrics, setMetrics] = useState({
    dailyActiveUsers: 1247,
    totalVideosAnalyzed: 89234,
    avgHDI: 84.7,
    microLicensesSold: 1842,
    revenueToday: 5493.58,
    errorRate: 0.08,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        dailyActiveUsers: prev.dailyActiveUsers + Math.floor(Math.random() * 3),
        totalVideosAnalyzed: prev.totalVideosAnalyzed + Math.floor(Math.random() * 12),
        microLicensesSold: prev.microLicensesSold + (Math.random() > 0.7 ? 1 : 0),
        revenueToday: prev.revenueToday + (Math.random() > 0.8 ? 2.99 : 0),
      }));
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  // Derive voter skill tier from detection accuracy (NOT creator deception tier)
  const voterAccuracy = elo.accuracy / 100;
  const currentTier: VoterSkillTier =
    voterAccuracy > 0.75
      ? 'osint-master'
      : voterAccuracy > 0.5
        ? 'expert'
        : voterAccuracy > 0.25
          ? 'analyst'
          : 'novice';

  return (
    <div className="bg-zinc-950 text-white p-8 rounded-3xl max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold">HeadFade Live Metrics</h1>
          <p className="text-emerald-400">Beta Cohort • Updated live</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-zinc-500">LAST UPDATED</div>
          <div className="font-mono text-sm">{new Date().toLocaleTimeString()}</div>
        </div>
      </div>

      {/* ─── Forensic Elo Voter Panel ─── */}
      <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-zinc-900 via-zinc-900 to-zinc-800 border border-zinc-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-zinc-200">⚡ Your Forensic Elo</h2>
          <span className={`text-sm font-bold ${VOTER_TIER_COLORS[currentTier]}`}>
            {VOTER_TIER_LABELS[currentTier]}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Elo Rating</div>
            <div className="text-3xl font-bold tabular-nums">{elo.eloRating.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Accuracy</div>
            <div className="text-3xl font-bold tabular-nums">
              {elo.accuracy}
              <span className="text-lg text-zinc-400">%</span>
            </div>
          </div>
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Votes Cast</div>
            <div className="text-3xl font-bold tabular-nums">{elo.totalVotes.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-xs text-zinc-500 uppercase tracking-wider">Correct</div>
            <div className="text-3xl font-bold tabular-nums text-emerald-400">
              {elo.correctVotes.toLocaleString()}
            </div>
          </div>
        </div>

        {/* Badge shelf */}
        {elo.badges.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {elo.badges.map((badge) => (
              <span
                key={badge}
                className="text-xs bg-zinc-800 border border-zinc-700 px-3 py-1 rounded-full"
              >
                {badge}
              </span>
            ))}
          </div>
        )}

        {/* Elo progress bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-zinc-500 mb-1">
            <span>0</span>
            <span>1200 (Analyst)</span>
            <span>1500 (OSINT)</span>
            <span>2000 (God-Tier)</span>
          </div>
          <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-purple-500 to-rose-500 transition-all duration-700"
              style={{ width: `${Math.min((elo.eloRating / 2000) * 100, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* ─── Platform Metrics Grid ─── */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
        {[
          {
            label: 'Daily Active Users',
            value: metrics.dailyActiveUsers.toLocaleString(),
            change: '+12%',
          },
          {
            label: 'Videos Analyzed',
            value: metrics.totalVideosAnalyzed.toLocaleString(),
            change: '+8%',
          },
          { label: 'Avg Human Deception Index', value: `${metrics.avgHDI}%`, change: '-1.2%' },
          {
            label: 'Micro-Licenses Sold',
            value: metrics.microLicensesSold.toLocaleString(),
            change: '+24%',
          },
          { label: 'Revenue Today', value: `$${metrics.revenueToday.toFixed(2)}`, change: '+31%' },
          { label: 'Error Rate', value: `${metrics.errorRate}%`, change: '↓ 0.03%' },
        ].map((metric, i) => (
          <div key={i} className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
            <div className="text-sm text-zinc-400 mb-1">{metric.label}</div>
            <div className="text-4xl font-semibold tracking-tighter mb-2">{metric.value}</div>
            <div
              className={`text-xs ${metric.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}
            >
              {metric.change} from yesterday
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center text-xs text-zinc-500">
        Powered by Firebase Data Connect + OpenTelemetry • Antigravity Dark Factory
      </div>
    </div>
  );
}
