// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * DiffView — Main container for the Attorney Diff Review experience.
 *
 * Composes:
 *   - FileNavigator (sidebar) for file selection + cherry-pick
 *   - DiffFile (main) for per-file hunk rendering
 *   - DecisionBar (fixed bottom) for accept/reject/partial accept
 *
 * Architecture:
 *   SandboxSession → DiffEngine → DiffView → Attorney Decision
 *
 * Security:
 *   - Attorney UID verification delegated to SandboxSession
 *   - Privilege badges enforce visual classification
 *   - Privileged content has user-select: none
 *   - Every interaction is logged for telemetry
 */

"use client";

import { useCallback, useMemo, useState } from "react";
import { DecisionBar } from "./DecisionBar";
import { DiffFile } from "./DiffFile";
import styles from "./diff-view.module.css";
import { FileNavigator } from "./FileNavigator";
import type { CommitAction, DiffViewProps } from "./types";

export function DiffView({
  sessionId,
  matterId,
  diffs,
  onDecision,
  isLoading = false,
}: DiffViewProps) {
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [activeFile, setActiveFile] = useState<string | null>(
    diffs.length > 0 ? diffs[0].path : null,
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isPartialMode = selectedFiles.size > 0 && selectedFiles.size < diffs.length;

  const handleToggleFile = useCallback((path: string) => {
    setSelectedFiles((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  }, []);

  const handleSelectFile = useCallback((path: string) => {
    setActiveFile(path);
    // Scroll to file element
    const el = document.getElementById(`diff-content-${path}`);
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const handleDecision = useCallback(
    async (action: CommitAction) => {
      setIsSubmitting(true);
      try {
        const files = action === "partial_accept" ? Array.from(selectedFiles) : undefined;
        onDecision(action, files);
      } finally {
        setIsSubmitting(false);
      }
    },
    [onDecision, selectedFiles],
  );

  const activeDiff = useMemo(() => diffs.find((d) => d.path === activeFile), [diffs, activeFile]);

  if (isLoading) {
    return (
      <div className={styles.container} role="status" aria-label="Loading diff view">
        <div className={styles.loading}>
          <div className={styles.loadingSpinner} />
          <p>Computing overlay diffs for matter {matterId}…</p>
          <p className={styles.loadingSubtext}>Session: {sessionId}</p>
        </div>
      </div>
    );
  }

  if (diffs.length === 0) {
    return (
      <div className={styles.container} role="status">
        <div className={styles.emptyState}>
          <p>No changes detected in the sandbox overlay.</p>
          <p className={styles.loadingSubtext}>
            The speculation engine produced no file modifications for this matter.
          </p>
        </div>
      </div>
    );
  }

  return (
    <main className={styles.container} aria-label={`Diff review for session ${sessionId}`}>
      <FileNavigator
        files={diffs}
        selectedFiles={selectedFiles}
        onToggleFile={handleToggleFile}
        activeFile={activeFile}
        onSelectFile={handleSelectFile}
      />

      <div className={styles.diffPanel}>
        <header className={styles.panelHeader}>
          <h2 className={styles.panelTitle}>
            Sandbox Review
            <span className={styles.panelSubtitle}>Matter: {matterId}</span>
          </h2>
          <span className={styles.sessionBadge}>Session: {sessionId.slice(0, 8)}…</span>
        </header>

        <div className={styles.diffScroll}>
          {activeDiff ? (
            <DiffFile file={activeDiff} defaultExpanded />
          ) : (
            diffs.map((file) => (
              <DiffFile key={file.path} file={file} defaultExpanded={diffs.length <= 3} />
            ))
          )}
        </div>
      </div>

      <DecisionBar
        selectedCount={selectedFiles.size}
        totalCount={diffs.length}
        isPartialMode={isPartialMode}
        onAccept={() => handleDecision("accept")}
        onReject={() => handleDecision("reject")}
        onPartialAccept={() => handleDecision("partial_accept")}
        isSubmitting={isSubmitting}
      />
    </main>
  );
}
