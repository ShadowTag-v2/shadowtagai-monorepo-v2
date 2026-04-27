/**
 * UnusualChassis.tsx — Structural Chassis from unusualmachines.com
 *
 * Extracted via Chrome DevTools MCP on 2026-04-25.
 * Source: https://www.unusualmachines.com/
 *
 * This is a slot-based layout component that preserves the structural
 * geometry of the source site while allowing Cinematic Legal-Tech
 * content injection via React children/slots.
 *
 * Layout Blueprint:
 *   1. Fixed header (transparent → solid on scroll)
 *   2. Full-bleed hero (648px, flex-center, overflow-hidden)
 *   3. Highlights section (white bg, 605px, 55px v-padding)
 *   4. Quick Links (bg-image + dark overlay, 449px)
 *   5. Events section (white bg, 346px)
 *   6. Contact section (bg-image + dark overlay, 756px)
 *   7. Footer (deep brand color, 60px)
 *
 * Container: max-width 1170px, margin 0 auto, padding 0 15px
 */

import React, { useEffect, useState, type ReactNode } from 'react';

/* ─── Slot Interface ─── */
export interface ChassisSlots {
  /** Logo element for the header */
  logo?: ReactNode;
  /** Navigation items */
  navItems?: ReactNode;
  /** CTA button in the header */
  headerCta?: ReactNode;
  /** Hero section content (overlaid on video/image bg) */
  heroContent?: ReactNode;
  /** Hero background element (<video>, <img>, or gradient) */
  heroBg?: ReactNode;
  /** Section 3: Highlights / News / Features grid */
  highlightsContent?: ReactNode;
  /** Section 3 title override */
  highlightsTitle?: string;
  /** Section 4: Quick Links / Icon grid */
  quickLinksContent?: ReactNode;
  /** Section 4 title override */
  quickLinksTitle?: string;
  /** Section 4 background element */
  quickLinksBg?: ReactNode;
  /** Section 5: Events / Metrics */
  eventsContent?: ReactNode;
  /** Section 5 title override */
  eventsTitle?: string;
  /** Section 6: Contact / CTA */
  contactContent?: ReactNode;
  /** Section 6 title override */
  contactTitle?: string;
  /** Section 6 background element */
  contactBg?: ReactNode;
  /** Footer content */
  footerContent?: ReactNode;
}

/* ─── Cinematic Theme Tokens ─── */
export interface ChassisTheme {
  /** Void background color */
  voidBg: string;
  /** Scrim overlay color with opacity */
  scrimColor: string;
  /** Section alternating dark bg */
  sectionDarkBg: string;
  /** Section light bg (for contrast sections) */
  sectionLightBg: string;
  /** Footer bg */
  footerBg: string;
  /** Primary text color */
  textPrimary: string;
  /** Muted text color */
  textMuted: string;
  /** Accent color */
  accent: string;
  /** Font family */
  fontFamily: string;
}

/* ─── Default Cinematic Theme ─── */
const CINEMATIC_THEME: ChassisTheme = {
  voidBg: '#050505',
  scrimColor: 'rgba(8, 13, 20, 0.95)',
  sectionDarkBg: '#0a0a0a',
  sectionLightBg: '#0f0f0f',
  footerBg: '#030303',
  textPrimary: '#ffffff',
  textMuted: '#8da2c0',
  accent: '#a0aabf',
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
};

