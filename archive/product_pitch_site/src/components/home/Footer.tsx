export function Footer() {
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
              {["About ShadowTagAI", "Investors", "Blog", "Careers", "Contact"].map((link) => (
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
            © {currentYear} ShadowTagAI, Inc. All rights reserved.
          </p>
          <p className="text-xs text-[#8b949e]/60">
            KovelAI is not a law firm and does not provide legal advice. Consult your attorney.
          </p>
        </div>
      </div>
    </footer>
  );
}
