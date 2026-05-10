/**
 * Lawyer Dashboard — Anxiety Radar Widget
 *
 * Sprint Item #11: Attorney command center with radar visualization.
 *
 * Shows:
 * - Client anxiety radar chart (8 categories)
 * - Urgency heatmap
 * - Escalation alerts
 * - Active session count
 * - Token usage summary
 *
 * @see lib/vault/intent-vault.ts
 */

'use client';

import { useState } from 'react';

// ─── Types ──────────────────────────────────────────────────────────

interface RadarDataPoint {
  category: string;
  value: number;
  max: number;
}

interface ClientProfile {
  clientId: string;
  displayName: string;
  riskLevel: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
  avgUrgency: number;
  totalQueries: number;
  escalationCount: number;
  lastActivity: string;
  radarData: RadarDataPoint[];
}

interface DashboardStats {
  activeSessions: number;
  totalClients: number;
  todayQueries: number;
  tokenUsage: {
    daily: number;
    dailyLimit: number;
    monthly: number;
    monthlyLimit: number;
  };
}

// ─── Risk Level Badge ───────────────────────────────────────────────

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    LOW: { bg: 'rgba(62, 254, 138, 0.1)', text: '#3efe8a', border: 'rgba(62, 254, 138, 0.3)' },
    MODERATE: {
      bg: 'rgba(122, 208, 255, 0.1)',
      text: '#7ad0ff',
      border: 'rgba(122, 208, 255, 0.3)',
    },
    HIGH: { bg: 'rgba(255, 179, 71, 0.1)', text: '#ffb347', border: 'rgba(255, 179, 71, 0.3)' },
    CRITICAL: { bg: 'rgba(255, 82, 82, 0.1)', text: '#ff5252', border: 'rgba(255, 82, 82, 0.3)' },
  };

  const c = colors[level] ?? colors.LOW;

  return (
    <span
      style={{
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: 600,
        background: c.bg,
        color: c.text,
        border: `1px solid ${c.border}`,
        textTransform: 'uppercase' as const,
        letterSpacing: '0.05em',
      }}
    >
      {level}
    </span>
  );
}

// ─── SVG Radar Chart ────────────────────────────────────────────────

function RadarChart({ data }: { data: RadarDataPoint[] }) {
  const size = 200;
  const center = size / 2;
  const maxRadius = 80;
  const levels = 4;

  const angleStep = (2 * Math.PI) / data.length;

  // Generate polygon points for the data
  const points = data.map((d, i) => {
    const angle = i * angleStep - Math.PI / 2;
    const radius = (d.max > 0 ? d.value / d.max : 0) * maxRadius;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    };
  });

  const polygonPoints = points.map((p) => `${p.x},${p.y}`).join(' ');

  return (
    <svg aria-hidden="true" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Grid rings */}
      {Array.from({ length: levels }, (_, i) => ({
        level: i + 1,
        radius: ((i + 1) / levels) * maxRadius,
      })).map((ring) => {
        const ringPoints = data
          .map((d) => {
            const angle = data.indexOf(d) * angleStep - Math.PI / 2;
            return `${center + ring.radius * Math.cos(angle)},${center + ring.radius * Math.sin(angle)}`;
          })
          .join(' ');
        return (
          <polygon
            key={`ring-level-${ring.level}`}
            points={ringPoints}
            fill="none"
            stroke="#3c494e"
            strokeWidth="0.5"
            opacity={0.3}
          />
        );
      })}

      {/* Axes */}
      {data.map((d, i) => {
        const angle = i * angleStep - Math.PI / 2;
        return (
          <line
            key={`axis-${d.label}`}
            x1={center}
            y1={center}
            x2={center + maxRadius * Math.cos(angle)}
            y2={center + maxRadius * Math.sin(angle)}
            stroke="#3c494e"
            strokeWidth="0.5"
            opacity={0.3}
          />
        );
      })}

      {/* Data polygon */}
      <polygon
        points={polygonPoints}
        fill="rgba(0, 212, 255, 0.15)"
        stroke="#00d4ff"
        strokeWidth="1.5"
      />

      {/* Data points */}
      {points.map((p) => (
        <circle key={`point-${p.x}-${p.y}`} cx={p.x} cy={p.y} r="3" fill="#00d4ff" />
      ))}

      {/* Labels */}
      {data.map((d, i) => {
        const angle = i * angleStep - Math.PI / 2;
        const labelRadius = maxRadius + 18;
        const x = center + labelRadius * Math.cos(angle);
        const y = center + labelRadius * Math.sin(angle);
        return (
          <text
            key={`label-${d.label}`}
            x={x}
            y={y}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#859398"
            fontSize="8"
            fontFamily="Inter, sans-serif"
          >
            {d.category.split(' ')[0]}
          </text>
        );
      })}
    </svg>
  );
}

