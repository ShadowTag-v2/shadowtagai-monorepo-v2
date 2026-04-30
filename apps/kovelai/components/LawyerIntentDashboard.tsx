/**
 * Lawyer Intent Dashboard — "The Anxiety Radar"
 *
 * The lawyer sees exactly what the client is secretly terrified of.
 * Instead of handing the lawyer a raw 200-page transcript of search
 * results, we parse the client's searches and group them into an
 * "Anxiety Vector" — revealing the client's psychological map and
 * exact fears BEFORE the first phone call.
 *
 * Integration: Receives data from the Privileged Search Tunnel route
 * via the Intent Vault background queue.
 */
'use client';
import { useMemo, useState } from 'react';

// ─── Types ────────────────────────────────────────────────────────────
interface AnxietyVector {
  topic: string;
  searchCount: number;
  peakHour: string;
  urgencyScore: number;
  trend: 'rising' | 'stable' | 'declining';
}

interface SearchLog {
  clientQuery: string;
  aiResponseSnippet: string;
  timestamp: string;
  category: string;
  source: 'google_enterprise' | 'perplexity_sonar';
}

interface LawyerIntentDashboardProps {
  searchLogs: SearchLog[];
  anxietyVectors: AnxietyVector[];
  clientName: string;
  sessionId: string;
  sessionStart: string;
  sessionExpiry: string;
}

// ─── Urgency Color Map ────────────────────────────────────────────────
function getUrgencyColor(score: number): {
  bg: string;
  border: string;
  text: string;
  badge: string;
} {
  if (score >= 9)
    return {
      bg: 'bg-red-950',
      border: 'border-red-500',
      text: 'text-red-300',
      badge: 'bg-red-600',
    };
  if (score >= 7)
    return {
      bg: 'bg-orange-950',
      border: 'border-orange-500',
      text: 'text-orange-300',
      badge: 'bg-orange-600',
    };
  if (score >= 5)
    return {
      bg: 'bg-yellow-950',
      border: 'border-yellow-500',
      text: 'text-yellow-300',
      badge: 'bg-yellow-600',
    };
  return {
    bg: 'bg-slate-900',
    border: 'border-slate-600',
    text: 'text-slate-400',
    badge: 'bg-slate-600',
  };
}

function getTrendIcon(trend: string): string {
  if (trend === 'rising') return '📈';
  if (trend === 'declining') return '📉';
  return '➡️';
}

