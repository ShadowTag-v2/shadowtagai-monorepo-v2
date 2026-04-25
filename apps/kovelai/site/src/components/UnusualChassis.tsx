/**
 * UnusualChassis.tsx
 *
 * Structural chassis extracted from unusualmachines.com layout geometry.
 * Bones only — no proprietary IP, images, logos, or copy.
 *
 * Layout Architecture:
 *   Header (fixed, z-50, h-24) → Hero Banner (h-[648px], flex, overflow-hidden)
 *   → Highlights (py-14, white bg) → Quick Access (py-14, dark overlay, z-10)
 *   → Events (py-14, white bg) → Contact (py-14, dark overlay)
 *   → Footer (py-5, #291e44)
 *
 * Breakpoints: 414px (mobile), 700px (tablet), 1024px (desktop), 1199px (wide)
 * Container: max-w-[1140px] mx-auto (matches source)
 */

import React from "react";

interface ChassisSection {
  id: string;
  children?: React.ReactNode;
  className?: string;
}

/* ─── Section Title ─── */
function SectionTitle({
  children,
  variant = "dark",
}: {
  children: React.ReactNode;
  variant?: "dark" | "light";
}) {
  return (
    <h2
      className={`
        inline-block text-4xl font-bold mb-11 tracking-tight
        ${variant === "light" ? "text-white" : "text-gray-900"}
      `}
    >
      {children}
    </h2>
  );
}

/* ─── Container ─── */
function Container({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}

/* ─── Main Chassis ─── */
export default function UnusualChassis({
  heroSlot,
  highlightsSlot,
  quickAccessSlot,
  eventsSlot,
  contactSlot,
  navSlot,
  footerSlot,
}: {
  heroSlot?: React.ReactNode;
  highlightsSlot?: React.ReactNode;
  quickAccessSlot?: React.ReactNode;
  eventsSlot?: React.ReactNode;
  contactSlot?: React.ReactNode;
  navSlot?: React.ReactNode;
  footerSlot?: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-black text-white antialiased">
      {/* ─── HEADER: Fixed, z-50, h-24 ─── */}
      <header className="fixed top-0 left-0 right-0 z-50 h-24 bg-transparent backdrop-blur-sm transition-colors duration-300">
        <Container className="h-full flex items-center justify-between">
          {/* Logo placeholder zone */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-white/10 border border-white/20" aria-label="Logo placeholder" />
            <span className="text-lg font-semibold tracking-tight">Brand</span>
          </div>

          {/* Nav slot */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
            {navSlot ?? (
              <>
                <a href="#highlights" className="text-white/70 hover:text-white transition-colors">Products</a>
                <a href="#quick-access" className="text-white/70 hover:text-white transition-colors">Solutions</a>
                <a href="#events" className="text-white/70 hover:text-white transition-colors">Resources</a>
                <a href="#contact" className="text-white/70 hover:text-white transition-colors">Contact</a>
              </>
            )}
          </nav>

          {/* CTA */}
          <button className="px-5 py-2.5 rounded-lg bg-white/10 border border-white/20 text-sm font-medium hover:bg-white/20 transition-all">
            Get Started
          </button>
        </Container>
      </header>

      {/* ─── HERO BANNER: h-[648px], flex, overflow-hidden, relative ─── */}
      <section
        id="hero"
        className="relative flex items-center justify-center h-[648px] overflow-hidden"
        aria-label="Hero banner"
      >
        {heroSlot ?? (
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-800" />
        )}
      </section>

      {/* ─── HIGHLIGHTS: py-14, white bg, block ─── */}
      <section
        id="highlights"
        className="py-14 bg-white text-gray-900"
        aria-label="Highlights"
      >
        <Container>
          <SectionTitle variant="dark">Highlights</SectionTitle>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {highlightsSlot ?? (
              <>
                {[1, 2, 3].map((i) => (
                  <div key={i} className="aspect-[4/3] rounded-2xl bg-gray-100 border border-gray-200" />
                ))}
              </>
            )}
          </div>
        </Container>
      </section>

      {/* ─── QUICK ACCESS: py-14, dark overlay, relative, z-10 ─── */}
      <section
        id="quick-access"
        className="relative z-10 py-14 bg-black/50 text-white"
        aria-label="Quick access"
      >
        <Container>
          <SectionTitle variant="light">Quick Access</SectionTitle>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickAccessSlot ?? (
              <>
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="aspect-square rounded-2xl bg-white/5 border border-white/10 hover:border-white/30 transition-colors" />
                ))}
              </>
            )}
          </div>
        </Container>
      </section>

      {/* ─── EVENTS: py-14, white bg ─── */}
      <section
        id="events"
        className="py-14 bg-white text-gray-900"
        aria-label="Events"
      >
        <Container>
          <SectionTitle variant="dark">Events</SectionTitle>
          {eventsSlot ?? (
            <div className="h-48 rounded-2xl bg-gray-100 border border-gray-200" />
          )}
        </Container>
      </section>

      {/* ─── CONTACT: py-14, dark overlay, relative ─── */}
      <section
        id="contact"
        className="relative py-14 bg-black/50 text-white"
        aria-label="Contact"
      >
        <Container>
          <SectionTitle variant="light">Get in Touch</SectionTitle>
          {contactSlot ?? (
            <div className="max-w-xl mx-auto space-y-6">
              <div className="h-12 rounded-lg bg-white/5 border border-white/10" />
              <div className="h-12 rounded-lg bg-white/5 border border-white/10" />
              <div className="h-32 rounded-lg bg-white/5 border border-white/10" />
              <button className="w-full py-3 rounded-lg bg-white/10 border border-white/20 hover:bg-white/20 transition-all font-medium">
                Send Message
              </button>
            </div>
          )}
        </Container>
      </section>

      {/* ─── FOOTER: py-5, #291e44 ─── */}
      <footer
        className="py-5 text-white/60 text-sm"
        style={{ backgroundColor: "#291e44" }}
        aria-label="Footer"
      >
        <Container className="flex items-center justify-between">
          {footerSlot ?? (
            <>
              <span>&copy; {new Date().getFullYear()} Brand. All rights reserved.</span>
              <div className="flex gap-4">
                <a href="#" className="hover:text-white transition-colors">Privacy</a>
                <a href="#" className="hover:text-white transition-colors">Terms</a>
              </div>
            </>
          )}
        </Container>
      </footer>
    </div>
  );
}