/* ─── Styles ─── */
const styles = {
  root: (theme: ChassisTheme): React.CSSProperties => ({
    width: '100%',
    minHeight: '100vh',
    backgroundColor: theme.voidBg,
    color: theme.textPrimary,
    fontFamily: theme.fontFamily,
    fontSize: '16px',
    fontWeight: 300,
    lineHeight: 1.6,
    overflowX: 'hidden' as const,
  }),

  /* Header — fixed, transparent → solid on scroll */
  header: (scrolled: boolean, theme: ChassisTheme): React.CSSProperties => ({
    position: 'fixed' as const,
    top: 0,
    left: 0,
    right: 0,
    height: '80px',
    zIndex: 50,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: scrolled ? theme.voidBg : 'transparent',
    borderBottom: scrolled ? `1px solid rgba(255,255,255,0.06)` : 'none',
    backdropFilter: scrolled ? 'blur(20px)' : 'none',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
  }),

  headerInner: {
    maxWidth: '1170px',
    width: '100%',
    margin: '0 auto',
    padding: '0 24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  } as React.CSSProperties,

  /* Hero — 648px, flex center, relative for bg layering */
  hero: {
    position: 'relative' as const,
    width: '100%',
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden' as const,
  } as React.CSSProperties,

  heroBgLayer: {
    position: 'absolute' as const,
    inset: 0,
    zIndex: 1,
  } as React.CSSProperties,

  heroScrim: (theme: ChassisTheme): React.CSSProperties => ({
    position: 'absolute' as const,
    inset: 0,
    zIndex: 2,
    backgroundColor: theme.scrimColor,
  }),

  heroContentLayer: {
    position: 'relative' as const,
    zIndex: 3,
    maxWidth: '1170px',
    width: '100%',
    margin: '0 auto',
    padding: '0 24px',
  } as React.CSSProperties,

  /* Alternating sections */
  section: (bg: string): React.CSSProperties => ({
    position: 'relative' as const,
    width: '100%',
    padding: '80px 0',
    backgroundColor: bg,
  }),

  sectionWithBg: {
    position: 'relative' as const,
    width: '100%',
    padding: '80px 0',
    overflow: 'hidden' as const,
  } as React.CSSProperties,

  sectionBgLayer: {
    position: 'absolute' as const,
    inset: 0,
    zIndex: 1,
  } as React.CSSProperties,

  sectionScrim: (theme: ChassisTheme): React.CSSProperties => ({
    position: 'absolute' as const,
    inset: 0,
    zIndex: 2,
    backgroundColor: theme.scrimColor,
  }),

  sectionContent: {
    position: 'relative' as const,
    zIndex: 3,
    maxWidth: '1170px',
    width: '100%',
    margin: '0 auto',
    padding: '0 24px',
  } as React.CSSProperties,

  sectionTitle: (theme: ChassisTheme): React.CSSProperties => ({
    fontSize: '14px',
    fontWeight: 500,
    letterSpacing: '0.15em',
    textTransform: 'uppercase' as const,
    color: theme.textMuted,
    marginBottom: '48px',
  }),

  /* Footer */
  footer: (theme: ChassisTheme): React.CSSProperties => ({
    width: '100%',
    backgroundColor: theme.footerBg,
    borderTop: '1px solid rgba(255,255,255,0.06)',
    padding: '40px 0',
  }),

  footerInner: {
    maxWidth: '1170px',
    width: '100%',
    margin: '0 auto',
    padding: '0 24px',
  } as React.CSSProperties,
} as const;

/* ─── CSS Keyframes (injected once) ─── */
const KEYFRAMES = `
@keyframes chassisFadeUp {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
`;

/* ─── Component ─── */
export function UnusualChassis({
  slots,
  theme = CINEMATIC_THEME,
}: {
  slots: ChassisSlots;
  theme?: ChassisTheme;
}) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <style>{KEYFRAMES}</style>
      <div style={styles.root(theme)}>
        {/* ─── SECTION 1: Fixed Header ─── */}
        <header style={styles.header(scrolled, theme)}>
          <div style={styles.headerInner as React.CSSProperties}>
            <div>{slots.logo}</div>
            <nav style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
              {slots.navItems}
            </nav>
            <div>{slots.headerCta}</div>
          </div>
        </header>

        {/* ─── SECTION 2: Full-Bleed Hero ─── */}
        <section style={styles.hero}>
          <div style={styles.heroBgLayer}>
            {slots.heroBg}
          </div>
          <div style={styles.heroScrim(theme)} />
          <div style={styles.heroContentLayer}>
            {slots.heroContent}
          </div>
        </section>

        {/* ─── SECTION 3: Highlights / Features ─── */}
        <section style={styles.section(theme.sectionDarkBg)}>
          <div style={styles.sectionContent}>
            {slots.highlightsTitle && (
              <div style={styles.sectionTitle(theme)}>
                {slots.highlightsTitle}
              </div>
            )}
            {slots.highlightsContent}
          </div>
        </section>

        {/* ─── SECTION 4: Quick Links / Icon Grid (with BG) ─── */}
        <section style={styles.sectionWithBg}>
          <div style={styles.sectionBgLayer}>
            {slots.quickLinksBg}
          </div>
          <div style={styles.sectionScrim(theme)} />
          <div style={styles.sectionContent}>
            {slots.quickLinksTitle && (
              <div style={styles.sectionTitle(theme)}>
                {slots.quickLinksTitle}
              </div>
            )}
            {slots.quickLinksContent}
          </div>
        </section>

        {/* ─── SECTION 5: Events / Metrics ─── */}
        <section style={styles.section(theme.sectionLightBg)}>
          <div style={styles.sectionContent}>
            {slots.eventsTitle && (
              <div style={styles.sectionTitle(theme)}>
                {slots.eventsTitle}
              </div>
            )}
            {slots.eventsContent}
          </div>
        </section>

        {/* ─── SECTION 6: Contact / CTA (with BG) ─── */}
        <section style={styles.sectionWithBg}>
          <div style={styles.sectionBgLayer}>
            {slots.contactBg}
          </div>
          <div style={styles.sectionScrim(theme)} />
          <div style={styles.sectionContent}>
            {slots.contactTitle && (
              <div style={styles.sectionTitle(theme)}>
                {slots.contactTitle}
              </div>
            )}
            {slots.contactContent}
          </div>
        </section>

        {/* ─── SECTION 7: Footer ─── */}
        <footer style={styles.footer(theme)}>
          <div style={styles.footerInner}>
            {slots.footerContent}
          </div>
        </footer>
      </div>
    </>
  );
}

/* ─── Pre-built CounselConduit Theme ─── */
export const COUNSELCONDUIT_THEME: ChassisTheme = {
  voidBg: '#050505',
  scrimColor: 'rgba(8, 13, 20, 0.95)',
  sectionDarkBg: '#080808',
  sectionLightBg: '#0c0c0c',
  footerBg: '#030303',
  textPrimary: '#ffffff',
  textMuted: '#8da2c0',
  accent: '#a0aabf',
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
};

/* ─── Pre-built UphillSnowball Theme ─── */
export const UPHILLSNOWBALL_THEME: ChassisTheme = {
  voidBg: '#020408',
  scrimColor: 'rgba(3, 5, 9, 0.96)',
  sectionDarkBg: '#060a10',
  sectionLightBg: '#0a0e16',
  footerBg: '#020306',
  textPrimary: '#ffffff',
  textMuted: '#9ca3af',
  accent: '#a0aabf',
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
};

export default UnusualChassis;
