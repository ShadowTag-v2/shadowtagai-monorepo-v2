import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Contact Sales | KovelAI",
  description: "Get in touch with the KovelAI sales team. Enterprise inquiries, custom deployments, and partnership opportunities.",
};

export default function ContactPage() {
  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      <div className="h-[72px]" />

      <section className="section-container">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#00bcd4]/10 border border-[#00bcd4]/20 text-[#00bcd4] text-xs font-medium mb-8 tracking-wide">
              CONTACT SALES
            </div>
            <h1 className="section-title text-4xl md:text-5xl mb-4">
              Let&apos;s Talk <span className="gradient-text">Legal AI</span>
            </h1>
            <p className="section-subtitle mx-auto">
              Whether you&apos;re a solo practitioner or an Am Law 200 firm, we&apos;ll help you launch
              your privileged AI portal.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Contact Form */}
            <div className="glass-card p-8">
              <h2 className="text-xl font-semibold mb-6">Send us a message</h2>
              <form className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-[#8b949e] mb-1.5">
                    Full Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#161b22] border border-[#00bcd4]/15 text-white text-sm focus:outline-none focus:border-[#00bcd4]/50 transition-colors"
                    placeholder="Jane Doe"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-[#8b949e] mb-1.5">
                    Work Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#161b22] border border-[#00bcd4]/15 text-white text-sm focus:outline-none focus:border-[#00bcd4]/50 transition-colors"
                    placeholder="jane@firmname.com"
                  />
                </div>
                <div>
                  <label htmlFor="firm" className="block text-sm font-medium text-[#8b949e] mb-1.5">
                    Firm Name
                  </label>
                  <input
                    type="text"
                    id="firm"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#161b22] border border-[#00bcd4]/15 text-white text-sm focus:outline-none focus:border-[#00bcd4]/50 transition-colors"
                    placeholder="Doe & Associates LLP"
                  />
                </div>
                <div>
                  <label htmlFor="size" className="block text-sm font-medium text-[#8b949e] mb-1.5">
                    Firm Size
                  </label>
                  <select
                    id="size"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#161b22] border border-[#00bcd4]/15 text-white text-sm focus:outline-none focus:border-[#00bcd4]/50 transition-colors appearance-none"
                  >
                    <option value="">Select firm size</option>
                    <option value="solo">Solo Practitioner</option>
                    <option value="small">2-10 Attorneys</option>
                    <option value="mid">11-50 Attorneys</option>
                    <option value="large">51-200 Attorneys</option>
                    <option value="amlw">Am Law 200+</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-[#8b949e] mb-1.5">
                    Message
                  </label>
                  <textarea
                    id="message"
                    rows={4}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#161b22] border border-[#00bcd4]/15 text-white text-sm focus:outline-none focus:border-[#00bcd4]/50 transition-colors resize-none"
                    placeholder="Tell us about your needs..."
                  />
                </div>
                <button type="submit" className="cta-button w-full justify-center mt-2">
                  Send Inquiry
                </button>
              </form>
            </div>

            {/* Contact Info */}
            <div className="space-y-6">
              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-2">📧 Email</h3>
                <p className="text-sm text-[#8b949e]">
                  Sales: <a href="mailto:sales@kovelai.com" className="text-[#00bcd4] hover:underline">sales@kovelai.com</a>
                </p>
                <p className="text-sm text-[#8b949e] mt-1">
                  Support: <a href="mailto:support@kovelai.com" className="text-[#00bcd4] hover:underline">support@kovelai.com</a>
                </p>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-2">📅 Schedule a Demo</h3>
                <p className="text-sm text-[#8b949e] mb-3">
                  See KovelAI in action. 30-minute live demo with a product specialist.
                </p>
                <a href="#" className="cta-button-outline text-sm">
                  Book a Demo Call
                </a>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-2">🏢 Enterprise</h3>
                <p className="text-sm text-[#8b949e]">
                  For Am Law 200 firms requiring dedicated infrastructure, BYOC/BYOK,
                  or FedRAMP compliance, contact our enterprise team directly.
                </p>
              </div>

              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold mb-2">📰 Media Inquiries</h3>
                <p className="text-sm text-[#8b949e]">
                  Press: <a href="mailto:press@shadowtagai.com" className="text-[#00bcd4] hover:underline">press@shadowtagai.com</a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
