export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Connect',
      desc: "Your clients access KovelAI through your firm's branded portal. Every session is logged under privilege.",
    },
    {
      num: '02',
      title: 'Protect',
      desc: 'Web searches, AI queries, and document uploads are routed through privileged infrastructure. Zero exposure.',
    },
    {
      num: '03',
      title: 'Bill',
      desc: 'Each privileged session generates billable entries. After-hours intake converts to retained matters automatically.',
    },
  ];

  return (
    <section className="py-20 md:py-28" id="how-it-works">
      <div className="max-w-[1140px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="section-label">Process</div>
        <h2 className="section-title">Three Steps to Privileged Revenue</h2>
        <div className="grid md:grid-cols-3 gap-8 mt-10">
          {steps.map((s) => (
            <div key={s.num} className="glass-card text-center">
              <div className="text-5xl font-extrabold text-gold leading-none mb-4">{s.num}</div>
              <h3 className="text-lg font-semibold text-primary-text mb-2">{s.title}</h3>
              <p className="text-sm leading-relaxed text-secondary-text">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
