export default function DiscoveryRisk() {
  const cards = [
    {
      icon: '🛡️',
      title: 'Client Searches Protected',
      desc: "Your client's web and AI research flows through a privilege-protected connection to your firm. Opposing counsel cannot discover what doesn\u0027t exist outside the privilege umbrella.",
    },
    {
      icon: '👁️',
      title: 'Attorney Stays in the Loop',
      desc: 'Every search, every AI query, every session — visible to you in real time. No more being ambushed by random discoverable searches your client ran at 2 AM.',
    },
    {
      icon: '💳',
      title: 'Billing Built Into Access',
      desc: 'Clients use their credit card to log in. You bill in accordance with the Rules of Professional Responsibility. Revenue flows automatically at the end of each billing cycle.',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="discovery-risk">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">The Heppner Problem</div>
        <h2 className="section-title">
          After <em>Heppner</em>, Your Client&apos;s Internet Is a Liability.
        </h2>
        <p className="section-desc mb-12">
          After <em>In re Heppner</em>, any client web search or AI interaction conducted outside
          privileged channels is discoverable in litigation. CounselConduit solves this — your
          client searches freely through a secure portal, you see everything, you give the first
          legal opinion, and you bill for the protection.
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
