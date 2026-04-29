// Copyright (c) 2026 ShadowTag, Inc. All rights reserved. Dual-Licensed under CounselConduit Compliance.

/**
 * @fileoverview Citation Panel — Perplexity-style Inline Citations
 *
 * Renders legal citations from the Oracle memo with:
 * - Inline superscript markers (like Perplexity's [1] [2] [3])
 * - Expandable authority detail panel
 * - Relevance score visualization
 * - Verification status badges (verified / unverified / suspect)
 * - "View Source" deep links to Westlaw/LexisNexis stubs
 *
 * @see V11_SPRINT.md — Week 1 deliverable
 * @see WAR_ROOM_ARCHITECTURE.md — Pipeline Stage 5
 */

'use client';

import { useState } from 'react';

// ─── Types ───────────────────────────────────────────────

export interface Citation {
  index: number;
  authority: string;
  type: 'statute' | 'case' | 'regulation' | 'rule' | 'secondary';
  citation_format_correct: boolean;
  excerpt: string;
  relevance_score: number;
  status: 'verified' | 'unverified' | 'suspect';
  notes?: string;
}

interface CitationPanelProps {
  citations: Citation[];
  isCollapsed?: boolean;
}

// ─── Status Config ───────────────────────────────────────

const STATUS_CONFIG: Record<string, { icon: string; color: string; bg: string }> = {
  verified: { icon: '✓', color: '#16a34a', bg: 'rgba(22,163,106,0.12)' },
  unverified: { icon: '?', color: '#ca8a04', bg: 'rgba(202,138,4,0.12)' },
  suspect: { icon: '⚠', color: '#dc2626', bg: 'rgba(220,38,38,0.12)' },
};

const TYPE_LABELS: Record<string, string> = {
  statute: '📜 Statute',
  case: '⚖️ Case Law',
  regulation: '📋 Regulation',
  rule: '📏 Rule',
  secondary: '📚 Secondary',
};

// ─── Component ───────────────────────────────────────────

