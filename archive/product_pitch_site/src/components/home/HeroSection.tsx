"use client";

import { useState, useEffect } from "react";

export const HERO_HEADLINES = [
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

export function HeroSection() {
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
