// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * DiffFile — Renders the complete diff for a single file.
 *
 * Displays:
 *   - File header with path, privilege badge, and confidence score
 *   - Expandable/collapsible hunk list
 *   - Language label for syntax context
 *   - All hunks from the file diff
 */

"use client";

import { useState } from "react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { DiffHunk } from "./DiffHunk";
import styles from "./diff-view.module.css";
import { PrivilegeBadge } from "./PrivilegeBadge";
import type { DiffFile as DiffFileType } from "./types";

interface DiffFileProps {
  file: DiffFileType;
  /** Default expanded state */
  defaultExpanded?: boolean;
}

function extractFilename(path: string): string {
  return path.split("/").pop() || path;
}

export function DiffFile({ file, defaultExpanded = true }: DiffFileProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const isPrivileged = file.privilegeStatus === "privileged";
  const filename = extractFilename(file.path);

  const addCount = file.hunks.reduce(
    (sum, h) => sum + h.changes.filter((c) => c.type === "add").length,
    0,
  );
  const deleteCount = file.hunks.reduce(
    (sum, h) => sum + h.changes.filter((c) => c.type === "delete").length,
    0,
  );

  return (
    <article className={styles.diffFile} aria-label={`Diff for ${file.path}`}>
      <button
        type="button"
        className={styles.fileHeader}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-controls={`diff-content-${file.path}`}
      >
        <span className={styles.expandIcon} aria-hidden="true">
          {isExpanded ? "▼" : "▶"}
        </span>

        <span className={styles.fileHeaderPath}>
          <span className={styles.fileHeaderName}>{filename}</span>
          <span className={styles.fileHeaderDir}>{file.path}</span>
        </span>

        <span className={styles.fileHeaderMeta}>
          <span className={styles.langBadge}>{file.language}</span>
          <PrivilegeBadge status={file.privilegeStatus} />
          <ConfidenceBadge confidence={file.aiConfidence} size="sm" />
          <span className={styles.statAdd}>+{addCount}</span>
          <span className={styles.statDel}>-{deleteCount}</span>
        </span>
      </button>

      {isExpanded && (
        <section
          id={`diff-content-${file.path}`}
          className={styles.diffContent}
          aria-label={`Changes in ${filename}`}
        >
          {file.hunks.length === 0 ? (
            <div className={styles.emptyDiff}>No changes detected</div>
          ) : (
            file.hunks.map((hunk, i) => (
              <DiffHunk
                key={`${hunk.oldStart}-${hunk.newStart}`}
                hunk={hunk}
                isPrivileged={isPrivileged}
                index={i}
              />
            ))
          )}
        </section>
      )}
    </article>
  );
}
