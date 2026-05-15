import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About | KovelAI — Built by ShadowTagAI",
  description: "KovelAI is a product of ShadowTagAI. Learn about our mission to make legal AI privileged, profitable, and production-ready.",
};

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      <div className="h-[72px]" />

      {/* Hero */}
      <section className="section-container text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#7c4dff]/10 border border-[#7c4dff]/20 text-[#7c4dff] text-xs font-medium mb-8 tracking-wide">
          ABOUT US
        </div>
        <h1 className="section-title text-4xl md:text-5xl lg:text-6xl mb-6 max-w-3xl mx-auto">
          The <span className="gradient-text-warm">Shopify for Legal AI</span>
        </h1>
        <p className="section-subtitle mx-auto text-lg">
          We believe every law firm deserves AI that keeps them privileged and paid.
        </p>
      </section>

      {/* Mission */}
      <section className="section-container !pt-0">
        <div className="glass-card p-8 md:p-12 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-6">Our Mission</h2>
          <div className="space-y-4 text-[#8b949e] leading-relaxed">
            <p>
              <strong className="text-white">The post-Heppner legal landscape changed everything.</strong>{" "}
              United States v. Heppner (S.D.N.Y., Feb. 10, 2026) expanded Kovel doctrine to AI-routed
              legal communications — opening the door for clients to use AI research tools under
              attorney-client privilege for the first time.
            </p>
            <p>
              But the technology didn&apos;t exist. Law firms had no way to offer clients AI research
              that preserved privilege, generated revenue, maintained oversight, and produced
              court-ready attestation. Until KovelAI.
            </p>
            <p>
              We built KovelAI as the &quot;Shopify for Legal AI&quot; — a privilege-preserving routing tier
              between law firms and foundational LLMs (Gemini, Claude, ChatGPT, Grok, Google),
              protected under Heppner. Clients get AI. Lawyers get paid. Everyone stays privileged.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="section-container">
        <h2 className="section-title text-3xl text-center mb-12">
          <span className="gradient-text">Google Cloud-Native</span> Architecture
        </h2>
        <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            {
              layer: "Control Plane",
              items: ["Tenant registry", "Plan/tier logic", "Billing orchestration", "Model routing policy", "Audit metadata"],
              icon: "🎛️",
            },
            {
              layer: "Data Plane",
              items: ["Per-firm storage namespace", "Per-firm transcript path", "Per-firm model policy", "Per-firm billing attribution"],
              icon: "💾",
            },
            {
              layer: "Security Plane",
              items: ["Judge 6 policy gate", "Kovel attestation engine", "RBAC + tenant isolation", "Cloud Armor WAF"],
              icon: "🔒",
            },
          ].map((plane) => (
            <div key={plane.layer} className="glass-card p-6">
              <div className="text-3xl mb-3">{plane.icon}</div>
              <h3 className="text-lg font-semibold mb-3">{plane.layer}</h3>
              <ul className="space-y-2">
                {plane.items.map((item) => (
                  <li key={item} className="flex items-center gap-2 text-sm text-[#8b949e]">
                    <span className="w-1 h-1 rounded-full bg-[#00bcd4]" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="section-container">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="section-title text-3xl mb-6">
            Built by <span className="gradient-text">ShadowTagAI</span>
          </h2>
          <p className="text-[#8b949e] leading-relaxed mb-8">
            ShadowTagAI is a Google Cloud-native startup building the infrastructure layer for
            privilege-preserving legal technology. We are ex-FAANG engineers and practicing
            attorneys who believe legal AI should be secure, profitable, and code-grade.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            {["Google Cloud Partner", "SOC 2 Type II", "HIPAA BAA Available", "GDPR Compliant"].map((badge) => (
              <span key={badge} className="px-4 py-2 rounded-xl bg-[#161b22] border border-[#00bcd4]/10 text-sm text-[#8b949e] font-medium">
                {badge}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="section-container text-center">
        <div className="glass-card p-8 md:p-12 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Join the Post-Heppner Movement</h2>
          <p className="text-[#8b949e] mb-8">
            Be among the first law firms to offer privileged AI research to your clients.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/#pricing" className="cta-button text-base">
              Start Free Trial
            </a>
            <a href="/contact" className="cta-button-outline text-base">
              Schedule a Demo
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}
