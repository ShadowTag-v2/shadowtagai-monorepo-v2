export default function DiscoveryRisk() {
  const cards = [
    {
      icon: "⚖️",
      title: "Privilege Shield",
      desc: "All client web activity routed through your firm's privileged infrastructure. Zero discoverable footprint.",
    },
    {
      icon: "🔒",
      title: "Zero Data Retention",
      desc: "No search logs, no browsing history, no metadata. The data that doesn't exist can't be subpoenaed.",
    },
    {
      icon: "💰",
      title: "Revenue at the Front Door",
      desc: "Clients pay for privileged access. Your firm captures intake revenue 24/7, even after hours.",
    },
  ];

  return (
    <section className="py-20 md:py-28" id="discovery-risk">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">The Heppner Problem</div>
        <h2 className="section-title">Your Clients&apos; Internet Searches Are Discoverable.</h2>
        <p className="section-desc mb-12">
          After <em>In re Heppner</em>, any client web search conducted outside privileged channels
          is fair game in litigation. This includes Google searches, legal research, and even AI
          chatbot interactions. KovelAI wraps these activities under attorney-client privilege — and
          bills for the protection.
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
