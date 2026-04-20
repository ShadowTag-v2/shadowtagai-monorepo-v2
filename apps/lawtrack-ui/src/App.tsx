import { useCallback, useEffect, useReducer, useState } from 'react';
import './index.css';

// ── Types ─────────────────────────────────────────────────────────────────────

interface Extraction {
  extraction_id: string;
  matter_id: string;
  trigger_event: string;
  exhibit_citation_id: string;
  calculated_due_date: string;
  jurisdiction_rule: string;
  days_to_respond: number;
  business_days_only: boolean;
  confidence: number;
  status: 'pending_approval' | 'approved' | 'rejected';
  created_at: string;
}

type Action =
  | { type: 'SET_QUEUE'; payload: Extraction[] }
  | { type: 'SET_DOCKET'; payload: Extraction[] }
  | { type: 'APPROVE'; id: string; updated: Extraction }
  | { type: 'REJECT'; id: string; updated: Extraction }
  | { type: 'SET_ERROR'; msg: string }
  | { type: 'SET_LOADING'; loading: boolean };

interface State {
  queue: Extraction[];
  docket: Extraction[];
  loading: boolean;
  error: string | null;
}

// ── API ───────────────────────────────────────────────────────────────────────

const API = import.meta.env.VITE_ZT_API_URL ?? 'http://localhost:8000';
// DEMO_MATTER_ID is the matter whose queue and docket this UI manages.
// In a multi-matter app this would come from routing / auth context.
const MATTER_ID = import.meta.env.VITE_MATTER_ID ?? 'aaaaaaaa-0000-0000-0000-000000000001';
// APPROVER_ID is the currently authenticated user. Replace with real auth.
const APPROVER_ID = import.meta.env.VITE_APPROVER_ID ?? 'ffffffff-0000-0000-0000-000000000001';

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${body}`);
  }
  return res.json() as Promise<T>;
}

// ── Reducer ───────────────────────────────────────────────────────────────────

const initial: State = { queue: [], docket: [], loading: false, error: null };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.loading, error: null };
    case 'SET_ERROR':
      return { ...state, loading: false, error: action.msg };
    case 'SET_QUEUE':
      return { ...state, queue: action.payload, loading: false };
    case 'SET_DOCKET':
      return { ...state, docket: action.payload, loading: false };
    case 'APPROVE':
      return {
        ...state,
        queue: state.queue.filter((e) => e.extraction_id !== action.id),
        docket: [...state.docket, action.updated].sort(
          (a, b) =>
            new Date(a.calculated_due_date).getTime() - new Date(b.calculated_due_date).getTime(),
        ),
      };
    case 'REJECT':
      return {
        ...state,
        queue: state.queue.filter((e) => e.extraction_id !== action.id),
      };
  }
}

// ── Components ────────────────────────────────────────────────────────────────

function ConfidencePip({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 90 ? 'var(--success-green)' : pct >= 70 ? 'var(--warn-amber)' : 'var(--alert-red)';
  return (
    <span className="confidence-pip" style={{ color, borderColor: color }}>
      {pct}%
    </span>
  );
}

function QueueCard({
  item,
  onApprove,
  onReject,
}: {
  item: Extraction;
  onApprove: (id: string) => void;
  onReject: (id: string, reason: string) => void;
}) {
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState('');
  const daysUntil = Math.ceil(
    (new Date(item.calculated_due_date).getTime() - Date.now()) / 86_400_000,
  );
  const urgent = daysUntil <= 7;

  return (
    <div className={`glass-panel queue-card animate-slide-up ${urgent ? 'urgent' : ''}`}>
      <div className="queue-card-header">
        <div>
          <span className="trigger-label">{item.trigger_event}</span>
          <span className="citation-id">{item.exhibit_citation_id}</span>
        </div>
        <ConfidencePip value={item.confidence} />
      </div>

      <div className="queue-meta">
        <span className={`due-badge ${urgent ? 'urgent' : ''}`}>
          Due {item.calculated_due_date}
          {urgent && <span> — {daysUntil}d</span>}
        </span>
        <span className="rule-tag">{item.jurisdiction_rule || 'FRCP'}</span>
        <span className="biz-days">
          {item.days_to_respond}d {item.business_days_only ? 'business' : 'calendar'}
        </span>
      </div>

      {rejecting ? (
        <div className="reject-form">
          <input
            className="reject-input"
            placeholder="Rejection reason (required)"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            autoFocus
          />
          <div className="action-row">
            <button
              type="button"
              className="btn-reject"
              disabled={!reason.trim()}
              onClick={() => {
                onReject(item.extraction_id, reason.trim());
                setRejecting(false);
              }}
            >
              Confirm Reject
            </button>
            <button type="button" className="btn-ghost" onClick={() => setRejecting(false)}>
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="action-row">
          <button type="button" className="btn-approve" onClick={() => onApprove(item.extraction_id)}>
            Approve
          </button>
          <button type="button" className="btn-reject-outline" onClick={() => setRejecting(true)}>
            Reject
          </button>
        </div>
      )}
    </div>
  );
}

function DocketRow({ item }: { item: Extraction }) {
  const daysUntil = Math.ceil(
    (new Date(item.calculated_due_date).getTime() - Date.now()) / 86_400_000,
  );
  const urgent = daysUntil <= 7;
  return (
    <div className="docket-row glass-panel">
      <div className="docket-date">
        <span className={urgent ? 'alert-text' : ''}>{item.calculated_due_date}</span>
      </div>
      <div className="docket-info">
        <span className="trigger-label">{item.trigger_event}</span>
        <span className="rule-tag">{item.jurisdiction_rule || 'FRCP'}</span>
      </div>
      <div className="docket-citation">{item.exhibit_citation_id}</div>
    </div>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const [state, dispatch] = useReducer(reducer, initial);
  const [tab, setTab] = useState<'queue' | 'docket'>('queue');

  const refresh = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', loading: true });
    try {
      const [queue, docket] = await Promise.all([
        apiFetch<Extraction[]>(
          `/api/v1/zt/matters/${MATTER_ID}/queue?include_status=pending_approval`,
        ),
        apiFetch<Extraction[]>(`/api/v1/zt/matters/${MATTER_ID}/docket`),
      ]);
      dispatch({ type: 'SET_QUEUE', payload: queue });
      dispatch({ type: 'SET_DOCKET', payload: docket });
    } catch (e) {
      dispatch({ type: 'SET_ERROR', msg: (e as Error).message });
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleApprove = useCallback(async (id: string) => {
    try {
      const updated = await apiFetch<Extraction>(`/api/v1/zt/extractions/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ approver_id: APPROVER_ID }),
      });
      dispatch({ type: 'APPROVE', id, updated });
    } catch (e) {
      dispatch({ type: 'SET_ERROR', msg: (e as Error).message });
    }
  }, []);

  const handleReject = useCallback(async (id: string, reason: string) => {
    try {
      const updated = await apiFetch<Extraction>(`/api/v1/zt/extractions/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ rejector_id: APPROVER_ID, reason }),
      });
      dispatch({ type: 'REJECT', id, updated });
    } catch (e) {
      dispatch({ type: 'SET_ERROR', msg: (e as Error).message });
    }
  }, []);

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <h1 className="sidebar-logo">
          Cor.<span style={{ color: 'var(--accent-cyan)' }}>LawTrack</span>
        </h1>
        <p className="sidebar-meta">
          Matter: {MATTER_ID.slice(0, 8)}&hellip;
          <br />
          ZT.1 Approval Queue
        </p>

        <nav className="sidebar-nav">
          <button
            type="button"
            className={`nav-item ${tab === 'queue' ? 'active' : ''}`}
            onClick={() => setTab('queue')}
          >
            Pending
            {state.queue.length > 0 && <span className="badge">{state.queue.length}</span>}
          </button>
          <button
            type="button"
            className={`nav-item ${tab === 'docket' ? 'active' : ''}`}
            onClick={() => setTab('docket')}
          >
            Docket
            {state.docket.length > 0 && (
              <span className="badge badge-approved">{state.docket.length}</span>
            )}
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="status-dot" />
          <span>KMS Enforced</span>
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        <header className="main-header">
          <div>
            <h2>{tab === 'queue' ? 'Approval Queue' : 'Master Docket'}</h2>
            <p className="header-sub">
              {tab === 'queue'
                ? 'Agent-drafted deadlines awaiting attorney verification'
                : 'Approved deadlines — chronological'}
            </p>
          </div>
          <button type="button" className="btn-refresh" onClick={refresh} disabled={state.loading}>
            {state.loading ? 'Loading…' : 'Refresh'}
          </button>
        </header>

        {state.error && (
          <div className="error-banner">
            <strong>Error:</strong> {state.error}
          </div>
        )}

        {tab === 'queue' && (
          <div className="card-grid">
            {state.queue.length === 0 && !state.loading && (
              <p className="empty-state">No pending extractions.</p>
            )}
            {state.queue.map((item) => (
              <QueueCard
                key={item.extraction_id}
                item={item}
                onApprove={handleApprove}
                onReject={handleReject}
              />
            ))}
          </div>
        )}

        {tab === 'docket' && (
          <div className="docket-list">
            {state.docket.length === 0 && !state.loading && (
              <p className="empty-state">No approved deadlines yet.</p>
            )}
            {state.docket.map((item) => (
              <DocketRow key={item.extraction_id} item={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
