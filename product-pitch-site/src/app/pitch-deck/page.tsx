"use client";

import { useState, useEffect, useCallback, useRef } from "react";

/* ===== SLIDE DATA ===== */
const slides = [
  {
    id: 1,
    label: "COVER",
    headline: "KovelAI",
    subline: "Post-Heppner Privileged Client AI",
    body: "Through Your Firm, And You Get Paid.",
    tagline: "Antigravity for the Practice of Law",
    color: "from-[#0a1628] to-[#0d1117]",
  },
  {
    id: 2,
    label: "THE PROBLEM",
    headline: "The 2 a.m. Nightmare",
    bullets: [
      "Clients research their own cases on public AI at 2 a.m.",
      "Heppner (Feb 2026) proved this instantly waives privilege.",
      "Lawyers chase receivables, burn out on unbillable midnight texts, and pay paralegals for grunt work.",
      "No safe, paid way for clients to vent and research under attorney supervision.",
    ],
    color: "from-[#1a0a0a] to-[#0d1117]",
    accent: "#ef4444",
  },
  {
    id: 3,
    label: "THE SOLUTION",
    headline: "The Privileged Wrapper",
    bullets: [
      "KovelAI is the Shopify for Legal AI.",
      "A zero-knowledge, attorney-supervised AI portal that law firms sell to clients.",
      "Every query is privileged by design. Every message is prepaid.",
      "You get paid while you sleep.",
    ],
    color: "from-[#0a1428] to-[#0d1117]",
    accent: "#00bcd4",
  },
  {
    id: 4,
    label: "MARKET VALIDATION",
    headline: "The Heppner Wake-Up Call",
    bullets: [
      "United States v. Heppner (S.D.N.Y., Feb 2026) made it official: unsupervised public AI destroys privilege.",
      "Lawyers and clients have been waiting for the fix.",
      'Early beta firms already seeing 100% conversion on $99–$250 intake sessions.',
    ],
    color: "from-[#140a1e] to-[#0d1117]",
    accent: "#7c4dff",
  },
  {
    id: 5,
    label: "MARKET SIZE",
    headline: "$500 Billion Opportunity",
    stats: [
      { value: "$500B+", label: "U.S. legal market" },
      { value: "1.3M", label: "Solo & small firm lawyers (beachhead)" },
      { value: "$15B+", label: "Annual spend on practice tools" },
    ],
    footnote: "KovelAI captures the new privileged AI layer every firm will mandate.",
    color: "from-[#0a1e14] to-[#0d1117]",
    accent: "#34a853",
  },
  {
    id: 6,
    label: "THE PRODUCT",
    headline: "Two Sides, One Platform",
    columns: [
      {
        title: "Client Side",
        icon: "\ud83d\udc64",
        items: [
          "24/7 privileged research",
          "Vent Mode \u2014 dump anxiety without per-message billing anxiety",
          "Google Search + Google Translate integrated",
        ],
      },
      {
        title: "Lawyer Side",
        icon: "\u2696\ufe0f",
        items: [
          "Oracle Studio \u2014 7-prompt system with Action Verb Auditor",
          "Permanent Notes auto-saved to Firm Vault",
          "Full oversight dashboard",
        ],
      },
    ],
    footnote: "Zero-knowledge. Fully Heppner/Kovel compliant.",
    color: "from-[#0a1628] to-[#0d1117]",
    accent: "#00bcd4",
  },
  {
    id: 7,
    label: "BUSINESS MODEL",
    headline: "The Cash Register",
    bullets: [
      "Client pays lawyer before query runs (Stripe Connect).",
      "Lawyer pays us one auto-scaling monthly tier.",
      "85%+ gross margins. Zero A/R. Zero unbillable hours.",
      "Paralegal arbitrage + after-hours monetization built in.",
    ],
    color: "from-[#0a1e14] to-[#0d1117]",
    accent: "#34a853",
  },
  {
    id: 8,
    label: "ADOPTION STRATEGY",
    headline: "The Avvo Assassination",
    bullets: [
      'Lawyers replace Avvo bios and "Contact Us" forms with one Magic Link.',
      '"Warning: Do not post on Avvo or Reddit. Pay $99 to use my firm\'s privileged AI portal instead."',
      "Clients pay, vent, lock themselves in psychologically.",
      "Lawyers slash Avvo budgets to fund KovelAI.",
    ],
    color: "from-[#1e1a0a] to-[#0d1117]",
    accent: "#fbbc04",
  },
  {
    id: 9,
    label: "COMPETITION",
    headline: "We Own the Empty Quadrant",
    matrix: {
      axes: ["Client-facing vs Lawyer-only", "Multi-model vs Single-model"],
      competitors: [
        "Harvey AI / CoCounsel / Lexis+ AI \u2192 Lawyer-only, single-model, no client portal.",
        "Avvo \u2192 Public, unprivileged, free labor for lawyers.",
      ],
      us: "KovelAI is the only privileged, prepaid, client-facing multi-model platform with Oracle Studio.",
    },
    color: "from-[#0a1628] to-[#0d1117]",
    accent: "#4285f4",
  },
  {
    id: 10,
    label: "THE MOAT",
    headline: "The Antigravity Moat",
    bullets: [
      "Heppner/Kovel legal moat (attorney-supervised + cryptographic attestation).",
      'Psychological lock-in (clients "get it off their chest" and never want to leave).',
      "Zero-churn cash register (you cannot unplug an ATM).",
      "Oracle Studio with Action Verb Auditor \u2192 institutional memory that compounds forever.",
    ],
    color: "from-[#140a1e] to-[#0d1117]",
    accent: "#7c4dff",
  },
  {
    id: 11,
    label: "FINANCIALS",
    headline: "Projections",
    rows: [
      { year: "Year 1", firms: "250 firms", arr: "$1M ARR" },
      { year: "Year 2", firms: "1,500 firms", arr: "$6M ARR" },
      { year: "Year 3", firms: "6,000 firms", arr: "$24M ARR" },
    ],
    footnote: "85–88% gross margins • <2% churn",
    color: "from-[#0a1e14] to-[#0d1117]",
    accent: "#34a853",
  },
  {
    id: 12,
    label: "THE ASK",
    headline: "Join the Lift-Off",
    bullets: [
      "Pre-Seed: $750K–$1.2M at $10M–$12M cap",
      "First customers live in 45 days.",
      "The only platform that pays both sides at the same time.",
    ],
    color: "from-[#0a1628] to-[#0d1117]",
    accent: "#00bcd4",
  },
  {
    id: 13,
    label: "THE TEAM",
    headline: "Built by lawyers who hated the old way",
    body: "Deep legal-tech + AI infrastructure experience. Founders with intimate knowledge of Kovel doctrine, Heppner compliance, and enterprise AI security.",
    color: "from-[#140a1e] to-[#0d1117]",
    accent: "#7c4dff",
  },
  // ——— APPENDIX SLIDES ———
  {
    id: 14,
    label: "APPENDIX: TECH STACK",
    headline: "Enterprise-Grade Infrastructure",
    techStack: [
      { category: "Runtime", items: ["Google Cloud Run (serverless)", "Firebase Hosting (CDN)", "Cloud Armor WAF"] },
      { category: "AI Layer", items: ["Gemini 3.1 Flash Lite (primary)", "Claude, ChatGPT, Grok, Perplexity (multi-model)", "LiteLLM Proxy (routing)"] },
      { category: "Security", items: ["Kovel Attestation (HMAC-SHA256)", "Zero-knowledge architecture", "SOC 2 + HIPAA BAA pathway"] },
      { category: "Payments", items: ["Stripe Connect (dual-billing)", "Auto-scaling tiers", "Idempotent webhooks"] },
    ],
    color: "from-[#0a1628] to-[#0d1117]",
    accent: "#4285f4",
  },
  {
    id: 15,
    label: "APPENDIX: SECURITY",
    headline: "Zero-Trust Security Architecture",
    securityLayers: [
      { icon: "\ud83d\udd12", title: "Privilege Preservation", desc: "Every session cryptographically attested under Kovel doctrine. HMAC-SHA256 receipts per query." },
      { icon: "\ud83d\udee1\ufe0f", title: "Data Isolation", desc: "Per-firm namespace isolation. No cross-tenant data leakage. Tenant-scoped Firestore paths." },
      { icon: "\u23f1\ufe0f", title: "Ephemeral Sessions", desc: "Client sessions auto-expire. Dead-man's switch. No export, no copy, no screenshot." },
      { icon: "\ud83d\udccb", title: "Audit Trail", desc: "Immutable transcripts for lawyer oversight. GDPR 30-day auto-delete via Cloud Tasks." },
    ],
    color: "from-[#140a1e] to-[#0d1117]",
    accent: "#ef4444",
  },
  {
    id: 16,
    label: "CLOSING VISION",
    headline: "Antigravity for the Practice of Law",
    closing: [
      "Turns 2 a.m. panic into prepaid peace of mind.",
      "For the client who finally feels heard.",
      "For the lawyer who finally gets paid.",
    ],
    tagline: "Thank you.",
    color: "from-[#0a1628] to-[#0d1117]",
  },
];

