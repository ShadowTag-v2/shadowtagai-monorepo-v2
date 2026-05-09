export function HeppnerSection() {
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
