// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * ConfidenceBadge — AI confidence indicator for speculation hunks.
 *
 * Visual scale:
 *   ≥0.8  → green  (high confidence, safe to accept)
 *   ≥0.5  → amber  (moderate confidence, review recommended)
 *   <0.5  → red    (low confidence, review critical) + pulse animation
 */

'use client';

import styles from './diff-view.module.css';
import type { ConfidenceBadgeProps } from './types';

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return 'High';
  if (confidence >= 0.5) return 'Moderate';
  return 'Low';
}

function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.8) return styles.confidenceHigh;
  if (confidence >= 0.5) return styles.confidenceMedium;
  return styles.confidenceLow;
}

export function ConfidenceBadge({ confidence, size = 'md' }: ConfidenceBadgeProps) {
  const pct = Math.round(confidence * 100);
  const label = getConfidenceLabel(confidence);
  const colorClass = getConfidenceClass(confidence);
  const sizeClass = size === 'sm' ? styles.confidenceSm : '';
  const pulseClass = confidence < 0.5 ? styles.confidencePulse : '';

  return (
    <span
      className={`${styles.confidenceBadge} ${colorClass} ${sizeClass} ${pulseClass}`.trim()}
      role="status"
      aria-label={`AI confidence: ${pct}% (${label})`}
      title={`AI Confidence: ${pct}% — ${label}`}
    >
      <span className={styles.confidenceDot} aria-hidden="true" />
      <span>{pct}%</span>
    </span>
  );
}
