'use client';

interface CTASectionProps {
  onOpenModal?: () => void;
}

export default function CTASection({ onOpenModal }: CTASectionProps) {
  return (
    <section className="py-20 md:py-28" id="contact">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="section-label">Get Started</div>
        <h2 className="section-title mx-auto" style={{ maxWidth: 700 }}>
          Your Clients Are Searching Right Now. Are Those Searches Protected?
        </h2>
        <p className="section-desc mx-auto mb-10">
          Every hour you wait is another hour your clients&apos; web and AI searches are exposed to
          discovery. Deploy CounselConduit for your practice — protect your clients, gain
          visibility, and bill automatically.
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
