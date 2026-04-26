export default function Management() {
  return (
    <section className="py-20 md:py-28 bg-surface-lowest" id="management">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Leadership</div>
        <h2 className="section-title">Management</h2>
        <div className="ceo-card mt-10">
          <div className="ceo-headshot bg-surface-high flex items-center justify-center text-gold text-3xl font-bold">
            EH
          </div>
          <div>
            <h3 className="text-lg font-semibold text-primary-text mb-1">Erik Hancock</h3>
            <div className="text-sm text-gold mb-3">Founder &amp; CEO</div>
            <p className="text-sm leading-relaxed text-secondary-text">
              Erik founded KovelAI to solve the post-<em>Heppner</em> privilege gap that leaves law
              firms and their clients exposed. With a background in legal technology and AI
              infrastructure, he leads the company&apos;s mission to make privileged access the
              default — not the exception — for every client interaction.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