// ─── Main Dashboard Component ───────────────────────────────────────

export function LawyerDashboard() {
  const [stats] = useState<DashboardStats>({
    activeSessions: 3,
    totalClients: 12,
    todayQueries: 47,
    tokenUsage: {
      daily: 850_000,
      dailyLimit: 2_000_000,
      monthly: 18_500_000,
      monthlyLimit: 50_000_000,
    },
  });

  const [clients] = useState<ClientProfile[]>([
    {
      clientId: 'c1',
      displayName: 'Client A',
      riskLevel: 'HIGH',
      avgUrgency: 7.2,
      totalQueries: 23,
      escalationCount: 3,
      lastActivity: new Date(Date.now() - 300000).toISOString(),
      radarData: [
        { category: 'CRIMINAL', value: 8, max: 23 },
        { category: 'ASSET', value: 12, max: 23 },
        { category: 'FAMILY', value: 1, max: 23 },
        { category: 'REGULATORY', value: 2, max: 23 },
        { category: 'EMPLOYMENT', value: 0, max: 23 },
        { category: 'IMMIGRATION', value: 0, max: 23 },
        { category: 'INJURY', value: 0, max: 23 },
        { category: 'GENERAL', value: 0, max: 23 },
      ],
    },
    {
      clientId: 'c2',
      displayName: 'Client B',
      riskLevel: 'LOW',
      avgUrgency: 3.1,
      totalQueries: 8,
      escalationCount: 0,
      lastActivity: new Date(Date.now() - 3600000).toISOString(),
      radarData: [
        { category: 'CRIMINAL', value: 0, max: 8 },
        { category: 'ASSET', value: 1, max: 8 },
        { category: 'FAMILY', value: 5, max: 8 },
        { category: 'REGULATORY', value: 0, max: 8 },
        { category: 'EMPLOYMENT', value: 2, max: 8 },
        { category: 'IMMIGRATION', value: 0, max: 8 },
        { category: 'INJURY', value: 0, max: 8 },
        { category: 'GENERAL', value: 0, max: 8 },
      ],
    },
  ]);

  const [selectedClient, setSelectedClient] = useState<ClientProfile | null>(null);

  // Usage bar width
  const dailyPct = Math.round((stats.tokenUsage.daily / stats.tokenUsage.dailyLimit) * 100);
  const monthlyPct = Math.round((stats.tokenUsage.monthly / stats.tokenUsage.monthlyLimit) * 100);

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0d1117',
        color: '#e2e0fc',
        fontFamily: 'Inter, sans-serif',
      }}
    >
      {/* ── Header ── */}
      <header
        style={{
          padding: '16px 24px',
          background: '#111125',
          borderBottom: '1px solid rgba(60, 73, 78, 0.15)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h1
          style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: '20px',
            fontWeight: 600,
            letterSpacing: '-0.02em',
            margin: 0,
          }}
        >
          Attorney Dashboard
        </h1>
        <span
          style={{
            padding: '4px 12px',
            background: 'rgba(62, 254, 138, 0.1)',
            color: '#3efe8a',
            border: '1px solid rgba(62, 254, 138, 0.3)',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 600,
          }}
        >
          KOVEL ACTIVE
        </span>
      </header>

      {/* ── Stats Bar ── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '16px',
          padding: '24px',
        }}
      >
        {[
          { label: 'Active Sessions', value: stats.activeSessions, color: '#3efe8a' },
          { label: 'Total Clients', value: stats.totalClients, color: '#a8e8ff' },
          { label: "Today's Queries", value: stats.todayQueries, color: '#7ad0ff' },
          {
            label: 'Escalations',
            value: clients.reduce((a, c) => a + c.escalationCount, 0),
            color: '#ffb347',
          },
        ].map((stat) => (
          <div
            key={stat.label}
            style={{
              padding: '20px',
              background: '#1a1a2e',
              borderRadius: '6px',
              borderTop: '0.5px solid rgba(180, 235, 255, 0.08)',
            }}
          >
            <div
              style={{
                fontSize: '28px',
                fontWeight: 700,
                color: stat.color,
                fontFamily: 'Space Grotesk',
              }}
            >
              {stat.value}
            </div>
            <div style={{ fontSize: '13px', color: '#859398', marginTop: '4px' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* ── Main Layout ── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
          padding: '0 24px 24px',
        }}
      >
        {/* ── Client List ── */}
        <div
          style={{
            background: '#1a1a2e',
            borderRadius: '6px',
            padding: '20px',
          }}
        >
          <h2
            style={{
              fontFamily: 'Space Grotesk',
              fontSize: '16px',
              fontWeight: 600,
              marginBottom: '16px',
            }}
          >
            Client Activity
          </h2>
          {clients.map((client) => (
            <button
              type="button"
              key={client.clientId}
              onClick={() => setSelectedClient(client)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') setSelectedClient(client);
              }}
              style={{
                padding: '16px',
                marginBottom: '8px',
                background: selectedClient?.clientId === client.clientId ? '#28283d' : '#111125',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                transition: 'background 0.2s',
                border: 'none',
                width: '100%',
                color: 'inherit',
                textAlign: 'left',
              }}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '14px' }}>{client.displayName}</div>
                <div style={{ fontSize: '12px', color: '#859398', marginTop: '4px' }}>
                  {client.totalQueries} queries • Avg urgency: {client.avgUrgency}/10
                </div>
              </div>
              <RiskBadge level={client.riskLevel} />
            </button>
          ))}
        </div>

        {/* ── Radar Panel ── */}
        <div
          style={{
            background: '#1a1a2e',
            borderRadius: '6px',
            padding: '20px',
          }}
        >
          <h2
            style={{
              fontFamily: 'Space Grotesk',
              fontSize: '16px',
              fontWeight: 600,
              marginBottom: '16px',
            }}
          >
            Anxiety Radar
          </h2>
          {selectedClient ? (
            <div style={{ textAlign: 'center' }}>
              <RadarChart data={selectedClient.radarData} />
              <div style={{ marginTop: '16px' }}>
                <RiskBadge level={selectedClient.riskLevel} />
                <span style={{ marginLeft: '12px', fontSize: '13px', color: '#bbc9cf' }}>
                  {selectedClient.displayName}
                </span>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#859398', padding: '40px' }}>
              Select a client to view their anxiety radar
            </div>
          )}
        </div>
      </div>

      {/* ── Token Usage ── */}
      <div style={{ padding: '0 24px 24px' }}>
        <div
          style={{
            background: '#1a1a2e',
            borderRadius: '6px',
            padding: '20px',
          }}
        >
          <h2
            style={{
              fontFamily: 'Space Grotesk',
              fontSize: '16px',
              fontWeight: 600,
              marginBottom: '16px',
            }}
          >
            Token Budget
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '13px', color: '#859398', marginBottom: '6px' }}>
                Daily: {(stats.tokenUsage.daily / 1000).toFixed(0)}K /{' '}
                {(stats.tokenUsage.dailyLimit / 1_000_000).toFixed(0)}M ({dailyPct}%)
              </div>
              <div
                style={{
                  background: '#111125',
                  borderRadius: '4px',
                  height: '8px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    width: `${dailyPct}%`,
                    height: '100%',
                    background: dailyPct > 80 ? '#ffb347' : '#00d4ff',
                    borderRadius: '4px',
                    transition: 'width 0.3s',
                  }}
                />
              </div>
            </div>
            <div>
              <div style={{ fontSize: '13px', color: '#859398', marginBottom: '6px' }}>
                Monthly: {(stats.tokenUsage.monthly / 1_000_000).toFixed(1)}M /{' '}
                {(stats.tokenUsage.monthlyLimit / 1_000_000).toFixed(0)}M ({monthlyPct}%)
              </div>
              <div
                style={{
                  background: '#111125',
                  borderRadius: '4px',
                  height: '8px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    width: `${monthlyPct}%`,
                    height: '100%',
                    background: monthlyPct > 80 ? '#ffb347' : '#00d4ff',
                    borderRadius: '4px',
                    transition: 'width 0.3s',
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
