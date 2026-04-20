import { useCallback, useEffect, useState } from 'react';
import './index.css';

// ── Types ─────────────────────────────────────────────────────────────────────

interface ClientSession {
  session_id: string;
  client_name: string;
  client_email: string;
  model_used: string;
  status: 'active' | 'completed' | 'expired';
  started_at: string;
  ended_at: string | null;
  kovel_hash: string;
  query_count: number;
}

interface TranscriptEntry {
  role: 'client' | 'attorney' | 'ai';
  content: string;
  timestamp: string;
  model?: string;
}

interface KovelReceipt {
  attestation_id: string;
  session_id: string;
  hmac_hash: string;
  attorney_bar_id: string;
  jurisdiction: string;
  created_at: string;
  privilege_type: string;
  heppner_compliant: boolean;
}

interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  enabled: boolean;
  tier: 'primary' | 'fallback' | 'research';
}

interface ClientInfo {
  client_id: string;
  name: string;
  email: string;
  last_session: string;
  total_sessions: number;
  status: 'authorized' | 'pending' | 'revoked';
}

// ── Demo Data ─────────────────────────────────────────────────────────────────

const DEMO_SESSIONS: ClientSession[] = [
  {
    session_id: 'sess_7b3e9a1f',
    client_name: 'Martinez Corp',
    client_email: 'legal@martinez-corp.com',
    model_used: 'gemini-3.1-flash-lite',
    status: 'active',
    started_at: '2026-04-18T14:23:00Z',
    ended_at: null,
    kovel_hash: 'a8f3b2c1d9e7f6a5b4c3d2e1f0a9b8c7',
    query_count: 12,
  },
  {
    session_id: 'sess_4d8c2e7b',
    client_name: 'Blackwell Industries',
    client_email: 'jblackwell@blackwell-ind.com',
    model_used: 'claude-sonnet-4.5',
    status: 'completed',
    started_at: '2026-04-18T09:15:00Z',
    ended_at: '2026-04-18T10:42:00Z',
    kovel_hash: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9',
    query_count: 28,
  },
  {
    session_id: 'sess_1a5f8d3c',
    client_name: 'Chen & Associates',
    client_email: 'mchen@chenlaw.co',
    model_used: 'gpt-4o',
    status: 'completed',
    started_at: '2026-04-17T16:00:00Z',
    ended_at: '2026-04-17T17:30:00Z',
    kovel_hash: 'f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6',
    query_count: 19,
  },
  {
    session_id: 'sess_9e2b6f4a',
    client_name: 'Rivera Holdings',
    client_email: 'arivera@riverahold.com',
    model_used: 'gemini-3.1-flash-lite',
    status: 'expired',
    started_at: '2026-04-16T11:00:00Z',
    ended_at: '2026-04-16T11:30:00Z',
    kovel_hash: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7',
    query_count: 3,
  },
];

const DEMO_TRANSCRIPT: TranscriptEntry[] = [
  {
    role: 'client',
    content: 'I need guidance on the tax implications of our proposed merger with TechVenture Inc.',
    timestamp: '2026-04-18T14:23:12Z',
  },
  {
    role: 'ai',
    content:
      'Based on the information provided, the merger between Martinez Corp and TechVenture Inc. would likely qualify as a tax-free reorganization under IRC § 368(a)(1)(A) if structured as a statutory merger. Key considerations include: (1) compliance with the continuity of interest doctrine requiring at least 40% stock consideration per Rev. Proc. 77-37, (2) the continuity of business enterprise requirement under Treas. Reg. § 1.368-1(d), and (3) potential application of the step transaction doctrine if there are post-merger asset dispositions planned.',
    timestamp: '2026-04-18T14:23:45Z',
    model: 'gemini-3.1-flash-lite',
  },
  {
    role: 'attorney',
    content:
      '[OVERSIGHT NOTE] The analysis correctly identifies § 368 as the governing framework. Recommend client review the specific consideration structure with their M&A team before proceeding.',
    timestamp: '2026-04-18T14:25:00Z',
  },
  {
    role: 'client',
    content: 'What about the impact on our existing NOL carryforwards?',
    timestamp: '2026-04-18T14:26:30Z',
  },
  {
    role: 'ai',
    content:
      'Post-merger NOL carryforward utilization will be subject to IRC § 382 limitations. Under § 382, if there is an ownership change (generally >50% shift in stock ownership by value over a 3-year testing period), annual NOL usage is limited to the value of the loss corporation multiplied by the long-term tax-exempt rate. Current rate as of April 2026 is approximately 5.2%. Additionally, consider the SRLY rules under Treas. Reg. § 1.1502-21 if filing consolidated returns post-merger.',
    timestamp: '2026-04-18T14:27:15Z',
    model: 'gemini-3.1-flash-lite',
  },
];

