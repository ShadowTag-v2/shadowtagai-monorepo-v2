'use client';

import type React from 'react';

/**
 * UnusualChassis — Structural layout chassis extracted from unusualmachines.com
 *
 * This component provides ONLY the structural bones:
 * - Sticky glassmorphic navigation bar
 * - Full-bleed hero zone (accepts children for video/animation overlays)
 * - Alternating content sections with contained max-width
 * - Feature card grid (responsive 3→2→1 columns)
 * - Full-width CTA band
 * - Multi-column footer with contact/links grid
 *
 * All proprietary content (images, logos, copy) has been stripped.
 * Design tokens sourced from KovelAI DESIGN.md (atmospheric-glass dark mode).
 */

/* ── Design Token Constants (from DESIGN.md) ── */
const TOKENS = {
  surface: '#0A0A0F',
  surfaceDim: '#0A0A0F',
  surfaceContainerLow: '#0D1117',
  surfaceContainer: '#111827',
  surfaceContainerHigh: '#1A1F2E',
  surfaceOverlay: '#0C0C12',
  surfaceCard: '#101621',
  surfaceAccentTint: '#0A2B30',
  onSurface: '#FFFFFF',
  onSurfaceVariant: '#8B949E',
  onSurfaceElevated: '#C9D1D9',
  tertiary: '#00BCD4',
  onTertiary: '#003238',
  tertiaryContainer: '#00838F',
  statusPremium: '#7C4DFF',
} as const;

/* ── Inline Styles (no Tailwind dependency for portability) ── */
const styles = {
  /* PAGE */
  page: {
    backgroundColor: TOKENS.surface,
    color: TOKENS.onSurface,
    fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
    minHeight: '100vh',
    overflow: 'hidden',
  } satisfies React.CSSProperties,

  /* NAVBAR — Sticky glassmorphic */
  nav: {
    position: 'sticky' as const,
    top: 0,
    zIndex: 100,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: 64,
    padding: '0 24px',
    backgroundColor: 'rgba(12, 12, 18, 0.8)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    borderBottom: '1px solid rgba(255,255,255,0.06)',
  } satisfies React.CSSProperties,

  navBrand: {
    fontSize: 20,
    fontWeight: 800,
    letterSpacing: '-0.02em',
    color: TOKENS.onSurface,
  } satisfies React.CSSProperties,

  navLinks: {
    display: 'flex',
    gap: 32,
    listStyle: 'none',
    margin: 0,
    padding: 0,
  } satisfies React.CSSProperties,

  navLink: {
    fontSize: 14,
    fontWeight: 500,
    color: TOKENS.onSurfaceVariant,
    textDecoration: 'none',
    letterSpacing: '0.02em',
    transition: 'color 0.2s ease',
    cursor: 'pointer',
  } satisfies React.CSSProperties,

  navCta: {
    backgroundColor: TOKENS.tertiary,
    color: TOKENS.onTertiary,
    border: 'none',
    borderRadius: 16,
    padding: '10px 28px',
    fontSize: 14,
    fontWeight: 600,
    letterSpacing: '0.02em',
    cursor: 'pointer',
    transition: 'background-color 0.2s ease',
  } satisfies React.CSSProperties,

  /* HERO — Full bleed zone (children injected here) */
  heroZone: {
    position: 'relative' as const,
    width: '100%',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  } satisfies React.CSSProperties,

  /* SECTION — Contained max-width with vertical rhythm */
  section: {
    position: 'relative' as const,
    maxWidth: 1200,
    margin: '0 auto',
    padding: '80px 24px',
  } satisfies React.CSSProperties,

  sectionHeading: {
    fontSize: 40,
    fontWeight: 800,
    lineHeight: 1.15,
    letterSpacing: '-0.02em',
    color: TOKENS.onSurface,
    marginBottom: 16,
  } satisfies React.CSSProperties,

  sectionSubheading: {
    fontSize: 18,
    fontWeight: 400,
    lineHeight: 1.6,
    color: TOKENS.onSurfaceVariant,
    maxWidth: 640,
    marginBottom: 48,
  } satisfies React.CSSProperties,

  /* FEATURE GRID — 3→2→1 responsive via CSS grid */
  featureGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
    gap: 24,
  } satisfies React.CSSProperties,

  featureCard: {
    backgroundColor: TOKENS.surfaceCard,
    border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: 16,
    padding: 24,
    transition: 'border-color 0.25s ease, transform 0.25s ease',
  } satisfies React.CSSProperties,

  featureCardIcon: {
    width: 48,
    height: 48,
    borderRadius: 12,
    backgroundColor: TOKENS.surfaceAccentTint,
    display: 'flex',
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    marginBottom: 16,
    color: TOKENS.tertiary,
    fontSize: 24,
  } satisfies React.CSSProperties,

  featureCardTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: TOKENS.onSurface,
    marginBottom: 8,
  } satisfies React.CSSProperties,

  featureCardDesc: {
    fontSize: 14,
    lineHeight: 1.6,
    color: TOKENS.onSurfaceVariant,
  } satisfies React.CSSProperties,

  /* FULL-WIDTH CTA BAND */
  ctaBand: {
    width: '100%',
    padding: '80px 24px',
    textAlign: 'center' as const,
    background: `linear-gradient(135deg, ${TOKENS.surfaceContainerLow} 0%, ${TOKENS.surfaceContainer} 100%)`,
    borderTop: '1px solid rgba(255,255,255,0.04)',
    borderBottom: '1px solid rgba(255,255,255,0.04)',
  } satisfies React.CSSProperties,

  /* ALTERNATING CONTENT — Text+Media split */
  splitSection: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 64,
    alignItems: 'center' as const,
    maxWidth: 1200,
    margin: '0 auto',
    padding: '80px 24px',
  } satisfies React.CSSProperties,

  mediaMock: {
    width: '100%',
    aspectRatio: '16/9',
    borderRadius: 16,
    backgroundColor: TOKENS.surfaceContainerHigh,
    border: '1px solid rgba(255,255,255,0.06)',
    display: 'flex',
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    color: TOKENS.onSurfaceVariant,
    fontSize: 14,
    fontWeight: 500,
  } satisfies React.CSSProperties,

  /* FOOTER */
  footer: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '64px 24px 32px',
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 32,
    borderTop: '1px solid rgba(255,255,255,0.06)',
  } satisfies React.CSSProperties,

  footerHeading: {
    fontSize: 14,
    fontWeight: 600,
    color: TOKENS.onSurface,
    marginBottom: 16,
    letterSpacing: '0.04em',
    textTransform: 'uppercase' as const,
  } satisfies React.CSSProperties,

  footerLink: {
    display: 'block',
    fontSize: 14,
    color: TOKENS.onSurfaceVariant,
    textDecoration: 'none',
    marginBottom: 8,
    transition: 'color 0.2s ease',
    cursor: 'pointer',
  } satisfies React.CSSProperties,

  footerBar: {
    maxWidth: 1200,
    margin: '0 auto',
    padding: '24px 24px 48px',
    display: 'flex',
    justifyContent: 'space-between' as const,
    alignItems: 'center' as const,
    fontSize: 12,
    color: TOKENS.onSurfaceVariant,
    borderTop: '1px solid rgba(255,255,255,0.04)',
  } satisfies React.CSSProperties,
} as const;

