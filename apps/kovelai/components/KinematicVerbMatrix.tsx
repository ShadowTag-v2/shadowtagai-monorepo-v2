/**
 * @fileoverview Kinematic Verb Matrix — Action Verb Audit UI
 *
 * Real-time dashboard component that visualizes legally significant
 * action verbs from client transcripts, mapped to causes of action.
 *
 * Features:
 * - Verb classification color coding by kinematic type
 * - Cause-of-action roll-up with confidence scores
 * - Interactive verb detail expansion
 * - Strength/weakness indicator per verb
 *
 * @see VERB_AUDITOR_PROMPT — The AI prompt driving verb extraction
 * @see WAR_ROOM_ARCHITECTURE.md — Pipeline architecture
 */

'use client';

import { useMemo, useState } from 'react';

// ─── Types ───────────────────────────────────────────────

interface VerbEntry {
  verb: string;
  context: string;
  kinematic_classification: string;
  cause_of_action: string;
  element_matched: string;
  confidence: number;
  strengthens_or_weakens: 'strengthens' | 'weakens' | 'neutral';
}

interface KinematicVerbMatrixProps {
  verbs: VerbEntry[];
  sessionId: string;
  isLoading?: boolean;
}

// ─── Classification Color Map ────────────────────────────

const CLASSIFICATION_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  CONTACT_FORCE: { bg: '#fef2f2', text: '#dc2626', label: 'Contact / Force' },
  MOTION_VIOLATION: { bg: '#fef9c3', text: '#ca8a04', label: 'Motion Violation' },
  KNOWLEDGE_STATE: { bg: '#eff6ff', text: '#2563eb', label: 'Knowledge State' },
  PROMISE_CONTRACT: { bg: '#f0fdf4', text: '#16a34a', label: 'Promise / Contract' },
  EMPLOYMENT_ACTION: { bg: '#faf5ff', text: '#9333ea', label: 'Employment Action' },
  SPEECH_ACT: { bg: '#fff7ed', text: '#ea580c', label: 'Speech Act' },
  EVIDENCE_ACTION: { bg: '#f0f9ff', text: '#0284c7', label: 'Evidence Action' },
  DOCUMENT_ACTION: { bg: '#fdf4ff', text: '#c026d3', label: 'Document Action' },
};

const STRENGTH_ICONS: Record<string, string> = {
  strengthens: '🟢',
  weakens: '🔴',
  neutral: '⚪',
};

// ─── Component ───────────────────────────────────────────

