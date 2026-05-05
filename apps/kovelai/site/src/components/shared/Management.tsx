import Image from 'next/image';

export default function Management() {
  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="management">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Leadership</div>
        <h2 className="section-title">Management</h2>
        <div className="ceo-card mt-10">
          <div className="ceo-photo-col">
            <Image
              src="/images/ceo-headshot.jpg"
              alt="Erik L. Hancock, JD — Founder & CEO of KovelAI"
              className="ceo-headshot"
              width={180}
              height={180}
              priority={false}
            />
            <div className="ceo-social">
              <a
                href="https://linkedin.com/in/erik-hancock-80442476"
                target="_blank"
                rel="noopener noreferrer"
                className="ceo-linkedin"
                aria-label="Erik Hancock on LinkedIn"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  aria-labelledby="linkedin-title"
                  role="img"
                >
                  <title id="linkedin-title">LinkedIn Icon</title>
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
                LinkedIn
              </a>
              <a
                href="https://x.com/KovelAi_Inc"
                target="_blank"
                rel="noopener noreferrer"
                className="ceo-x"
                aria-label="KovelAI on X"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  aria-labelledby="x-title"
                  role="img"
                >
                  <title id="x-title">X Icon</title>
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
                X
              </a>
            </div>
          </div>
          <div>
            <h3 className="text-xl font-semibold text-primary-text mb-1">Erik L. Hancock, JD</h3>
            <div className="text-sm text-gold mb-3 font-medium">Founder — CEO</div>
            <p className="text-sm leading-relaxed text-secondary-text mb-4">
              Erik founded KovelAI to solve the post-<em>Heppner</em> privilege gap that leaves law
              firms and their clients exposed. With a background in legal technology and AI
              infrastructure, he leads the company&apos;s mission to make privileged access the
              default — not the exception — for every client interaction.
            </p>
            <div className="ceo-contact-grid">
              <div className="ceo-contact-item">
                <span className="ceo-contact-label">Company</span>
                <span className="ceo-contact-value">ShadowTagAi Inc.</span>
              </div>
              <div className="ceo-contact-item">
                <span className="ceo-contact-label">Address</span>
                <span className="ceo-contact-value">
                  495 N Main St., #119
                  <br />
                  Lakeport, CA 95453
                </span>
              </div>
              <div className="ceo-contact-item">
                <span className="ceo-contact-label">Telephone</span>
                <a href="tel:+13692355643" className="ceo-contact-value ceo-contact-link">
                  (369) 235-5643
                </a>
              </div>
              <div className="ceo-contact-item">
                <span className="ceo-contact-label">Facsimile</span>
                <span className="ceo-contact-value">(707) 263-8659</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