/* ── Slot Interfaces ── */
interface UnusualChassisProps {
  /** Brand name for nav (default: "KovelAI") */
  brandName?: string;
  /** Navigation link labels */
  navLinks?: string[];
  /** CTA button label */
  ctaLabel?: string;
  /** Hero zone — inject video/animation overlay here */
  heroContent?: React.ReactNode;
  /** Feature cards — array of { icon, title, description } */
  features?: Array<{ icon: string; title: string; description: string }>;
  /** Footer link groups */
  footerGroups?: Array<{ heading: string; links: string[] }>;
  /** Children (additional sections) */
  children?: React.ReactNode;
}

export function UnusualChassis({
  brandName = 'KovelAI',
  navLinks = ['Platform', 'For Law Firms', 'Pricing', 'Post-Heppner', 'Investors'],
  ctaLabel = 'Start Free Trial',
  heroContent,
  features = [],
  footerGroups = [],
  children,
}: UnusualChassisProps) {
  return (
    <div style={styles.page}>
      {/* ── NAVBAR ── */}
      <nav style={styles.nav} id="chassis-nav">
        <span style={styles.navBrand}>{brandName}</span>
        <ul style={styles.navLinks}>
          {navLinks.map((label) => (
            <li key={label}>
              <a href={`#${label.toLowerCase().replace(/\s+/g, '-')}`} style={styles.navLink}>
                {label}
              </a>
            </li>
          ))}
        </ul>
        <button type="button" style={styles.navCta}>
          {ctaLabel}
        </button>
      </nav>

      {/* ── HERO ZONE (full bleed injection point) ── */}
      <section style={styles.heroZone} id="chassis-hero">
        {heroContent ?? (
          <div style={{ textAlign: 'center', padding: '0 24px' }}>
            <h1
              style={{
                ...styles.sectionHeading,
                fontSize: 64,
                fontWeight: 900,
                letterSpacing: '-0.03em',
              }}
            >
              {/* Placeholder — inject real headline */}
              Hero Headline Slot
            </h1>
            <p style={{ ...styles.sectionSubheading, margin: '16px auto 32px' }}>
              Subheadline slot for value proposition
            </p>
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
              <button type="button" style={styles.navCta}>
                {ctaLabel}
              </button>
              <button
                type="button"
                style={{
                  ...styles.navCta,
                  backgroundColor: 'transparent',
                  border: `1px solid ${TOKENS.tertiary}`,
                  color: TOKENS.tertiary,
                }}
              >
                Learn More
              </button>
            </div>
          </div>
        )}
      </section>

      {/* ── ALTERNATING CONTENT SECTION ── */}
      <div style={styles.splitSection} id="chassis-split-1">
        <div>
          <h2 style={styles.sectionHeading}>Feature Section Slot</h2>
          <p style={styles.sectionSubheading}>
            Alternating text-and-media layout. Left text, right media.
          </p>
        </div>
        <div style={styles.mediaMock}>Media Placeholder</div>
      </div>

      <div style={{ ...styles.splitSection, direction: 'rtl' }} id="chassis-split-2">
        <div style={{ direction: 'ltr' }}>
          <h2 style={styles.sectionHeading}>Reversed Section Slot</h2>
          <p style={styles.sectionSubheading}>Reversed layout. Media left, text right.</p>
        </div>
        <div style={{ ...styles.mediaMock, direction: 'ltr' }}>Media Placeholder</div>
      </div>

      {/* ── FEATURE CARD GRID ── */}
      <section style={styles.section} id="chassis-features">
        <h2 style={{ ...styles.sectionHeading, textAlign: 'center' }}>Features Grid Slot</h2>
        <p style={{ ...styles.sectionSubheading, textAlign: 'center', margin: '16px auto 48px' }}>
          Responsive 3→2→1 column card grid
        </p>
        <div style={styles.featureGrid}>
          {(features.length > 0
            ? features
            : Array.from({ length: 6 }, (_, i) => ({
                icon: '⬡',
                title: `Feature ${i + 1}`,
                description: 'Feature description slot — inject real content here.',
              }))
          ).map((feat, i) => (
            <div key={i} style={styles.featureCard}>
              <div style={styles.featureCardIcon}>{feat.icon}</div>
              <h3 style={styles.featureCardTitle}>{feat.title}</h3>
              <p style={styles.featureCardDesc}>{feat.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA BAND (full width) ── */}
      <section style={styles.ctaBand} id="chassis-cta">
        <h2 style={{ ...styles.sectionHeading, marginBottom: 16 }}>Call-to-Action Band Slot</h2>
        <p style={{ ...styles.sectionSubheading, margin: '0 auto 32px', textAlign: 'center' }}>
          Full-width conversion zone
        </p>
        <button type="button" style={styles.navCta}>
          {ctaLabel}
        </button>
      </section>

      {/* ── CUSTOM CHILDREN INJECTION POINT ── */}
      {children}

      {/* ── FOOTER ── */}
      <footer style={styles.footer} id="chassis-footer">
        {(footerGroups.length > 0
          ? footerGroups
          : [
              { heading: 'Platform', links: ['Overview', 'Features', 'Pricing', 'Security'] },
              { heading: 'Company', links: ['About', 'Careers', 'Press', 'Contact'] },
              { heading: 'Legal', links: ['Privacy', 'Terms', 'Compliance', 'Post-Heppner'] },
              { heading: 'Connect', links: ['Investors', 'Partners', 'Support', 'API Docs'] },
            ]
        ).map((group) => (
          <div key={group.heading}>
            <h4 style={styles.footerHeading}>{group.heading}</h4>
            {group.links.map((link) => (
              <a
                key={link}
                href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
                style={styles.footerLink}
              >
                {link}
              </a>
            ))}
          </div>
        ))}
      </footer>
      <div style={styles.footerBar}>
        <span>
          © {new Date().getFullYear()} {brandName}. All Rights Reserved.
        </span>
        <span>Privilege-Protected AI</span>
      </div>
    </div>
  );
}

export default UnusualChassis;
