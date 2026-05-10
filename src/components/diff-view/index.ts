// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * Attorney Diff View — Public API exports.
 *
 * Re-exports all components and types needed to render
 * the sandbox diff review experience.
 */

export { ConfidenceBadge } from './ConfidenceBadge';
export { DecisionBar } from './DecisionBar';
export { DiffFile } from './DiffFile';
export { DiffHunk } from './DiffHunk';
export { DiffView } from './DiffView';
export { FileNavigator } from './FileNavigator';
export { PrivilegeBadge } from './PrivilegeBadge';

export type {
  CommitAction,
  ConfidenceBadgeProps,
  DecisionBarProps,
  DiffChange,
  DiffFile as DiffFileType,
  DiffHunk as DiffHunkType,
  DiffViewProps,
  FileNavigatorProps,
  PrivilegeBadgeProps,
} from './types';
