export function AboutSection() {
  return (
    <section className="relative overflow-hidden" id="about">
      <div className="section-container">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="section-title mb-6">
            Built by <span className="gradient-text">ShadowTagAI</span>
          </h2>
          <p className="text-lg text-[#8b949e] leading-relaxed mb-8">
            KovelAI is a product of ShadowTagAI — the Google Cloud-native platform
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
