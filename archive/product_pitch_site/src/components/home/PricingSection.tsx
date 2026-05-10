"use client";

import { useState } from "react";

export function PricingSection() {
  const [loadingTier, setLoadingTier] = useState<string | null>(null);

  const plans = [
    {
      name: "Consumer Syndicate",
      tier: "solo" as const,
      price: "$149",
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
      name: "Enterprise Base SLA",
      tier: "practice" as const,
      price: "$20,000",
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
      cta: "Contact Sales",
      featured: true,
      badge: "Most Popular",
    },
    {
      name: "Enterprise EU26 Premium",
      tier: "enterprise" as const,
      price: "$28,333",
      period: "/mo",
      description: "For Am Law 200 firms. Dedicated infrastructure. Zero compromise.",
      features: [
        "Everything in Base SLA",
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
