/**
 * HeadFade Design System — Forensic Cyan Token Registry
 *
 * Single source of truth for all color tokens used across the HeadFade PWA.
 * Import from here instead of hardcoding hex values in components.
 *
 * Palette rationale: "Forensic Cyan" positions HeadFade as a data-verified,
 * human-deception forensics platform. The cyan spectrum conveys analytical
 * precision, trust, and technological authority.
 */

// ─── Primary Brand Colors ────────────────────────────────────────────────────

/** Primary accent — buttons, active states, badges */
export const CYAN_PRIMARY = '#0891B2';

/** Secondary accent — slightly lighter, used for gradients alongside primary */
export const CYAN_SECONDARY = '#06B6D4';

/** Light accent — text highlights, progress bars, active state backgrounds */
export const CYAN_LIGHT = '#67E8F9';

/** Tint — very light background for selected/active UI elements */
export const CYAN_TINT = '#E0F7FA';

/** Deep — dark rich cyan for deep UI sections, dark mode panels */
export const CYAN_DEEP = '#164E63';

// ─── Background & Surface Colors ─────────────────────────────────────────────

/** Dark navy base — primary dark background */
export const BG_DARK = '#0A1628';

/** Dark navy secondary — slightly lighter for layered surfaces */
export const BG_DARK_ALT = '#0C1E35';

/** Dark navy tertiary — used in multi-stop gradients */
export const BG_DARK_TERTIARY = '#0A1A2E';

/** Deep teal text on light backgrounds */
export const TEXT_DARK = '#0A2540';

// ─── Semantic RGBA Tokens ─────────────────────────────────────────────────────

/** Primary at 18% opacity — vote button inactive backgrounds */
export const CYAN_PRIMARY_18 = 'rgba(8,145,178,0.18)';

/** Primary at 12% opacity — tile vote button inactive backgrounds */
export const CYAN_PRIMARY_12 = 'rgba(8,145,178,0.12)';

/** Primary at 20% opacity — navigation dots inactive */
export const CYAN_PRIMARY_20 = 'rgba(8,145,178,0.2)';

/** Primary at 40% opacity — borders */
export const CYAN_PRIMARY_40 = 'rgba(8,145,178,0.4)';

/** Light at 45% opacity — vote distribution backgrounds, borders */
export const CYAN_LIGHT_45 = 'rgba(103,232,249,0.45)';

/** Light at 40% opacity — border accent */
export const CYAN_LIGHT_40 = 'rgba(103,232,249,0.4)';

/** Light at 50% opacity — border accent stronger */
export const CYAN_LIGHT_50 = 'rgba(103,232,249,0.5)';

// ─── Gradient Presets ─────────────────────────────────────────────────────────

/** Standard horizontal brand gradient */
export const GRADIENT_BRAND = `linear-gradient(90deg,${CYAN_PRIMARY},${CYAN_SECONDARY})`;

/** Deep-to-light horizontal gradient (scroll bars, progress indicators) */
export const GRADIENT_DEEP = `linear-gradient(90deg,${CYAN_DEEP},${CYAN_PRIMARY})`;

/** Angled brand gradient for CTAs and hero sections */
export const GRADIENT_BRAND_135 = `linear-gradient(135deg,${CYAN_PRIMARY} 0%,${CYAN_SECONDARY} 100%)`;

/** Campaign banner full-spectrum gradient */
export const GRADIENT_BANNER = `linear-gradient(90deg,${CYAN_DEEP} 0%,${CYAN_PRIMARY} 50%,${CYAN_SECONDARY} 100%)`;

/** Auth modal dark panel background */
export const GRADIENT_AUTH_PANEL = `linear-gradient(145deg,${BG_DARK} 0%,${BG_DARK_ALT} 60%,${BG_DARK_TERTIARY} 100%)`;

/** Sidebar dark gradient */
export const GRADIENT_SIDEBAR = `linear-gradient(135deg,${CYAN_DEEP},${BG_DARK})`;

// ─── Brand Object (legacy compat — used by page.tsx) ──────────────────────────

export const brand = {
  accent: CYAN_PRIMARY,
} as const;

// ─── Category Colors ──────────────────────────────────────────────────────────

export const CATEGORY_PALETTE = [CYAN_PRIMARY, '#0EA5E9', '#10B981', '#F59E0B'] as const;
