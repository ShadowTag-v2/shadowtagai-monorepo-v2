// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * DecisionBar — Attorney action bar for accept/reject/cherry-pick decisions.
 *
 * Fixed to bottom of viewport during review. Shows:
 *   - Selection count (for partial accept mode)
 *   - Accept All / Reject All buttons
 *   - Accept Selected button (only in partial mode with ≥1 file selected)
 *
 * Interaction: 150ms scale transform + ripple on button press.
 */

"use client";

import styles from "./diff-view.module.css";
import type { DecisionBarProps } from "./types";

export function DecisionBar({
  selectedCount,
  totalCount,
  isPartialMode,
  onAccept,
  onReject,
  onPartialAccept,
  isSubmitting,
}: DecisionBarProps) {
  return (
    <div className={styles.decisionBar} role="toolbar" aria-label="Review decision actions">
      <div className={styles.decisionInfo}>
        {isPartialMode ? (
          <span className={styles.decisionCount}>
            {selectedCount} of {totalCount} files selected
          </span>
        ) : (
          <span className={styles.decisionCount}>
            {totalCount} file{totalCount !== 1 ? "s" : ""} ready for review
          </span>
        )}
      </div>

      <div className={styles.decisionActions}>
        <button
          type="button"
          className={`${styles.decisionBtn} ${styles.btnReject}`}
          onClick={onReject}
          disabled={isSubmitting}
          aria-label="Reject all changes"
        >
          {isSubmitting ? <span className={styles.spinner} aria-hidden="true" /> : "✕"} Reject All
        </button>

        {isPartialMode && selectedCount > 0 && (
          <button
            type="button"
            className={`${styles.decisionBtn} ${styles.btnPartial}`}
            onClick={onPartialAccept}
            disabled={isSubmitting}
            aria-label={`Accept ${selectedCount} selected files`}
          >
            {isSubmitting ? <span className={styles.spinner} aria-hidden="true" /> : "◐"} Accept
            Selected ({selectedCount})
          </button>
        )}

        <button
          type="button"
          className={`${styles.decisionBtn} ${styles.btnAccept}`}
          onClick={onAccept}
          disabled={isSubmitting}
          aria-label="Accept all changes"
        >
          {isSubmitting ? <span className={styles.spinner} aria-hidden="true" /> : "✓"} Accept All
        </button>
      </div>
    </div>
  );
}
