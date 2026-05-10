// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Shared TypeScript interfaces for the Attorney Diff View component.
 *
 * These types map 1:1 to the Python FileDiff / DiffHunk structures
 * in apps/counselconduit/api/sandbox/firestore_bridge.py
 */

export interface DiffChange {
  type: 'add' | 'delete' | 'context';
  content: string;
  lineNumber: number;
}

export interface DiffHunk {
  oldStart: number;
  oldLines: number;
  newStart: number;
  newLines: number;
  changes: DiffChange[];
}

export interface DiffFile {
  path: string;
  language: string;
  hunks: DiffHunk[];
  privilegeStatus: 'privileged' | 'work_product' | 'public';
  aiConfidence: number; // 0-1 score from speculation engine
  originalHash: string;
  overlayHash: string;
  hunkCount: number;
}

export type CommitAction = 'accept' | 'reject' | 'partial_accept';

/**
 * API response from GET /api/sandbox/{sessionId}/diffs
 * Mirrors Python DiffResponse (sandbox_api.py)
 */
export interface DiffResponse {
  session_id: string;
  matter_id: string;
  diffs: DiffFile[];
  file_count: number;
}

/**
 * API response from POST /api/sandbox/{sessionId}/commit
 * Mirrors Python CommitResponse (sandbox_api.py)
 */
export interface CommitResponse {
  success: boolean;
  committed_files: string[];
  rejected_files: string[];
  audit_id: string;
  error: string;
  duration_ms: number;
}

export interface DiffViewProps {
  /** Session ID from SandboxSession */
  sessionId: string;
  /** Matter ID for privilege tracking */
  matterId: string;
  /** Map of file paths to their diff hunks */
  diffs: DiffFile[];
  /** Callback when attorney makes a decision */
  onDecision: (action: CommitAction, selectedFiles?: string[]) => void;
  /** Loading state while overlay computes */
  isLoading?: boolean;
}

export interface DecisionBarProps {
  selectedCount: number;
  totalCount: number;
  isPartialMode: boolean;
  onAccept: () => void;
  onReject: () => void;
  onPartialAccept: () => void;
  isSubmitting: boolean;
}

export interface ConfidenceBadgeProps {
  confidence: number;
  size?: 'sm' | 'md';
}

export interface PrivilegeBadgeProps {
  status: DiffFile['privilegeStatus'];
}

export interface FileNavigatorProps {
  files: DiffFile[];
  selectedFiles: Set<string>;
  onToggleFile: (path: string) => void;
  activeFile: string | null;
  onSelectFile: (path: string) => void;
}