// ─── Component ────────────────────────────────────────────────────────
export default function LawyerIntentDashboard({
  searchLogs,
  anxietyVectors,
  clientName,
  sessionId,
  sessionStart,
  sessionExpiry,
}: LawyerIntentDashboardProps) {
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [expandedLog, setExpandedLog] = useState<number | null>(null);

  // Sort vectors by urgency (highest first)
  const sortedVectors = useMemo(
    () => [...anxietyVectors].sort((a, b) => b.urgencyScore - a.urgencyScore),
    [anxietyVectors],
  );

  // Filter logs by category
  const filteredLogs = useMemo(
    () =>
      activeFilter === 'all'
        ? searchLogs
        : searchLogs.filter((log) => log.category === activeFilter),
    [searchLogs, activeFilter],
  );

  // Calculate session metrics
  const totalSearches = searchLogs.length;
  const peakAnxiety = sortedVectors.length > 0 ? sortedVectors[0] : null;
  const uniqueCategories = new Set(searchLogs.map((l) => l.category)).size;

  return (
    <div className="min-h-screen bg-black text-white font-sans">
      {/* ─── Header ──────────────────────────────────────────────── */}
      <header className="border-b border-slate-800 px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight">Client Research & Intent Radar</h1>
            <p className="text-slate-500 text-sm mt-1 font-mono">
              Session {sessionId.slice(0, 8)}… • {clientName} • Kovel Protected
            </p>
          </div>
          <div className="flex items-center gap-6 text-xs text-slate-500 font-mono">
            <div>
              <span className="text-slate-600">START</span>
              <div className="text-slate-300">{new Date(sessionStart).toLocaleString()}</div>
            </div>
            <div>
              <span className="text-red-600">EXPIRES</span>
              <div className="text-red-400">{new Date(sessionExpiry).toLocaleString()}</div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8 space-y-8">
        {/* ─── Summary Metrics ───────────────────────────────────── */}
        <div className="grid grid-cols-4 gap-4">
          <MetricCard
            label="Total Searches"
            value={totalSearches.toString()}
            sublabel="queries executed"
          />
          <MetricCard
            label="Anxiety Categories"
            value={uniqueCategories.toString()}
            sublabel="distinct fear vectors"
          />
          <MetricCard
            label="Peak Concern"
            value={peakAnxiety?.topic.replace(/_/g, ' ') ?? 'N/A'}
            sublabel={peakAnxiety ? `${peakAnxiety.searchCount} queries` : ''}
            highlight
          />
          <MetricCard
            label="Privilege Status"
            value="PROTECTED"
            sublabel="Kovel Doctrine active"
            isGreen
          />
        </div>

        {/* ─── Anxiety Vector Grid ───────────────────────────────── */}
        <section>
          <h2 className="text-lg font-bold text-slate-300 uppercase tracking-widest mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            Anxiety Vectors
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {sortedVectors.map((vec) => {
              const colors = getUrgencyColor(vec.urgencyScore);
              return (
                <button
                  key={vec.topic}
                  onClick={() => setActiveFilter(activeFilter === vec.topic ? 'all' : vec.topic)}
                  className={`${colors.bg} border ${colors.border} p-5 rounded-xl text-left transition-all hover:scale-[1.02] ${
                    activeFilter === vec.topic ? 'ring-2 ring-white/30' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`text-[10px] font-black uppercase tracking-widest ${colors.text}`}
                    >
                      {vec.topic.replace(/_/g, ' ')}
                    </span>
                    <span className="text-base">{getTrendIcon(vec.trend)}</span>
                  </div>
                  <div className="text-3xl font-black text-white mt-1">
                    {vec.searchCount}
                    <span className="text-sm font-normal text-slate-500 ml-1">queries</span>
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <span
                      className={`${colors.badge} text-white text-[10px] font-bold px-2 py-0.5 rounded-full`}
                    >
                      URGENCY {vec.urgencyScore}/10
                    </span>
                    <span className="text-slate-600 text-xs">Peak: {vec.peakHour}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        {/* ─── Search Transcript ─────────────────────────────────── */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-slate-300 uppercase tracking-widest flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full" />
              Privileged Search Transcript
            </h2>
            {activeFilter !== 'all' && (
              <button
                onClick={() => setActiveFilter('all')}
                className="text-xs text-slate-500 hover:text-white transition-colors font-mono"
              >
                ✕ Clear filter: {activeFilter}
              </button>
            )}
          </div>

          <div className="space-y-3">
            {filteredLogs.map((log, idx) => (
              <div
                key={idx}
                className="bg-slate-900/60 border border-slate-800 rounded-lg hover:border-slate-700 transition-colors cursor-pointer"
                onClick={() => setExpandedLog(expandedLog === idx ? null : idx)}
              >
                <div className="p-4 flex items-start gap-4">
                  <div className="shrink-0 mt-1">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        log.source === 'google_enterprise'
                          ? 'bg-blue-900 text-blue-300'
                          : 'bg-purple-900 text-purple-300'
                      }`}
                    >
                      {log.source === 'google_enterprise' ? 'GOOGLE ZDR' : 'SONAR PRO'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-bold text-blue-400 mb-1">
                      Q: &ldquo;{log.clientQuery}&rdquo;
                    </div>
                    {expandedLog === idx ? (
                      <div className="text-sm text-slate-400 border-l-2 border-slate-700 pl-3 mt-2 whitespace-pre-wrap">
                        {log.aiResponseSnippet}
                      </div>
                    ) : (
                      <div className="text-sm text-slate-500 truncate">
                        A: {log.aiResponseSnippet.slice(0, 120)}…
                      </div>
                    )}
                  </div>
                  <div className="shrink-0 text-right">
                    <div className="text-xs text-slate-600 font-mono">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </div>
                    <div className="text-[10px] text-slate-700 uppercase mt-1">
                      {log.category.replace(/_/g, ' ')}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredLogs.length === 0 && (
            <div className="text-center text-slate-600 py-12 font-mono text-sm">
              No search activity recorded in this session.
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────
function MetricCard({
  label,
  value,
  sublabel,
  highlight = false,
  isGreen = false,
}: {
  label: string;
  value: string;
  sublabel: string;
  highlight?: boolean;
  isGreen?: boolean;
}) {
  return (
    <div
      className={`p-5 rounded-xl border ${
        highlight
          ? 'bg-red-950/50 border-red-800'
          : isGreen
            ? 'bg-green-950/50 border-green-800'
            : 'bg-slate-900/50 border-slate-800'
      }`}
    >
      <div className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-2">
        {label}
      </div>
      <div
        className={`text-2xl font-black ${
          highlight ? 'text-red-400' : isGreen ? 'text-green-400' : 'text-white'
        }`}
      >
        {value}
      </div>
      <div className="text-xs text-slate-600 mt-1">{sublabel}</div>
    </div>
  );
}