/* ===== PRICING TIERS ===== */
const pricingSlide = {
  tiers: [
    { name: "Solo", price: "$299/mo", clients: "25 portals" },
    { name: "Practice", price: "$599/mo", clients: "Unlimited", featured: true },
    { name: "Enterprise", price: "$999/mo", clients: "Dedicated infra" },
  ],
};

const TOTAL_SLIDES = slides.length;
const ACCESS_CODE = "kovelai2026";

/* ===== PITCH DECK PAGE ===== */
export default function PitchDeckPage() {
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [accessCode, setAccessCode] = useState("");
  const [accessError, setAccessError] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [email, setEmail] = useState("");
  const slideRefs = useRef<(HTMLElement | null)[]>([]);
  const slideTimings = useRef<Record<number, number>>({});
  const lastSlideTime = useRef(Date.now());

  // Check localStorage for previous access
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem("kovelai_deck_access");
      if (stored === "granted") setIsUnlocked(true);
    }
  }, []);

  // Track slide timing
  useEffect(() => {
    if (!isUnlocked) return;
    const now = Date.now();
    const elapsed = now - lastSlideTime.current;
    if (elapsed > 500) {
      slideTimings.current[currentSlide] = (slideTimings.current[currentSlide] || 0) + elapsed;
    }
    lastSlideTime.current = now;
  }, [currentSlide, isUnlocked]);

  // Save analytics on unload (item 21)
  useEffect(() => {
    if (!isUnlocked) return;
    const handleUnload = () => {
      const now = Date.now();
      slideTimings.current[currentSlide] = (slideTimings.current[currentSlide] || 0) + (now - lastSlideTime.current);
      try {
        localStorage.setItem("kovelai_deck_analytics", JSON.stringify({
          timings: slideTimings.current,
          totalSlides: TOTAL_SLIDES,
          timestamp: new Date().toISOString(),
        }));
      } catch { /* localStorage may be full */ }
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, [isUnlocked, currentSlide]);

  // IntersectionObserver for slide tracking (item 4)
  useEffect(() => {
    if (!isUnlocked) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const idx = slideRefs.current.indexOf(entry.target as HTMLElement);
            if (idx >= 0) setCurrentSlide(idx);
          }
        });
      },
      { threshold: 0.5 }
    );
    slideRefs.current.forEach((ref) => {
      if (ref) observer.observe(ref);
    });
    return () => observer.disconnect();
  }, [isUnlocked]);

  // Keyboard navigation (item 11)
  const scrollToSlide = useCallback((idx: number) => {
    const clamped = Math.max(0, Math.min(TOTAL_SLIDES - 1, idx));
    slideRefs.current[clamped]?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (!isUnlocked) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown" || e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        scrollToSlide(currentSlide + 1);
      } else if (e.key === "ArrowUp" || e.key === "ArrowLeft") {
        e.preventDefault();
        scrollToSlide(currentSlide - 1);
      } else if (e.key === "Home") {
        e.preventDefault();
        scrollToSlide(0);
      } else if (e.key === "End") {
        e.preventDefault();
        scrollToSlide(TOTAL_SLIDES - 1);
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isUnlocked, currentSlide, scrollToSlide]);

  // Download handler with email capture (item 16)
  const handleDownload = () => {
    setShowEmailModal(true);
  };

  const handleEmailSubmit = () => {
    if (email) {
      try {
        const downloads = JSON.parse(localStorage.getItem("kovelai_deck_downloads") || "[]");
        downloads.push({ email, timestamp: new Date().toISOString() });
        localStorage.setItem("kovelai_deck_downloads", JSON.stringify(downloads));
      } catch { /* ignore */ }
    }
    setShowEmailModal(false);
    setTimeout(() => window.print(), 200);
  };

  // Access gate handler (items 8 + 17)
  const handleAccessSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (accessCode.toLowerCase().trim() === ACCESS_CODE) {
      setIsUnlocked(true);
      localStorage.setItem("kovelai_deck_access", "granted");
      setAccessError(false);
    } else {
      setAccessError(true);
    }
  };

  /* ===== ACCESS GATE ===== */
  if (!isUnlocked) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] px-6">
        <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] rounded-full bg-[#00bcd4]/5 blur-[150px]" />
        <div className="absolute bottom-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-[#7c4dff]/5 blur-[120px]" />

        <div className="relative z-10 text-center max-w-md w-full">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center mx-auto mb-8 shadow-[0_0_40px_rgba(0,188,212,0.3)]">
            <span className="text-2xl font-black text-[#0a0a0f]">K</span>
          </div>

          <h1 className="text-3xl font-black text-white mb-2">Investor Access</h1>
          <p className="text-[#8b949e] mb-8">This pitch deck is confidential. Enter the access code to continue.</p>

          <form onSubmit={handleAccessSubmit} className="space-y-4">
            <input
              type="password"
              value={accessCode}
              onChange={(e) => { setAccessCode(e.target.value); setAccessError(false); }}
              placeholder="Access code"
              className={`w-full px-5 py-3.5 rounded-xl bg-white/5 border text-white placeholder:text-[#8b949e]/50 text-center text-lg tracking-widest font-mono focus:outline-none focus:ring-2 focus:ring-[#00bcd4]/50 transition-all ${
                accessError ? "border-red-500/50 shake" : "border-white/10"
              }`}
              autoFocus
            />
            {accessError && (
              <p className="text-red-400 text-sm animate-pulse">Invalid access code. Please try again.</p>
            )}
            <button
              type="submit"
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] text-[#0a0a0f] font-semibold hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              View Pitch Deck
            </button>
          </form>

          <a href="/" className="inline-block mt-6 text-sm text-[#8b949e] hover:text-white transition-colors">
            &larr; Back to KovelAI
          </a>
        </div>

        <style jsx>{`
          .shake { animation: shake 0.4s ease-in-out; }
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-8px); }
            75% { transform: translateX(8px); }
          }
        `}</style>
      </div>
    );
  }

  /* ===== MAIN DECK ===== */
  return (
    <>
      {/* Print styles (item 20) */}
      <style jsx global>{`
        @media print {
          @page {
            size: 11in 8.5in landscape;
            margin: 0;
          }
          body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          .no-print {
            display: none !important;
          }
          .deck-slide {
            break-inside: avoid;
            page-break-after: always;
            height: 100vh !important;
            min-height: 100vh !important;
            max-height: 100vh !important;
            overflow: hidden !important;
          }
          .deck-slide:last-child {
            page-break-after: auto;
          }
          .slide-enter {
            opacity: 1 !important;
            transform: none !important;
          }
          * {
            animation: none !important;
            transition: none !important;
          }
        }

        /* Slide transitions (item 3) */
        .slide-enter {
          opacity: 0;
          transform: translateY(40px);
          transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
                      transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .slide-enter.visible {
          opacity: 1;
          transform: translateY(0);
        }

        /* Smooth scroll snap */
        html {
          scroll-behavior: smooth;
        }
      `}</style>

      {/* Sticky header (item 7 — back link) */}
      <div className="no-print fixed top-0 left-0 right-0 z-50 bg-[#0d1117]/95 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="flex items-center gap-2 text-[#8b949e] hover:text-white transition-colors text-sm">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M10 4L6 8l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
              Back
            </a>
            <div className="h-4 w-px bg-white/10" />
            <a href="/" className="flex items-center gap-2 group">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center font-bold text-xs text-[#0a0a0f]">
                K
              </div>
              <span className="text-sm font-bold text-white hidden sm:inline">
                Kovel<span className="bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] bg-clip-text text-transparent">AI</span>
              </span>
            </a>
          </div>

          {/* Progress indicator (item 4) */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5">
              {slides.map((_, i) => (
                <button
                  key={i}
                  onClick={() => scrollToSlide(i)}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    i === currentSlide
                      ? "w-6 bg-[#00bcd4]"
                      : i < currentSlide
                      ? "w-1.5 bg-[#00bcd4]/40"
                      : "w-1.5 bg-white/15"
                  }`}
                  aria-label={`Go to slide ${i + 1}`}
                />
              ))}
            </div>
            <span className="text-xs text-[#8b949e] font-mono tabular-nums min-w-[3.5rem] text-right">
              {currentSlide + 1} / {TOTAL_SLIDES}
            </span>
            <span className="text-xs text-[#8b949e] hidden md:inline">• Confidential</span>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] text-[#0a0a0f] text-xs font-semibold hover:scale-[1.03] active:scale-[0.98] transition-all"
            >
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <path d="M8 1v10M4 8l4 4 4-4M2 13h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span className="hidden sm:inline">Download PDF</span>
            </button>
          </div>
        </div>
      </div>

      {/* Email capture modal (item 16) */}
      {showEmailModal && (
        <div className="no-print fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-[#161b22] border border-white/10 rounded-2xl p-8 max-w-sm w-full mx-4 shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-2">Download Pitch Deck</h3>
            <p className="text-sm text-[#8b949e] mb-6">Enter your email to receive updates and download the PDF.</p>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="investor@example.com"
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-[#8b949e]/50 focus:outline-none focus:ring-2 focus:ring-[#00bcd4]/50 mb-4"
              autoFocus
            />
            <div className="flex gap-3">
              <button
                onClick={() => setShowEmailModal(false)}
                className="flex-1 py-2.5 rounded-xl border border-white/10 text-[#8b949e] hover:text-white text-sm transition-colors"
              >
                Skip
              </button>
              <button
                onClick={handleEmailSubmit}
                className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] text-[#0a0a0f] font-semibold text-sm hover:scale-[1.02] active:scale-[0.98] transition-all"
              >
                Download
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard hint */}
      <div className="no-print fixed bottom-6 right-6 z-40 text-[10px] text-[#8b949e]/40 font-mono hidden lg:block">
        ←↑↓→ navigate • space next
      </div>

      {/* Deck container */}
      <div className="pt-14 print:pt-0">
        {/* ——— SLIDE 1: COVER ——— */}
        <SlideWrapper idx={0} refs={slideRefs} className="flex flex-col items-center justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] relative overflow-hidden px-6 sm:px-8">
          <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-[#00bcd4]/5 blur-[150px]" />
          <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full bg-[#7c4dff]/5 blur-[120px]" />
          <div className="relative z-10 text-center max-w-3xl">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center mx-auto mb-10 shadow-[0_0_60px_rgba(0,188,212,0.3)]">
              <span className="text-3xl font-black text-[#0a0a0f]">K</span>
            </div>
            <h1 className="text-5xl sm:text-6xl md:text-8xl font-black tracking-tighter text-white mb-4">
              Kovel<span className="bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] bg-clip-text text-transparent">AI</span>
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-[#8b949e] mb-2 font-light">Post-Heppner Privileged Client AI</p>
            <p className="text-base sm:text-lg md:text-xl text-white/70 mb-1">Through Your Firm, And You Get Paid.</p>
            <p className="text-sm text-[#00bcd4]/70 italic mt-8">Antigravity for the Practice of Law</p>
            <p className="text-xs text-[#8b949e]/50 mt-16 font-mono uppercase tracking-widest">Confidential • Pre-Seed • 2026</p>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 2: PROBLEM ——— */}
        <SlideWrapper idx={1} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#1a0a0a] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-5xl mx-auto">
            <div className="text-xs font-mono text-[#ef4444]/60 tracking-widest uppercase mb-4">02 — The Problem</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              The 2 a.m. <span className="text-[#ef4444]">Nightmare</span>
            </h2>
            <div className="grid sm:grid-cols-2 gap-6 sm:gap-8">
              {slides[1].bullets!.map((b, i) => (
                <div key={i} className="p-5 sm:p-6 rounded-2xl bg-[#0d1117]/80 border border-[#ef4444]/10 hover:border-[#ef4444]/30 transition-colors">
                  <div className="w-8 h-8 rounded-lg bg-[#ef4444]/10 flex items-center justify-center text-[#ef4444] text-sm font-bold mb-4">
                    {String(i + 1).padStart(2, "0")}
                  </div>
                  <p className="text-[#c9d1d9] leading-relaxed">{b}</p>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 3: SOLUTION ——— */}
        <SlideWrapper idx={2} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1428] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto">
            <div className="text-xs font-mono text-[#00bcd4]/60 tracking-widest uppercase mb-4">03 — The Solution</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              The Privileged <span className="bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] bg-clip-text text-transparent">Wrapper</span>
            </h2>
            <div className="space-y-5 sm:space-y-6">
              {slides[2].bullets!.map((b, i) => (
                <div key={i} className="flex items-start gap-4 p-5 rounded-xl bg-white/[0.02] border-l-2 border-[#00bcd4]/40">
                  <div className="w-2 h-2 rounded-full bg-[#00bcd4] mt-2 shrink-0" />
                  <p className="text-base sm:text-lg md:text-xl text-[#c9d1d9] leading-relaxed">{b}</p>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 4: MARKET VALIDATION ——— */}
        <SlideWrapper idx={3} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#140a1e] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto">
            <div className="text-xs font-mono text-[#7c4dff]/60 tracking-widest uppercase mb-4">04 — Market Validation</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              The Heppner <span className="text-[#7c4dff]">Wake-Up Call</span>
            </h2>
            <div className="p-6 sm:p-8 md:p-10 rounded-2xl bg-[#0d1117]/80 border border-[#7c4dff]/15 shadow-[0_0_40px_rgba(124,77,255,0.05)]">
              {slides[3].bullets!.map((b, i) => (
                <div key={i} className={`py-4 sm:py-5 ${i > 0 ? "border-t border-white/5" : ""}`}>
                  <p className="text-base sm:text-lg text-[#c9d1d9] leading-relaxed">{b}</p>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 5: MARKET SIZE ——— */}
        <SlideWrapper idx={4} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1e14] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-xs font-mono text-[#34a853]/60 tracking-widest uppercase mb-4">05 — Market Size</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 sm:mb-16 tracking-tight">
              <span className="text-[#34a853]">$500 Billion</span> Opportunity
            </h2>
            <div className="flex flex-col items-center gap-5 sm:gap-6 mb-12">
              {slides[4].stats!.map((s, i) => (
                <div
                  key={i}
                  className="w-full rounded-full py-4 sm:py-5 px-6 sm:px-8 border flex items-center justify-center gap-3 sm:gap-4 transition-all"
                  style={{
                    maxWidth: `${80 - i * 15}%`,
                    background: `rgba(52,168,83,${0.05 + i * 0.08})`,
                    borderColor: `rgba(52,168,83,${0.15 + i * 0.15})`,
                    boxShadow: i === 2 ? "0 0 30px rgba(52,168,83,0.15)" : "none",
                  }}
                >
                  <span className={`text-xl sm:text-2xl md:text-3xl font-black ${i === 2 ? "text-white" : "text-[#34a853]"}`}>
                    {s.value}
                  </span>
                  <span className="text-xs sm:text-sm text-[#8b949e]">{s.label}</span>
                </div>
              ))}
            </div>
            <p className="text-[#8b949e] text-sm">{slides[4].footnote}</p>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 6: PRODUCT ——— */}
        <SlideWrapper idx={5} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-5xl mx-auto">
            <div className="text-xs font-mono text-[#00bcd4]/60 tracking-widest uppercase mb-4">06 — The Product</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-10 sm:mb-12 tracking-tight">
              Two Sides. <span className="bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] bg-clip-text text-transparent">One Platform.</span>
            </h2>
            <div className="grid sm:grid-cols-2 gap-6 sm:gap-8 mb-8">
              {slides[5].columns!.map((col, i) => (
                <div key={i} className="p-6 sm:p-8 rounded-2xl bg-[#0d1117]/80 border border-[#00bcd4]/10 hover:border-[#00bcd4]/25 transition-colors">
                  <div className="text-3xl sm:text-4xl mb-4">{col.icon}</div>
                  <h3 className="text-xl sm:text-2xl font-bold text-white mb-5 sm:mb-6">{col.title}</h3>
                  <ul className="space-y-3">
                    {col.items.map((item, j) => (
                      <li key={j} className="flex items-start gap-3 text-sm sm:text-base text-[#c9d1d9]">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#00bcd4] mt-2 shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-3 sm:gap-4">
              {pricingSlide.tiers.map((tier) => (
                <div
                  key={tier.name}
                  className={`p-4 sm:p-5 rounded-xl text-center border transition-all ${
                    tier.featured
                      ? "bg-[#00bcd4]/10 border-[#00bcd4]/30 shadow-[0_0_20px_rgba(0,188,212,0.1)]"
                      : "bg-white/[0.02] border-white/5"
                  }`}
                >
                  <div className="text-[10px] sm:text-xs text-[#8b949e] uppercase tracking-wider mb-1">{tier.name}</div>
                  <div className={`text-lg sm:text-xl font-bold ${tier.featured ? "text-[#00bcd4]" : "text-white"}`}>{tier.price}</div>
                  <div className="text-[10px] sm:text-xs text-[#8b949e] mt-1">{tier.clients}</div>
                </div>
              ))}
            </div>
            <p className="text-center text-xs text-[#8b949e] mt-6">{slides[5].footnote}</p>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 7: BUSINESS MODEL ——— */}
        <SlideWrapper idx={6} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1e14] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto">
            <div className="text-xs font-mono text-[#34a853]/60 tracking-widest uppercase mb-4">07 — Business Model</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              The Cash <span className="text-[#34a853]">Register</span>
            </h2>
            <div className="space-y-5 sm:space-y-6">
              {slides[6].bullets!.map((b, i) => {
                const colors = ["#34a853", "#4285f4", "#fbbc04", "#00bcd4"];
                return (
                  <div key={i} className="flex items-start gap-4 p-5 rounded-xl bg-white/[0.02]" style={{ borderLeft: `3px solid ${colors[i]}` }}>
                    <p className="text-base sm:text-lg text-[#c9d1d9] leading-relaxed">{b}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 8: ADOPTION ——— */}
        <SlideWrapper idx={7} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#1e1a0a] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto">
            <div className="text-xs font-mono text-[#fbbc04]/60 tracking-widest uppercase mb-4">08 — Adoption Strategy</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              The Avvo <span className="text-[#fbbc04]">Assassination</span>
            </h2>
            <div className="space-y-4 sm:space-y-5">
              {slides[7].bullets!.map((b, i) => (
                <div key={i} className="p-5 sm:p-6 rounded-2xl bg-[#0d1117]/80 border border-[#fbbc04]/10">
                  <p className="text-base sm:text-lg text-[#c9d1d9] leading-relaxed">{b}</p>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 9: COMPETITION ——— */}
        <SlideWrapper idx={8} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-5xl mx-auto">
            <div className="text-xs font-mono text-[#4285f4]/60 tracking-widest uppercase mb-4">09 — Competition</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-10 sm:mb-12 tracking-tight">
              We Own the <span className="text-[#4285f4]">Empty Quadrant</span>
            </h2>
            <div className="grid grid-cols-2 gap-1 mb-10 max-w-3xl mx-auto">
              <div className="p-4 sm:p-6 rounded-tl-2xl bg-white/[0.03] border border-white/5">
                <div className="text-[10px] sm:text-xs text-[#8b949e] uppercase mb-2 sm:mb-3">Secure + Cost Center</div>
                <p className="text-xs sm:text-sm text-[#c9d1d9]">Harvey AI, Westlaw, CoCounsel, Lexis+ AI</p>
              </div>
              <div className="p-4 sm:p-6 rounded-tr-2xl bg-[#00bcd4]/10 border-2 border-[#00bcd4]/40 shadow-[0_0_30px_rgba(0,188,212,0.1)]">
                <div className="text-[10px] sm:text-xs text-[#00bcd4] uppercase mb-2 sm:mb-3 font-bold">Secure + Revenue \u2605</div>
                <p className="text-base sm:text-lg font-bold text-white">KovelAI</p>
                <p className="text-[10px] sm:text-xs text-[#8b949e] mt-1">Privileged + prepaid + client-facing</p>
              </div>
              <div className="p-4 sm:p-6 rounded-bl-2xl bg-white/[0.02] border border-white/5">
                <div className="text-[10px] sm:text-xs text-[#8b949e] uppercase mb-2 sm:mb-3">Risky + Cost Center</div>
                <p className="text-xs sm:text-sm text-[#c9d1d9]">ChatGPT Direct, Google Direct</p>
              </div>
              <div className="p-4 sm:p-6 rounded-br-2xl bg-white/[0.02] border border-white/5">
                <div className="text-[10px] sm:text-xs text-[#8b949e] uppercase mb-2 sm:mb-3">Risky + Revenue</div>
                <p className="text-xs sm:text-sm text-[#c9d1d9]">Avvo, LegalZoom</p>
              </div>
            </div>
            <p className="text-center text-[#8b949e] text-xs sm:text-sm">{slides[8].matrix!.us}</p>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 10: MOAT ——— */}
        <SlideWrapper idx={9} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#140a1e] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto">
            <div className="text-xs font-mono text-[#7c4dff]/60 tracking-widest uppercase mb-4">10 — Competitive Advantages</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              The Antigravity <span className="text-[#7c4dff]">Moat</span>
            </h2>
            <div className="grid sm:grid-cols-2 gap-5 sm:gap-6">
              {slides[9].bullets!.map((b, i) => (
                <div key={i} className="p-5 sm:p-6 rounded-2xl bg-[#0d1117]/80 border border-[#7c4dff]/10">
                  <div className="w-8 h-8 rounded-lg bg-[#7c4dff]/15 flex items-center justify-center text-[#7c4dff] text-sm font-bold mb-4">
                    {String(i + 1).padStart(2, "0")}
                  </div>
                  <p className="text-sm sm:text-base text-[#c9d1d9] leading-relaxed">{b}</p>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 11: FINANCIALS ——— */}
        <SlideWrapper idx={10} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1e14] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-xs font-mono text-[#34a853]/60 tracking-widest uppercase mb-4">11 — Financial Projections</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 sm:mb-16 tracking-tight">
              <span className="text-[#34a853]">Projections</span>
            </h2>
            <div className="grid grid-cols-3 gap-4 sm:gap-6 mb-10">
              {slides[10].rows!.map((r, i) => (
                <div
                  key={i}
                  className="p-5 sm:p-8 rounded-2xl border bg-[#0d1117]/80 text-center"
                  style={{
                    borderColor: `rgba(52,168,83,${0.15 + i * 0.15})`,
                    boxShadow: i === 2 ? "0 0 30px rgba(52,168,83,0.1)" : "none",
                  }}
                >
                  <div className="text-xs sm:text-sm text-[#8b949e] mb-2">{r.year}</div>
                  <div className="text-xl sm:text-3xl font-black text-[#34a853] mb-1">{r.arr}</div>
                  <div className="text-[10px] sm:text-xs text-[#8b949e]">{r.firms}</div>
                </div>
              ))}
            </div>
            <p className="text-[#8b949e] text-xs sm:text-sm">{slides[10].footnote}</p>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 12: THE ASK ——— */}
        <SlideWrapper idx={11} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] px-6 sm:px-8 py-20 relative overflow-hidden">
          <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-[#00bcd4]/5 blur-[120px]" />
          <div className="max-w-4xl mx-auto relative z-10 text-center">
            <div className="text-xs font-mono text-[#00bcd4]/60 tracking-widest uppercase mb-4">12 — The Ask</div>
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              Join the <span className="bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] bg-clip-text text-transparent">Lift-Off</span>
            </h2>
            <div className="inline-block p-6 sm:p-8 md:p-10 rounded-2xl bg-[#0d1117]/80 border border-[#00bcd4]/20 shadow-[0_0_50px_rgba(0,188,212,0.08)] mb-8">
              <div className="text-2xl sm:text-3xl md:text-4xl font-black text-[#00bcd4] mb-2">$750K – $1.2M</div>
              <div className="text-base sm:text-lg text-[#8b949e]">Pre-Seed at $10M–$12M cap</div>
            </div>
            <div className="space-y-4">
              {slides[11].bullets!.slice(1).map((b, i) => (
                <p key={i} className="text-base sm:text-lg text-[#c9d1d9]">{b}</p>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 13: TEAM ——— */}
        <SlideWrapper idx={12} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#140a1e] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-3xl mx-auto text-center">
            <div className="text-xs font-mono text-[#7c4dff]/60 tracking-widest uppercase mb-4">13 — The Team</div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-10 tracking-tight">
              Built by lawyers who <span className="text-[#7c4dff]">hated the old way</span>
            </h2>
            <div className="p-6 sm:p-8 rounded-2xl bg-[#0d1117]/80 border border-[#7c4dff]/10">
              <p className="text-lg sm:text-xl text-[#c9d1d9] leading-relaxed">
                {slides[12].body}
              </p>
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 14: APPENDIX — TECH STACK (item 13) ——— */}
        <SlideWrapper idx={13} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-5xl mx-auto">
            <div className="text-xs font-mono text-[#4285f4]/60 tracking-widest uppercase mb-4">Appendix A — Tech Stack</div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-10 sm:mb-12 tracking-tight">
              Enterprise-Grade <span className="text-[#4285f4]">Infrastructure</span>
            </h2>
            <div className="grid sm:grid-cols-2 gap-5 sm:gap-6">
              {slides[13].techStack!.map((stack, i) => (
                <div key={i} className="p-5 sm:p-6 rounded-2xl bg-[#0d1117]/80 border border-[#4285f4]/10">
                  <h3 className="text-sm font-bold text-[#4285f4] uppercase tracking-wider mb-4">{stack.category}</h3>
                  <ul className="space-y-2.5">
                    {stack.items.map((item, j) => (
                      <li key={j} className="flex items-start gap-2.5 text-sm text-[#c9d1d9]">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#4285f4]/60 mt-1.5 shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 15: APPENDIX — SECURITY (item 13) ——— */}
        <SlideWrapper idx={14} refs={slideRefs} className="flex flex-col justify-center bg-gradient-to-b from-[#140a1e] to-[#0d1117] px-6 sm:px-8 py-20">
          <div className="max-w-5xl mx-auto">
            <div className="text-xs font-mono text-[#ef4444]/60 tracking-widest uppercase mb-4">Appendix B — Security</div>
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-black text-white mb-10 sm:mb-12 tracking-tight">
              Zero-Trust <span className="text-[#ef4444]">Security</span> Architecture
            </h2>
            <div className="grid sm:grid-cols-2 gap-5 sm:gap-6">
              {slides[14].securityLayers!.map((layer, i) => (
                <div key={i} className="p-5 sm:p-6 rounded-2xl bg-[#0d1117]/80 border border-[#ef4444]/10">
                  <div className="text-2xl sm:text-3xl mb-3">{layer.icon}</div>
                  <h3 className="text-base sm:text-lg font-bold text-white mb-2">{layer.title}</h3>
                  <p className="text-xs sm:text-sm text-[#8b949e] leading-relaxed">{layer.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </SlideWrapper>

        {/* ——— SLIDE 16: CLOSING ——— */}
        <SlideWrapper idx={15} refs={slideRefs} className="flex flex-col items-center justify-center bg-gradient-to-b from-[#0a1628] to-[#0d1117] px-6 sm:px-8 py-20 relative overflow-hidden">
          <div className="absolute top-1/4 left-1/3 w-[500px] h-[500px] rounded-full bg-[#00bcd4]/5 blur-[150px]" />
          <div className="absolute bottom-1/3 right-1/3 w-[400px] h-[400px] rounded-full bg-[#7c4dff]/5 blur-[120px]" />
          <div className="relative z-10 text-center max-w-3xl">
            <h2 className="text-3xl sm:text-4xl md:text-6xl font-black text-white mb-12 tracking-tight">
              Antigravity for the{" "}
              <span className="bg-gradient-to-r from-[#00bcd4] to-[#7c4dff] bg-clip-text text-transparent">
                Practice of Law
              </span>
            </h2>
            <div className="space-y-4 mb-12">
              {slides[15].closing!.map((line, i) => (
                <p key={i} className="text-lg sm:text-xl text-[#c9d1d9]">{line}</p>
              ))}
            </div>
            <p className="text-2xl font-bold text-white">{slides[15].tagline}</p>
            <div className="mt-16 flex items-center justify-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center font-bold text-sm text-[#0a0a0f]">
                K
              </div>
              <span className="text-base font-bold text-white">
                Kovel<span className="bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] bg-clip-text text-transparent">AI</span>
              </span>
            </div>
            <p className="text-xs text-[#8b949e]/40 mt-8 font-mono">kovelai.com • Confidential</p>
          </div>
        </SlideWrapper>
      </div>
    </>
  );
}

/* ===== SLIDE WRAPPER COMPONENT (handles transitions, refs, responsive) ===== */
function SlideWrapper({
  idx,
  refs,
  className,
  children,
}: {
  idx: number;
  refs: React.MutableRefObject<(HTMLElement | null)[]>;
  className: string;
  children: React.ReactNode;
}) {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(el);
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={(el) => {
        sectionRef.current = el;
        refs.current[idx] = el;
      }}
      className={`deck-slide min-h-screen slide-enter ${isVisible ? "visible" : ""} ${className}`}
    >
      {children}
    </section>
  );
}
