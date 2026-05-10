export function HowItWorks() {
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
