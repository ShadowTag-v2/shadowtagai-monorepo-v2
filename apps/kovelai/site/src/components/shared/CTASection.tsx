'use client';

interface CTASectionProps {
  onOpenModal?: () => void;
}

export default function CTASection({ onOpenModal }: CTASectionProps) {
  return (
    <section className="py-20 md:py-28" id="contact">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="section-label">Deploy Protection</div>
        <h2 className="section-title mx-auto" style={{ maxWidth: 700 }}>
          Your Clients Are Searching Right Now. You Should Be in the Loop.
        </h2>
        <p className="section-desc mx-auto mb-4">
          Every unprotected search your client runs is another liability on your desk. They&apos;re
          Googling their case, asking ChatGPT for legal opinions, and sending you discoverable
          research at random hours.
        </p>
        <p className="section-desc mx-auto mb-10">
          Deploy CounselConduit — give your clients a privileged portal where they can search
          freely. You see everything, you provide the first legal opinion, and opposing counsel
          can&apos;t discover a word of it.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            type="button"
            onClick={onOpenModal}
            className="btn-gold text-base py-3 px-8"
            id="ctaBottomTrial"
          >
            Start Free Trial
          </button>
          <button type="button" onClick={onOpenModal} className="btn-ghost text-base py-3 px-8">
            Schedule a Demo
          </button>
        </div>
      </div>
    </section>
  );
}
