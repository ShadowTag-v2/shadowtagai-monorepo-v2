import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Products | KovelAI — Platform Overview",
  description: "Explore KovelAI's product suite: Client AI Portal, Lawyer Oversight Dashboard, Oracle Memo Pipeline, and Kovel Attestation System.",
};

export default function ProductsPage() {
  const products = [
    {
      name: "Client AI Portal",
      tagline: "Ephemeral. Privileged. Multi-Model.",
      description: "A sleek client-facing research interface supporting Gemini, Claude, ChatGPT, Grok, Google Search, and Google Translate. Auto-logout with screen wipe. No export. No copy. Dead-man's switch ensures zero data persistence outside the session.",
      features: [
        "Multi-model selector with real-time streaming",
        "Ephemeral session architecture — nothing persists client-side",
        "Per-query Kovel Attestation with HMAC-SHA256",
        "Auto-logout after configurable inactivity period",
        "Dead-man's switch: screen wipe on session end",
        "Mobile-responsive with touch-optimized UI",
      ],
      icon: "👤",
      color: "#00bcd4",
    },
    {
      name: "Lawyer Dashboard",
      tagline: "Real-time oversight. Zero latency.",
      description: "Monitor every client AI session in real-time. View immutable transcripts, query analytics, billing breakdowns, and compliance status from a single pane of glass.",
      features: [
        "Real-time session monitoring",
        "Immutable transcript archive (Firestore-backed)",
        "Per-client, per-model billing analytics",
        "Compliance status and audit logs",
        "Team management with role-based access",
        "Export-ready compliance reports",
      ],
      icon: "⚖️",
      color: "#7c4dff",
    },
    {
      name: "Oracle Memo",
      tagline: "7-stage AI analysis pipeline.",
      description: "Automated legal memo generation with multi-model consensus, citation verification, risk scoring, and privilege tagging. From raw query to court-ready memorandum in under 60 seconds.",
      features: [
        "Multi-model consensus (3+ model cross-validation)",
        "Citation verification against legal databases",
        "Risk scoring (low / medium / high / critical)",
        "Privilege tagging with Kovel doctrine alignment",
        "Structured output: IRAC format with headnotes",
        "SSE streaming for real-time generation feedback",
      ],
      icon: "📋",
      color: "#e040fb",
    },
    {
      name: "Kovel Attestation System",
      tagline: "Cryptographic proof of privilege.",
      description: "Every client-AI session generates a tamper-evident Kovel Attestation Receipt — a cryptographic hash proving the communication occurred under attorney-client privilege per Heppner's four-factor test.",
      features: [
        "HMAC-SHA256 cryptographic hash per session",
        "Heppner four-factor compliance metadata",
        "Tamper-evident chain linking sessions to matters",
        "Export-ready for discovery and court proceedings",
        "Automated GDPR 30-day deletion via Cloud Tasks",
        "Evidence-grade audit trail",
      ],
      icon: "🛡️",
      color: "#00e5ff",
    },
  ];

  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      {/* Navigation placeholder — shares with layout */}
      <div className="h-[72px]" />

      {/* Hero */}
      <section className="section-container text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#00bcd4]/10 border border-[#00bcd4]/20 text-[#00bcd4] text-xs font-medium mb-8 tracking-wide">
          PRODUCT SUITE
        </div>
        <h1 className="section-title text-4xl md:text-5xl lg:text-6xl mb-6 max-w-3xl mx-auto">
          Everything Your Firm Needs to{" "}
          <span className="gradient-text">Ship Legal AI</span>
        </h1>
        <p className="section-subtitle mx-auto text-lg">
          Four integrated products. One platform. Zero privilege risk.
        </p>
      </section>

      {/* Product Cards */}
      <section className="section-container !pt-0">
        <div className="space-y-8">
          {products.map((product, i) => (
            <div
              key={product.name}
              className="glass-card p-8 md:p-10"
            >
              <div className="grid md:grid-cols-[300px_1fr] gap-8 items-start">
                {/* Product Identity */}
                <div>
                  <div
                    className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl mb-4"
                    style={{ background: `${product.color}15`, border: `1px solid ${product.color}30` }}
                  >
                    {product.icon}
                  </div>
                  <h2 className="text-2xl font-bold mb-1">{product.name}</h2>
                  <p className="text-sm font-medium" style={{ color: product.color }}>
                    {product.tagline}
                  </p>
                </div>

                {/* Product Details */}
                <div>
                  <p className="text-[#8b949e] leading-relaxed mb-6">
                    {product.description}
                  </p>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {product.features.map((feature) => (
                      <div key={feature} className="flex items-start gap-2.5">
                        <svg className="w-4 h-4 mt-0.5 shrink-0" viewBox="0 0 16 16" fill={product.color}>
                          <path d="M13.854 3.646a.5.5 0 010 .708l-7 7a.5.5 0 01-.708 0l-3.5-3.5a.5.5 0 11.708-.708L6.5 10.293l6.646-6.647a.5.5 0 01.708 0z"/>
                        </svg>
                        <span className="text-sm text-[#c9d1d9]">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="section-container text-center">
        <h2 className="section-title text-3xl mb-4">
          Ready to <span className="gradient-text">get started</span>?
        </h2>
        <p className="section-subtitle mx-auto mb-8">
          Launch your firm&apos;s AI portal in under 15 minutes.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a href="/#pricing" className="cta-button text-base">
            Start Free Trial
          </a>
          <a href="/contact" className="cta-button-outline text-base">
            Talk to Sales
          </a>
        </div>
      </section>
    </main>
  );
}
