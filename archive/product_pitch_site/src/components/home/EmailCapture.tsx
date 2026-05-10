"use client";

import { trackEvent } from "@/lib/analytics";
import { useState } from "react";

export function EmailCapture() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || submitted) return;
    setLoading(true);
    trackEvent("email_capture", { source: "pricing_bottom" });
    // Fire-and-forget to Google Apps Script or Cloud Function
    try {
      await fetch("https://script.google.com/macros/s/AKfycbzE_placeholder/exec", {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source: "kovelai-pitch", timestamp: new Date().toISOString() }),
      });
    } catch {
      // no-cors means we can't read the response — that's ok
    }
    setSubmitted(true);
    setLoading(false);
  }

  return (
    <section className="section-container" id="early-access">
      <div className="max-w-xl mx-auto text-center">
        <h2 className="text-2xl md:text-3xl font-bold mb-3">
          Get <span className="gradient-text">Early Access</span>
        </h2>
        <p className="text-sm text-[#8b949e] mb-6">
          Join the waitlist. We&apos;ll notify you when your firm&apos;s portal is ready.
        </p>
        {submitted ? (
          <div className="glass-card p-6 text-center">
            <div className="text-2xl mb-2">✓</div>
            <p className="text-[#00bcd4] font-medium">You&apos;re on the list!</p>
            <p className="text-xs text-[#8b949e] mt-1">We&apos;ll be in touch within 48 hours.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-3 items-stretch">
            <input
              type="email"
              required
              placeholder="partner@firmname.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 px-4 py-3 rounded-xl bg-[#161b22] border border-[#30363d] text-white text-sm placeholder:text-[#484f58] focus:border-[#00bcd4] focus:outline-none focus:ring-1 focus:ring-[#00bcd4]/30 transition-colors"
            />
            <button
              type="submit"
              disabled={loading}
              className="cta-button !py-3 whitespace-nowrap"
            >
              {loading ? "Joining…" : "Join Waitlist"}
            </button>
          </form>
        )}
        <p className="text-[10px] text-[#8b949e]/50 mt-3">
          No spam. Unsubscribe anytime. Your email is never shared.
        </p>
      </div>
    </section>
  );
}
