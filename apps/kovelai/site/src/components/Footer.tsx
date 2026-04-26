export default function Footer() {
  return (
    <footer className="border-t border-[rgba(77,70,58,0.15)] pt-12 pb-6">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-10 mb-10">
          <div>
            <div className="text-xl font-bold text-primary-text mb-3">KovelAI</div>
            <p className="text-sm text-secondary-text leading-relaxed">
              Post-Heppner privileged client AI and web search infrastructure for law firms.
              Capture revenue, protect privilege, automate intake.
            </p>
          </div>
          <div>
            <div className="footer-heading">Platform</div>
            <ul className="footer-links">
              <li><a href="#features">Features</a></li>
              <li><a href="#how-it-works">How It Works</a></li>
              <li><a href="#discovery-risk">Discovery Risk</a></li>
            </ul>
          </div>
          <div>
            <div className="footer-heading">Company</div>
            <ul className="footer-links">
              <li><a href="#management">Leadership</a></li>
              <li><a href="/privacy">Privacy Policy</a></li>
              <li><a href="/terms">Terms of Service</a></li>
              <li><a href="#blog">Blog</a></li>
            </ul>
          </div>
          <div>
            <div className="footer-heading">Contact</div>
            <ul className="footer-links">
              <li><a href="#" onClick={(e) => { e.preventDefault(); document.getElementById('contactModal')?.classList.add('modal-overlay--visible'); }}>Contact Sales</a></li>
              <li><a href="mailto:founder@shadowtagai.com">Email</a></li>
              <li><a href="https://shadowtagai.web.app" target="_blank" rel="noopener noreferrer">ShadowTagAI ↗</a></li>
            </ul>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row justify-between items-center gap-2 pt-6 border-t border-[rgba(77,70,58,0.1)] text-xs text-[#998f81]">
          <span>© 2024–2026 KovelAI. All rights reserved.</span>
          <span>
            A{' '}
            <a href="https://shadowtagai.web.app" className="text-gold underline">
              ShadowTag AI
            </a>{' '}
            Company
          </span>
        </div>
      </div>
    </footer>
  );
}
