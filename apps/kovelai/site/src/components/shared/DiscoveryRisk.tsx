export default function DiscoveryRisk() {
  const cards = [
    {
      icon: '🛡️',
      title: 'Your Client Is Protected',
      desc: "Your client's web and AI research flows through a secure, privilege-protected connection to your firm. What they search stays inside the privilege umbrella — opposing counsel cannot discover it, because it never existed outside your protection.",
    },
    {
      icon: '🧠',
      title: 'Clients Relax, Recall, Research',
      desc: 'Your clients can search at will — nights, weekends, 3 AM before a hearing. CounselConduit lets them relax enough to recall all the facts of their case, explore their concerns, and prepare mentally for trial — without creating discoverable evidence.',
    },
    {
      icon: '👁️',
      title: 'You Monitor the Entire Cycle',
      desc: "Every search, every AI query, every session — visible to you in real time. You give the first legal opinion instead of being surprised. You bill your client's credit card at the end of the billing cycle, in full compliance with the Rules of Professional Responsibility.",
    },
  ];

  return (
    <section className="py-20 md:py-28" id="discovery-risk">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">The Heppner Problem</div>
        <h2 className="section-title">
          After <em>Heppner</em>, Your Client&apos;s Internet Is a Weapon Against Them.
        </h2>
        <p className="section-desc mb-12">
          After <em>In re Heppner</em>, every web search and AI interaction your client conducts
          outside of your privileged infrastructure is discoverable. Opposing counsel can subpoena
          it, weaponize it, and ambush you at trial. CounselConduit protects your clients by routing
          their research through a secure connection to your firm — they search freely, you see
          everything, and the privilege holds.
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
