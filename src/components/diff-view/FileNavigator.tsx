// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * FileNavigator — Sidebar file tree with cherry-pick checkboxes.
 *
 * Features:
 *   - File list with privilege badges and confidence scores
 *   - Checkbox toggle for cherry-pick (partial accept) mode
 *   - Active file highlighting
 *   - Keyboard navigable (Tab through, Space to toggle)
 */

'use client';

import { ConfidenceBadge } from './ConfidenceBadge';
import styles from './diff-view.module.css';
import { PrivilegeBadge } from './PrivilegeBadge';
import type { FileNavigatorProps } from './types';

function extractFilename(path: string): string {
  return path.split('/').pop() || path;
}

function extractDirectory(path: string): string {
  const parts = path.split('/');
  return parts.length > 1 ? `${parts.slice(0, -1).join('/')}/` : '';
}

export function FileNavigator({
  files,
  selectedFiles,
  onToggleFile,
  activeFile,
  onSelectFile,
}: FileNavigatorProps) {
  return (
    <nav className={styles.fileNavigator} aria-label="Changed files">
      <div className={styles.navHeader}>
        <h3 className={styles.navTitle}>
          Changed Files
          <span className={styles.navCount}>{files.length}</span>
        </h3>
      </div>

      <div className={styles.fileList} role="listbox" aria-label="File list">
        {files.map((file) => {
          const isActive = activeFile === file.path;
          const isSelected = selectedFiles.has(file.path);
          const dir = extractDirectory(file.path);
          const filename = extractFilename(file.path);

          return (
            <div
              key={file.path}
              className={`${styles.fileItem} ${isActive ? styles.fileItemActive : ''}`}
              role="option"
              aria-selected={isActive}
              tabIndex={0}
            >
              <label className={styles.fileCheckbox}>
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggleFile(file.path)}
                  aria-label={`Select ${file.path} for partial accept`}
                />
              </label>

              <button
                type="button"
                className={styles.fileButton}
                onClick={() => onSelectFile(file.path)}
                aria-label={`View diff for ${file.path}`}
              >
                <span className={styles.filePath}>
                  {dir && <span className={styles.fileDir}>{dir}</span>}
                  <span className={styles.fileName}>{filename}</span>
                </span>

                <span className={styles.fileMeta}>
                  <PrivilegeBadge status={file.privilegeStatus} />
                  <ConfidenceBadge confidence={file.aiConfidence} size="sm" />
                  <span className={styles.hunkCount}>
                    {file.hunkCount} hunk{file.hunkCount !== 1 ? 's' : ''}
                  </span>
                </span>
              </button>
            </div>
          );
        })}
      </div>
    </nav>
  );
}
