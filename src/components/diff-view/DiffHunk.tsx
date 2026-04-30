// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * DiffHunk — Renders a single contiguous block of changes within a file diff.
 *
 * Each hunk displays:
 *   - Hunk header with line range (@@ -old +new @@)
 *   - Context lines (dimmed)
 *   - Added lines (green background)
 *   - Deleted lines (red background)
 *
 * Privileged content gets `user-select: none` to prevent clipboard exfiltration.
 */

'use client';

import styles from './diff-view.module.css';
import type { DiffHunk as DiffHunkType } from './types';

interface DiffHunkProps {
  hunk: DiffHunkType;
  /** If true, disables text selection (privileged content) */
  isPrivileged: boolean;
  /** Index within the file (for unique IDs) */
  index: number;
}

export function DiffHunk({ hunk, isPrivileged, index }: DiffHunkProps) {
  const hunkHeader = `@@ -${hunk.oldStart},${hunk.oldLines} +${hunk.newStart},${hunk.newLines} @@`;

  return (
    <section
      className={styles.hunk}
      aria-label={`Change hunk ${index + 1}: lines ${hunk.oldStart}-${hunk.oldStart + hunk.oldLines}`}
    >
      <div className={styles.hunkHeader} aria-hidden="true">
        <code>{hunkHeader}</code>
      </div>

      <table
        className={`${styles.hunkTable} ${isPrivileged ? styles.noSelect : ''}`}
        role="presentation"
      >
        <tbody>
          {hunk.changes.map((change, i) => {
            const lineClass =
              change.type === 'add'
                ? styles.lineAdd
                : change.type === 'delete'
                  ? styles.lineDelete
                  : styles.lineContext;

            const prefix = change.type === 'add' ? '+' : change.type === 'delete' ? '-' : ' ';

            return (
              <tr
                key={`${hunk.oldStart}-${i}`}
                className={lineClass}
                aria-label={`${change.type === 'add' ? 'Added' : change.type === 'delete' ? 'Deleted' : 'Context'} line ${change.lineNumber}`}
              >
                <td className={styles.lineNumber} aria-hidden="true">
                  {change.lineNumber}
                </td>
                <td className={styles.linePrefix} aria-hidden="true">
                  {prefix}
                </td>
                <td className={styles.lineContent}>
                  <code>{change.content || '\u00A0'}</code>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