export function KinematicVerbMatrix({
  verbs,
  sessionId,
  isLoading = false,
}: KinematicVerbMatrixProps) {
  const [expandedVerb, setExpandedVerb] = useState<number | null>(null);
  const [filterAction, setFilterAction] = useState<string | null>(null);

  // Roll-up: causes of action with aggregated confidence
  const causesOfAction = useMemo(() => {
    const map = new Map<string, { count: number; totalConf: number; verbs: VerbEntry[] }>();

    for (const verb of verbs) {
      const existing = map.get(verb.cause_of_action);
      if (existing) {
        existing.count++;
        existing.totalConf += verb.confidence;
        existing.verbs.push(verb);
      } else {
        map.set(verb.cause_of_action, {
          count: 1,
          totalConf: verb.confidence,
          verbs: [verb],
        });
      }
    }

    return Array.from(map.entries())
      .map(([action, data]) => ({
        action,
        count: data.count,
        avgConfidence: Math.round((data.totalConf / data.count) * 100),
        verbs: data.verbs,
      }))
      .sort((a, b) => b.avgConfidence - a.avgConfidence);
  }, [verbs]);

  const filteredVerbs = filterAction
    ? verbs.filter((v) => v.cause_of_action === filterAction)
    : verbs;

  if (isLoading) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h2 style={styles.title}>⚡ Kinematic Verb Matrix</h2>
          <span style={styles.badge}>Analyzing...</span>
        </div>
        <div style={styles.loadingBar}>
          <div style={styles.loadingBarFill} />
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.title}>⚡ Kinematic Verb Matrix</h2>
        <span style={styles.badge}>
          {verbs.length} verbs · {causesOfAction.length} causes of action
        </span>
      </div>

      {/* Causes of Action Roll-Up */}
      <div style={styles.rollUpGrid}>
        {causesOfAction.map((coa) => (
          <button
            key={coa.action}
            onClick={() => setFilterAction(filterAction === coa.action ? null : coa.action)}
            style={{
              ...styles.rollUpCard,
              ...(filterAction === coa.action ? styles.rollUpCardActive : {}),
            }}
          >
            <div style={styles.rollUpAction}>{coa.action}</div>
            <div style={styles.rollUpMeta}>
              <span>{coa.count} verbs</span>
              <span style={styles.confidenceBar}>
                <span
                  style={{
                    ...styles.confidenceFill,
                    width: `${coa.avgConfidence}%`,
                    backgroundColor:
                      coa.avgConfidence > 80
                        ? '#16a34a'
                        : coa.avgConfidence > 50
                          ? '#ca8a04'
                          : '#dc2626',
                  }}
                />
              </span>
              <span style={styles.confidenceLabel}>{coa.avgConfidence}%</span>
            </div>
          </button>
        ))}
      </div>

      {/* Verb Table */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Verb</th>
              <th style={styles.th}>Classification</th>
              <th style={styles.th}>Cause of Action</th>
              <th style={styles.th}>Confidence</th>
              <th style={styles.th}>Impact</th>
            </tr>
          </thead>
          <tbody>
            {filteredVerbs.map((verb, idx) => {
              const classInfo =
                CLASSIFICATION_COLORS[verb.kinematic_classification] ||
                CLASSIFICATION_COLORS.CONTACT_FORCE;
              const isExpanded = expandedVerb === idx;

              return (
                <>
                  <tr
                    key={`verb-${idx}`}
                    onClick={() => setExpandedVerb(isExpanded ? null : idx)}
                    style={{
                      ...styles.tr,
                      cursor: 'pointer',
                    }}
                  >
                    <td style={styles.td}>
                      <code style={styles.verbCode}>{verb.verb}</code>
                    </td>
                    <td style={styles.td}>
                      <span
                        style={{
                          ...styles.classificationBadge,
                          backgroundColor: classInfo.bg,
                          color: classInfo.text,
                        }}
                      >
                        {classInfo.label}
                      </span>
                    </td>
                    <td style={styles.td}>{verb.cause_of_action}</td>
                    <td style={styles.td}>
                      <span
                        style={{
                          ...styles.confidenceChip,
                          backgroundColor:
                            verb.confidence > 0.8
                              ? '#dcfce7'
                              : verb.confidence > 0.5
                                ? '#fef9c3'
                                : '#fee2e2',
                        }}
                      >
                        {Math.round(verb.confidence * 100)}%
                      </span>
                    </td>
                    <td style={styles.td}>
                      {STRENGTH_ICONS[verb.strengthens_or_weakens]} {verb.strengthens_or_weakens}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr key={`detail-${idx}`}>
                      <td colSpan={5} style={styles.expandedRow}>
                        <div style={styles.expandedContent}>
                          <div>
                            <strong>Context:</strong> <em>&ldquo;{verb.context}&rdquo;</em>
                          </div>
                          <div>
                            <strong>Element Matched:</strong> {verb.element_matched}
                          </div>
                          <div style={styles.expandedMeta}>
                            Session: {sessionId} · Classification: {verb.kinematic_classification}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div style={styles.legend}>
        {Object.entries(CLASSIFICATION_COLORS).map(([key, val]) => (
          <span key={key} style={styles.legendItem}>
            <span
              style={{
                ...styles.legendDot,
                backgroundColor: val.text,
              }}
            />
            {val.label}
          </span>
        ))}
      </div>
    </div>
  );
}

// ─── Styles ──────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: '#0a0a0a',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '16px',
    padding: '24px',
    fontFamily: '"Inter", -apple-system, sans-serif',
    color: '#e5e5e5',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '18px',
    fontWeight: 700,
    margin: 0,
    color: '#ffffff',
  },
  badge: {
    fontSize: '12px',
    background: 'rgba(255,255,255,0.06)',
    padding: '4px 12px',
    borderRadius: '100px',
    color: '#a3a3a3',
  },
  loadingBar: {
    height: '4px',
    borderRadius: '2px',
    background: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  loadingBarFill: {
    height: '100%',
    width: '40%',
    background: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
    borderRadius: '2px',
    animation: 'shimmer 1.5s infinite ease-in-out',
  },
  rollUpGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '8px',
    marginBottom: '20px',
  },
  rollUpCard: {
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: '10px',
    padding: '12px',
    cursor: 'pointer',
    textAlign: 'left' as const,
    transition: 'all 0.2s ease',
    color: '#e5e5e5',
    fontFamily: 'inherit',
    fontSize: 'inherit',
  },
  rollUpCardActive: {
    border: '1px solid #3b82f6',
    background: 'rgba(59,130,246,0.08)',
  },
  rollUpAction: {
    fontSize: '13px',
    fontWeight: 600,
    marginBottom: '6px',
  },
  rollUpMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '11px',
    color: '#a3a3a3',
  },
  confidenceBar: {
    flex: 1,
    height: '4px',
    borderRadius: '2px',
    background: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
    display: 'inline-block',
  },
  confidenceFill: {
    height: '100%',
    borderRadius: '2px',
    transition: 'width 0.5s ease',
    display: 'block',
  },
  confidenceLabel: {
    fontWeight: 600,
    fontSize: '11px',
  },
  tableWrapper: {
    overflowX: 'auto' as const,
    borderRadius: '10px',
    border: '1px solid rgba(255,255,255,0.06)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
    fontSize: '13px',
  },
  th: {
    padding: '10px 14px',
    textAlign: 'left' as const,
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    color: '#a3a3a3',
    fontWeight: 500,
    fontSize: '11px',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  tr: {
    borderBottom: '1px solid rgba(255,255,255,0.04)',
    transition: 'background 0.15s ease',
  },
  td: {
    padding: '10px 14px',
  },
  verbCode: {
    fontFamily: '"JetBrains Mono", "Fira Code", monospace',
    fontSize: '13px',
    fontWeight: 600,
    color: '#f0abfc',
  },
  classificationBadge: {
    padding: '2px 8px',
    borderRadius: '6px',
    fontSize: '11px',
    fontWeight: 600,
  },
  confidenceChip: {
    padding: '2px 8px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: 600,
    color: '#171717',
  },
  expandedRow: {
    padding: 0,
    background: 'rgba(255,255,255,0.02)',
  },
  expandedContent: {
    padding: '12px 14px',
    fontSize: '12px',
    lineHeight: 1.6,
    borderTop: '1px dashed rgba(255,255,255,0.08)',
  },
  expandedMeta: {
    marginTop: '8px',
    color: '#737373',
    fontSize: '11px',
  },
  legend: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '12px',
    marginTop: '16px',
    paddingTop: '16px',
    borderTop: '1px solid rgba(255,255,255,0.06)',
  },
  legendItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    fontSize: '11px',
    color: '#a3a3a3',
  },
  legendDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    display: 'inline-block',
  },
};

export default KinematicVerbMatrix;