const DEMO_RECEIPT: KovelReceipt = {
  attestation_id: 'att_7b3e9a1f_001',
  session_id: 'sess_7b3e9a1f',
  hmac_hash: 'HMAC-SHA256:a8f3b2c1d9e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2',
  attorney_bar_id: 'NY-4521873',
  jurisdiction: 'S.D.N.Y.',
  created_at: '2026-04-18T14:23:00Z',
  privilege_type: 'Kovel (Accountant-Client under Attorney Umbrella)',
  heppner_compliant: true,
};

const DEMO_MODELS: ModelConfig[] = [
  {
    id: 'gemini-flash',
    name: 'Gemini 3.1 Flash Lite',
    provider: 'Google',
    enabled: true,
    tier: 'primary',
  },
  {
    id: 'claude-sonnet',
    name: 'Claude Sonnet 4.5',
    provider: 'Anthropic',
    enabled: true,
    tier: 'fallback',
  },
  { id: 'gpt-4o', name: 'GPT-4o', provider: 'OpenAI', enabled: true, tier: 'fallback' },
  { id: 'grok-3', name: 'Grok 3', provider: 'xAI', enabled: false, tier: 'research' },
  {
    id: 'perplexity',
    name: 'Perplexity Sonar',
    provider: 'Perplexity',
    enabled: false,
    tier: 'research',
  },
  {
    id: 'deepseek-r1',
    name: 'DeepSeek R1',
    provider: 'DeepSeek',
    enabled: false,
    tier: 'research',
  },
];

const DEMO_CLIENTS: ClientInfo[] = [
  {
    client_id: 'cl_001',
    name: 'Martinez Corp',
    email: 'legal@martinez-corp.com',
    last_session: '2026-04-18',
    total_sessions: 15,
    status: 'authorized',
  },
  {
    client_id: 'cl_002',
    name: 'Blackwell Industries',
    email: 'jblackwell@blackwell-ind.com',
    last_session: '2026-04-18',
    total_sessions: 28,
    status: 'authorized',
  },
  {
    client_id: 'cl_003',
    name: 'Chen & Associates',
    email: 'mchen@chenlaw.co',
    last_session: '2026-04-17',
    total_sessions: 7,
    status: 'authorized',
  },
  {
    client_id: 'cl_004',
    name: 'Rivera Holdings',
    email: 'arivera@riverahold.com',
    last_session: '2026-04-16',
    total_sessions: 3,
    status: 'pending',
  },
  {
    client_id: 'cl_005',
    name: 'Thompson Legal Group',
    email: 'kthompson@tlg.law',
    last_session: '—',
    total_sessions: 0,
    status: 'revoked',
  },
];

// ── Navigation ────────────────────────────────────────────────────────────────

type View = 'overview' | 'sessions' | 'clients' | 'models' | 'billing';

