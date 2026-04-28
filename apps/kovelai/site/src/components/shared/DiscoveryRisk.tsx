export default function DiscoveryRisk() {
  const cards = [
    {
      icon: '🛡️',
      title: 'You Deploy Protection for Your Clients',
      desc: "Like a police chief buying bulletproof vests for the force — you purchase KovelAI as privileged infrastructure for your clients. Their web and AI research flows through a secure connection to your firm. What they search stays inside the privilege umbrella. The other side can't discover it, because it never existed outside your protection.",
    },
    {
      icon: '🧠',
      title: 'Clients Search Freely, Recall Everything',
      desc: 'Your clients can search whenever anxiety strikes — nights, weekends, 3 AM before a hearing. KovelAI lets them relax enough to recall all the facts of their case and explore their concerns without creating discoverable evidence. No more panic-googling that hands the other side ammunition.',
    },
    {
      icon: '👁️',
      title: 'You Sit in the Loop on Every Session',
      desc: 'Every search, every AI query, every session — visible to you in real time. You give the first legal opinion instead of being ambushed by your client sending you incorrect AI-generated legal conclusions at random hours. You bill their credit card at the end of the billing cycle, in full compliance with the Rules of Professional Responsibility.',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="discovery-risk">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">The Heppner Ultimatum</div>
        <h2 className="section-title">
          &ldquo;Either You Do It Through Our Portal, or Proceed at Your Peril.&rdquo;
        </h2>
        <p className="section-desc mb-12">
          That&apos;s the conversation. After <em>In re Heppner</em> (S.D.N.Y., Feb. 2026), every
          web search, AI interaction, and digital footprint your client creates outside your firm is
          discoverable. Opposing counsel can subpoena it, weaponize it, and ambush you at trial.
          KovelAI is not a nice-to-have — it&apos;s mandatory privileged infrastructure you deploy
          for every active case. The client understands the risk. They&apos;re happy to pay for
          protection — it&apos;s their case on the line.
        </p>
        <div className="grid md:grid-cols-3 gap-6">
          {cards.map((c) => (
            <div key={c.title} className="glass-card">
              <div className="text-2xl mb-3">{c.icon}</div>
              <h3 className="text-base font-semibold text-primary-text mb-2">{c.title}</h3>
              <p className="text-sm leading-relaxed text-secondary-text">{c.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
