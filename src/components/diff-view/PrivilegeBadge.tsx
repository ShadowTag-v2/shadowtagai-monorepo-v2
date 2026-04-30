// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

/**
 * PrivilegeBadge — Visual indicator for document privilege classification.
 *
 * Classifications:
 *   🔒 privileged     — Attorney-client privilege (no copy/paste, no select)
 *   📋 work_product   — Attorney work product (protected but viewable)
 *   📄 public         — No privilege restrictions
 *
 * Security: Privileged content gets `user-select: none` to prevent clipboard
 * exfiltration. This is a UI-level guardrail, not a security boundary.
 */

'use client';

import styles from './diff-view.module.css';
import type { PrivilegeBadgeProps } from './types';

const PRIVILEGE_CONFIG: Record<string, { icon: string; label: string; className: string }> = {
  privileged: {
    icon: '🔒',
    label: 'Attorney-Client Privilege',
    className: styles.privilegeProtected,
  },
  work_product: {
    icon: '📋',
    label: 'Work Product',
    className: styles.privilegeWorkProduct,
  },
  public: {
    icon: '📄',
    label: 'Public Document',
    className: styles.privilegePublic,
  },
};

export function PrivilegeBadge({ status }: PrivilegeBadgeProps) {
  const config = PRIVILEGE_CONFIG[status] || PRIVILEGE_CONFIG.public;

  return (
    <span
      className={`${styles.privilegeBadge} ${config.className}`}
      role="status"
      aria-label={config.label}
      title={config.label}
    >
      <span aria-hidden="true">{config.icon}</span>
      <span>{config.label}</span>
    </span>
  );
}