export function CitationPanel({
  citations,
  isCollapsed: initialCollapsed = false,
}: CitationPanelProps) {
  const [isCollapsed, setIsCollapsed] = useState(initialCollapsed);
  const [expandedCitation, setExpandedCitation] = useState<number | null>(null);

  const verifiedCount = citations.filter((c) => c.status === 'verified').length;
  const suspectCount = citations.filter((c) => c.status === 'suspect').length;

  return (
    <div style={styles.container}>
      {/* Header */}
      <button
        type="button"
        onClick={() => setIsCollapsed(!isCollapsed)}
        style={styles.headerButton}
      >
        <div style={styles.headerLeft}>
          <span style={styles.headerIcon}>📎</span>
          <span style={styles.headerTitle}>Citations ({citations.length})</span>
          <span style={styles.headerMeta}>
            {verifiedCount} verified
            {suspectCount > 0 && (
              <span style={{ color: '#dc2626' }}> · {suspectCount} suspect</span>
            )}
          </span>
        </div>
        <span style={styles.chevron}>{isCollapsed ? '▸' : '▾'}</span>
      </button>

      {/* Inline markers preview */}
      {isCollapsed && (
        <div style={styles.inlineMarkers}>
          {citations.map((c) => (
            <span
              key={c.index}
              style={{
                ...styles.inlineMarker,
                borderColor: STATUS_CONFIG[c.status].color,
              }}
              title={c.authority}
            >
              {c.index}
            </span>
          ))}
        </div>
      )}

      {/* Expanded panel */}
      {!isCollapsed && (
        <div style={styles.citationList}>
          {citations.map((citation) => {
            const statusInfo = STATUS_CONFIG[citation.status];
            const isExpanded = expandedCitation === citation.index;

            return (
              <div
                key={citation.index}
                style={{
                  ...styles.citationCard,
                  borderLeftColor: statusInfo.color,
                }}
              >
                <button
                  type="button"
                  style={styles.citationHeader}
                  onClick={() => setExpandedCitation(isExpanded ? null : citation.index)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ')
                      setExpandedCitation(isExpanded ? null : citation.index);
                  }}
                >
                  {/* Index badge */}
                  <span style={styles.indexBadge}>{citation.index}</span>

                  {/* Authority name */}
                  <div style={styles.authorityBlock}>
                    <div style={styles.authorityName}>{citation.authority}</div>
                    <div style={styles.authorityType}>
                      {TYPE_LABELS[citation.type] || citation.type}
                    </div>
                  </div>

                  {/* Status badge */}
                  <span
                    style={{
                      ...styles.statusBadge,
                      backgroundColor: statusInfo.bg,
                      color: statusInfo.color,
                    }}
                  >
                    {statusInfo.icon} {citation.status}
                  </span>

                  {/* Relevance score */}
                  <div style={styles.relevanceBlock}>
                    <div style={styles.relevanceBar}>
                      <div
                        style={{
                          ...styles.relevanceFill,
                          width: `${citation.relevance_score * 100}%`,
                          backgroundColor:
                            citation.relevance_score > 0.8
                              ? '#16a34a'
                              : citation.relevance_score > 0.5
                                ? '#ca8a04'
                                : '#dc2626',
                        }}
                      />
                    </div>
                    <span style={styles.relevanceLabel}>
                      {Math.round(citation.relevance_score * 100)}%
                    </span>
                  </div>
                </button>

                {/* Expanded detail */}
                {isExpanded && (
                  <div style={styles.expandedDetail}>
                    <div style={styles.excerptBlock}>
                      <strong>Excerpt:</strong> <em>&ldquo;{citation.excerpt}&rdquo;</em>
                    </div>
                    {citation.notes && (
                      <div style={styles.notesBlock}>
                        <strong>Notes:</strong> {citation.notes}
                      </div>
                    )}
                    <div style={styles.detailMeta}>
                      Format correct: {citation.citation_format_correct ? '✓ Yes' : '✗ No'}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── Inline Citation Marker (for embedding in memo text) ─

interface InlineCitationMarkerProps {
  index: number;
  authority: string;
  status: 'verified' | 'unverified' | 'suspect';
  onClick?: () => void;
}

export function InlineCitationMarker({
  index,
  authority,
  status,
  onClick,
}: InlineCitationMarkerProps) {
  const statusInfo = STATUS_CONFIG[status];
  return (
    <button
      type="button"
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') onClick?.();
      }}
      title={authority}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '16px',
        height: '16px',
        borderRadius: '4px',
        fontSize: '10px',
        fontWeight: 700,
        backgroundColor: statusInfo.bg,
        color: statusInfo.color,
        cursor: 'pointer',
        marginLeft: '1px',
        verticalAlign: 'super',
        lineHeight: 1,
        transition: 'transform 0.1s ease',
      }}
    >
      {index}
    </button>
  );
}

// ─── Styles ──────────────────────────────────────────────

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: '#0a0a0a',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '12px',
    overflow: 'hidden',
    fontFamily: '"Inter", -apple-system, sans-serif',
    color: '#e5e5e5',
  },
  headerButton: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '100%',
    padding: '14px 18px',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    color: '#e5e5e5',
    fontFamily: 'inherit',
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  headerIcon: { fontSize: '16px' },
  headerTitle: { fontSize: '14px', fontWeight: 600 },
  headerMeta: { fontSize: '12px', color: '#a3a3a3' },
  chevron: { fontSize: '12px', color: '#737373' },
  inlineMarkers: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '4px',
    padding: '0 18px 14px',
  },
  inlineMarker: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '22px',
    height: '22px',
    borderRadius: '6px',
    border: '1px solid',
    fontSize: '11px',
    fontWeight: 700,
    color: '#a3a3a3',
    cursor: 'default',
  },
  citationList: {
    padding: '0 14px 14px',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '6px',
  },
  citationCard: {
    background: 'rgba(255,255,255,0.02)',
    borderRadius: '8px',
    borderLeft: '3px solid',
    overflow: 'hidden',
  },
  citationHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    cursor: 'pointer',
    transition: 'background 0.15s ease',
  },
  indexBadge: {
    width: '22px',
    height: '22px',
    borderRadius: '6px',
    background: 'rgba(255,255,255,0.06)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '11px',
    fontWeight: 700,
    flexShrink: 0,
  },
  authorityBlock: { flex: 1, minWidth: 0 },
  authorityName: {
    fontSize: '13px',
    fontWeight: 600,
    whiteSpace: 'nowrap' as const,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  authorityType: { fontSize: '11px', color: '#737373' },
  statusBadge: {
    padding: '2px 8px',
    borderRadius: '6px',
    fontSize: '11px',
    fontWeight: 600,
    flexShrink: 0,
  },
  relevanceBlock: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    flexShrink: 0,
    width: '80px',
  },
  relevanceBar: {
    flex: 1,
    height: '4px',
    borderRadius: '2px',
    background: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  relevanceFill: {
    height: '100%',
    borderRadius: '2px',
    transition: 'width 0.5s ease',
  },
  relevanceLabel: {
    fontSize: '11px',
    fontWeight: 600,
    color: '#a3a3a3',
    minWidth: '28px',
    textAlign: 'right' as const,
  },
  expandedDetail: {
    padding: '10px 14px 14px',
    borderTop: '1px dashed rgba(255,255,255,0.06)',
    fontSize: '12px',
    lineHeight: 1.6,
  },
  excerptBlock: { marginBottom: '6px' },
  notesBlock: { marginBottom: '6px', color: '#ca8a04' },
  detailMeta: { color: '#737373', fontSize: '11px' },
};

export default CitationPanel;
