"use client";

import { useState } from "react";

export function PlatformSection() {
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
