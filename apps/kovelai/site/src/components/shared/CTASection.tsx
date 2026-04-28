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
          Your Clients Are Searching Right Now. Deploy Their Portal Today.
        </h2>
        <p className="section-desc mx-auto mb-4">
          Your clients are Googling their case, asking ChatGPT for legal opinions, and creating
          discoverable evidence with every search. After <em>Heppner</em>, the other side can — and
          will — obtain all of it.
        </p>
        <p className="section-desc mx-auto mb-10">
          Deploy KovelAI for your clients. You buy it, they use it, you monitor everything. Like a
          medical portal, except for lawyers — their research stays privileged, you give the first
          legal opinion, and opposing counsel discovers nothing. Either they do it through your
          firm&apos;s KovelAI, or they proceed at their peril.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            type="button"
            onClick={onOpenModal}
            className="btn-gold text-base py-3 px-8"
            id="ctaBottomTrial"
          >
            Deploy for Your Clients
          </button>
          <button type="button" onClick={onOpenModal} className="btn-ghost text-base py-3 px-8">
            Schedule a Demo
          </button>
        </div>
      </div>
    </section>
  );
}