const NAV_ITEMS: { view: View; icon: string; label: string; badge?: number }[] = [
  { view: 'overview', icon: '◉', label: 'Dashboard' },
  { view: 'sessions', icon: '◫', label: 'Sessions', badge: 1 },
  { view: 'clients', icon: '◎', label: 'Clients' },
  { view: 'models', icon: '⬡', label: 'Model Routing' },
  { view: 'billing', icon: '◈', label: 'Billing' },
];

// ── Utility ───────────────────────────────────────────────────────────────────

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Components ────────────────────────────────────────────────────────────────

function StatCard({
  value,
  label,
  accent,
}: {
  value: string | number;
  label: string;
  accent: string;
}) {
  return (
    <div className={`glass-panel stat-card ${accent} animate-fade-in`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

function OverviewView({ onNavigate }: { onNavigate: (v: View) => void }) {
  const activeSessions = DEMO_SESSIONS.filter((s) => s.status === 'active').length;
  const totalQueries = DEMO_SESSIONS.reduce((sum, s) => sum + s.query_count, 0);
  const enabledModels = DEMO_MODELS.filter((m) => m.enabled).length;
  const authorizedClients = DEMO_CLIENTS.filter((c) => c.status === 'authorized').length;

  return (
    <>
      <div className="stats-grid">
        <StatCard value={activeSessions} label="Active Sessions" accent="green" />
        <StatCard value={totalQueries} label="Total Queries (7d)" accent="cyan" />
        <StatCard value={enabledModels} label="Models Active" accent="violet" />
        <StatCard value={authorizedClients} label="Authorized Clients" accent="gold" />
      </div>

      <div className="section-header">
        <div>
          <div className="section-title">Recent Sessions</div>
          <div className="section-subtitle">Client research sessions with privilege protection</div>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('sessions')}>
          View All →
        </button>
      </div>

      <div className="glass-panel animate-slide-up">
        <table className="session-table">
          <thead>
            <tr>
              <th>Client</th>
              <th>Model</th>
              <th>Status</th>
              <th>Queries</th>
              <th>Started</th>
            </tr>
          </thead>
          <tbody>
            {DEMO_SESSIONS.slice(0, 3).map((s) => (
              <tr key={s.session_id}>
                <td style={{ fontWeight: 600 }}>{s.client_name}</td>
                <td>
                  <span className="badge badge-model">{s.model_used}</span>
                </td>
                <td>
                  <span className={`badge badge-${s.status}`}>
                    {s.status === 'active' && '● '}
                    {s.status.charAt(0).toUpperCase() + s.status.slice(1)}
                  </span>
                </td>
                <td>{s.query_count}</td>
                <td style={{ color: 'var(--text-tertiary)' }}>{relativeTime(s.started_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 'var(--space-xl)' }}>
        <div className="section-header">
          <div>
            <div className="section-title">Privilege Shield</div>
            <div className="section-subtitle">
              Kovel attestation status under <em>United States v. Heppner</em>
            </div>
          </div>
        </div>

        <div className="glass-panel receipt-card animate-slide-up">
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 'var(--space-md)',
            }}
          >
            <div>
              <span className="badge badge-privileged">◈ Privilege Protected</span>
              <span className="badge badge-active" style={{ marginLeft: 'var(--space-sm)' }}>
                Heppner Compliant
              </span>
            </div>
            <span style={{ fontSize: '0.73rem', color: 'var(--text-muted)' }}>
              {DEMO_SESSIONS.length} sessions attested
            </span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Latest Attestation</span>
            <span className="receipt-value">{DEMO_RECEIPT.attestation_id}</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Jurisdiction</span>
            <span className="receipt-value">{DEMO_RECEIPT.jurisdiction}</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Attorney Bar ID</span>
            <span className="receipt-value">{DEMO_RECEIPT.attorney_bar_id}</span>
          </div>
          <div className="receipt-hash">{DEMO_RECEIPT.hmac_hash}</div>
        </div>
      </div>
    </>
  );
}

function SessionDetailView({ session, onBack }: { session: ClientSession; onBack: () => void }) {
  const [tab, setTab] = useState<'transcript' | 'receipt' | 'memo'>('transcript');

  return (
    <div className="animate-fade-in">
      <button
        className="btn btn-ghost btn-sm"
        onClick={onBack}
        style={{ marginBottom: 'var(--space-md)' }}
      >
        ← Back to Sessions
      </button>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-md)',
          marginBottom: 'var(--space-lg)',
        }}
      >
        <div className="client-avatar" style={{ width: 56, height: 56, fontSize: '1.2rem' }}>
          {session.client_name.charAt(0)}
        </div>
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{session.client_name}</h3>
          <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 4 }}>
            <span className={`badge badge-${session.status}`}>
              {session.status === 'active' && '● '}
              {session.status}
            </span>
            <span className="badge badge-model">{session.model_used}</span>
            <span className="badge badge-privileged">◈ Kovel</span>
          </div>
        </div>
      </div>

      <div className="tab-bar">
        <button
          className={`tab-btn ${tab === 'transcript' ? 'active' : ''}`}
          onClick={() => setTab('transcript')}
        >
          Transcript
        </button>
        <button
          className={`tab-btn ${tab === 'receipt' ? 'active' : ''}`}
          onClick={() => setTab('receipt')}
        >
          Kovel Receipt
        </button>
        <button
          className={`tab-btn ${tab === 'memo' ? 'active' : ''}`}
          onClick={() => setTab('memo')}
        >
          Oracle Memo
        </button>
      </div>

      {tab === 'transcript' && (
        <div className="glass-panel transcript-panel">
          {DEMO_TRANSCRIPT.map((entry, i) => (
            <div className="transcript-entry" key={i}>
              <div className={`transcript-role ${entry.role}`}>
                {entry.role === 'ai' ? `AI (${entry.model})` : entry.role}
              </div>
              <div className="transcript-text">{entry.content}</div>
              <div className="transcript-time">{formatTime(entry.timestamp)}</div>
            </div>
          ))}
        </div>
      )}

      {tab === 'receipt' && (
        <div className="glass-panel receipt-card">
          <div className="receipt-field">
            <span className="receipt-label">Attestation ID</span>
            <span className="receipt-value">{DEMO_RECEIPT.attestation_id}</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Session ID</span>
            <span
              className="receipt-value"
              style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}
            >
              {DEMO_RECEIPT.session_id}
            </span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Privilege Type</span>
            <span className="receipt-value">{DEMO_RECEIPT.privilege_type}</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Attorney Bar ID</span>
            <span className="receipt-value">{DEMO_RECEIPT.attorney_bar_id}</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Jurisdiction</span>
            <span className="receipt-value">{DEMO_RECEIPT.jurisdiction}</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Heppner Compliant</span>
            <span className="receipt-value">
              {DEMO_RECEIPT.heppner_compliant ? '✓ Yes' : '✗ No'}
            </span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Created</span>
            <span className="receipt-value">{formatDate(DEMO_RECEIPT.created_at)}</span>
          </div>
          <div className="receipt-hash">{DEMO_RECEIPT.hmac_hash}</div>
          <div style={{ marginTop: 'var(--space-md)', display: 'flex', gap: 'var(--space-sm)' }}>
            <button className="btn btn-primary btn-sm">Download Receipt</button>
            <button className="btn btn-secondary btn-sm">Verify Hash</button>
          </div>
        </div>
      )}

      {tab === 'memo' && (
        <div className="glass-panel oracle-memo">
          <h3>Research Summary — Tax Implications of Proposed Merger</h3>
          <p>
            The client inquiry concerns the federal tax treatment of a proposed merger between
            Martinez Corp and TechVenture Inc. Based on the facts presented, the transaction appears
            to qualify as a<span className="memo-citation"> IRC § 368(a)(1)(A)</span> tax-free
            reorganization.
          </p>

          <h3>Key Legal Framework</h3>
          <p>
            The governing authority for tax-free mergers is{' '}
            <span className="memo-citation">IRC § 368</span>, as interpreted by{' '}
            <span className="memo-citation">Treas. Reg. § 1.368-1</span> and relevant case law. Two
            primary doctrines must be satisfied:
          </p>
          <ol style={{ paddingLeft: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
            <li style={{ marginBottom: 'var(--space-sm)' }}>
              <strong>Continuity of Interest</strong> — Per{' '}
              <span className="memo-citation">Rev. Proc. 77-37</span>, at least 40% of consideration
              must be stock.
            </li>
            <li style={{ marginBottom: 'var(--space-sm)' }}>
              <strong>Continuity of Business Enterprise</strong> — Under
              <span className="memo-citation"> Treas. Reg. § 1.368-1(d)</span>, the acquiring
              corporation must continue historic business or use a significant portion of historic
              assets.
            </li>
          </ol>

          <h3>NOL Carryforward Limitation</h3>
          <p>
            Post-merger NOL utilization is subject to{' '}
            <span className="memo-citation">IRC § 382</span> annual limitations. The current
            long-term tax-exempt rate of approximately 5.2% (April 2026) would cap annual usage at
            the equity value of the loss corporation multiplied by this rate.
          </p>

          <h3>Recommended Actions</h3>
          <ol style={{ paddingLeft: 'var(--space-lg)', color: 'var(--text-secondary)' }}>
            <li style={{ marginBottom: 'var(--space-sm)' }}>
              Confirm consideration structure achieves ≥40% stock ratio
            </li>
            <li style={{ marginBottom: 'var(--space-sm)' }}>
              Obtain § 382 valuation from independent appraiser
            </li>
            <li style={{ marginBottom: 'var(--space-sm)' }}>
              Review step transaction risk for any planned post-merger dispositions
            </li>
            <li>Coordinate with M&amp;A counsel on SRLY rules for consolidated return filing</li>
          </ol>

          <div
            style={{
              marginTop: 'var(--space-lg)',
              padding: 'var(--space-md)',
              background: 'var(--accent-gold-dim)',
              borderRadius: 'var(--radius-sm)',
              borderLeft: '3px solid var(--accent-gold)',
            }}
          >
            <strong style={{ color: 'var(--accent-gold)', fontSize: '0.8rem' }}>
              PRIVILEGE NOTICE
            </strong>
            <p style={{ fontSize: '0.8rem', marginTop: 'var(--space-xs)' }}>
              This memo is generated within a Kovel-privileged session and constitutes attorney work
              product protected under <em>United States v. Heppner</em> (S.D.N.Y., Feb. 10, 2026).
              Do not distribute outside the attorney-client relationship.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function SessionsView() {
  const [selectedSession, setSelectedSession] = useState<ClientSession | null>(null);

  if (selectedSession) {
    return <SessionDetailView session={selectedSession} onBack={() => setSelectedSession(null)} />;
  }

  return (
    <>
      <div className="section-header">
        <div>
          <div className="section-title">All Sessions</div>
          <div className="section-subtitle">Privilege-protected client research sessions</div>
        </div>
        <button className="btn btn-primary btn-sm">+ New Session</button>
      </div>

      <div className="glass-panel animate-slide-up">
        <table className="session-table">
          <thead>
            <tr>
              <th>Session</th>
              <th>Client</th>
              <th>Model</th>
              <th>Status</th>
              <th>Queries</th>
              <th>Started</th>
              <th>Kovel Hash</th>
            </tr>
          </thead>
          <tbody>
            {DEMO_SESSIONS.map((s) => (
              <tr key={s.session_id} onClick={() => setSelectedSession(s)}>
                <td
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.8rem',
                    color: 'var(--text-tertiary)',
                  }}
                >
                  {s.session_id}
                </td>
                <td style={{ fontWeight: 600 }}>{s.client_name}</td>
                <td>
                  <span className="badge badge-model">{s.model_used}</span>
                </td>
                <td>
                  <span className={`badge badge-${s.status}`}>
                    {s.status === 'active' && '● '}
                    {s.status}
                  </span>
                </td>
                <td>{s.query_count}</td>
                <td style={{ color: 'var(--text-tertiary)' }}>
                  {formatDate(s.started_at)} {formatTime(s.started_at)}
                </td>
                <td
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '0.73rem',
                    color: 'var(--accent-gold)',
                  }}
                >
                  {s.kovel_hash.slice(0, 12)}…
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function ClientsView() {
  return (
    <>
      <div className="section-header">
        <div>
          <div className="section-title">Client Management</div>
          <div className="section-subtitle">
            Authorized clients for privileged AI research sessions
          </div>
        </div>
        <button className="btn btn-primary btn-sm">+ Authorize Client</button>
      </div>

      <div className="client-grid">
        {DEMO_CLIENTS.map((c) => (
          <div className="glass-panel client-card animate-fade-in" key={c.client_id}>
            <div className="client-avatar">{c.name.charAt(0)}</div>
            <div className="client-info" style={{ flex: 1 }}>
              <h4>{c.name}</h4>
              <p>{c.email}</p>
              <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 6 }}>
                <span
                  className={`badge ${c.status === 'authorized' ? 'badge-active' : c.status === 'pending' ? 'badge-completed' : 'badge-expired'}`}
                >
                  {c.status}
                </span>
                <span style={{ fontSize: '0.73rem', color: 'var(--text-muted)' }}>
                  {c.total_sessions} sessions
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

function ModelsView() {
  const [models, setModels] = useState(DEMO_MODELS);

  const toggleModel = useCallback((id: string) => {
    setModels((prev) => prev.map((m) => (m.id === id ? { ...m, enabled: !m.enabled } : m)));
  }, []);

  return (
    <>
      <div className="section-header">
        <div>
          <div className="section-title">Model Routing Configuration</div>
          <div className="section-subtitle">
            Control which LLM providers are available to clients. All routing passes through Judge
            #6.
          </div>
        </div>
      </div>

      <div className="model-grid">
        {models.map((m) => (
          <div
            className={`glass-panel model-card ${m.enabled ? 'active' : 'disabled'}`}
            key={m.id}
            onClick={() => toggleModel(m.id)}
          >
            <div className="model-name">{m.name}</div>
            <div className="model-provider">{m.provider}</div>
            <div style={{ marginTop: 'var(--space-sm)' }}>
              <span
                className={`badge ${m.tier === 'primary' ? 'badge-active' : m.tier === 'fallback' ? 'badge-completed' : 'badge-privileged'}`}
              >
                {m.tier}
              </span>
            </div>
            <div
              className={`model-toggle ${m.enabled ? 'on' : ''}`}
              role="switch"
              aria-checked={m.enabled}
              aria-label={`Toggle ${m.name}`}
            />
          </div>
        ))}
      </div>

      <div className="glass-panel" style={{ marginTop: 'var(--space-xl)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: 'var(--success)',
              boxShadow: '0 0 6px var(--success)',
            }}
          />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.87rem' }}>Judge #6 Gate Active</div>
            <div style={{ fontSize: '0.73rem', color: 'var(--text-tertiary)' }}>
              All model routing decisions pass through ATP 5-19 policy evaluation. Hallucination
              circuit breaker (RKILL) is armed.
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function BillingView() {
  return (
    <>
      <div className="section-header">
        <div>
          <div className="section-title">Billing & Subscription</div>
          <div className="section-subtitle">Stripe Connect dual-billing configuration</div>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard value="$149" label="Monthly Plan" accent="gold" />
        <StatCard value="62" label="Queries This Month" accent="cyan" />
        <StatCard value="$0.00" label="Overage Charges" accent="green" />
        <StatCard value="3" label="Active Clients" accent="violet" />
      </div>

      <div className="detail-grid">
        <div className="glass-panel animate-fade-in">
          <div className="section-title" style={{ marginBottom: 'var(--space-md)' }}>
            Subscription Details
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Plan</span>
            <span className="receipt-value">Solo — $149/mo</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Billing Cycle</span>
            <span className="receipt-value">Monthly (renews May 18, 2026)</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Stripe Account</span>
            <span
              className="receipt-value"
              style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}
            >
              acct_••••keMi
            </span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Beta Discount</span>
            <span className="receipt-value">
              <span className="badge badge-active">50% off (3mo)</span>
            </span>
          </div>
          <div style={{ marginTop: 'var(--space-md)' }}>
            <button className="btn btn-secondary btn-sm">Manage in Stripe ↗</button>
          </div>
        </div>

        <div className="glass-panel animate-fade-in">
          <div className="section-title" style={{ marginBottom: 'var(--space-md)' }}>
            Client Billing (Stripe Connect)
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Revenue (MTD)</span>
            <span className="receipt-value" style={{ fontWeight: 700, color: 'var(--success)' }}>
              $1,240.00
            </span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Paying Clients</span>
            <span className="receipt-value">3 of 4</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Average Per Query</span>
            <span className="receipt-value">$20.00</span>
          </div>
          <div className="receipt-field">
            <span className="receipt-label">Payout Status</span>
            <span className="receipt-value">
              <span className="badge badge-active">● Enabled</span>
            </span>
          </div>
          <div style={{ marginTop: 'var(--space-md)' }}>
            <button className="btn btn-secondary btn-sm">View Payouts ↗</button>
          </div>
        </div>
      </div>
    </>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState<View>('overview');
  const [, setTime] = useState(Date.now());

  // Refresh relative times every minute
  useEffect(() => {
    const id = setInterval(() => setTime(Date.now()), 60000);
    return () => clearInterval(id);
  }, []);

  const viewTitle: Record<View, { title: string; sub: string }> = {
    overview: {
      title: 'Attorney Dashboard',
      sub: 'CounselConduit — Privilege-Preserving AI Research',
    },
    sessions: {
      title: 'Sessions',
      sub: 'Client research sessions with Kovel privilege protection',
    },
    clients: { title: 'Clients', sub: 'Manage authorized clients for AI research portal' },
    models: { title: 'Model Routing', sub: 'Configure LLM providers and routing policies' },
    billing: { title: 'Billing', sub: 'Stripe Connect subscription and client billing' },
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>
            Counsel<span>Conduit</span>
          </h1>
          <p>Attorney Portal</p>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.view}
              className={`nav-btn ${view === item.view ? 'active' : ''}`}
              onClick={() => setView(item.view)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
              {item.badge && <span className="nav-badge">{item.badge}</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>KMS Enforced • Heppner Compliant</span>
        </div>
      </aside>

      {/* Main */}
      <div className="main-area">
        <header className="main-header">
          <div>
            <h2>{viewTitle[view].title}</h2>
            <div className="header-sub">{viewTitle[view].sub}</div>
          </div>
          <div style={{ display: 'flex', gap: 'var(--space-sm)', alignItems: 'center' }}>
            <span className="badge badge-privileged">◈ Kovel Shield Active</span>
            <button className="btn btn-secondary btn-sm">⟳ Refresh</button>
          </div>
        </header>

        <div className="main-body">
          {view === 'overview' && <OverviewView onNavigate={setView} />}
          {view === 'sessions' && <SessionsView />}
          {view === 'clients' && <ClientsView />}
          {view === 'models' && <ModelsView />}
          {view === 'billing' && <BillingView />}
        </div>
      </div>
    </div>
  );
}
