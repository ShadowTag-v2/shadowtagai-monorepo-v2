/**
 * libs/ui/components/Button.tsx
 * Canonical Button component for the UphillSnowball monorepo.
 * Invariant #92: Shared Component Library Mandate.
 *
 * Usage:
 *   import { Button } from 'libs/ui/components/Button';
 *   <Button variant="primary" size="md" onClick={handleClick}>Submit</Button>
 *
 * 5 canonical variants: primary, secondary, ghost, outline, icon.
 * All legacy button variants across 14+ landing pages MUST migrate to this.
 */

import type React from 'react';
import '../styles/buttons.css';

/** Canonical variant set — NO new variants without Invariant #92 review. */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'outline' | 'icon' | 'danger';

/** Size modifiers */
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant. Default: 'primary' */
  variant?: ButtonVariant;
  /** Size modifier. Default: 'md' */
  size?: ButtonSize;
  /** Render as full-width block element */
  block?: boolean;
  /** Leading icon (React node) */
  icon?: React.ReactNode;
  /** Loading state — disables button and shows spinner */
  loading?: boolean;
  /** Accessible label for icon-only buttons */
  'aria-label'?: string;
}

/**
 * Canonical Button component.
 *
 * Design principles (SIMPLICITY_DOCTRINE.md §2):
 * - ONE concern: rendering a clickable element with consistent styling.
 * - Does NOT handle business logic, routing, or state management.
 * - Styling is DECOMPLECTED from behavior via CSS custom properties.
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  block = false,
  icon,
  loading = false,
  children,
  className = '',
  disabled,
  ...rest
}) => {
  const classes = [
    'btn',
    `btn--${variant}`,
    size !== 'md' ? `btn--${size}` : '',
    block ? 'btn--block' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={classes} disabled={disabled || loading} {...rest}>
      {loading ? (
        <span className="btn__spinner" aria-hidden="true">
          ⏳
        </span>
      ) : icon ? (
        <span className="btn__icon" aria-hidden="true">
          {icon}
        </span>
      ) : null}
      {children}
    </button>
  );
};

export default Button;
