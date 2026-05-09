"use client";

import { trackEvent } from "@/lib/analytics";
import { useState, useEffect } from "react";

export function NavBar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const navLinks = [
    { label: "Platform", href: "#platform" },
    { label: "For Law Firms", href: "#law-firms" },
    { label: "Pricing", href: "#pricing" },
    { label: "Post-Heppner", href: "#heppner" },
    { label: "Investors", href: "/pitch-deck" },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? "nav-glass scrolled" : "nav-glass"
      }`}
    >
      <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between h-[72px]">
        {/* Logo */}
        <a href="#" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center font-bold text-sm text-[#0a0a0f] transition-transform duration-300 group-hover:scale-110">
            K
          </div>
          <span className="text-lg font-bold tracking-tight">
            Kovel<span className="gradient-text">AI</span>
          </span>
        </a>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="px-4 py-2 text-sm font-medium text-[#8b949e] hover:text-white transition-colors duration-200 rounded-lg hover:bg-white/[0.03]"
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">
          <a href="#pricing" className="cta-button text-sm !py-2.5 !px-5">
            Start Free Trial
          </a>
        </div>

        {/* Mobile Toggle */}
        {/* Mobile Toggle — Item 15: polished animation */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2 relative z-50"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
        >
          <span
            className={`w-5 h-0.5 bg-white transition-all duration-300 ease-[cubic-bezier(0.68,-0.6,0.32,1.6)] origin-center ${mobileOpen ? "rotate-45 translate-y-2" : ""}`}
          />
          <span
            className={`w-5 h-0.5 bg-white transition-all duration-200 ${mobileOpen ? "opacity-0 scale-x-0" : "opacity-100 scale-x-100"}`}
          />
          <span
            className={`w-5 h-0.5 bg-white transition-all duration-300 ease-[cubic-bezier(0.68,-0.6,0.32,1.6)] origin-center ${mobileOpen ? "-rotate-45 -translate-y-2" : ""}`}
          />
        </button>
      </div>

      {/* Mobile Menu — Item 15: slide-down with staggered links */}
      <div
        className={`md:hidden overflow-hidden transition-all duration-400 ease-[cubic-bezier(0.4,0,0.2,1)] bg-[#0d1117]/95 backdrop-blur-xl border-t border-[#00bcd4]/10 ${
          mobileOpen ? "max-h-[400px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="px-6 py-4 flex flex-col gap-2">
          {navLinks.map((link, i) => (
            <a
              key={link.href}
              href={link.href}
              className="py-3 px-4 text-sm font-medium text-[#8b949e] hover:text-white rounded-lg hover:bg-white/[0.03] transition-all duration-300"
              style={{
                transitionDelay: mobileOpen ? `${i * 50}ms` : "0ms",
                transform: mobileOpen ? "translateX(0)" : "translateX(-12px)",
                opacity: mobileOpen ? 1 : 0,
              }}
              onClick={() => {
                setMobileOpen(false);
                trackEvent("nav_click", { link: link.label, source: "mobile" });
              }}
            >
              {link.label}
            </a>
          ))}
          <a
            href="#pricing"
            className="cta-button text-sm mt-2 justify-center"
            onClick={() => {
              setMobileOpen(false);
              trackEvent("cta_click", { button: "start_free_trial", source: "mobile_nav" });
            }}
          >
            Start Free Trial
          </a>
        </div>
      </div>
    </nav>
  );
}
