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
              Erik founded KovelAI after watching attorneys get blindsided by discoverable client
              searches post-<em>Heppner</em>. His mission: give every attorney a turnkey portal they
              can deploy for their clients — privileged web and AI search access that protects the
              client, empowers the attorney, and bills automatically.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
