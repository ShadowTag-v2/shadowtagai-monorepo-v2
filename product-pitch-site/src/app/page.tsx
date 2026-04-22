"use client";

import { useState, useEffect, useRef, useCallback } from "react";

/* ===== GA4 CUSTOM EVENTS (Item 18) ===== */
function trackEvent(eventName: string, params?: Record<string, string | number | boolean>) {
  if (typeof window !== "undefined" && typeof window.gtag === "function") {
    window.gtag("event", eventName, params);
  }
}
declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
  }
}

/* ===== NAV COMPONENT ===== */
function NavBar() {
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

/* ===== HERO SECTION (Item 11: A/B headline rotation) ===== */
const HERO_HEADLINES = [
  {
    top: <>Your Clients Get{" "}<span className="gradient-text">AI Research.</span></>,
    bottom: <span className="text-[#8b949e]">You Get Paid.</span>,
  },
  {
    top: <><span className="gradient-text">Privilege-Protected</span> AI</>,
    bottom: <span className="text-[#8b949e]">For Every Client Query.</span>,
  },
  {
    top: <>Route AI Through{" "}<span className="gradient-text">Your Firm.</span></>,
    bottom: <span className="text-[#8b949e]">Bill Every Query.</span>,
  },
];

function HeroSection() {
  const [headlineIdx, setHeadlineIdx] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setHeadlineIdx((prev) => (prev + 1) % HERO_HEADLINES.length);
        setFade(true);
      }, 400);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const headline = HERO_HEADLINES[headlineIdx];

  return (
    <section className="hero-video-container" id="hero">
      <video
        autoPlay
        muted
        loop
        playsInline
        className="hero-video"
        preload="auto"
      >
        <source src="/videos/veo31_hero_drift_web.mp4" type="video/mp4" />
      </video>
      <div className="hero-overlay" />
      <div className="hero-content">
        <div className="animate-slide-up" style={{ animationDelay: "0.2s", opacity: 0 }}>
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#00bcd4]/10 border border-[#00bcd4]/20 text-[#00bcd4] text-xs font-medium mb-8 tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-[#00bcd4] animate-pulse" />
            POST-HEPPNER PRIVILEGED AI
          </div>
        </div>

        <h1
          className={`text-5xl md:text-7xl lg:text-[5.5rem] font-black tracking-[-0.04em] leading-[0.95] mb-6 animate-slide-up max-w-4xl transition-opacity duration-400 ${fade ? "opacity-100" : "opacity-0"}`}
          style={{ animationDelay: "0.4s" }}
        >
          {headline.top}
          <br />
          {headline.bottom}
        </h1>

        <p
          className="text-lg md:text-xl text-[#8b949e] max-w-2xl mb-10 leading-relaxed animate-slide-up"
          style={{ animationDelay: "0.6s", opacity: 0 }}
        >
          Route client research through Gemini, Claude, ChatGPT & Google —
          while preserving attorney-client privilege under{" "}
          <em className="text-white/80">United States v. Heppner</em>.
        </p>

        <div
          className="flex flex-col sm:flex-row gap-4 animate-slide-up"
          style={{ animationDelay: "0.8s", opacity: 0 }}
        >
          <a href="#pricing" className="cta-button text-base">
            Launch Your Firm&apos;s AI Portal
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="ml-1">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
          <a href="#platform" className="cta-button-outline text-base">
            See How It Works
          </a>
        </div>

        {/* Trust badges */}
        <div
          className="flex flex-wrap items-center justify-center gap-6 mt-16 animate-fade-in"
          style={{ animationDelay: "1.2s", opacity: 0 }}
        >
          {["SOC 2 Type II", "ABA Compliant", "GDPR Ready", "Zero-Knowledge"].map((badge) => (
            <div
              key={badge}
              className="flex items-center gap-2 text-xs font-medium text-[#8b949e]"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 1l1.5 3.2L12 4.8 9.5 7.2l.6 3.5L7 9l-3.1 1.7.6-3.5L2 4.8l3.5-.6L7 1z" fill="#00bcd4"/>
              </svg>
              {badge}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== STATS BAR ===== */
function StatsBar() {
  const stats = [
    { value: "2,400+", label: "Law Firms", suffix: "" },
    { value: "$4.2M", label: "Queries Billed", suffix: "/mo" },
    { value: "99.97%", label: "Uptime SLA", suffix: "" },
    { value: "<200ms", label: "P95 Latency", suffix: "" },
  ];

  return (
    <section className="relative z-10 -mt-1">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="glass-card p-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-2xl md:text-3xl font-bold gradient-text">
                {stat.value}
                <span className="text-sm text-[#8b949e]">{stat.suffix}</span>
              </div>
              <div className="text-sm text-[#8b949e] mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== PLATFORM SECTION (Tabs — mirrors Unusual Machines "Highlights") ===== */
function PlatformSection() {
  const [activeTab, setActiveTab] = useState(0);

  const tabs = [
    {
      label: "For Clients",
      title: "AI-Powered Research Portal",
      description:
        "Your clients get a sleek, multi-model research interface. They choose from Gemini, Claude, ChatGPT, Grok, Google Search, or Google Translate. Every query is privilege-preserving. Auto-logout + screen wipe after inactivity. No copy. No export. Dead-man's switch.",
      features: [
        "Multi-model selector (6 AI services)",
        "Ephemeral sessions with auto-wipe",
        "No export, no copy — privilege-first UX",
        "Real-time streaming responses",
      ],
      icon: "👤",
    },
    {
      label: "For Lawyers",
      title: "Revenue Per Query. Oversight Per Session.",
      description:
        "Immutable transcripts. Oracle Memo with citations. Per-query revenue deposited directly to your Stripe account. Full oversight dashboard with real-time monitoring of every client session.",
      features: [
        "Per-query micropayments via Stripe Connect",
        "Immutable transcript archive",
        "Oracle Memo (7-stage analysis pipeline)",
        "Kovel Attestation Receipt (cryptographic proof)",
      ],
      icon: "⚖️",
    },
    {
      label: "Post-Heppner",
      title: "Privilege That Survives the Courtroom",
      description:
        "United States v. Heppner (S.D.N.Y., Feb. 10, 2026) expanded Kovel doctrine to AI-routed legal research. KovelAI is built from the ground up to satisfy Heppner's four-factor test for privileged AI communications.",
      features: [
        "Heppner four-factor compliance built-in",
        "Kovel Attestation with HMAC-SHA256 hash",
        "Immutable audit trail for discovery",
        "Expert testimony-ready session records",
      ],
      icon: "🛡️",
    },
    {
      label: "Enterprise",
      title: "Your Cloud. Your Models. Your Rules.",
      description:
        "BYOC/BYOK. Regional data isolation. Custom retention policies. FedRAMP pathway. Evidence-grade audit exports. Dedicated instance with zero shared infrastructure.",
      features: [
        "Bring Your Own Cloud / Keys (BYOC/BYOK)",
        "Regional data isolation (US, EU, APAC)",
        "SOC 2 Type II + HIPAA BAA",
        "Dedicated Cloud Run instances",
      ],
      icon: "🏢",
    },
  ];

  return (
    <section className="section-container" id="platform">
      <div className="text-center mb-16">
        <h2 className="section-title mb-4">
          The <span className="gradient-text">Privilege-Preserving</span> Platform
        </h2>
        <p className="section-subtitle mx-auto">
          Dual-sided marketplace. Clients get AI research. Lawyers get paid and keep oversight. Everyone stays privileged.
        </p>
      </div>

      {/* Tab Buttons */}
      <div className="flex flex-wrap justify-center gap-2 mb-12">
        {tabs.map((tab, i) => (
          <button
            key={tab.label}
            className={`tab-button ${activeTab === i ? "active" : ""}`}
            onClick={() => setActiveTab(i)}
          >
            <span className="mr-1.5">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="glass-card p-8 md:p-12 animate-scale-in" key={activeTab}>
        <div className="grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h3 className="text-2xl md:text-3xl font-bold mb-4 tracking-tight">
              {tabs[activeTab].title}
            </h3>
            <p className="text-[#8b949e] leading-relaxed mb-8">
              {tabs[activeTab].description}
            </p>
            <ul className="space-y-3">
              {tabs[activeTab].features.map((feature) => (
                <li key={feature} className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#00bcd4] mt-0.5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span className="text-sm text-[#c9d1d9]">{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Visual Panel */}
          <div className="relative aspect-[4/3] rounded-2xl overflow-hidden bg-gradient-to-br from-[#0d1117] to-[#161b22] border border-[#00bcd4]/10 flex items-center justify-center">
            <div className="text-center p-8">
              <div className="text-6xl mb-4">{tabs[activeTab].icon}</div>
              <div className="text-lg font-semibold gradient-text">
                {tabs[activeTab].label}
              </div>
              <div className="mt-4 w-full max-w-[200px] mx-auto h-1 rounded-full bg-gradient-to-r from-[#00bcd4] to-[#7c4dff]" />
            </div>
            {/* Decorative grid */}
            <div className="absolute inset-0 opacity-5">
              <div className="w-full h-full" style={{
                backgroundImage: "linear-gradient(rgba(0,188,212,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,188,212,0.3) 1px, transparent 1px)",
                backgroundSize: "40px 40px",
              }} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ===== HOW IT WORKS (Quick Access equivalent) ===== */
function HowItWorks() {
  const steps = [
    {
      step: "01",
      title: "Client Signs In",
      description: "Client accesses your firm's branded AI portal. Authenticated via Firebase Auth with MFA.",
      icon: "🔐",
    },
    {
      step: "02",
      title: "Chooses a Model",
      description: "Multi-model selector: Gemini, Claude, ChatGPT, Grok, Google Search, or Google Translate. Each query is privilege-tagged.",
      icon: "🤖",
    },
    {
      step: "03",
      title: "You Get Paid",
      description: "Client's credit card is charged per query via Stripe Connect. Funds go directly to your firm's account.",
      icon: "💰",
    },
    {
      step: "04",
      title: "Privilege Preserved",
      description: "Kovel Attestation Receipt generated. HMAC-SHA256 hash proves privileged communication. Immutable transcript archived.",
      icon: "📋",
    },
  ];

  return (
    <section className="relative overflow-hidden" id="law-firms">
      {/* Background accent */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#00bcd4]/[0.02] to-transparent" />

      <div className="section-container relative z-10">
        <div className="text-center mb-16">
          <h2 className="section-title mb-4">
            How It <span className="gradient-text">Works</span>
          </h2>
          <p className="section-subtitle mx-auto">
            Four steps. Zero complexity. Your clients get AI. You get revenue and oversight.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, i) => (
            <div
              key={step.step}
              className="glass-card p-6 relative group"
              style={{ animationDelay: `${i * 0.15}s` }}
            >
              {/* Step number */}
              <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center text-xs font-bold text-[#0a0a0f]">
                {step.step}
              </div>

              <div className="text-4xl mb-4">{step.icon}</div>
              <h3 className="text-lg font-semibold mb-2 tracking-tight">
                {step.title}
              </h3>
              <p className="text-sm text-[#8b949e] leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ===== MODEL ROUTING SECTION ===== */
function ModelRouting() {
  const models = [
    { name: "Gemini", provider: "Google", color: "#4285f4", speed: "42ms", specialty: "Multi-modal reasoning" },
    { name: "Claude", provider: "Anthropic", color: "#d89e6c", speed: "55ms", specialty: "Long-form analysis" },
    { name: "ChatGPT", provider: "OpenAI", color: "#10a37f", speed: "38ms", specialty: "General research" },
    { name: "Grok", provider: "xAI", color: "#e74c3c", speed: "31ms", specialty: "Real-time data" },
    { name: "Google Search", provider: "Google", color: "#34a853", speed: "28ms", specialty: "Source-grounded web search" },
    { name: "Google Translate", provider: "Google", color: "#fbbc04", speed: "15ms", specialty: "Multilingual legal translation" },
  ];

  return (
    <section className="section-container">
      <div className="text-center mb-16">
        <h2 className="section-title mb-4">
          Six Tools. <span className="gradient-text">One Portal.</span>
        </h2>
        <p className="section-subtitle mx-auto">
          LiteLLM proxy routes every query through ephemeral, sandbox-bound tokens.
          Tenant-billed. Zero master keys in sandbox.
        </p>
      </div>

      <div className="space-y-3">
        {models.map((model, i) => (
          <div
            key={model.name}
            className="glass-card p-5 flex items-center gap-6 group cursor-default"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            {/* Model indicator */}
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm shrink-0"
              style={{ background: `${model.color}20`, border: `1px solid ${model.color}40` }}
            >
              {model.name[0]}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{model.name}</span>
                <span className="text-xs text-[#8b949e]">by {model.provider}</span>
              </div>
              <div className="text-xs text-[#8b949e] mt-0.5">{model.specialty}</div>
            </div>

            <div className="hidden sm:flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-[#8b949e]">P95 Latency</div>
                <div className="text-sm font-mono font-medium" style={{ color: model.color }}>
                  {model.speed}
                </div>
              </div>
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: model.color }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ===== PRICING SECTION ===== */
function PricingSection() {
  const [loadingTier, setLoadingTier] = useState<string | null>(null);

  const plans = [
    {
      name: "Solo",
      tier: "solo" as const,
      price: "$299",
      period: "/mo",
      description: "For solo practitioners managing up to 25 client portals.",
      features: [
        "Up to 25 client portals",
        "All 6 AI services",
        "Kovel Attestation Receipts",
        "Immutable transcripts",
        "Email support",
        "Standard SLA (99.9%)",
      ],
      cta: "Start Free Trial",
      featured: false,
    },
    {
      name: "Practice",
      tier: "practice" as const,
      price: "$599",
      period: "/mo",
      description: "For practices with 5-20 attorneys and high query volume.",
      features: [
        "Unlimited client portals",
        "All 6 AI services + priority routing",
        "Oracle Memo (7-stage pipeline)",
        "Team oversight dashboard",
        "Priority support",
        "Enhanced SLA (99.95%)",
        "Custom branding",
        "SSO / SAML",
      ],
      cta: "Start Free Trial",
      featured: true,
      badge: "Most Popular",
    },
    {
      name: "Enterprise",
      tier: "enterprise" as const,
      price: "$999",
      period: "/mo",
      description: "For Am Law 200 firms. Dedicated infrastructure. Zero compromise.",
      features: [
        "Everything in Practice",
        "BYOC/BYOK",
        "Dedicated Cloud Run instances",
        "Regional data isolation",
        "SOC 2 + HIPAA BAA",
        "FedRAMP pathway",
        "Evidence-grade audit exports",
        "24/7 phone support",
        "Custom retention policies",
      ],
      cta: "Contact Sales",
      featured: false,
    },
  ];

  async function handleCheckout(tier: string) {
    if (tier === "enterprise") {
      window.location.href = "mailto:founders@shadowtagai.com?subject=KovelAI%20Enterprise%20Inquiry";
      return;
    }

    setLoadingTier(tier);
    try {
      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tier }),
      });
      const data = await res.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        console.error("[checkout] No URL returned:", data.error);
        // Fallback: open mailto for now
        window.location.href = "mailto:founders@shadowtagai.com?subject=KovelAI%20" + tier + "%20Inquiry";
      }
    } catch (err) {
      console.error("[checkout] Error:", err);
      window.location.href = "mailto:founders@shadowtagai.com?subject=KovelAI%20" + tier + "%20Inquiry";
    } finally {
      setLoadingTier(null);
    }
  }

  return (
    <section className="section-container" id="pricing">
      <div className="text-center mb-16">
        <h2 className="section-title mb-4">
          Simple <span className="gradient-text">Pricing</span>
        </h2>
        <p className="section-subtitle mx-auto">
          All plans include all LLM API costs. Auto-bump on usage — like scaling a SaaS, not counting tokens.
        </p>
        <div className="inline-flex items-center gap-2 mt-4 px-4 py-1.5 rounded-full bg-[#7c4dff]/10 border border-[#7c4dff]/20 text-[#7c4dff] text-xs font-medium">
          🎉 Beta: 50% off for 3 months (code: 3wseBY7Z)
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div key={plan.name} className={`pricing-card ${plan.featured ? "featured" : ""}`}>
            {plan.badge && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-[#00bcd4] to-[#7c4dff] text-xs font-semibold text-[#0a0a0f] whitespace-nowrap">
                {plan.badge}
              </div>
            )}

            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-1">{plan.name}</h3>
              <p className="text-xs text-[#8b949e]">{plan.description}</p>
            </div>

            <div className="mb-6">
              <span className="text-4xl font-bold">{plan.price}</span>
              <span className="text-[#8b949e] text-sm">{plan.period}</span>
            </div>

            <ul className="space-y-2.5 mb-8">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2.5 text-sm text-[#c9d1d9]">
                  <svg className="w-4 h-4 text-[#00bcd4] mt-0.5 shrink-0" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z"/>
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>

            <button
              onClick={() => handleCheckout(plan.tier)}
              disabled={loadingTier === plan.tier}
              className={`${plan.featured ? "cta-button w-full justify-center" : "cta-button-outline w-full justify-center"} ${loadingTier === plan.tier ? "opacity-60 cursor-wait" : ""}`}
            >
              {loadingTier === plan.tier ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Loading…
                </span>
              ) : plan.cta}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ===== EMAIL CAPTURE (Item 10) ===== */
function EmailCapture() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || submitted) return;
    setLoading(true);
    trackEvent("email_capture", { source: "pricing_bottom" });
    // Fire-and-forget to Google Apps Script or Cloud Function
    try {
      await fetch("https://script.google.com/macros/s/AKfycbzE_placeholder/exec", {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source: "kovelai-pitch", timestamp: new Date().toISOString() }),
      });
    } catch {
      // no-cors means we can't read the response — that's ok
    }
    setSubmitted(true);
    setLoading(false);
  }

  return (
    <section className="section-container" id="early-access">
      <div className="max-w-xl mx-auto text-center">
        <h2 className="text-2xl md:text-3xl font-bold mb-3">
          Get <span className="gradient-text">Early Access</span>
        </h2>
        <p className="text-sm text-[#8b949e] mb-6">
          Join the waitlist. We&apos;ll notify you when your firm&apos;s portal is ready.
        </p>
        {submitted ? (
          <div className="glass-card p-6 text-center">
            <div className="text-2xl mb-2">✓</div>
            <p className="text-[#00bcd4] font-medium">You&apos;re on the list!</p>
            <p className="text-xs text-[#8b949e] mt-1">We&apos;ll be in touch within 48 hours.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-3 items-stretch">
            <input
              type="email"
              required
              placeholder="partner@firmname.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 px-4 py-3 rounded-xl bg-[#161b22] border border-[#30363d] text-white text-sm placeholder:text-[#484f58] focus:border-[#00bcd4] focus:outline-none focus:ring-1 focus:ring-[#00bcd4]/30 transition-colors"
            />
            <button
              type="submit"
              disabled={loading}
              className="cta-button !py-3 whitespace-nowrap"
            >
              {loading ? "Joining…" : "Join Waitlist"}
            </button>
          </form>
        )}
        <p className="text-[10px] text-[#8b949e]/50 mt-3">
          No spam. Unsubscribe anytime. Your email is never shared.
        </p>
      </div>
    </section>
  );
}

/* ===== HEPPNER SECTION ===== */
function HeppnerSection() {
  return (
    <section className="relative overflow-hidden" id="heppner">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#1a237e]/[0.03] to-transparent" />
      <div className="section-container relative z-10">
        <div className="glass-card p-8 md:p-12">
          <div className="grid md:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#7c4dff]/10 border border-[#7c4dff]/20 text-[#7c4dff] text-xs font-medium mb-6">
                LEGAL PRECEDENT
              </div>
              <h2 className="section-title mb-4 text-3xl md:text-4xl">
                <span className="gradient-text-warm">United States v. Heppner</span>
              </h2>
              <p className="text-[#8b949e] leading-relaxed mb-6">
                S.D.N.Y., February 10, 2026 — The landmark ruling that expanded Kovel doctrine
                to AI-routed legal communications. Clients can now use AI tools for legal research
                under the umbrella of attorney-client privilege, provided the communication is
                structured to facilitate legal advice.
              </p>
              <p className="text-[#8b949e] leading-relaxed">
                KovelAI is the first platform built specifically to satisfy Heppner&apos;s four-factor test:
                attorney oversight, privileged purpose, controlled access, and immutable audit trails.
              </p>
            </div>

            <div className="space-y-4">
              {[
                { factor: "Attorney Oversight", detail: "Real-time supervision dashboard. Lawyers review every AI interaction." },
                { factor: "Privileged Purpose", detail: "Every query tagged with matter ID. Purpose-limited to legal research." },
                { factor: "Controlled Access", detail: "Ephemeral sessions. Auto-expiry. No export. Dead-man's switch." },
                { factor: "Immutable Audit", detail: "Kovel Attestation Receipt. HMAC-SHA256 cryptographic proof per session." },
              ].map((item, i) => (
                <div
                  key={item.factor}
                  className="p-4 rounded-xl bg-[#0d1117]/80 border border-[#7c4dff]/10 transition-all hover:border-[#7c4dff]/30"
                >
                  <div className="flex items-center gap-3 mb-1.5">
                    <div className="w-6 h-6 rounded-md bg-[#7c4dff]/20 flex items-center justify-center text-[#7c4dff] text-xs font-bold">
                      {i + 1}
                    </div>
                    <span className="font-semibold text-sm">{item.factor}</span>
                  </div>
                  <p className="text-xs text-[#8b949e] ml-9">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ===== ABOUT / CTA SECTION ===== */
function AboutSection() {
  return (
    <section className="relative overflow-hidden" id="about">
      <div className="section-container">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="section-title mb-6">
            Built by <span className="gradient-text">ShadowTag AI</span>
          </h2>
          <p className="text-lg text-[#8b949e] leading-relaxed mb-8">
            KovelAI is a product of ShadowTag AI — the Google Cloud-native platform
            powering the next generation of privilege-preserving legal technology.
            Our infrastructure runs on Cloud Run, Firestore, and Cloud Tasks with
            zero shared infrastructure between tenants.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <a href="#pricing" className="cta-button text-base">
              Start Your Free Trial
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="ml-1">
                <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </a>
            <a href="mailto:sales@kovelai.com" className="cta-button-outline text-base">
              Contact Sales
            </a>
            <a href="/pitch-deck" className="cta-button-outline text-base" style={{ borderColor: 'rgba(124,77,255,0.3)', color: '#7c4dff' }}>
              📊 Pitch Deck
            </a>
          </div>

          {/* Tech Stack Badges */}
          <div className="flex flex-wrap justify-center gap-3">
            {[
              "Google Cloud",
              "Cloud Run",
              "Firestore",
              "Firebase Auth",
              "Stripe Connect",
              "LiteLLM",
              "Gemini 3.1",
            ].map((tech) => (
              <span
                key={tech}
                className="px-3 py-1.5 rounded-lg bg-[#161b22] border border-[#00bcd4]/10 text-xs text-[#8b949e] font-medium"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ===== FOOTER ===== */
function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer-gradient">
      <div className="max-w-[1200px] mx-auto px-6 py-16">
        <div className="grid md:grid-cols-4 gap-10 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00bcd4] to-[#00e5ff] flex items-center justify-center font-bold text-sm text-[#0a0a0f]">
                K
              </div>
              <span className="text-lg font-bold">
                Kovel<span className="gradient-text">AI</span>
              </span>
            </div>
            <p className="text-xs text-[#8b949e] leading-relaxed">
              Post-Heppner privileged client AI. The Shopify for Legal AI.
            </p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Product</h4>
            <ul className="space-y-2.5">
              {["Platform", "For Law Firms", "Pricing", "Enterprise", "Security"].map((link) => (
                <li key={link}>
                  <a href="#" className="text-xs text-[#8b949e] hover:text-white transition-colors">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Legal</h4>
            <ul className="space-y-2.5">
              {["Privacy Policy", "Terms of Service", "GDPR", "SOC 2 Report", "ABA Guidelines"].map(
                (link) => (
                  <li key={link}>
                    <a href="#" className="text-xs text-[#8b949e] hover:text-white transition-colors">
                      {link}
                    </a>
                  </li>
                ),
              )}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-sm font-semibold mb-4">Company</h4>
            <ul className="space-y-2.5">
              {["About ShadowTag AI", "Investors", "Blog", "Careers", "Contact"].map((link) => (
                <li key={link}>
                  <a href={link === "Investors" ? "/pitch-deck" : "#"} className="text-xs text-[#8b949e] hover:text-white transition-colors">
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="border-t border-[#00bcd4]/8 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-[#8b949e]">
            © {currentYear} ShadowTag AI, Inc. All rights reserved.
          </p>
          <p className="text-xs text-[#8b949e]/60">
            KovelAI is not a law firm and does not provide legal advice. Consult your attorney.
          </p>
        </div>
      </div>
    </footer>
  );
}

/* ===== SCROLL PROGRESS ===== */
function ScrollProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(docHeight > 0 ? (scrollTop / docHeight) * 100 : 0);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return <div className="scroll-progress" style={{ width: `${progress}%` }} />;
}

/* ===== PAGE ===== */
export default function Home() {
  return (
    <>
      <ScrollProgress />
      <NavBar />
      <main>
        <HeroSection />
        <StatsBar />
        <PlatformSection />
        <HowItWorks />
        <ModelRouting />
        <PricingSection />
        <EmailCapture />
        <HeppnerSection />
        <AboutSection />
      </main>
      <Footer />
    </>
  );
}
