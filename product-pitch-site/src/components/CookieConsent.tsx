"use client";

import { useState, useEffect } from "react";

/**
 * Item 16: GDPR Cookie Consent Banner
 * Stores consent in localStorage. Only loads GA4 after user accepts.
 * Minimal, non-intrusive design matching the KovelAI glass aesthetic.
 */
export default function CookieConsent() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem("kovelai_cookie_consent");
    if (!consent) {
      // Delay banner appearance for better UX
      const timer = setTimeout(() => setVisible(true), 2000);
      return () => clearTimeout(timer);
    }
  }, []);

  const accept = () => {
    localStorage.setItem("kovelai_cookie_consent", "accepted");
    setVisible(false);
    // Reload to activate GA4 if needed
    window.location.reload();
  };

  const decline = () => {
    localStorage.setItem("kovelai_cookie_consent", "declined");
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-[9999] p-4 md:p-6 animate-slideUp"
      style={{ animation: "slideUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards" }}
    >
      <div className="max-w-4xl mx-auto bg-[#161b22]/95 backdrop-blur-xl border border-[#30363d] rounded-2xl p-5 md:p-6 flex flex-col md:flex-row items-start md:items-center gap-4 shadow-2xl shadow-black/40">
        <div className="flex-1">
          <p className="text-sm text-[#c9d1d9] leading-relaxed">
            <span className="font-semibold text-white">We value your privacy.</span>{" "}
            We use cookies for analytics (Google Analytics 4) to improve your experience.
            No tracking cookies are used for advertising.{" "}
            <a
              href="/privacy"
              className="text-[#00bcd4] hover:underline"
            >
              Privacy Policy
            </a>
          </p>
        </div>
        <div className="flex gap-3 shrink-0">
          <button
            onClick={decline}
            className="px-5 py-2.5 text-sm font-medium text-[#8b949e] hover:text-white border border-[#30363d] hover:border-[#484f58] rounded-xl transition-all duration-200"
          >
            Decline
          </button>
          <button
            onClick={accept}
            className="px-5 py-2.5 text-sm font-medium text-[#0a0a0f] bg-gradient-to-r from-[#00bcd4] to-[#00e5ff] rounded-xl hover:shadow-lg hover:shadow-[#00bcd4]/20 transition-all duration-200"
          >
            Accept
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes slideUp {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}
