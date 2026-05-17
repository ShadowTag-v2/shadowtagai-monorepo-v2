"use client";

interface CTASectionProps {
  onOpenModal?: () => void;
}

export default function CTASection({ onOpenModal }: CTASectionProps) {
  return (
    <section className="py-20 md:py-28" id="contact">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="section-label">Get Started</div>
        <h2 className="section-title mx-auto" style={{ maxWidth: 700 }}>
          Your Clients Are Googling Right Now. Is That Search Privileged?
        </h2>
        <p className="section-desc mx-auto mb-10">
          Every hour without KovelAI is another hour of discoverable client web activity. Start your
          free trial in 60 seconds — no credit card, no commitment, full Kovel Doctrine protection
          from day one.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <a
            href="https://buy.stripe.com/test_aEU5nR1Jy9Mg8zS000"
            className="btn-gold text-base py-3 px-8"
            id="ctaBottomTrial"
          >
            Start Free Trial
          </a>
          <button type="button" onClick={onOpenModal} className="btn-ghost text-base py-3 px-8">
            Schedule a Demo
          </button>
        </div>
      </div>
    </section>
  );
}
